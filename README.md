# ProspecMan

**Converta um briefing de áudio em uma estrutura de projeto completa, documentada e pronta para desenvolvimento.**

---

## O que faz

1. **Recebe um áudio** com a descrição do projeto (briefing em voz)
2. **Transcreve** com Whisper Large v3 via Groq API (gratuito)
3. **Coleta referências** fazendo scraping das URLs fornecidas
4. **Analisa imagens** de referência com Claude Vision
5. **Gera um plano completo** com Claude (arquitetura, stack, agentes IA, cronograma, custos)
6. **Cria a pasta do projeto** com 6 documentos markdown detalhados
7. **Abre o VS Code** automaticamente

---

## Pré-requisitos

| Requisito | Instalação |
|-----------|-----------|
| Python 3.11+ | [python.org](https://python.org) |
| VS Code | [code.visualstudio.com](https://code.visualstudio.com) |
| Chave Anthropic API | [console.anthropic.com](https://console.anthropic.com) |
| Chave Groq API (gratuita) | [console.groq.com](https://console.groq.com) |

---

## Instalação

```powershell
# Clone ou abra a pasta no VS Code
# Execute o script de setup (PowerShell)
.\setup.ps1

# Ative o ambiente virtual
.venv\Scripts\Activate.ps1

# Edite as chaves de API
notepad .env
```

---

## Uso

### Comando Principal

```powershell
python main.py run --audio briefing.mp3 -u https://concorrente.com -u https://instagram.com/empresa
```

### Com Imagens de Referência

```powershell
python main.py run `
  --audio briefing.m4a `
  -u https://referencia1.com `
  -i design_ref.png `
  -i logo_cliente.jpg
```

### Sem Áudio (texto direto — para testes)

```powershell
python main.py run --transcript "Quero uma landing page para uma barbearia premium em São Paulo..."
```

### Comandos de Teste Individuais

```powershell
# Testar só a transcrição
python main.py test-audio briefing.mp3

# Testar só o scraping
python main.py test-scrape https://site.com

# Testar só o planejamento (texto direto)
python main.py test-plan "Briefing do projeto aqui..."
```

---

## Estrutura do Projeto Gerado

Cada projeto criado pelo ProspecMan contém:

```
nome-do-projeto/
├── docs/
│   ├── 00_OVERVIEW.md        # Visão geral, features, riscos
│   ├── 01_ARCHITECTURE.md    # Arquitetura técnica e padrões
│   ├── 02_TECH_STACK.md      # Stack detalhada com justificativas
│   ├── 03_AI_AGENTS.md       # Agentes Claude para o desenvolvimento
│   ├── 04_TIMELINE.md        # Cronograma por fases com tarefas
│   └── 05_COST_ANALYSIS.md   # Análise financeira detalhada
├── src/                      # Código-fonte (a implementar)
├── assets/references/        # Imagens de referência copiadas
├── .vscode/
│   ├── extensions.json       # Extensões recomendadas
│   └── settings.json         # Configurações do editor
├── CLAUDE.md                 # Contexto para Claude Code
├── README.md                 # README do projeto
├── .env.example              # Template de variáveis
└── .gitignore
```

---

## Stack Padrão por Tipo de Projeto

| Tipo | Frontend | Backend | Banco |
|------|----------|---------|-------|
| Landing Page | Next.js 14 + Tailwind | — | — |
| Full-Stack Web | Next.js 14 + shadcn/ui | FastAPI | PostgreSQL |
| CRM/ERP | Next.js 14 + TanStack Table | FastAPI + Celery | PostgreSQL + Redis |
| E-commerce | Next.js 14 + shadcn/ui | Next.js API Routes | PostgreSQL |
| Mobile App | React Native + Expo | FastAPI | PostgreSQL |
| API Backend | — | FastAPI | PostgreSQL |

---

## Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `ANTHROPIC_API_KEY` | Chave Claude API | ✅ |
| `GROQ_API_KEY` | Chave Groq (Whisper gratuito) | ✅ |
| `DEFAULT_OUTPUT_DIR` | Pasta de saída dos projetos | ❌ (padrão: `./projects`) |
| `DEFAULT_LANGUAGE` | Idioma da transcrição | ❌ (padrão: `pt`) |
| `USD_TO_BRL_RATE` | Taxa de câmbio para cálculos | ❌ (padrão: `5.70`) |
| `VSCODE_COMMAND` | Comando do VS Code | ❌ (padrão: `code`) |

---

## Arquitetura do ProspecMan

```
                    ┌─────────────┐
          Áudio ───▶│   Whisper   │──▶ Transcrição
                    │  (Groq API) │
                    └─────────────┘
                                        ┌──────────────┐
          URLs ────▶ Web Scraper ──────▶│              │
                                        │    Claude    │──▶ ProjectPlan (JSON)
         Imagens ──▶ Claude Vision ────▶│  (Planner)   │
                                        └──────────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │   Project Generator   │
                                    │  - Cria pastas        │
                                    │  - Gera 6x .md files  │
                                    │  - Abre VS Code       │
                                    └───────────────────────┘
```
