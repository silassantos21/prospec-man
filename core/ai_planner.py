"""Pipeline de planejamento de projetos com Claude."""

import json
import re
from anthropic import Anthropic
from .models import ProjectPlan

SYSTEM_PROMPT = """Você é ProspecAI, um arquiteto de software sênior e especialista em planejamento de projetos digitais.

Sua missão é analisar briefings de projetos (transcrições de áudio) e materiais de referência (sites, imagens) \
para produzir planos de projeto completos, detalhados e acionáveis.

Você tem profundo conhecimento em:
- Arquitetura de software moderna (Next.js, FastAPI, PostgreSQL, Redis, Docker)
- Stacks tecnológicas atuais e suas trade-offs
- Estimativas realistas de desenvolvimento (não seja otimista demais)
- Análise de custos de infraestrutura, APIs e serviços
- Agentes de IA com Claude (Anthropic), LangChain e CrewAI
- Padrões de UI/UX modernos (Tailwind, shadcn/ui, Framer Motion)

REGRAS CRÍTICAS:
1. Responda APENAS com JSON válido — zero texto antes ou depois
2. Todo conteúdo em Português do Brasil
3. project_slug: apenas kebab-case sem acentos (ex: "crm-barbearia", "landing-clinica")
4. Estimativas de tempo realistas: landing page = 1-3 semanas, SaaS completo = 3-6 meses
5. Custo em USD com conversão BRL usando taxa fornecida no contexto
6. Agentes de IA devem ser específicos e úteis para ESTE projeto"""

# Schema legível que Claude consegue seguir com precisão
JSON_SCHEMA = """
{
  "project_name": "Nome completo e descritivo do projeto",
  "project_slug": "nome-sem-acentos-kebab-case",
  "project_type": "landing_page | fullstack_web | api_backend | mobile_app | crm_erp | ecommerce | saas | data_pipeline | chatbot",
  "description": "Descrição clara do projeto em 2-3 frases",
  "problem_statement": "Qual problema concreto este projeto resolve?",
  "target_audience": "Quem são os usuários finais e stakeholders?",
  "key_features": ["Feature 1", "Feature 2", "Feature 3"],
  "differentials": ["Diferencial competitivo 1", "Diferencial 2"],
  "tech_stack": {
    "frontend": {
      "primary": "Next.js 14 + TypeScript",
      "secondary": ["Tailwind CSS", "shadcn/ui", "Framer Motion"],
      "justification": "Por que esta stack frontend foi escolhida"
    },
    "backend": {
      "primary": "FastAPI (Python 3.12)",
      "secondary": ["SQLAlchemy", "Pydantic v2", "Celery"],
      "justification": "Por que este backend"
    },
    "database": {
      "primary": "PostgreSQL 16",
      "secondary": ["Prisma ORM", "pgvector"],
      "justification": "Por que este banco de dados"
    },
    "auth": {
      "primary": "NextAuth.js v5",
      "secondary": ["JWT", "OAuth2 Google"],
      "justification": "Por que esta solução de auth"
    },
    "cache": {
      "primary": "Redis (Upstash)",
      "secondary": ["React Query"],
      "justification": "Por que usar cache"
    },
    "infrastructure": {
      "primary": "Vercel (frontend) + Railway (backend)",
      "secondary": ["GitHub Actions CI/CD", "Docker"],
      "justification": "Por que esta infraestrutura"
    },
    "monitoring": {
      "primary": "Sentry",
      "secondary": ["Vercel Analytics"],
      "justification": "Por que este monitoramento"
    },
    "ai_ml": {
      "primary": "Claude claude-sonnet-4-6 API",
      "secondary": ["LangChain", "Pinecone"],
      "justification": "Descreva por que IA é necessária. Se o projeto NÃO usa IA nativa, use null aqui."
    }
  },
  "architecture_overview": "Descrição da arquitetura em 4-6 frases explicando os componentes e como se integram",
  "architecture_diagram_description": "Descrição textual do diagrama: quais serviços existem, como se comunicam, fluxo de dados",
  "ai_agents": [
    {
      "name": "NomeDoAgente",
      "role": "Papel específico no projeto",
      "model": "claude-sonnet-4-6",
      "tools": ["bash", "read_file", "write_file", "web_search"],
      "purpose": "Descrição detalhada do que este agente faz e quando deve ser usado",
      "prompt_template": "Você é um especialista em [área]. Sua função é [responsabilidade específica]. Sempre [comportamento esperado]."
    }
  ],
  "timeline": {
    "phases": [
      {
        "name": "Nome da Fase",
        "duration_days": 14,
        "tasks": ["Tarefa detalhada 1", "Tarefa 2", "Tarefa 3"],
        "deliverables": ["Entregável concreto 1", "Entregável 2"]
      }
    ],
    "total_days": 30,
    "total_weeks": 4.3,
    "assumptions": ["Premissa que afeta o prazo 1", "Premissa 2"]
  },
  "cost_analysis": {
    "development": [
      {
        "name": "Nome do item de custo de desenvolvimento",
        "monthly_cost_usd": 0.0,
        "setup_cost_usd": 0.0,
        "is_free_tier_available": true,
        "notes": "Observações sobre este custo"
      }
    ],
    "infrastructure": [
      {
        "name": "Serviço de infraestrutura",
        "monthly_cost_usd": 5.0,
        "setup_cost_usd": 0.0,
        "is_free_tier_available": true,
        "notes": "Detalhes do plano free tier vs pago"
      }
    ],
    "apis": [
      {
        "name": "API/Serviço externo",
        "monthly_cost_usd": 20.0,
        "setup_cost_usd": 0.0,
        "is_free_tier_available": false,
        "notes": "Precificação e limites de uso"
      }
    ],
    "total_monthly_usd": 25.0,
    "total_monthly_brl": 142.50,
    "total_setup_usd": 0.0,
    "total_setup_brl": 0.0,
    "roi_analysis": "Análise de retorno sobre investimento: quando o projeto se paga, métricas de sucesso",
    "free_tier_viable": true
  },
  "mvp_scope": ["Feature essencial do MVP 1", "Feature essencial 2"],
  "future_features": ["Feature v2 1", "Feature v2 2"],
  "risks": ["Risco técnico 1: descrição e como mitigar", "Risco de negócio 1"],
  "references_summary": "O que foi aprendido das referências fornecidas e como influencia o projeto"
}"""


def generate_project_plan(
    transcript: str,
    scraped_content: str,
    image_descriptions: str,
    api_key: str,
    usd_brl_rate: float = 5.70,
) -> ProjectPlan:
    """
    Envia o briefing ao Claude e retorna um ProjectPlan estruturado.

    Args:
        transcript: Texto transcrito do áudio de briefing.
        scraped_content: Conteúdo extraído das URLs de referência.
        image_descriptions: Análise das imagens de referência.
        api_key: Chave da API Anthropic.
        usd_brl_rate: Taxa de câmbio USD/BRL atual.

    Returns:
        ProjectPlan validado com Pydantic.
    """
    client = Anthropic(api_key=api_key)

    user_message = f"""## BRIEFING DO PROJETO (transcrição de áudio)

{transcript}

## CONTEÚDO DAS REFERÊNCIAS WEB
{scraped_content if scraped_content else "Nenhuma referência web fornecida."}

## ANÁLISE DAS IMAGENS DE REFERÊNCIA
{image_descriptions if image_descriptions else "Nenhuma imagem de referência fornecida."}

---

**Taxa de câmbio atual:** 1 USD = {usd_brl_rate} BRL

Com base em TODAS as informações acima, gere o plano de projeto completo seguindo EXATAMENTE o schema JSON abaixo.
Adapte todos os campos ao projeto específico descrito no briefing.
Responda APENAS com o JSON — sem texto antes ou depois, sem blocos de código markdown.

{JSON_SCHEMA}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text.strip()

    # Remove blocos de código markdown se o Claude os incluir por engano
    json_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw_text, re.DOTALL)
    json_text = json_match.group(1) if json_match else raw_text

    # Remove qualquer texto antes do primeiro { ou depois do último }
    start = json_text.find("{")
    end = json_text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(
            f"Claude não retornou JSON válido. Resposta recebida:\n{raw_text[:500]}..."
        )

    json_text = json_text[start:end]

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido retornado pelo Claude: {e}\n\nTexto recebido:\n{json_text[:500]}")

    return ProjectPlan.model_validate(data)
