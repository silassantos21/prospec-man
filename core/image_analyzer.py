"""Análise de imagens de referência usando Claude Vision."""

import base64
import pathlib
from anthropic import Anthropic

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
MAX_IMAGE_SIZE_MB = 5


def _encode_image(image_path: pathlib.Path) -> tuple[str, str]:
    """Codifica imagem em base64 e retorna (data, media_type)."""
    media_type = MEDIA_TYPES.get(image_path.suffix.lower(), "image/jpeg")
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def analyze_images(image_paths: list[str], api_key: str) -> str:
    """
    Analisa imagens de referência com Claude Vision.

    Args:
        image_paths: Lista de caminhos para imagens locais.
        api_key: Chave da API Anthropic.

    Returns:
        Análise detalhada das imagens em texto.
    """
    if not image_paths:
        return ""

    client = Anthropic(api_key=api_key)
    content: list[dict] = []
    valid_count = 0
    skipped = []

    for img_path in image_paths:
        path = pathlib.Path(img_path)

        if not path.exists():
            skipped.append(f"{img_path} (não encontrado)")
            continue
        if path.suffix.lower() not in SUPPORTED_FORMATS:
            skipped.append(f"{img_path} (formato não suportado)")
            continue

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_IMAGE_SIZE_MB:
            skipped.append(f"{img_path} ({size_mb:.1f} MB, limite: {MAX_IMAGE_SIZE_MB} MB)")
            continue

        try:
            data, media_type = _encode_image(path)
            content.append(
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": data},
                }
            )
            content.append({"type": "text", "text": f"[Imagem {valid_count + 1}: {path.name}]"})
            valid_count += 1
        except Exception as e:
            skipped.append(f"{img_path} (erro: {e})")

    if not content:
        return f"Nenhuma imagem válida encontrada. Ignoradas: {', '.join(skipped)}"

    content.append(
        {
            "type": "text",
            "text": (
                f"Analise estas {valid_count} imagem(ns) de referência para um projeto de software.\n"
                "Para cada imagem, descreva detalhadamente:\n"
                "1. **Estilo Visual e Design**: paleta de cores, tipografia, espaçamento, estética geral\n"
                "2. **Tipo de Negócio/Serviço**: o que a empresa/serviço oferece\n"
                "3. **Elementos de UI/UX**: componentes, layout, navegação, padrões de interação\n"
                "4. **Identidade da Marca**: tom, personalidade, público-alvo percebido\n"
                "5. **Insights para Desenvolvimento**: o que deve ser replicado ou inspirado neste projeto\n\n"
                "Responda em Português do Brasil. Seja específico e útil para um desenvolvedor."
            ),
        }
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": content}],
    )

    result = response.content[0].text
    if skipped:
        result += f"\n\n**Imagens ignoradas:** {', '.join(skipped)}"
    return result
