"""Transcrição de áudio usando Whisper via API Groq (gratuito e rápido)."""

import pathlib
from groq import Groq

SUPPORTED_FORMATS = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".ogg", ".flac"}
MAX_FILE_SIZE_MB = 25


def transcribe_audio(file_path: str, api_key: str, language: str = "pt") -> str:
    """
    Transcreve um arquivo de áudio para texto usando Whisper Large v3 via Groq.

    Args:
        file_path: Caminho para o arquivo de áudio.
        api_key: Chave da API Groq.
        language: Código do idioma (padrão: "pt" para português).

    Returns:
        Texto transcrito do áudio.
    """
    path = pathlib.Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo de áudio não encontrado: {file_path}")

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS)
        raise ValueError(f"Formato '{path.suffix}' não suportado. Use: {supported}")

    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"Arquivo muito grande: {file_size_mb:.1f} MB. "
            f"Limite: {MAX_FILE_SIZE_MB} MB. Comprima o áudio antes de enviar."
        )

    client = Groq(api_key=api_key)

    with open(path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(path.name, audio_file.read()),
            model="whisper-large-v3",
            language=language,
            response_format="text",
            prompt=(
                "Este é um briefing de projeto de software em português do Brasil. "
                "Pode conter termos técnicos, nomes de tecnologias e descrições de funcionalidades."
            ),
        )

    # Groq retorna string diretamente no response_format="text"
    return transcription if isinstance(transcription, str) else transcription.text
