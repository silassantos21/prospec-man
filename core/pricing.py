"""Cálculo de precificação do serviço — puramente determinístico, sem chamada de IA.

O Claude estima horas por fase e a complexidade geral do projeto (campos estruturados
em ProjectPlan). Este módulo transforma essas estimativas técnicas em um preço sugerido,
usando o valor/hora que o usuário define — mantendo o controle financeiro 100% do lado
do usuário e evitando erros de aritmética da IA.
"""

from .models import ComplexityLevel, PricingEstimate, ProjectPlan

COMPLEXITY_MULTIPLIERS: dict[ComplexityLevel, float] = {
    ComplexityLevel.LOW: 1.0,
    ComplexityLevel.MEDIUM: 1.15,
    ComplexityLevel.HIGH: 1.3,
}

PRICE_RANGE_MIN_FACTOR = 0.9
PRICE_RANGE_MAX_FACTOR = 1.15


def _default_payment_milestones(plan: ProjectPlan) -> list[str]:
    phases = plan.timeline.phases
    if len(phases) >= 3:
        return [
            f"40% na assinatura (antes de iniciar {phases[0].name})",
            f"30% na entrega de {phases[len(phases) // 2].name}",
            f"30% na entrega final ({phases[-1].name})",
        ]
    return [
        "40% na assinatura do projeto",
        "30% na entrega do MVP",
        "30% na entrega final",
    ]


def _future_evolution_note(plan: ProjectPlan) -> str:
    n = len(plan.future_features)
    if n == 0:
        return "Nenhuma evolução futura mapeada no momento — esta estimativa cobre apenas o escopo atual."
    return (
        f"Este projeto tem {n} funcionalidade(s) futura(s) mapeada(s) (ver `future_features`), "
        "não incluídas nesta estimativa. Cobre horas adicionais separadamente se o cliente solicitar."
    )


def calculate_pricing(
    plan: ProjectPlan,
    hourly_rate_brl: float,
    usd_brl_rate: float,
) -> PricingEstimate:
    """Calcula o preço sugerido do projeto a partir das horas/complexidade do plano.

    Args:
        plan: Plano de projeto já gerado (contém timeline.total_hours e complexity_level).
        hourly_rate_brl: Valor/hora base definido pelo usuário.
        usd_brl_rate: Taxa de câmbio USD/BRL para converter os valores.

    Returns:
        PricingEstimate com o detalhamento completo do cálculo.
    """
    total_hours = plan.timeline.total_hours
    multiplier = COMPLEXITY_MULTIPLIERS[plan.complexity_level]

    subtotal_brl = total_hours * hourly_rate_brl
    risk_buffer_brl = subtotal_brl * (multiplier - 1.0)
    recommended_price_brl = subtotal_brl + risk_buffer_brl

    hourly_rate_usd = hourly_rate_brl / usd_brl_rate if usd_brl_rate > 0 else 0.0
    subtotal_usd = subtotal_brl / usd_brl_rate if usd_brl_rate > 0 else 0.0
    risk_buffer_usd = risk_buffer_brl / usd_brl_rate if usd_brl_rate > 0 else 0.0
    recommended_price_usd = recommended_price_brl / usd_brl_rate if usd_brl_rate > 0 else 0.0

    return PricingEstimate(
        hourly_rate_brl=hourly_rate_brl,
        hourly_rate_usd=hourly_rate_usd,
        total_hours=total_hours,
        complexity_level=plan.complexity_level,
        complexity_multiplier=multiplier,
        subtotal_brl=subtotal_brl,
        subtotal_usd=subtotal_usd,
        risk_buffer_brl=risk_buffer_brl,
        risk_buffer_usd=risk_buffer_usd,
        recommended_price_brl=recommended_price_brl,
        recommended_price_usd=recommended_price_usd,
        price_range_min_brl=recommended_price_brl * PRICE_RANGE_MIN_FACTOR,
        price_range_max_brl=recommended_price_brl * PRICE_RANGE_MAX_FACTOR,
        payment_milestones=_default_payment_milestones(plan),
        future_evolution_note=_future_evolution_note(plan),
    )
