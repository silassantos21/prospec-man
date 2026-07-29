"""Gerador de estrutura de pastas e arquivos de documentação do projeto."""

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .models import PricingEstimate, ProjectPlan, ProjectType, TechCategory, TechStack


# ---------------------------------------------------------------------------
# Helpers de formatação markdown
# ---------------------------------------------------------------------------


def _bullet_list(items: list[str], checked: bool = False) -> str:
    if not items:
        return "_Nenhum item._"
    prefix = "- [ ] " if checked else "- "
    return "\n".join(f"{prefix}{item}" for item in items)


def _tech_row(label: str, cat: TechCategory | None) -> str:
    if not cat:
        return ""
    secondary = ", ".join(f"`{s}`" for s in cat.secondary[:4]) if cat.secondary else "—"
    return f"| {label} | `{cat.primary}` | {secondary} |"


# ---------------------------------------------------------------------------
# Geradores de cada documento markdown
# ---------------------------------------------------------------------------


def _doc_overview(plan: ProjectPlan, created_at: str) -> str:
    return f"""# {plan.project_name}

> {plan.description}

**Tipo de Projeto:** `{plan.project_type.value}`
**Gerado em:** {created_at}
**Estimativa Total:** {plan.timeline.total_days} dias ({plan.timeline.total_weeks:.1f} semanas)
**Custo Mensal Estimado:** USD {plan.cost_analysis.total_monthly_usd:.2f} / BRL {plan.cost_analysis.total_monthly_brl:.2f}

---

## Problema que Resolve

{plan.problem_statement}

## Público-Alvo

{plan.target_audience}

## Funcionalidades Principais

{_bullet_list(plan.key_features)}

## Diferenciais

{_bullet_list(plan.differentials)}

## Escopo do MVP (Mínimo Produto Viável)

{_bullet_list(plan.mvp_scope, checked=True)}

## Funcionalidades Futuras (v2+)

{_bullet_list(plan.future_features)}

## Riscos Identificados

{_bullet_list(plan.risks)}

## Resumo das Referências Analisadas

{plan.references_summary}
"""


def _doc_architecture(plan: ProjectPlan) -> str:
    return f"""# Arquitetura do Sistema — {plan.project_name}

## Visão Geral

{plan.architecture_overview}

## Diagrama de Arquitetura

```
{plan.architecture_diagram_description}
```

## Componentes Principais

{_generate_stack_table(plan.tech_stack)}

## Decisões Arquiteturais

As decisões foram baseadas no briefing do projeto e nas referências fornecidas.
Consulte [02_TECH_STACK.md](02_TECH_STACK.md) para justificativas detalhadas de cada escolha.

## Padrões de Projeto Recomendados

- **Frontend:** Component-driven development com Server Components (Next.js App Router)
- **Backend:** Clean Architecture (Domain → Application → Infrastructure)
- **API:** REST com versionamento (`/api/v1/`) ou tRPC para type-safety full-stack
- **Estado:** Zustand (client state) + React Query / TanStack Query (server state)
- **Testes:** Vitest (unit) + Playwright (E2E)
"""


def _generate_stack_table(stack: TechStack) -> str:
    rows = [
        "| Camada | Tecnologia Principal | Complementos |",
        "|--------|---------------------|-------------|",
    ]
    for label, cat in [
        ("Frontend", stack.frontend),
        ("Backend", stack.backend),
        ("Banco de Dados", stack.database),
        ("Autenticação", stack.auth),
        ("Cache", stack.cache),
        ("Infraestrutura", stack.infrastructure),
        ("Monitoramento", stack.monitoring),
        ("IA / ML", stack.ai_ml),
    ]:
        row = _tech_row(label, cat)
        if row:
            rows.append(row)
    return "\n".join(rows)


def _doc_tech_stack(plan: ProjectPlan) -> str:
    stack = plan.tech_stack
    sections = [f"# Stack Tecnológica — {plan.project_name}\n"]

    sections.append(_generate_stack_table(stack))
    sections.append("\n---\n")

    def add_section(title: str, cat: TechCategory | None) -> None:
        if not cat:
            return
        secondary_md = (
            "\n".join(f"- `{s}`" for s in cat.secondary) if cat.secondary else "_Nenhum_"
        )
        sections.append(
            f"## {title}\n\n"
            f"**Tecnologia Principal:** `{cat.primary}`\n\n"
            f"**Complementos:**\n{secondary_md}\n\n"
            f"**Justificativa:** {cat.justification}\n"
        )

    add_section("Frontend", stack.frontend)
    add_section("Backend", stack.backend)
    add_section("Banco de Dados", stack.database)
    add_section("Autenticação & Autorização", stack.auth)
    add_section("Cache & Sessão", stack.cache)
    add_section("Infraestrutura & Deploy", stack.infrastructure)
    add_section("Monitoramento & Observabilidade", stack.monitoring)
    add_section("IA / Machine Learning", stack.ai_ml)

    # Stack padrão por tipo de projeto
    sections.append(_default_stack_note(plan.project_type))

    return "\n".join(sections)


def _default_stack_note(project_type: ProjectType) -> str:
    notes = {
        ProjectType.LANDING_PAGE: (
            "## Comandos de Setup Rápido\n\n"
            "```bash\n"
            "npx create-next-app@latest . --typescript --tailwind --app\n"
            "npx shadcn@latest init\n"
            "npm install framer-motion react-hook-form zod\n"
            "```\n"
        ),
        ProjectType.FULLSTACK_WEB: (
            "## Comandos de Setup Rápido\n\n"
            "```bash\n"
            "# Frontend\n"
            "npx create-next-app@latest frontend --typescript --tailwind --app\n"
            "npx shadcn@latest init\n"
            "npm install @tanstack/react-query zustand zod react-hook-form\n\n"
            "# Backend\n"
            "pip install fastapi uvicorn sqlalchemy pydantic alembic python-jose passlib\n"
            "```\n"
        ),
        ProjectType.CRM_ERP: (
            "## Comandos de Setup Rápido\n\n"
            "```bash\n"
            "# Frontend\n"
            "npx create-next-app@latest frontend --typescript --tailwind --app\n"
            "npx shadcn@latest init\n"
            "npm install @tanstack/react-table @tanstack/react-query recharts\n\n"
            "# Backend\n"
            "pip install fastapi uvicorn sqlalchemy alembic celery redis\n"
            "```\n"
        ),
        ProjectType.ECOMMERCE: (
            "## Comandos de Setup Rápido\n\n"
            "```bash\n"
            "npx create-next-app@latest . --typescript --tailwind --app\n"
            "npm install stripe @stripe/stripe-js @tanstack/react-query zustand\n"
            "npx shadcn@latest init\n"
            "```\n"
        ),
        ProjectType.MOBILE_APP: (
            "## Comandos de Setup Rápido\n\n"
            "```bash\n"
            "npx create-expo-app@latest . --template blank-typescript\n"
            "npx expo install nativewind tailwindcss react-native-reanimated\n"
            "npm install zustand @tanstack/react-query expo-router\n"
            "```\n"
        ),
    }
    return notes.get(project_type, "")


def _doc_ai_agents(plan: ProjectPlan) -> str:
    lines = [
        f"# Agentes de IA — {plan.project_name}\n",
        f"Este projeto utiliza **{len(plan.ai_agents)} agente(s) de IA** especializados para auxiliar "
        "no desenvolvimento e operação.\n",
        "---\n",
    ]

    for i, agent in enumerate(plan.ai_agents, 1):
        tools_md = "\n".join(f"- `{t}`" for t in agent.tools)
        lines.append(
            f"## Agente {i}: {agent.name}\n\n"
            f"**Papel:** {agent.role}  \n"
            f"**Modelo:** `{agent.model}`\n\n"
            f"### Propósito\n\n{agent.purpose}\n\n"
            f"### Ferramentas Disponíveis\n\n{tools_md}\n\n"
            f"### System Prompt Template\n\n"
            f"```\n{agent.prompt_template}\n```\n\n"
            "---\n"
        )

    lines.append(
        "## Como Usar os Agentes com Claude Code\n\n"
        "```bash\n"
        "# Iniciar Claude Code no projeto\n"
        "claude\n\n"
        "# Ou via VS Code\n"
        "# Ctrl+Shift+P → 'Claude: Open Chat'\n"
        "```\n\n"
        "Consulte a documentação oficial: https://claude.ai/code\n"
    )

    return "\n".join(lines)


def _doc_timeline(plan: ProjectPlan) -> str:
    timeline = plan.timeline

    # Tabela resumo
    phase_rows = [
        "| # | Fase | Duração |",
        "|---|------|---------|",
    ]
    for i, phase in enumerate(timeline.phases, 1):
        phase_rows.append(f"| {i} | {phase.name} | {phase.duration_days} dias |")
    phase_rows.append(f"| | **Total** | **{timeline.total_days} dias ({timeline.total_weeks:.1f} semanas)** |")

    # Detalhamento
    phase_details = []
    for i, phase in enumerate(timeline.phases, 1):
        tasks_md = _bullet_list(phase.tasks, checked=True)
        deliverables_md = _bullet_list(phase.deliverables)
        phase_details.append(
            f"### Fase {i}: {phase.name} ({phase.duration_days} dias)\n\n"
            f"#### Tarefas\n\n{tasks_md}\n\n"
            f"#### Entregáveis\n\n{deliverables_md}\n"
        )

    assumptions_md = _bullet_list(timeline.assumptions)

    return (
        f"# Cronograma do Projeto — {plan.project_name}\n\n"
        f"## Resumo\n\n"
        + "\n".join(phase_rows)
        + "\n\n---\n\n"
        "## Detalhamento das Fases\n\n"
        + "\n---\n\n".join(phase_details)
        + "\n---\n\n"
        f"## Premissas\n\n{assumptions_md}\n"
    )


def _doc_cost_analysis(plan: ProjectPlan) -> str:
    ca = plan.cost_analysis

    def cost_table(items: list) -> str:
        rows = [
            "| Serviço/Item | Mensal (USD) | Setup (USD) | Free Tier | Observações |",
            "|--------------|-------------|------------|-----------|-------------|",
        ]
        for item in items:
            ft = "✅ Sim" if item.is_free_tier_available else "❌ Não"
            rows.append(
                f"| {item.name} | ${item.monthly_cost_usd:.2f} | ${item.setup_cost_usd:.2f} | {ft} | {item.notes} |"
            )
        return "\n".join(rows)

    infra_table = cost_table(ca.infrastructure) if ca.infrastructure else "_Nenhum custo de infraestrutura._"
    apis_table = cost_table(ca.apis) if ca.apis else "_Nenhuma API externa necessária._"
    dev_table = cost_table(ca.development) if ca.development else "_Sem custos de desenvolvimento diretos._"

    free_tier_msg = (
        "✅ **Este projeto pode começar com free tier** das ferramentas listadas."
        if ca.free_tier_viable
        else "⚠️ **Este projeto requer planos pagos** desde o início. Veja os itens sem free tier acima."
    )

    return f"""# Análise de Custo-Benefício — {plan.project_name}

## Resumo Financeiro

| Categoria | Mensal (USD) | Mensal (BRL) |
|-----------|-------------|-------------|
| Infraestrutura | ${sum(i.monthly_cost_usd for i in ca.infrastructure):.2f} | R$ {sum(i.monthly_cost_usd for i in ca.infrastructure) * (ca.total_monthly_brl / ca.total_monthly_usd if ca.total_monthly_usd > 0 else 5.70):.2f} |
| APIs Externas | ${sum(i.monthly_cost_usd for i in ca.apis):.2f} | R$ {sum(i.monthly_cost_usd for i in ca.apis) * (ca.total_monthly_brl / ca.total_monthly_usd if ca.total_monthly_usd > 0 else 5.70):.2f} |
| **Total Mensal** | **${ca.total_monthly_usd:.2f}** | **R$ {ca.total_monthly_brl:.2f}** |
| **Setup Inicial** | **${ca.total_setup_usd:.2f}** | **R$ {ca.total_setup_brl:.2f}** |

{free_tier_msg}

---

## Infraestrutura & Hosting

{infra_table}

## APIs & Serviços Externos

{apis_table}

## Ferramentas de Desenvolvimento

{dev_table}

---

## Análise de ROI

{ca.roi_analysis}

---

## Notas sobre Escalabilidade de Custos

- Preços baseados em uso inicial (MVP/early stage)
- Custos aumentam com volume de usuários e dados
- Reavalie a stack se atingir 10k+ usuários ativos
- Considere contratos anuais para economias de 20-40%
"""


def _doc_pricing(plan: ProjectPlan, pricing: PricingEstimate) -> str:
    hours_rows = [
        "| # | Fase | Dias | Horas |",
        "|---|------|------|-------|",
    ]
    for i, phase in enumerate(plan.timeline.phases, 1):
        hours_rows.append(f"| {i} | {phase.name} | {phase.duration_days} | {phase.estimated_hours:.1f}h |")
    hours_rows.append(f"| | **Total** | **{plan.timeline.total_days}** | **{pricing.total_hours:.1f}h** |")

    milestones_md = _bullet_list(pricing.payment_milestones)

    return f"""# Estimativa de Investimento e Precificação — {plan.project_name}

> ⚠️ **Documento de uso interno** — apoia a decisão de quanto cobrar do cliente. Não confundir com \
[05_COST_ANALYSIS.md](05_COST_ANALYSIS.md), que trata do custo *operacional* (infra/APIs) do projeto já pronto.

## Resumo

| Item | Valor |
|------|-------|
| Horas totais estimadas | **{pricing.total_hours:.1f}h** |
| Complexidade do projeto | **{pricing.complexity_level.value}** (multiplicador {pricing.complexity_multiplier:.2f}x) |
| Valor/hora aplicado | R$ {pricing.hourly_rate_brl:.2f} (USD {pricing.hourly_rate_usd:.2f}) |
| **Preço sugerido** | **R$ {pricing.price_range_min_brl:.2f} – R$ {pricing.price_range_max_brl:.2f}** |

**Justificativa da complexidade:** {plan.complexity_justification}

---

## Horas por Fase

{chr(10).join(hours_rows)}

---

## Detalhamento do Cálculo

| Etapa | Valor (BRL) | Valor (USD) |
|-------|-------------|-------------|
| Subtotal ({pricing.total_hours:.1f}h × R$ {pricing.hourly_rate_brl:.2f}/h) | R$ {pricing.subtotal_brl:.2f} | USD {pricing.subtotal_usd:.2f} |
| Buffer de complexidade/risco ({pricing.complexity_multiplier:.2f}x) | R$ {pricing.risk_buffer_brl:.2f} | USD {pricing.risk_buffer_usd:.2f} |
| **Preço recomendado** | **R$ {pricing.recommended_price_brl:.2f}** | **USD {pricing.recommended_price_usd:.2f}** |
| Faixa sugerida (−10% / +15%) | R$ {pricing.price_range_min_brl:.2f} – R$ {pricing.price_range_max_brl:.2f} | — |

---

## Marcos de Pagamento Sugeridos

{milestones_md}

---

## Evoluções Futuras

{pricing.future_evolution_note}

---

## Como Ajustar Este Valor

Esta é uma estimativa de apoio, não um preço final. Para recalcular com outro valor/hora:

- **CLI:** `python main.py run --hourly-rate <valor>`
- **API:** envie o campo `hourly_rate_brl` na requisição `POST /projects`
- Padrão atual: R$ {pricing.hourly_rate_brl:.2f}/hora (configurável em `.env` via `DEFAULT_HOURLY_RATE_BRL`)
"""


def _generate_claude_md(plan: ProjectPlan, pricing: PricingEstimate) -> str:
    stack = plan.tech_stack

    stack_lines = []
    for label, cat in [
        ("Frontend", stack.frontend),
        ("Backend", stack.backend),
        ("Banco de Dados", stack.database),
        ("Infraestrutura", stack.infrastructure),
    ]:
        if cat:
            stack_lines.append(f"- **{label}:** {cat.primary}")

    return f"""# {plan.project_name}

## Contexto do Projeto

{plan.description}

**Problema:** {plan.problem_statement}

**Público-alvo:** {plan.target_audience}

## Stack Tecnológica

{chr(10).join(stack_lines)}

Detalhes completos em [docs/02_TECH_STACK.md](docs/02_TECH_STACK.md).

## Estrutura do Projeto

```
{plan.project_slug}/
├── docs/           # Planejamento e documentação
│   ├── 00_OVERVIEW.md
│   ├── 01_ARCHITECTURE.md
│   ├── 02_TECH_STACK.md
│   ├── 03_AI_AGENTS.md
│   ├── 04_TIMELINE.md
│   ├── 05_COST_ANALYSIS.md
│   └── 06_PRICING.md
├── src/            # Código-fonte (a criar)
└── CLAUDE.md       # Este arquivo
```

## Funcionalidades Principais

{_bullet_list(plan.key_features[:6])}

## Agentes de IA Disponíveis

{_bullet_list([f"**{a.name}** — {a.role}" for a in plan.ai_agents])}

Prompts completos em [docs/03_AI_AGENTS.md](docs/03_AI_AGENTS.md).

## Estimativa

- **Total:** {plan.timeline.total_days} dias ({plan.timeline.total_weeks:.1f} semanas) — {pricing.total_hours:.1f}h de desenvolvimento
- **Custo Mensal:** USD {plan.cost_analysis.total_monthly_usd:.2f} / BRL {plan.cost_analysis.total_monthly_brl:.2f}
- **Preço Sugerido:** R$ {pricing.price_range_min_brl:.2f} – R$ {pricing.price_range_max_brl:.2f} (ver [docs/06_PRICING.md](docs/06_PRICING.md))

## Arquitetura

{plan.architecture_overview}
"""


def _generate_readme(plan: ProjectPlan, created_at: str) -> str:
    return f"""# {plan.project_name}

{plan.description}

## Pré-requisitos

- Node.js 20+ (para projetos frontend)
- Python 3.12+ (para projetos backend)
- Docker (opcional, recomendado)

## Instalação

```bash
# Clone o repositório
git clone <url-do-repo>
cd {plan.project_slug}

# Instale dependências (adaptar conforme o projeto)
npm install      # Frontend
pip install -r requirements.txt  # Backend
```

## Variáveis de Ambiente

```bash
cp .env.example .env
# Edite .env com suas chaves
```

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [docs/00_OVERVIEW.md](docs/00_OVERVIEW.md) | Visão geral e escopo |
| [docs/01_ARCHITECTURE.md](docs/01_ARCHITECTURE.md) | Arquitetura técnica |
| [docs/02_TECH_STACK.md](docs/02_TECH_STACK.md) | Stack e justificativas |
| [docs/03_AI_AGENTS.md](docs/03_AI_AGENTS.md) | Agentes de IA para desenvolvimento |
| [docs/04_TIMELINE.md](docs/04_TIMELINE.md) | Cronograma detalhado |
| [docs/05_COST_ANALYSIS.md](docs/05_COST_ANALYSIS.md) | Análise de custos operacionais |
| [docs/06_PRICING.md](docs/06_PRICING.md) | Estimativa de investimento e precificação (uso interno) |

---

_Gerado por [ProspecMan](https://github.com/prospec-man) em {created_at}_
"""


def _get_vscode_extensions(plan: ProjectPlan) -> dict:
    base = [
        "anthropic.claude-code",
        "eamodio.gitlens",
        "yzhang.markdown-all-in-one",
        "streetsidesoftware.code-spell-checker",
        "esbenp.prettier-vscode",
    ]

    frontend_exts = [
        "bradlc.vscode-tailwindcss",
        "dbaeumer.vscode-eslint",
        "ms-vscode.vscode-typescript-next",
        "formulahendry.auto-rename-tag",
        "Prisma.prisma",
        "dsznajder.es7-react-js-snippets",
    ]

    backend_exts = [
        "ms-python.python",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "ms-python.vscode-pylance",
    ]

    ptype = plan.project_type
    if ptype in (ProjectType.LANDING_PAGE, ProjectType.FULLSTACK_WEB, ProjectType.ECOMMERCE, ProjectType.SAAS):
        base.extend(frontend_exts)
    if ptype in (ProjectType.API_BACKEND, ProjectType.DATA_PIPELINE, ProjectType.CHATBOT):
        base.extend(backend_exts)
    if ptype in (ProjectType.CRM_ERP, ProjectType.FULLSTACK_WEB):
        base.extend(frontend_exts + backend_exts)

    return {"recommendations": list(dict.fromkeys(base))}


def _get_gitignore(plan: ProjectPlan) -> str:
    base = """# Dependências
node_modules/
.pnp
.pnp.js

# Build
.next/
out/
dist/
build/
*.egg-info/
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Ambiente
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.venv/
venv/
env/

# Logs
*.log
npm-debug.log*
yarn-debug.log*

# Editor
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Cobertura de testes
coverage/
.nyc_output/
htmlcov/
"""
    return base


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------


def create_project(
    plan: ProjectPlan,
    output_dir: Path,
    pricing: PricingEstimate,
    reference_images: list[str] | None = None,
    open_vscode: bool = True,
    vscode_command: str = "code",
) -> Path:
    """
    Cria a estrutura completa do projeto no disco.

    Args:
        plan: Plano de projeto gerado pelo Claude.
        output_dir: Diretório raiz onde o projeto será criado.
        pricing: Estimativa de precificação calculada a partir do plano (ver core.pricing).
        reference_images: Caminhos das imagens de referência para copiar.
        open_vscode: Se True, abre o VS Code após criar o projeto.
        vscode_command: Comando do VS Code (padrão: "code").

    Returns:
        Path do projeto criado.
    """
    created_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Resolve um slug único caso a pasta já exista
    base_path = output_dir / plan.project_slug
    project_path = base_path
    counter = 2
    while project_path.exists():
        project_path = base_path.parent / f"{base_path.name}-{counter}"
        counter += 1

    # Cria estrutura de pastas
    dirs = [
        project_path / "docs",
        project_path / "docs" / "raw",
        project_path / "src",
        project_path / "assets" / "references",
        project_path / ".vscode",
        project_path / ".claude",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Copia imagens de referência
    if reference_images:
        for img_path in reference_images:
            src = Path(img_path)
            if src.exists():
                shutil.copy2(src, project_path / "assets" / "references" / src.name)

    # Gera todos os documentos
    docs: dict[str, str] = {
        "docs/00_OVERVIEW.md": _doc_overview(plan, created_at),
        "docs/01_ARCHITECTURE.md": _doc_architecture(plan),
        "docs/02_TECH_STACK.md": _doc_tech_stack(plan),
        "docs/03_AI_AGENTS.md": _doc_ai_agents(plan),
        "docs/04_TIMELINE.md": _doc_timeline(plan),
        "docs/05_COST_ANALYSIS.md": _doc_cost_analysis(plan),
        "docs/06_PRICING.md": _doc_pricing(plan, pricing),
        "CLAUDE.md": _generate_claude_md(plan, pricing),
        "README.md": _generate_readme(plan, created_at),
        ".gitignore": _get_gitignore(plan),
        "src/.gitkeep": "",
    }

    for rel_path, content in docs.items():
        file_path = project_path / rel_path
        file_path.write_text(content, encoding="utf-8")

    # .vscode/extensions.json
    import json

    exts = _get_vscode_extensions(plan)
    (project_path / ".vscode" / "extensions.json").write_text(
        json.dumps(exts, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # .vscode/settings.json
    vscode_settings = {
        "editor.formatOnSave": True,
        "editor.tabSize": 2,
        "editor.rulers": [100],
        "files.trimTrailingWhitespace": True,
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "[python]": {"editor.defaultFormatter": "ms-python.black-formatter"},
        "typescript.preferences.importModuleSpecifier": "relative",
    }
    (project_path / ".vscode" / "settings.json").write_text(
        json.dumps(vscode_settings, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # .env.example básico
    env_example = "# Variáveis de ambiente do projeto\n# Copie para .env e preencha\n\n"
    if plan.tech_stack.database:
        env_example += "DATABASE_URL=postgresql://user:password@localhost:5432/dbname\n"
    if plan.tech_stack.auth:
        env_example += "NEXTAUTH_SECRET=your-secret-here\nNEXTAUTH_URL=http://localhost:3000\n"
    if plan.tech_stack.ai_ml:
        env_example += "ANTHROPIC_API_KEY=sk-ant-...\n"
    (project_path / ".env.example").write_text(env_example, encoding="utf-8")

    # Abre o VS Code
    if open_vscode:
        _open_vscode(project_path, vscode_command)

    return project_path


def _open_vscode(project_path: Path, vscode_command: str = "code") -> None:
    """Abre o VS Code na pasta do projeto."""
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                f'"{vscode_command}" "{project_path}"',
                shell=True,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            subprocess.Popen([vscode_command, str(project_path)])
    except Exception:
        pass  # Falha silenciosa — main.py trata isso
