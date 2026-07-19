"""Interactive supply-chain analytics demo built from synthetic order rows."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import generate_demo_data
from src.kpis import (
    filter_period,
    monthly_kpis,
    route_scorecard,
    safe_delta,
    supplier_scorecard,
)
from src.validation import (
    DataValidationError,
    quality_summary,
    validate_inventory,
    validate_transactions,
)


st.set_page_config(
    page_title="Logistics KPI Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Syne', sans-serif; }
    .block-container { padding: 2rem 2.5rem; }
    .kpi-card {
        background: #0D1421; border: 1px solid #1A2540; border-radius: 12px;
        padding: 1.2rem 1.3rem; margin-bottom: 1rem; min-height: 122px;
    }
    .kpi-value {
        font-family: 'DM Mono', monospace; font-size: 1.85rem;
        font-weight: 500; color: #00D4AA; line-height: 1.1; margin: 0.35rem 0;
    }
    .kpi-label {
        font-size: 0.72rem; color: #7383A3; text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .kpi-delta { font-family: 'DM Mono', monospace; font-size: 0.76rem; }
    .delta-up { color: #00D4AA; } .delta-down { color: #FF6B6B; }
    .section-header {
        font-size: 0.72rem; font-weight: 700; color: #7383A3;
        text-transform: uppercase; letter-spacing: 0.16em;
        margin: 1.8rem 0 0.8rem; border-left: 2px solid #00D4AA;
        padding-left: 0.7rem;
    }
    [data-testid="stSidebar"] { border-right: 1px solid #1A2540; }
    </style>
    """,
    unsafe_allow_html=True,
)

COLORS = {
    "teal": "#00D4AA",
    "red": "#FF6B6B",
    "yellow": "#FFD93D",
    "purple": "#A78BFA",
    "grid": "#273553",
    "text": "#9AABCA",
}

BASE_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "DM Mono, monospace", "color": COLORS["text"], "size": 11},
    "margin": {"l": 15, "r": 15, "t": 45, "b": 20},
}


def style_chart(fig: go.Figure, title: str, **layout: object) -> go.Figure:
    """Apply shared Plotly styling without duplicate layout keyword errors."""
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(title=title, **layout)
    fig.update_xaxes(gridcolor=COLORS["grid"], showline=False)
    fig.update_yaxes(gridcolor=COLORS["grid"], showline=False)
    return fig


def kpi_card(
    label: str,
    value: str,
    delta: float,
    delta_unit: str = "",
    good_direction: str = "up",
    has_comparison: bool = True,
) -> str:
    """Render one KPI and make the preferred direction explicit."""
    is_good = (delta >= 0 and good_direction == "up") or (
        delta < 0 and good_direction == "down"
    )
    css_class = "delta-up" if is_good else "delta-down"
    arrow = "▲" if delta >= 0 else "▼"
    sign = "+" if delta >= 0 else ""
    comparison = (
        f"{arrow} {sign}{delta:.1f}{delta_unit} vs. mes anterior"
        if has_comparison
        else "Un solo mes seleccionado"
    )
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-delta {css_class}">{comparison}</div>
    </div>
    """


@st.cache_data
def load_demo_data(seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cache the deterministic scenario while keeping raw rows available."""
    return generate_demo_data(seed)


with st.sidebar:
    st.markdown("### 📦 Logistics Dashboard")
    st.caption("Escenario de demostración reproducible")
    seed = int(
        st.number_input(
            "Escenario (semilla)", min_value=1, max_value=999, value=42, step=1
        )
    )

transactions, inventory = load_demo_data(seed)

try:
    validate_transactions(transactions)
    validate_inventory(inventory)
except DataValidationError as error:
    st.error(f"El conjunto de demostración no pasó la validación: {error}")
    st.stop()

month_options = inventory["month"].dt.strftime("%Y-%m").tolist()
month_labels = {
    month: pd.Period(month, freq="M").to_timestamp().strftime("%b %Y")
    for month in month_options
}

with st.sidebar:
    start_month, end_month = st.select_slider(
        "Periodo de análisis",
        options=month_options,
        value=(month_options[0], month_options[-1]),
        format_func=month_labels.get,
    )
    st.markdown("---")
    st.markdown(
        "**Métricas**  \nOTD · Fill rate · Costo por unidad · Lead time · Rotación"
    )
    st.caption("Python · pandas · Streamlit · Plotly")

filtered_transactions, filtered_inventory = filter_period(
    transactions, inventory, start_month, end_month
)
monthly = monthly_kpis(filtered_transactions, filtered_inventory)
suppliers = supplier_scorecard(filtered_transactions)
routes = route_scorecard(filtered_transactions)
quality = quality_summary(filtered_transactions)

current = monthly.iloc[-1]
previous = monthly.iloc[-2] if len(monthly) > 1 else current
has_comparison = len(monthly) > 1

st.title("Logistics KPI Dashboard")
st.caption(
    f"{monthly.iloc[0]['month_label']} → {monthly.iloc[-1]['month_label']} · "
    f"{len(filtered_transactions):,} órdenes"
)
st.info(
    "Datos transaccionales **sintéticos y deterministas**. No es información de una "
    "empresa ni un sistema en tiempo real; cada KPI se calcula desde las órdenes del escenario."
)

card_columns = st.columns(5)
cards = [
    (
        "On-Time Delivery",
        f"{current['otd']:.1f}%",
        safe_delta(current["otd"], previous["otd"]),
        " pp",
        "up",
    ),
    (
        "Rotación anualizada",
        f"{current['turnover']:.1f}x",
        safe_delta(current["turnover"], previous["turnover"]),
        "x",
        "up",
    ),
    (
        "Flete por unidad",
        f"MX${current['freight']:.2f}",
        safe_delta(current["freight"], previous["freight"]),
        " MXN",
        "down",
    ),
    (
        "Unit fill rate",
        f"{current['fulfillment']:.1f}%",
        safe_delta(current["fulfillment"], previous["fulfillment"]),
        " pp",
        "up",
    ),
    (
        "Lead time promedio",
        f"{current['lead_time_days']:.1f} d",
        safe_delta(current["lead_time_days"], previous["lead_time_days"]),
        " d",
        "down",
    ),
]
for column, card in zip(card_columns, cards, strict=True):
    with column:
        st.markdown(
            kpi_card(*card, has_comparison=has_comparison), unsafe_allow_html=True
        )

st.markdown('<div class="section-header">Tendencias de servicio</div>', unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    fig = go.Figure(
        go.Scatter(
            x=monthly["month_label"],
            y=monthly["otd"],
            mode="lines+markers",
            line={"color": COLORS["teal"], "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(0,212,170,0.08)",
            name="OTD",
        )
    )
    fig.add_hline(
        y=95,
        line_dash="dot",
        line_color=COLORS["yellow"],
        annotation_text="Meta demo 95%",
    )
    style_chart(fig, "On-Time Delivery (%)", yaxis_range=[70, 100])
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = go.Figure(
        go.Scatter(
            x=monthly["month_label"],
            y=monthly["fulfillment"],
            mode="lines+markers",
            line={"color": COLORS["purple"], "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(167,139,250,0.08)",
            name="Fill rate",
        )
    )
    fig.add_hline(
        y=95,
        line_dash="dot",
        line_color=COLORS["yellow"],
        annotation_text="Meta demo 95%",
    )
    style_chart(fig, "Unit fill rate (%)", yaxis_range=[80, 100])
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    colors = [
        COLORS["teal"] if value <= monthly["freight"].mean() else COLORS["red"]
        for value in monthly["freight"]
    ]
    fig = go.Figure(
        go.Bar(
            x=monthly["month_label"],
            y=monthly["freight"],
            marker_color=colors,
            text=[f"${value:.1f}" for value in monthly["freight"]],
            textposition="outside",
        )
    )
    style_chart(fig, "Costo de flete por unidad (MXN)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = go.Figure(
        go.Scatter(
            x=monthly["month_label"],
            y=monthly["turnover"],
            mode="lines+markers",
            line={"color": COLORS["yellow"], "width": 2.5},
            name="Rotación",
        )
    )
    style_chart(fig, "Rotación de inventario anualizada (x)")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-header">Desempeño de proveedores</div>', unsafe_allow_html=True)
left, right = st.columns([3, 2])
with left:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="OTD %",
            x=suppliers["supplier"],
            y=suppliers["otd"],
            marker_color=COLORS["teal"],
        )
    )
    fig.add_trace(
        go.Scatter(
            name="Lead time (días)",
            x=suppliers["supplier"],
            y=suppliers["lead_time"],
            mode="lines+markers",
            yaxis="y2",
            line={"color": COLORS["yellow"], "width": 2},
        )
    )
    style_chart(
        fig,
        "OTD y lead time por proveedor",
        yaxis={"title": "OTD %", "range": [0, 105]},
        yaxis2={
            "title": "Lead time (días)",
            "overlaying": "y",
            "side": "right",
            "range": [0, max(12, suppliers["lead_time"].max() + 2)],
            "showgrid": False,
        },
        legend={"orientation": "h", "y": -0.2},
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    display_suppliers = suppliers[
        ["supplier", "otd", "lead_time", "defect_rate", "orders"]
    ].copy()
    display_suppliers.columns = [
        "Proveedor",
        "OTD %",
        "Lead (d)",
        "Defectos %",
        "Órdenes",
    ]
    st.dataframe(display_suppliers, hide_index=True, use_container_width=True)

st.markdown('<div class="section-header">Análisis de rutas</div>', unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    fig = px.scatter(
        routes,
        x="avg_days",
        y="cost_unit",
        size="volume",
        color="otd",
        hover_name="route",
        color_continuous_scale=[COLORS["red"], COLORS["yellow"], COLORS["teal"]],
        range_color=[75, 100],
        labels={
            "avg_days": "Lead time promedio (días)",
            "cost_unit": "Costo por unidad (MXN)",
            "otd": "OTD %",
            "volume": "Unidades",
        },
    )
    style_chart(fig, "Matriz costo–servicio por ruta")
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = go.Figure(
        go.Bar(
            x=routes["volume"],
            y=routes["route"],
            orientation="h",
            marker_color=routes["otd"],
            marker_colorscale=[COLORS["red"], COLORS["yellow"], COLORS["teal"]],
            text=[f"{value:,} u" for value in routes["volume"]],
            textposition="inside",
        )
    )
    style_chart(fig, "Volumen despachado por ruta", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-header">Lectura operativa del escenario</div>', unsafe_allow_html=True)
lowest_supplier = suppliers.sort_values("otd").iloc[0]
highest_cost_route = routes.sort_values("cost_unit", ascending=False).iloc[0]
insight_left, insight_right = st.columns(2)
with insight_left:
    st.warning(
        f"**Prioridad de proveedor:** {lowest_supplier['supplier']} tiene el OTD más bajo "
        f"del periodo ({lowest_supplier['otd']:.1f}%). Revisar causas de atraso y nivel de servicio."
    )
with insight_right:
    st.warning(
        f"**Prioridad de transporte:** {highest_cost_route['route']} registra el mayor costo "
        f"unitario (MX${highest_cost_route['cost_unit']:.2f}). Validar tarifa, consolidación y volumen."
    )

with st.expander("Definiciones y controles de calidad"):
    st.markdown(
        """
        - **OTD:** órdenes entregadas en o antes de la fecha prometida / órdenes entregadas.
        - **Unit fill rate:** unidades despachadas / unidades solicitadas.
        - **Flete por unidad:** costo total de flete / unidades despachadas.
        - **Lead time:** promedio de días entre pedido y entrega.
        - **Rotación anualizada:** 12 × COGS mensual / inventario promedio mensual.

        Las metas de 95% son referencias del escenario, no estándares universales.
        """
    )
    st.json(quality)

st.markdown("---")
st.caption(
    "Demo de portafolio · Emmanuel Beristain Guzmán · "
    "Los resultados son sintéticos y no representan desempeño empresarial real."
)
