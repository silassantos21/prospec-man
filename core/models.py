from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator


class ProjectType(str, Enum):
    LANDING_PAGE = "landing_page"
    FULLSTACK_WEB = "fullstack_web"
    API_BACKEND = "api_backend"
    MOBILE_APP = "mobile_app"
    CRM_ERP = "crm_erp"
    ECOMMERCE = "ecommerce"
    SAAS = "saas"
    DATA_PIPELINE = "data_pipeline"
    CHATBOT = "chatbot"


class TechCategory(BaseModel):
    primary: str = Field(description="Tecnologia principal")
    secondary: list[str] = Field(default=[], description="Bibliotecas e ferramentas")
    # default="" para tolerar quando Claude omite o campo
    justification: str = Field(default="", description="Justificativa da escolha")


class TechStack(BaseModel):
    frontend: Optional[TechCategory] = None
    backend: Optional[TechCategory] = None
    database: Optional[TechCategory] = None
    auth: Optional[TechCategory] = None
    cache: Optional[TechCategory] = None
    infrastructure: TechCategory
    monitoring: Optional[TechCategory] = None
    ai_ml: Optional[TechCategory] = None

    @model_validator(mode="before")
    @classmethod
    def coerce_invalid_categories(cls, data: Any) -> Any:
        """Descarta TechCategory malformada (sem 'primary') ao invés de falhar."""
        if not isinstance(data, dict):
            return data
        optional_fields = ["frontend", "backend", "database", "auth", "cache", "monitoring", "ai_ml"]
        for field in optional_fields:
            val = data.get(field)
            if isinstance(val, dict) and "primary" not in val:
                data[field] = None
        return data


class AIAgent(BaseModel):
    name: str
    role: str
    model: str = Field(default="claude-sonnet-4-6")
    tools: list[str]
    purpose: str
    prompt_template: str


class TimelinePhase(BaseModel):
    name: str
    duration_days: int
    tasks: list[str]
    deliverables: list[str]


class Timeline(BaseModel):
    phases: list[TimelinePhase]
    total_days: int
    total_weeks: float
    assumptions: list[str]


class CostItem(BaseModel):
    name: str
    monthly_cost_usd: float
    setup_cost_usd: float
    is_free_tier_available: bool
    notes: str


class CostAnalysis(BaseModel):
    development: list[CostItem]
    infrastructure: list[CostItem]
    apis: list[CostItem]
    total_monthly_usd: float
    total_monthly_brl: float
    total_setup_usd: float
    total_setup_brl: float
    roi_analysis: str
    free_tier_viable: bool


class ProjectPlan(BaseModel):
    project_name: str
    project_slug: str
    project_type: ProjectType
    description: str
    problem_statement: str
    target_audience: str
    key_features: list[str]
    differentials: list[str]
    tech_stack: TechStack
    architecture_overview: str
    architecture_diagram_description: str
    ai_agents: list[AIAgent]
    timeline: Timeline
    cost_analysis: CostAnalysis
    mvp_scope: list[str]
    future_features: list[str]
    risks: list[str]
    references_summary: str
