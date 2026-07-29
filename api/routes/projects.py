import asyncio
import io
import os
import smtplib
import tempfile
import zipfile
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

from core.ai_planner import generate_project_plan
from core.audio_transcriber import transcribe_audio
from core.image_analyzer import analyze_images
from core.models import PricingEstimate, ProjectPlan
from core.pricing import calculate_pricing
from core.project_generator import create_project
from core.web_scraper import format_scraped_content, scrape_urls

router = APIRouter(tags=["projects"])


def _send_project_zip(project_path: Path, project_name: str, to_email: str, from_user: str, from_password: str) -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in project_path.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(project_path.parent))
    buf.seek(0)

    msg = EmailMessage()
    msg["Subject"] = f"ProspecMan: {project_name}"
    msg["From"] = from_user
    msg["To"] = to_email
    msg.set_content(
        f'Seu projeto "{project_name}" foi gerado pelo ProspecMan.\n\n'
        "Em anexo: estrutura completa do projeto (README, CLAUDE.md, arquivos de configuração)."
    )
    msg.add_attachment(buf.read(), maintype="application", subtype="zip", filename=f"{project_name}.zip")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_user, from_password)
        smtp.send_message(msg)


class ProjectResponse(BaseModel):
    success: bool
    project_name: str
    project_slug: str
    project_type: str
    project_path: str
    plan: ProjectPlan
    created_at: str
    timeline_days: int
    cost_monthly_usd: float
    cost_monthly_brl: float
    free_tier_viable: bool
    pricing: PricingEstimate
    total_hours: float
    recommended_price_brl: float
    recommended_price_usd: float


@router.post("/projects", response_model=ProjectResponse)
async def create_project_endpoint(
    request: Request,
    audio: Optional[UploadFile] = File(None),
    transcript: Optional[str] = Form(None),
    urls: List[str] = Form(default=[]),
    language: str = Form(default="pt"),
    open_vscode: bool = Form(default=False),
    images: List[UploadFile] = File(default=[]),
    email: Optional[str] = Form(None),
    hourly_rate_brl: Optional[float] = Form(None),
):
    """
    Gera uma estrutura de projeto completa a partir de briefing.

    - **audio**: arquivo de audio com o briefing (.mp3, .m4a, .wav, etc.)
    - **transcript**: texto do briefing como alternativa ao audio
    - **urls**: URLs de referencia (repita o campo para multiplas)
    - **images**: imagens de referencia (repita o campo para multiplas)
    - **language**: idioma da transcricao (padrao: pt)
    - **open_vscode**: abrir VS Code apos criar o projeto (padrao: false)
    - **hourly_rate_brl**: valor/hora para a estimativa de precificacao (padrao: config do servidor)
    """
    if not audio and not transcript:
        raise HTTPException(
            status_code=400,
            detail="Forneca 'audio' (arquivo) ou 'transcript' (texto do briefing).",
        )

    settings = request.app.state.settings
    temp_files: list[str] = []

    try:
        # Transcricao de audio
        final_transcript = transcript or ""
        if audio and audio.filename:
            suffix = Path(audio.filename).suffix or ".mp3"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(await audio.read())
            tmp.close()
            temp_files.append(tmp.name)
            # transcribe_audio é bloqueante — roda em thread para não bloquear o event loop
            final_transcript = await asyncio.to_thread(
                transcribe_audio, tmp.name, settings.groq_api_key, language
            )

        # Web scraping — scrape_urls usa asyncio.run() internamente, precisa de thread separada
        scraped_content = ""
        valid_urls = [u for u in urls if u.strip()]
        if valid_urls:
            scraped = await asyncio.to_thread(scrape_urls, valid_urls)
            scraped_content = format_scraped_content(scraped)

        # Analise de imagens
        image_paths: list[str] = []
        for img in images:
            if img and img.filename:
                suffix = Path(img.filename).suffix or ".jpg"
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(await img.read())
                tmp.close()
                image_paths.append(tmp.name)
                temp_files.append(tmp.name)

        image_descriptions = ""
        if image_paths:
            image_descriptions = await asyncio.to_thread(
                analyze_images, image_paths, settings.anthropic_api_key
            )

        # Geracao do plano com Claude
        plan = await asyncio.to_thread(
            generate_project_plan,
            final_transcript,
            scraped_content,
            image_descriptions,
            settings.anthropic_api_key,
            settings.usd_to_brl_rate,
        )

        # Calculo da precificacao (deterministico, sem IA) a partir das horas/complexidade do plano
        pricing = calculate_pricing(
            plan,
            hourly_rate_brl or settings.default_hourly_rate_brl,
            settings.usd_to_brl_rate,
        )

        # Criacao da estrutura de pastas no PC
        output_dir = settings.default_output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        project_path = await asyncio.to_thread(
            create_project,
            plan,
            output_dir,
            pricing,
            image_paths or None,
            open_vscode,
            settings.vscode_command,
        )

        if email and settings.email_user and settings.email_password:
            try:
                await asyncio.to_thread(
                    _send_project_zip,
                    project_path,
                    plan.project_slug,
                    email,
                    settings.email_user,
                    settings.email_password,
                )
            except Exception:
                pass  # email é não-fatal: projeto já foi gerado

        return ProjectResponse(
            success=True,
            project_name=plan.project_name,
            project_slug=plan.project_slug,
            project_type=plan.project_type.value,
            project_path=str(project_path),
            plan=plan,
            created_at=datetime.now().isoformat(),
            timeline_days=plan.timeline.total_days,
            cost_monthly_usd=plan.cost_analysis.total_monthly_usd,
            cost_monthly_brl=plan.cost_analysis.total_monthly_brl,
            free_tier_viable=plan.cost_analysis.free_tier_viable,
            pricing=pricing,
            total_hours=pricing.total_hours,
            recommended_price_brl=pricing.recommended_price_brl,
            recommended_price_usd=pricing.recommended_price_usd,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for f in temp_files:
            try:
                os.unlink(f)
            except OSError:
                pass
