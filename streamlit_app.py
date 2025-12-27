import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

from src.data_loader import get_curve
from src.shocks import apply_parallel_shock, apply_steepener, apply_custom_shock
from src.risk import calculate_dv01, calculate_duration

# --- Page Config & Custom CSS ---
st.set_page_config(
    page_title="Rates Playground | Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Mode / Terminal Polish)
st.markdown("""
<style>
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Metrics Box Styling */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 8px;
    }
    
    /* Remove default Streamlit Menu/Footer for clean look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0E1117;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("📈 Rates Playground")
    st.caption("Live yield curve analytics engine")
with col_head2:
    st.markdown("### `Live Session`")

# --- Logic: Load Data ---
try:
    with st.spinner("Connecting to Treasury Feed..."):
        date_str, original_curve = get_curve()
except Exception as e:
    st.error(f"🔥 Data Feed Error: {e}")
    st.stop()

# --- Sidebar: Control Center ---
with st.sidebar:
    st.header("⚙️ Controls")
    st.markdown("---")
    
    # 1. Market Context
    st.subheader("Market Data")
    st.info(f"**Data Date**: {date_str}")
    
    st.markdown("---")
    
    # 2. Shock Configuration
    st.subheader("Scenarios")
    shock_type = st.selectbox(
        "Shock Mode",
        ["None", "Parallel Shift", "Steepener", "Custom"],
        index=0
    )

    shocked_curve = None
    shock_desc = "Baseline"

    if shock_type == "Parallel Shift":
        bps = st.slider("Magnitude (bps)", -200, 200, 0, step=10, help="Shift the whole curve up or down")
        if bps != 0:
            shocked_curve = apply_parallel_shock(original_curve, float(bps))
            shock_desc = f"Parallel {bps:+} bps"

    elif shock_type == "Steepener":
        long_end_bps = st.slider("Long End Move (bps)", -200, 200, 0, step=10, help="Twist the curve around the 2Y point")
        if long_end_bps != 0:
            shocked_curve = apply_steepener(original_curve, float(long_end_bps), pivot_tenor=2.0)
            shock_desc = f"Steepener {long_end_bps:+} bps"

    elif shock_type == "Custom":
        col_c1, col_c2 = st.columns(2)
        s2y = col_c1.number_input("2Y (bps)", value=0.0)
        s10y = col_c2.number_input("10Y (bps)", value=0.0)
        
        custom_shocks = {}
        if s2y != 0: custom_shocks[2.0] = s2y
        if s10y != 0: custom_shocks[10.0] = s10y
        
        if custom_shocks:
            shocked_curve = apply_custom_shock(original_curve, custom_shocks)
            shock_desc = "Custom Mix"
            
    st.markdown("---")
    
# --- Top-Level Metrics (Bloomberg Style) ---
# We track 2Y and 10Y rates specifically
t2, t10 = 2.0, 10.0
r2_orig = original_curve.get(t2, 0.0)
r10_orig = original_curve.get(t10, 0.0)

r2_new = shocked_curve.get(t2, r2_orig) if shocked_curve else r2_orig
r10_new = shocked_curve.get(t10, r10_orig) if shocked_curve else r10_orig

delta2 = (r2_new - r2_orig) * 100
delta10 = (r10_new - r10_orig) * 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("2Y Yield", f"{r2_new:.2f}%", f"{delta2:+.1f} bps", delta_color="inverse")
m2.metric("10Y Yield", f"{r10_new:.2f}%", f"{delta10:+.1f} bps", delta_color="inverse")
m3.metric("Curve (2s10s)", f"{(r10_new - r2_new):.2f}%", f"{(delta10 - delta2):+.1f} bps")
m4.metric("Scenario", shock_desc)

# --- Visualization (Plotly) ---
st.markdown("### 📊 Market View")

# Prepare Data
tenors = sorted(original_curve.keys())
orig_rates = [original_curve[t] for t in tenors]

fig = go.Figure()

# 1. Original Curve
fig.add_trace(go.Scatter(
    x=tenors, 
    y=orig_rates,
    mode='lines+markers',
    name='Baseline',
    line=dict(color='#888888', width=2, dash='dot'),
    hovertemplate='<b>%{y:.2f}%</b> (Baseline)<extra></extra>'
))

# 2. Shocked Curve
if shocked_curve:
    shock_rates = [shocked_curve[t] for t in tenors]
    fig.add_trace(go.Scatter(
        x=tenors, 
        y=shock_rates,
        mode='lines+markers',
        name='Scenario',
        line=dict(color='#00CC96', width=4),
        hovertemplate='<b>%{y:.2f}%</b> (Shocked)<extra></extra>'
    ))

fig.update_layout(
    xaxis_title="Tenor (Years)",
    yaxis_title="Yield (%)",
    height=550,
    hovermode="x unified",
    paper_bgcolor='rgba(0,0,0,0)', # Transparent for dark mode
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=14),
    xaxis=dict(showgrid=True, gridcolor='#333333'),
    yaxis=dict(showgrid=True, gridcolor='#333333'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# --- Analyst Insights (Educational + Risk) ---
st.markdown("### 🧠 Insights")

col_risk, col_edu = st.columns([1, 1])

with col_risk:
    st.markdown("#### Risk Impact")
    if shocked_curve:
        # Calculate Duration Impact
        # Assume a hypothetical 10Y bond
        dur_10 = calculate_duration(r10_new, 10.0)
        dv01_10 = calculate_dv01(r10_new, 10.0)
        
        st.markdown(f"""
        Checking a hypothetical **10-Year Zero Coupon Bond**:
        *   **Price Sensitivity (ModDur)**: `{dur_10:.2f}`
        *   **DV01 ($)**: `{dv01_10:.4f}` per $100 face
        
        So if you held **$10MM** face value, this move hits your P&L by roughly:
        **${(dv01_10/100 * 10_000_000 * max(abs(delta10), 1) ):,.0f}**
        """)
    else:
        st.info("Shift the curve to see how P&L and Risk numbers react.")

with col_edu:
    st.markdown("#### What's happening?")
    if shock_type == "Parallel Shift":
        st.write("Parallel shifts usually happen when the market reprices everything at once. Think big inflation news or a surprise from the Fed that hits short and long term expectations equally.")
    elif shock_type == "Steepener":
        st.write("Steepeners happen when the spread widens. A 'Bear Steepener' (long rates up) usually means the market is getting scared of future inflation, even if the Fed holds steady today.")
    else:
        st.write("The Yield Curve basically tells you how expensive money is over time. Steep curve means growth (or inflation) ahead. Inverted curve usually signals a recession.")
