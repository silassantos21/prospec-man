import sys
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = Field(description="Chave da API Anthropic (Claude)")
    groq_api_key: str = Field(description="Chave da API Groq (Whisper)")
    default_output_dir: Path = Field(default=Path("./projects"))
    default_language: str = Field(default="pt")
    usd_to_brl_rate: float = Field(default=5.70)
    vscode_command: str = Field(default="code")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        from rich.console import Console
        from rich.panel import Panel

        Console().print(
            Panel(
                f"[red]Erro ao carregar configurações:[/red] {e}\n\n"
                "Certifique-se de que o arquivo [bold].env[/bold] existe.\n"
                "Execute: [bold]copy .env.example .env[/bold] e preencha as chaves de API.",
                title="Erro de Configuração",
                border_style="red",
            )
        )
        sys.exit(1)
