"""
Logistics Dashboard — Supply Chain KPIs
=========================================
Interactive dashboard for monitoring logistics operations:
- Delivery performance (OTD)
- Inventory turnover
- Freight cost per unit
- Supplier lead time
- Order fulfillment rate

Author: Emmanuel Beristain Guzmán
GitHub: https://github.com/net421
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Logistics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.main { background-color: #080C14; }
.block-container { padding: 2rem 2.5rem; }

/* KPI Cards */
.kpi-card {
    background: #0D1421;
    border: 1px solid #1A2540;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #00D4AA; }
.kpi-value {
    font-family: 'DM Mono', monospace;
    font-size: 2.2rem;
    font-weight: 500;
    color: #00D4AA;
    line-height: 1;
    margin: 0.3rem 0;
}
.kpi-label {
    font-size: 0.75rem;
    color: #4A5A7A;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
.kpi-delta {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    margin-top: 0.3rem;
}
.delta-up   { color: #00D4AA; }
.delta-down { color: #FF6B6B; }

/* Section headers */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    color: #4A5A7A;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin: 1.8rem 0 0.8rem;
    border-left: 2px solid #00D4AA;
    padding-left: 0.7rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #080C14;
    border-right: 1px solid #1A2540;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA GENERATION (realistic synthetic data)
# ─────────────────────────────────────────────

@st.cache_data
def generate_data(seed: int = 42) -> dict:
    """Generate 12 months of realistic logistics KPI data."""
    rng = np.random.default_rng(seed)
    months = pd.date_range(start="2024-01-01", periods=12, freq="MS")
    month_labels = [m.strftime("%b %Y") for m in months]

    # On-Time Delivery (%) — slight upward trend
    otd = np.clip(rng.normal(loc=87, scale=3, size=12) +
                  np.linspace(0, 6, 12), 75, 99).round(1)

    # Inventory Turnover (times/year)
    turnover = np.clip(rng.normal(loc=8.2, scale=0.8, size=12) +
                       np.linspace(0, 1.5, 12), 5, 14).round(2)

    # Freight cost per unit ($)
    freight = np.clip(rng.normal(loc=18.5, scale=1.5, size=12) -
                      np.linspace(0, 2.5, 12), 12, 28).round(2)

    # Order fulfillment rate (%)
    fulfillment = np.clip(rng.normal(loc=92, scale=2, size=12) +
                          np.linspace(0, 4, 12), 82, 99.5).round(1)

    # Supplier lead time (days)
    lead_time = np.clip(rng.normal(loc=9.5, scale=1.2, size=12) -
                        np.linspace(0, 1.5, 12), 5, 18).round(1)

    # Orders per month
    orders = (rng.normal(loc=420, scale=35, size=12) +
              np.linspace(0, 80, 12)).round(0).astype(int)

    # Build monthly DataFrame
    df_monthly = pd.DataFrame({
        "month":       month_labels,
        "date":        months,
        "otd":         otd,
        "turnover":    turnover,
        "freight":     freight,
        "fulfillment": fulfillment,
        "lead_time":   lead_time,
        "orders":      orders,
    })

    # Supplier performance table
    suppliers = ["Proveedor Alpha", "Proveedor Beta", "Proveedor Gamma",
                 "Proveedor Delta", "Proveedor Epsilon"]
    df_suppliers = pd.DataFrame({
        "supplier":    suppliers,
        "otd":         rng.uniform(78, 97, len(suppliers)).round(1),
        "lead_time":   rng.uniform(5, 16, len(suppliers)).round(1),
        "defect_rate": rng.uniform(0.5, 4.5, len(suppliers)).round(2),
        "orders":      rng.integers(80, 350, len(suppliers)),
    })

    # Route performance
    routes = ["CDMX → Monterrey", "CDMX → Guadalajara", "Puebla → Veracruz",
              "Monterrey → Tijuana", "Guadalajara → Cancún"]
    df_routes = pd.DataFrame({
        "route":       routes,
        "avg_days":    rng.uniform(1.5, 4.5, len(routes)).round(1),
        "cost_unit":   rng.uniform(12, 32, len(routes)).round(2),
        "volume":      rng.integers(200, 800, len(routes)),
        "otd":         rng.uniform(80, 98, len(routes)).round(1),
    })

    return {
        "monthly":   df_monthly,
        "suppliers": df_suppliers,
        "routes":    df_routes,
    }


# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────

COLORS = {
    "teal":   "#00D4AA",
    "red":    "#FF6B6B",
    "yellow": "#FFD93D",
    "blue":   "#4ECDC4",
    "purple": "#A78BFA",
    "bg":     "#0D1421",
    "grid":   "#1A2540",
    "text":   "#8899BB",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color=COLORS["text"], size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor=COLORS["grid"], showline=False, tickcolor=COLORS["text"]),
    yaxis=dict(gridcolor=COLORS["grid"], showline=False, tickcolor=COLORS["text"]),
)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📦 Logistics Dashboard")
    st.markdown("---")

    st.markdown("**Filter by period**")
    all_months = generate_data()["monthly"]["month"].tolist()
    start_idx = st.slider("Start month", 0, 11, 0)
    end_idx   = st.slider("End month",   0, 11, 11)

    st.markdown("---")
    st.markdown("**Data seed** *(regenerate)*")
    seed = st.number_input("Seed", min_value=1, max_value=999, value=42)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem; color:#4A5A7A; line-height:1.8'>
    <b style='color:#00D4AA'>KPIs monitored</b><br>
    OTD · Turnover · Freight<br>
    Fulfillment · Lead Time<br><br>
    <b style='color:#00D4AA'>Built with</b><br>
    Python · Streamlit · Plotly<br><br>
    <b style='color:#00D4AA'>Author</b><br>
    Emmanuel Beristain G.<br>
    github.com/net421
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LOAD & FILTER DATA
# ─────────────────────────────────────────────

data       = generate_data(seed=seed)
df         = data["monthly"].iloc[start_idx:end_idx + 1]
df_sup     = data["suppliers"]
df_routes  = data["routes"]

# Current vs previous month for deltas
curr = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else curr


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────

st.markdown(f"""
<div style='margin-bottom:1.5rem'>
  <div style='font-size:0.7rem;color:#4A5A7A;letter-spacing:0.15em;text-transform:uppercase'>
    Supply Chain Operations
  </div>
  <h1 style='font-family:Syne,sans-serif;font-size:2rem;font-weight:800;
             color:#E8F0FF;margin:0.2rem 0 0'>
    Logistics Dashboard
  </h1>
  <div style='font-family:DM Mono,monospace;font-size:0.75rem;color:#4A5A7A'>
    {df.iloc[0]["month"]} → {df.iloc[-1]["month"]} &nbsp;·&nbsp; {len(df)} months
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  KPI CARDS
# ─────────────────────────────────────────────

def kpi_card(label, value, delta, unit="", good_direction="up"):
    arrow   = "▲" if delta >= 0 else "▼"
    is_good = (delta >= 0 and good_direction == "up") or \
              (delta < 0  and good_direction == "down")
    cls     = "delta-up" if is_good else "delta-down"
    sign    = "+" if delta >= 0 else ""
    return f"""
    <div class='kpi-card'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{value}{unit}</div>
      <div class='kpi-delta {cls}'>{arrow} {sign}{delta:.1f}{unit} vs prev month</div>
    </div>
    """

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(kpi_card(
        "On-Time Delivery", f"{curr['otd']:.1f}", curr['otd'] - prev['otd'], "%"
    ), unsafe_allow_html=True)

with c2:
    st.markdown(kpi_card(
        "Inventory Turnover", f"{curr['turnover']:.1f}", curr['turnover'] - prev['turnover'], "x"
    ), unsafe_allow_html=True)

with c3:
    st.markdown(kpi_card(
        "Freight Cost/Unit", f"${curr['freight']:.2f}", curr['freight'] - prev['freight'],
        good_direction="down"
    ), unsafe_allow_html=True)

with c4:
    st.markdown(kpi_card(
        "Fulfillment Rate", f"{curr['fulfillment']:.1f}", curr['fulfillment'] - prev['fulfillment'], "%"
    ), unsafe_allow_html=True)

with c5:
    st.markdown(kpi_card(
        "Avg Lead Time", f"{curr['lead_time']:.1f}", curr['lead_time'] - prev['lead_time'],
        "d", good_direction="down"
    ), unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TREND CHARTS — OTD & FULFILLMENT
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Performance trends</div>", unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["otd"],
        mode="lines+markers",
        line=dict(color=COLORS["teal"], width=2.5),
        marker=dict(size=6, color=COLORS["teal"]),
        fill="tozeroy",
        fillcolor="rgba(0,212,170,0.06)",
        name="OTD %",
    ))
    fig.add_hline(y=95, line_dash="dot", line_color=COLORS["yellow"],
                  annotation_text="Target 95%", annotation_font_color=COLORS["yellow"])
    fig.update_layout(**CHART_LAYOUT, title="On-Time Delivery (%)",
                      yaxis_range=[70, 100])
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["fulfillment"],
        mode="lines+markers",
        line=dict(color=COLORS["purple"], width=2.5),
        marker=dict(size=6, color=COLORS["purple"]),
        fill="tozeroy",
        fillcolor="rgba(167,139,250,0.06)",
        name="Fulfillment %",
    ))
    fig.add_hline(y=95, line_dash="dot", line_color=COLORS["yellow"],
                  annotation_text="Target 95%", annotation_font_color=COLORS["yellow"])
    fig.update_layout(**CHART_LAYOUT, title="Order Fulfillment Rate (%)",
                      yaxis_range=[75, 100])
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  FREIGHT COST & LEAD TIME
# ─────────────────────────────────────────────

col_l2, col_r2 = st.columns(2)

with col_l2:
    fig = go.Figure(go.Bar(
        x=df["month"], y=df["freight"],
        marker_color=[COLORS["teal"] if v <= df["freight"].mean()
                      else COLORS["red"] for v in df["freight"]],
        text=[f"${v:.2f}" for v in df["freight"]],
        textposition="outside",
        textfont=dict(size=9, color=COLORS["text"]),
    ))
    fig.update_layout(**CHART_LAYOUT, title="Freight Cost per Unit ($)",
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_r2:
    fig = go.Figure(go.Scatter(
        x=df["month"], y=df["lead_time"],
        mode="lines+markers",
        line=dict(color=COLORS["yellow"], width=2.5),
        marker=dict(size=6, color=COLORS["yellow"]),
        fill="tozeroy",
        fillcolor="rgba(255,217,61,0.06)",
    ))
    fig.update_layout(**CHART_LAYOUT, title="Supplier Lead Time (days)")
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  ORDERS VOLUME
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Order volume</div>", unsafe_allow_html=True)

fig = go.Figure(go.Bar(
    x=df["month"], y=df["orders"],
    marker=dict(
        color=df["orders"],
        colorscale=[[0, "#0D1421"], [1, "#00D4AA"]],
        showscale=False,
    ),
    text=df["orders"],
    textposition="outside",
    textfont=dict(size=10, color=COLORS["text"]),
))
fig.update_layout(**CHART_LAYOUT, title="Monthly Orders Processed",
                  height=280, showlegend=False)
st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  SUPPLIER PERFORMANCE
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Supplier performance</div>", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([3, 2])

with col_s1:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="OTD %",
        x=df_sup["supplier"], y=df_sup["otd"],
        marker_color=COLORS["teal"], opacity=0.85,
    ))
    fig.add_trace(go.Scatter(
        name="Lead Time (days)",
        x=df_sup["supplier"], y=df_sup["lead_time"],
        mode="lines+markers",
        yaxis="y2",
        line=dict(color=COLORS["yellow"], width=2),
        marker=dict(size=7),
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title="Supplier OTD & Lead Time",
        yaxis=dict(title="OTD %", gridcolor=COLORS["grid"], range=[0, 110]),
        yaxis2=dict(title="Lead Time (days)", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)", range=[0, 25]),
        legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_s2:
    st.markdown("**Supplier scorecard**")
    df_display = df_sup[["supplier", "otd", "lead_time", "defect_rate", "orders"]].copy()
    df_display.columns = ["Supplier", "OTD %", "Lead (d)", "Defect %", "Orders"]
    df_display = df_display.sort_values("OTD %", ascending=False)
    st.dataframe(
        df_display.style
            .background_gradient(subset=["OTD %"], cmap="RdYlGn", vmin=70, vmax=100)
            .background_gradient(subset=["Defect %"], cmap="RdYlGn_r", vmin=0, vmax=5)
            .format({"OTD %": "{:.1f}", "Lead (d)": "{:.1f}", "Defect %": "{:.2f}"}),
        use_container_width=True, hide_index=True,
    )


# ─────────────────────────────────────────────
#  ROUTE ANALYSIS
# ─────────────────────────────────────────────

st.markdown("<div class='section-header'>Route analysis</div>", unsafe_allow_html=True)

col_r1, col_r2 = st.columns(2)

with col_r1:
    fig = px.scatter(
        df_routes, x="avg_days", y="cost_unit",
        size="volume", color="otd",
        text="route",
        color_continuous_scale=["#FF6B6B", "#FFD93D", "#00D4AA"],
        range_color=[75, 100],
        labels={"avg_days": "Avg Transit Days",
                "cost_unit": "Cost per Unit ($)",
                "otd": "OTD %"},
        title="Route Efficiency Map",
    )
    fig.update_traces(textposition="top center",
                      textfont=dict(size=9, color=COLORS["text"]))
    fig.update_layout(**CHART_LAYOUT,
                      coloraxis_colorbar=dict(title="OTD %", tickfont=dict(size=9)))
    st.plotly_chart(fig, use_container_width=True)

with col_r2:
    fig = go.Figure(go.Bar(
        x=df_routes["volume"],
        y=df_routes["route"],
        orientation="h",
        marker=dict(
            color=df_routes["otd"],
            colorscale=[[0, "#FF6B6B"], [0.5, "#FFD93D"], [1, "#00D4AA"]],
            showscale=True,
            colorbar=dict(title="OTD %", thickness=12, len=0.8),
        ),
        text=[f"{v} units" for v in df_routes["volume"]],
        textposition="inside",
        textfont=dict(size=10),
    ))
    fig.update_layout(**CHART_LAYOUT, title="Volume by Route",
                      xaxis_title="Units shipped", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<div style='text-align:center;font-size:0.7rem;color:#4A5A7A;padding:0.5rem 0'>
  Logistics Dashboard · Emmanuel Beristain Guzmán ·
  <a href='https://github.com/net421' style='color:#00D4AA'>github.com/net421</a>
</div>
""", unsafe_allow_html=True)
