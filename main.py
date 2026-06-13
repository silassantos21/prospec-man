#!/usr/bin/env python3
"""ProspecMan — Gerador Inteligente de Estruturas de Projetos de Software."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from config import get_settings
from core.ai_planner import generate_project_plan
from core.audio_transcriber import transcribe_audio
from core.image_analyzer import analyze_images
from core.project_generator import create_project, _open_vscode
from core.web_scraper import format_scraped_content, scrape_urls

console = Console()

BANNER = """[bold blue]
  ____                               __  __
 |  _ \ _ __ ___  ___ _ __   ___  __|  \/  | __ _ _ __
 | |_) | '__/ _ \/ __| '_ \ / _ \/ __| |\/| |/ _` | '_ \\
 |  __/| | | (_) \__ \ |_) |  __/ (__| |  | | (_| | | | |
 |_|   |_|  \___/|___/ .__/ \___|\___|_|  |_|\__,_|_| |_|
                      |_|
[/bold blue][dim]  Gerador Inteligente de Projetos com IA[/dim]
"""


@click.group()
def cli() -> None:
    """ProspecMan — converta um áudio de briefing em estrutura de projeto completa."""
    pass


@cli.command()
@click.option(
    "--audio", "-a",
    type=click.Path(exists=True),
    default=None,
    help="Arquivo de áudio com o briefing (.mp3, .m4a, .wav, etc.)",
)
@click.option(
    "--transcript", "-t",
    default=None,
    help="Texto do briefing como alternativa ao áudio (para testes)",
)
@click.option(
    "--url", "-u",
    multiple=True,
    help="URL de referência (use múltiplas vezes: -u url1 -u url2)",
)
@click.option(
    "--image", "-i",
    multiple=True,
    type=click.Path(),
    help="Imagem de referência (use múltiplas vezes: -i img1.png -i img2.jpg)",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Diretório de saída (padrão: ./projects)",
)
@click.option(
    "--no-vscode",
    is_flag=True,
    default=False,
    help="Não abrir o VS Code automaticamente",
)
def run(
    audio: str | None,
    transcript: str | None,
    url: tuple[str, ...],
    image: tuple[str, ...],
    output: str | None,
    no_vscode: bool,
) -> None:
    """Processa um briefing e gera a estrutura completa do projeto."""

    console.print(BANNER)

    if not audio and not transcript:
        console.print(
            Panel(
                "Forneça [bold]--audio[/bold] (arquivo de áudio) "
                "ou [bold]--transcript[/bold] (texto direto).\n\n"
                "Exemplo:\n"
                "  [cyan]python main.py run --audio briefing.mp3 -u https://site.com[/cyan]",
                title="[red]Input Necessário[/red]",
                border_style="red",
            )
        )
        sys.exit(1)

    settings = get_settings()
    output_dir = Path(output) if output else settings.default_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    transcript_text = transcript or ""
    scraped_content = ""
    image_descriptions = ""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:

        # ETAPA 1 — Transcrição de áudio
        if audio:
            task = progress.add_task("[cyan]Transcrevendo áudio com Whisper...", total=None)
            try:
                transcript_text = transcribe_audio(audio, settings.groq_api_key, settings.default_language)
                progress.update(task, description="[green]✓ Áudio transcrito com sucesso")
                progress.stop_task(task)
            except Exception as e:
                progress.update(task, description=f"[red]✗ Erro na transcrição: {e}")
                progress.stop_task(task)
                console.print(f"\n[red]Erro ao transcrever áudio:[/red] {e}")
                sys.exit(1)

        # ETAPA 2 — Web scraping
        if url:
            task = progress.add_task(
                f"[cyan]Coletando dados de {len(url)} URL(s)...", total=None
            )
            try:
                scraped = scrape_urls(list(url))
                scraped_content = format_scraped_content(scraped)
                success_count = sum(1 for s in scraped if s.get("success"))
                progress.update(
                    task,
                    description=f"[green]✓ {success_count}/{len(url)} URL(s) coletadas",
                )
                progress.stop_task(task)
            except Exception as e:
                progress.update(task, description=f"[yellow]⚠ Scraping parcial: {e}")
                progress.stop_task(task)

        # ETAPA 3 — Análise de imagens
        if image:
            task = progress.add_task(
                f"[cyan]Analisando {len(image)} imagem(ns) com Claude Vision...", total=None
            )
            try:
                image_descriptions = analyze_images(list(image), settings.anthropic_api_key)
                progress.update(task, description=f"[green]✓ {len(image)} imagem(ns) analisadas")
                progress.stop_task(task)
            except Exception as e:
                progress.update(task, description=f"[yellow]⚠ Análise de imagens falhou: {e}")
                progress.stop_task(task)

        # ETAPA 4 — Geração do plano com Claude
        task = progress.add_task("[cyan]Gerando plano de projeto com Claude...", total=None)
        try:
            plan = generate_project_plan(
                transcript_text,
                scraped_content,
                image_descriptions,
                settings.anthropic_api_key,
                settings.usd_to_brl_rate,
            )
            progress.update(task, description="[green]✓ Plano de projeto gerado")
            progress.stop_task(task)
        except Exception as e:
            progress.update(task, description=f"[red]✗ Erro ao gerar plano: {e}")
            progress.stop_task(task)
            console.print(f"\n[red]Erro ao gerar plano com Claude:[/red] {e}")
            sys.exit(1)

        # ETAPA 5 — Criação da estrutura de pastas
        task = progress.add_task("[cyan]Criando estrutura de pastas e arquivos...", total=None)
        try:
            project_path = create_project(
                plan,
                output_dir,
                reference_images=list(image) if image else None,
                open_vscode=not no_vscode,
                vscode_command=settings.vscode_command,
            )
            progress.update(task, description="[green]✓ Projeto criado no disco")
            progress.stop_task(task)
        except Exception as e:
            progress.update(task, description=f"[red]✗ Erro ao criar projeto: {e}")
            progress.stop_task(task)
            console.print(f"\n[red]Erro ao criar projeto:[/red] {e}")
            sys.exit(1)

    # -----------------------------------------------------------------------
    # Painel de resultado
    # -----------------------------------------------------------------------
    console.print()

    result_table = Table(show_header=False, box=None, padding=(0, 1))
    result_table.add_column(style="bold")
    result_table.add_column()
    result_table.add_row("Nome", plan.project_name)
    result_table.add_row("Tipo", plan.project_type.value)
    result_table.add_row("Localização", str(project_path))
    result_table.add_row("Estimativa", f"{plan.timeline.total_days} dias ({plan.timeline.total_weeks:.1f} semanas)")
    result_table.add_row(
        "Custo Mensal",
        f"USD {plan.cost_analysis.total_monthly_usd:.2f} / BRL {plan.cost_analysis.total_monthly_brl:.2f}",
    )
    result_table.add_row("Free Tier", "✅ Sim" if plan.cost_analysis.free_tier_viable else "⚠️ Requer plano pago")
    result_table.add_row("Agentes IA", str(len(plan.ai_agents)))
    result_table.add_row("Fases do Projeto", str(len(plan.timeline.phases)))

    console.print(
        Panel(
            result_table,
            title="[bold green]✅ Projeto Criado com Sucesso![/bold green]",
            border_style="green",
        )
    )

    docs_info = Text()
    docs_info.append("\nArquivos gerados:\n", style="bold")
    docs_info.append(f"  📄 docs/00_OVERVIEW.md\n")
    docs_info.append(f"  🏗️  docs/01_ARCHITECTURE.md\n")
    docs_info.append(f"  🛠️  docs/02_TECH_STACK.md\n")
    docs_info.append(f"  🤖 docs/03_AI_AGENTS.md\n")
    docs_info.append(f"  📅 docs/04_TIMELINE.md\n")
    docs_info.append(f"  💰 docs/05_COST_ANALYSIS.md\n")
    docs_info.append(f"  📋 CLAUDE.md\n")
    console.print(docs_info)

    if not no_vscode:
        console.print("[dim]VS Code sendo aberto...[/dim]")
    else:
        console.print(
            f"[yellow]Para abrir no VS Code:[/yellow] [cyan]code \"{project_path}\"[/cyan]"
        )


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True))
def test_audio(audio_file: str) -> None:
    """Testa somente a transcrição de um arquivo de áudio."""
    console.print(f"[cyan]Transcrevendo:[/cyan] {audio_file}")
    settings = get_settings()
    try:
        text = transcribe_audio(audio_file, settings.groq_api_key, settings.default_language)
        console.print(Panel(text, title="Transcrição", border_style="blue"))
    except Exception as e:
        console.print(f"[red]Erro:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("url")
def test_scrape(url: str) -> None:
    """Testa somente o scraping de uma URL."""
    console.print(f"[cyan]Coletando:[/cyan] {url}")
    try:
        scraped = scrape_urls([url])
        content = format_scraped_content(scraped)
        console.print(Panel(content[:2000], title="Conteúdo Extraído", border_style="blue"))
    except Exception as e:
        console.print(f"[red]Erro:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("transcript_text")
@click.option("--output", "-o", default=None)
def test_plan(transcript_text: str, output: str | None) -> None:
    """Testa somente o planejamento com Claude a partir de um texto."""
    console.print("[cyan]Gerando plano com Claude...[/cyan]")
    settings = get_settings()
    output_dir = Path(output) if output else settings.default_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        plan = generate_project_plan(transcript_text, "", "", settings.anthropic_api_key)
        project_path = create_project(plan, output_dir, open_vscode=False)
        console.print(f"[green]Plano gerado:[/green] {project_path}")
        console.print(f"  Nome: {plan.project_name}")
        console.print(f"  Tipo: {plan.project_type.value}")
        console.print(f"  Semanas: {plan.timeline.total_weeks:.1f}")
    except Exception as e:
        console.print(f"[red]Erro:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
