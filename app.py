import os
import tempfile
import warnings

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from analysis.csv_loader import load_csv
from analysis.data_profiler import profile_dataset
from analysis.statistics import numeric_summary
from analysis.anomaly import detect_iqr_anomalies
from analysis.report import create_report

warnings.filterwarnings("ignore")

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="InsightOps",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE - INITIALIZE ALL VARIABLES
# ============================================================

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "📊 Dashboard"

if "df" not in st.session_state:
    st.session_state.df = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = {}

if "objective" not in st.session_state:
    st.session_state.objective = (
        "Analyze data/sample.csv as a business analyst. "
        "Find the single biggest business problem. "
        "1. Inspect the data. "
        "2. Compare regions and products. "
        "3. Check discount vs profit. "
        "4. Detect unusual values. "
        "5. Investigate WHY the main problem exists. "
        "6. Give evidence from the data. "
        "7. Give 3 actionable recommendations. "
        "8. State limitations. "
        "Use tools for all calculations. "
        "Do not invent or assume anything."
    )
# ============================================================
# CUSTOM CSS - PROPER ALIGNMENT
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 80% 10%, rgba(50, 70, 150, 0.10), transparent 30%),
        radial-gradient(circle at 20% 80%, rgba(120, 50, 180, 0.08), transparent 30%),
        #070b14;
    color: #f5f7ff;
}

/* Main container - proper alignment */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1200px !important;
    margin-left: 300px !important;
}

/* SIDEBAR - Fixed on left */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #080d19 0%,
            #0a0e1b 60%,
            #080b14 100%
        );
    border-right: 1px solid rgba(255,255,255,0.08);
    min-width: 280px !important;
    width: 280px !important;
    max-width: 280px !important;
    flex-shrink: 0 !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    z-index: 999 !important;
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.2rem !important;
    padding-top: 1.5rem !important;
    height: 100vh !important;
    overflow-y: auto !important;
}

/* Hide scrollbar for cleaner look */
section[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 3px !important;
}

section[data-testid="stSidebar"]::-webkit-scrollbar-track {
    background: transparent !important;
}

section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
}

/* Hide collapse buttons */
button[kind="header"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

.st-emotion-cache-1wmy9hl {
    display: none !important;
}

.st-emotion-cache-1r4qj8v {
    display: none !important;
}

/* Sidebar brand */
.sidebar-brand {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 4px;
    color: white;
    letter-spacing: -0.5px;
}

.sidebar-subtitle {
    color: #b5a9ff;
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 20px;
    font-weight: 400;
}

.sidebar-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    margin: 8px 0 12px 0;
}

/* Navigation buttons */
section[data-testid="stSidebar"] .stButton {
    width: 100%;
    margin-bottom: 2px;
}

section[data-testid="stSidebar"] .stButton > button {
    border-radius: 6px;
    border: none;
    min-height: 38px;
    font-weight: 500;
    font-size: 14px;
    background: transparent !important;
    color: #aeb5ca !important;
    text-align: left !important;
    padding: 8px 14px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    justify-content: flex-start !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    border-color: rgba(255,255,255,0.15) !important;
}

section[data-testid="stSidebar"] .stButton > button[data-kind="primary"] {
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    border-color: rgba(255,255,255,0.15) !important;
}

section[data-testid="stSidebar"] .stButton > button[data-kind="secondary"] {
    background: transparent !important;
    color: #aeb5ca !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}

/* Sidebar cards */
.sidebar-card {
    margin-top: 16px;
    padding: 12px 14px;
    border-radius: 10px;
    background: rgba(16, 23, 40, 0.6);
    border: 1px solid rgba(100,120,180,0.12);
    font-size: 11px;
    line-height: 1.6;
    color: #aeb5ca;
}

.sidebar-card b {
    color: #c8ccdc;
}

.status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 6px 0;
    font-size: 11px;
    color: #aeb5ca;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #2be477;
    box-shadow: 0 0 8px rgba(43,228,119,0.6);
}

/* Main title */
.main-title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 2px;
}

.main-subtitle {
    font-size: 12px;
    color: #b4bbcc;
    margin-top: -2px;
}

.gemini-badge {
    border: 1px solid #6554ff;
    border-radius: 7px;
    padding: 6px 12px;
    font-size: 11px;
    color: #e8e4ff;
    background: rgba(80,50,180,0.10);
    text-align: center;
    white-space: nowrap;
}

/* Section title */
.section-title {
    font-size: 15px;
    font-weight: 700;
    margin-top: 6px;
    margin-bottom: 6px;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, rgba(20,28,48,0.98), rgba(10,15,28,0.98));
    border: 1px solid rgba(120,140,190,0.15);
    border-radius: 10px;
    padding: 14px 16px;
    min-height: 120px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    text-align: left;
}

.kpi-icon {
    font-size: 22px;
    margin-bottom: 6px;
}

.kpi-label {
    font-size: 11px;
    color: #aeb5c7;
}

.kpi-value {
    font-size: 22px;
    font-weight: 800;
    margin-top: 2px;
    color: white;
}

.kpi-small {
    font-size: 10px;
    color: #7f879a;
    margin-top: 3px;
}

.dashboard-card {
    background:
        linear-gradient(
            145deg,
            rgba(18,25,43,0.96),
            rgba(9,14,26,0.98)
        );
    border: 1px solid rgba(120,140,190,0.16);
    border-radius: 10px;
    padding: 14px;
}

.problem-card {
    background:
        linear-gradient(
            145deg,
            rgba(27,20,48,0.98),
            rgba(12,15,29,0.98)
        );
    border: 1px solid rgba(110,80,255,0.35);
    border-radius: 10px;
    padding: 15px;
}

.problem-title {
    color: #ffb34d;
    font-size: 12px;
    font-weight: 700;
}

.problem-text {
    font-size: 13px;
    line-height: 1.65;
    color: #d9dcef;
}

.insight-card {
    background: rgba(25,30,52,0.8);
    border: 1px solid rgba(100,110,210,0.25);
    border-radius: 8px;
    padding: 11px;
    margin-top: 10px;
}

.insight-title {
    color: #d4caff;
    font-size: 11px;
    font-weight: 700;
}

.insight-text {
    color: #b7bdd0;
    font-size: 11px;
    line-height: 1.55;
}

.recommendation {
    display: flex;
    gap: 12px;
    margin: 10px 0;
    align-items: flex-start;
    background: rgba(25,30,52,0.6);
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid rgba(100,110,210,0.15);
}

.rec-number {
    min-width: 26px;
    height: 26px;
    border-radius: 7px;
    background: linear-gradient(135deg,#1e86ff,#813cff);
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 700;
    font-size: 12px;
    color: white;
    flex-shrink: 0;
}

.rec-text {
    font-size: 12px;
    line-height: 1.5;
    color: #d2d6e3;
    padding-top: 2px;
}

/* Form controls */
[data-testid="stFileUploader"] {
    background: rgba(18,24,40,0.8);
    border-radius: 8px;
}

textarea {
    background: #111625 !important;
    color: white !important;
    border: 1px solid #303950 !important;
}

div[data-baseweb="select"] > div {
    background: #171b29;
    border-color: #343b52;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(120,140,190,0.15);
    border-radius: 8px;
}

.footer {
    text-align: center;
    color: #6f7689;
    font-size: 10px;
    padding-top: 16px;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Upload button */
.stButton > button:has(> div:contains("Analyze")) {
    background: linear-gradient(90deg, #d946ef, #237eff) !important;
    color: white !important;
    text-align: center !important;
    justify-content: center !important;
    font-weight: 700 !important;
    border: none !important;
}

.stButton > button:has(> div:contains("Analyze")):hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 25px rgba(70,100,255,0.25);
}

/* AI Business Analyst button */
.stButton > button:has(> div:contains("🤖 AI Business Analyst")) {
    background: linear-gradient(90deg, #8b3dff, #2f8cff) !important;
    color: white !important;
    text-align: center !important;
    justify-content: center !important;
    font-weight: 700 !important;
    border: none !important;
}

.stButton > button:has(> div:contains("🤖 AI Business Analyst")):hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 25px rgba(139, 61, 255, 0.4) !important;
}

/* Info boxes */
.stAlert {
    background: rgba(18,24,40,0.8) !important;
    border-radius: 8px !important;
}

</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR - FIXED ON LEFT (AI Business Analyst moved up)
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">📊 InsightOps</div>
        <div class="sidebar-subtitle">
        Autonomous Business<br>
        Data Analyst
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Navigation items - AI Business Analyst moved to top after Overview
    nav_items = [
        "📊 Dashboard",
        "📈 Overview",
        "🤖 AI Business Analyst",  # Moved up
        "📊 Segment Analysis",
        "📦 Product Analysis",
        "♙ Discount Analysis",
        "△ Anomaly Detection",
        "♧ Correlations",
        "📄 Reports"
    ]

    for item in nav_items:
        is_active = (item == st.session_state.current_tab)
        
        if st.button(
            item,
            key=f"nav_{item}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.current_tab = item
            st.rerun()

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sidebar-card">
        <b>About InsightOps</b><br><br>
        InsightOps uses Python for fast analytics
        and Gemini AI reasoning for business
        insights and recommendations.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-card">
        <b>Engine Status</b>

        <div class="status-row">
        <span class="status-dot"></span>
        Python Analytics — Ready
        </div>

        <div class="status-row">
        <span class="status-dot"></span>
        AI Reasoning — Ready
        </div>

        <div class="status-row">
        <span class="status-dot"></span>
        Visualizations — Ready
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# HEADER
# ============================================================

col1, col2 = st.columns([4, 1])

with col1:
    st.markdown(
        """
        <div class="main-title">📊 InsightOps</div>
        <div class="main-subtitle">Autonomous Business Data Analyst · Turn raw data into business decisions.</div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="gemini-badge">✦ AI Powered by Gemini</div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# UPLOAD AREA
# ============================================================

upload_col, question_col, button_col = st.columns(
    [4, 4, 2],
    gap="small"
)

with upload_col:

    st.markdown(
        '<div class="section-title">📁 Uploaded File</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload Dataset",
        type=["csv"],
        label_visibility="collapsed"
    )

with question_col:

    st.markdown(
        '<div class="section-title">🎯 Business Question</div>',
        unsafe_allow_html=True
    )

    objective = st.text_area(
        "Business Objective",
        value=st.session_state.objective,
        height=68,
        label_visibility="collapsed",
        key="objective_input"
    )
    
    st.session_state.objective = objective

with button_col:

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    analyze_button = st.button(
        "🚀 Analyze Dataset",
        use_container_width=True
    )

# ============================================================
# ADD AI BUSINESS ANALYST BUTTON UNDER ANALYZE BUTTON
# ============================================================

# Create a row for the AI button (same width as analyze button)
ai_button_container = st.columns([8, 2])  # Match the layout ratio

with ai_button_container[0]:
    # This is the same width as the analyze button area
    ai_button = st.button(
        "🤖 AI Business Analyst",
        use_container_width=True,
        key="ai_business_analyst_btn"
    )
    
    if ai_button:
        st.session_state.current_tab = "🤖 AI Business Analyst"
        st.rerun()

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):
    if value is None or pd.isna(value):
        return "$0"

    try:
        value = float(value)
    except (ValueError, TypeError):
        return "$0"

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"

    return f"${value:,.0f}"

def pct(value):
    if value is None or pd.isna(value):
        return "0.00%"

    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return "0.00%"

def safe_sum(series):
    if series is None:
        return 0
    try:
        numeric_series = pd.to_numeric(series, errors='coerce')
        return numeric_series.sum()
    except:
        return 0

def safe_mean(series):
    if series is None:
        return 0
    try:
        numeric_series = pd.to_numeric(series, errors='coerce')
        return numeric_series.mean()
    except:
        return 0

def find_column(df, candidates):

    normalized = {
        str(col).strip().lower().replace("_", " ").replace("-", " "): col
        for col in df.columns
    }

    for candidate in candidates:

        key = (
            candidate.lower()
            .strip()
            .replace("_", " ")
            .replace("-", " ")
        )

        if key in normalized:
            return normalized[key]

    for col in df.columns:

        col_normalized = (
            str(col)
            .lower()
            .strip()
            .replace("_", " ")
            .replace("-", " ")
        )

        for candidate in candidates:

            candidate_normalized = (
                candidate.lower()
                .strip()
                .replace("_", " ")
                .replace("-", " ")
            )

            if candidate_normalized in col_normalized:
                return col

    return None

def detect_business_columns(df):

    return {

        "date": find_column(
            df,
            [
                "order date",
                "date",
                "transaction date",
                "sales date"
            ]
        ),

        "region": find_column(
            df,
            [
                "region",
                "sales region",
                "area"
            ]
        ),

        "product": find_column(
            df,
            [
                "product",
                "product name",
                "item",
                "item name"
            ]
        ),

        "category": find_column(
            df,
            [
                "category",
                "product category"
            ]
        ),

        "subcategory": find_column(
            df,
            [
                "sub-category",
                "subcategory",
                "sub category"
            ]
        ),

        "sales": find_column(
            df,
            [
                "sales",
                "revenue",
                "total sales",
                "amount"
            ]
        ),

        "profit": find_column(
            df,
            [
                "profit",
                "net profit",
                "earnings"
            ]
        ),

        "discount": find_column(
            df,
            [
                "discount",
                "discount rate",
                "discount percentage"
            ]
        ),

        "quantity": find_column(
            df,
            [
                "quantity",
                "qty",
                "units"
            ]
        ),

        "segment": find_column(
            df,
            [
                "segment",
                "customer segment"
            ]
        ),

        "customer": find_column(
            df,
            [
                "customer",
                "customer name",
                "customer id"
            ]
        )
    }

def regional_analysis(df, region_col, sales_col, profit_col, discount_col):

    if not region_col:
        return None

    if sales_col:
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
    if profit_col:
        df[profit_col] = pd.to_numeric(df[profit_col], errors='coerce')
    if discount_col:
        df[discount_col] = pd.to_numeric(df[discount_col], errors='coerce')

    aggregations = {}

    if sales_col:
        aggregations["sales"] = (sales_col, "sum")

    if profit_col:
        aggregations["profit"] = (profit_col, "sum")

    if discount_col:
        aggregations["discount"] = (discount_col, "mean")

    if not aggregations:
        return None

    result = df.groupby(region_col).agg(**aggregations)

    result["transactions"] = df.groupby(region_col).size()

    if sales_col and "sales" in result.columns:
        result["avg_sales"] = (
            result["sales"] / result["transactions"]
        )

    if profit_col and "profit" in result.columns and "sales" in result.columns:
        result["avg_profit"] = (
            result["profit"] / result["transactions"]
        )

        result["margin"] = np.where(
            result["sales"] != 0,
            result["profit"] / result["sales"] * 100,
            0
        )

    sort_col = "sales" if sales_col and "sales" in result.columns else "transactions"
    return result.sort_values(sort_col, ascending=False)

def product_analysis(df, product_col, sales_col, profit_col):

    if not product_col:
        return None

    if sales_col:
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
    if profit_col:
        df[profit_col] = pd.to_numeric(df[profit_col], errors='coerce')

    aggregations = {}

    if sales_col:
        aggregations["sales"] = (sales_col, "sum")

    if profit_col:
        aggregations["profit"] = (profit_col, "sum")

    if not aggregations:
        return None

    result = df.groupby(product_col).agg(**aggregations)

    result["transactions"] = df.groupby(product_col).size()

    sort_col = "sales" if sales_col and "sales" in result.columns else "transactions"
    return result.sort_values(sort_col, ascending=False)

def calculate_discount_profit_correlation(
    df,
    discount_col,
    profit_col
):

    if not discount_col or not profit_col:
        return None

    df[discount_col] = pd.to_numeric(df[discount_col], errors='coerce')
    df[profit_col] = pd.to_numeric(df[profit_col], errors='coerce')

    temp = df[[discount_col, profit_col]].dropna()

    if len(temp) < 2:
        return None

    try:
        return temp[discount_col].corr(temp[profit_col])
    except:
        return None

def detect_anomalies_local(
    df,
    metric_col
):

    if not metric_col:
        return pd.DataFrame()

    df[metric_col] = pd.to_numeric(df[metric_col], errors='coerce')
    series = df[metric_col].dropna()

    if len(series) < 4:
        return pd.DataFrame()

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    mask = (series < lower) | (series > upper)

    return df.loc[mask].copy()

def build_business_insight(
    df,
    cols,
    regional,
    discount_corr
):

    region_col = cols["region"]
    sales_col = cols["sales"]
    profit_col = cols["profit"]
    discount_col = cols["discount"]

    if regional is None:
        return (
            "⚠️ InsightOps could not determine a specific "
            "business problem from the available columns."
        )

    if "margin" in regional.columns and len(regional) > 0:

        worst_region = regional["margin"].idxmin()
        worst_margin = regional.loc[worst_region, "margin"]

        best_margin = regional["margin"].max()

        if discount_col and "discount" in regional.columns:

            worst_discount = regional.loc[worst_region, "discount"]

            return (
                f"High discounting in the <b>{worst_region}</b> "
                f"region is reducing profitability despite "
                f"strong sales volume. The region has the "
                f"lowest profit margin at "
                f"<b>{worst_margin:.2f}%</b> and an average "
                f"discount of <b>{worst_discount:.2f}%</b>."
            )

        return (
            f"<b>{worst_region}</b> is the weakest-performing "
            f"region with a profit margin of "
            f"<b>{worst_margin:.2f}%</b>, compared with a "
            f"best regional margin of "
            f"<b>{best_margin:.2f}%</b>."
        )

    if profit_col and sales_col:

        total_sales = safe_sum(df[sales_col])
        total_profit = safe_sum(df[profit_col])

        margin = (
            total_profit / total_sales * 100
            if total_sales
            else 0
        )

        return (
            f"Overall profitability is "
            f"<b>{margin:.2f}%</b> based on the available "
            f"sales and profit data."
        )

    return (
        "InsightOps found useful business metrics but could "
        "not determine a single dominant business problem."
    )

def build_recommendations(
    df,
    cols,
    regional
):

    recommendations = []

    if regional is not None and "margin" in regional.columns:

        worst = regional["margin"].idxmin()

        recommendations.append(
            f"Review pricing and discounting practices in the "
            f"{worst} region."
        )

        recommendations.append(
            f"Investigate the lowest-margin transactions in "
            f"{worst} and identify recurring product patterns."
        )

    if cols["discount"]:

        recommendations.append(
            "Establish discount approval controls for unusually "
            "high discount transactions."
        )

    recommendations.append(
        "Validate important patterns using additional historical "
        "and operational data before making major decisions."
    )

    return recommendations[:3]

def create_chart_layout(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        font=dict(
            family="Inter",
            size=10,
            color="#d8dcea"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )

    return fig

# ============================================================
# LOAD DATA
# ============================================================

if uploaded_file is not None:

    if (
        st.session_state.file_name
        != uploaded_file.name
    ):

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".csv"
            ) as temp:

                temp.write(
                    uploaded_file.getvalue()
                )

                temp_path = temp.name

            df = load_csv(temp_path)

            os.unlink(temp_path)

            st.session_state.df = df
            st.session_state.file_name = uploaded_file.name
            st.session_state.analysis_complete = False
            st.session_state.analysis_data = {}

        except Exception as e:

            st.error(
                f"Could not read CSV: {e}"
            )

            st.stop()

    df = st.session_state.df

    if df is None:
        st.stop()

    st.success(
        f"Dataset loaded: **{uploaded_file.name}**"
    )

else:

    st.info(
        "Upload a CSV business dataset to begin."
    )

# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_button and uploaded_file is not None:

    with st.spinner(
        "InsightOps is investigating your dataset..."
    ):

        cols = detect_business_columns(df)

        regional = regional_analysis(
            df,
            cols["region"],
            cols["sales"],
            cols["profit"],
            cols["discount"]
        )

        products = product_analysis(
            df,
            cols["product"] or cols["category"],
            cols["sales"],
            cols["profit"]
        )

        correlation = calculate_discount_profit_correlation(
            df,
            cols["discount"],
            cols["profit"]
        )

        anomaly_column = (
            cols["discount"]
            or cols["profit"]
            or cols["sales"]
            or cols["quantity"]
        )

        anomalies = detect_anomalies_local(
            df,
            anomaly_column
        )

        insight = build_business_insight(
            df,
            cols,
            regional,
            correlation
        )

        recommendations = build_recommendations(
            df,
            cols,
            regional
        )

        st.session_state.analysis_data = {
            "cols": cols,
            "regional": regional,
            "products": products,
            "correlation": correlation,
            "anomalies": anomalies,
            "insight": insight,
            "recommendations": recommendations
        }

        st.session_state.analysis_complete = True
        st.rerun()

elif analyze_button and uploaded_file is None:
    st.warning("Please upload a CSV file first.")

# ============================================================
# USE ANALYSIS DATA (if available)
# ============================================================

if st.session_state.analysis_complete and st.session_state.analysis_data:

    analysis = st.session_state.analysis_data
    df = st.session_state.df

    cols = analysis["cols"]
    regional = analysis["regional"]
    products = analysis["products"]
    correlation = analysis["correlation"]
    anomalies = analysis["anomalies"]
    insight = analysis["insight"]
    recommendations = analysis["recommendations"]

    # KPI VALUES
    total_rows = len(df)
    total_columns = len(df.columns)
    missing_values = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())

    sales_col = cols["sales"]
    profit_col = cols["profit"]
    discount_col = cols["discount"]

    total_sales = safe_sum(df[sales_col]) if sales_col else 0
    total_profit = safe_sum(df[profit_col]) if profit_col else 0
    average_sales = safe_mean(df[sales_col]) if sales_col else 0
    average_profit = safe_mean(df[profit_col]) if profit_col else 0

else:
    # Default values when no analysis is done
    df = None
    cols = {}
    regional = None
    products = None
    correlation = None
    anomalies = pd.DataFrame()
    insight = "Upload a dataset and click 'Analyze Dataset' to get insights."
    recommendations = ["Upload a dataset to get recommendations."]
    total_rows = 0
    total_columns = 0
    missing_values = 0
    duplicates = 0
    sales_col = None
    profit_col = None
    discount_col = None
    total_sales = 0
    total_profit = 0
    average_sales = 0
    average_profit = 0

# ============================================================
# TAB CONTENT
# ============================================================

current_tab = st.session_state.current_tab

# ============================================================
# TAB 1: DASHBOARD
# ============================================================

if current_tab == "📊 Dashboard":

    st.markdown(
        """
        <div class="section-title">
        📊 Dashboard Overview
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete and df is not None:
        # KPI CARDS
        kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

        kpi_items = [
            {"icon": "📄", "label": "Total Rows", "value": f"{total_rows:,}", "sub": "Transactions"},
            {"icon": "▦", "label": "Columns", "value": f"{total_columns:,}", "sub": "Fields"},
            {"icon": "⚠️", "label": "Missing Values", "value": f"{missing_values:,}", "sub": "Total Missing"},
            {"icon": "✓", "label": "Duplicates", "value": f"{duplicates:,}", "sub": "Duplicate Rows"},
            {"icon": "💰", "label": "Total Revenue", "value": money(total_sales), "sub": "Sum"},
            {"icon": "📈", "label": "Total Profit", "value": money(total_profit), "sub": "Sum"}
        ]

        with kpi_col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi_items[0]['icon']}</div>
                <div class="kpi-label">{kpi_items[0]['label']}</div>
                <div class="kpi-value">{kpi_items[0]['value']}</div>
                <div class="kpi-small">{kpi_items[0]['sub']}</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi_items[1]['icon']}</div>
                <div class="kpi-label">{kpi_items[1]['label']}</div>
                <div class="kpi-value">{kpi_items[1]['value']}</div>
                <div class="kpi-small">{kpi_items[1]['sub']}</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi_items[2]['icon']}</div>
                <div class="kpi-label">{kpi_items[2]['label']}</div>
                <div class="kpi-value">{kpi_items[2]['value']}</div>
                <div class="kpi-small">{kpi_items[2]['sub']}</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_col4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi_items[3]['icon']}</div>
                <div class="kpi-label">{kpi_items[3]['label']}</div>
                <div class="kpi-value">{kpi_items[3]['value']}</div>
                <div class="kpi-small">{kpi_items[3]['sub']}</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_col5:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi_items[4]['icon']}</div>
                <div class="kpi-label">{kpi_items[4]['label']}</div>
                <div class="kpi-value">{kpi_items[4]['value']}</div>
                <div class="kpi-small">{kpi_items[4]['sub']}</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi_col6:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{kpi_items[5]['icon']}</div>
                <div class="kpi-label">{kpi_items[5]['label']}</div>
                <div class="kpi-value">{kpi_items[5]['value']}</div>
                <div class="kpi-small">{kpi_items[5]['sub']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # CHARTS ROW
        chart_left, chart_middle, chart_right = st.columns(
            [1.55, 1, 1],
            gap="small"
        )

        # REVENUE VS PROFIT
        with chart_left:

            st.markdown(
                """
                <div class="section-title">
                💰 Revenue vs Profit Over Time
                </div>
                """,
                unsafe_allow_html=True
            )

            if cols.get("date") and sales_col:

                temp = df.copy()

                temp[cols["date"]] = pd.to_datetime(
                    temp[cols["date"]],
                    errors="coerce"
                )

                temp = temp.dropna(
                    subset=[cols["date"]]
                )

                if len(temp) > 0:

                    temp[sales_col] = pd.to_numeric(temp[sales_col], errors='coerce')

                    temp["Month"] = temp[
                        cols["date"]
                    ].dt.strftime("%b")

                    temp["MonthNumber"] = temp[
                        cols["date"]
                    ].dt.month

                    if profit_col:
                        temp[profit_col] = pd.to_numeric(temp[profit_col], errors='coerce')

                        monthly = (
                            temp
                            .groupby(
                                ["MonthNumber", "Month"]
                            )
                            .agg(
                                Revenue=(sales_col, "sum"),
                                Profit=(profit_col, "sum")
                            )
                            .reset_index()
                            .sort_values("MonthNumber")
                        )

                        fig = go.Figure()

                        fig.add_trace(
                            go.Scatter(
                                x=monthly["Month"],
                                y=monthly["Revenue"],
                                name="Revenue",
                                mode="lines+markers",
                                line=dict(width=2.5),
                                marker=dict(size=6)
                            )
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=monthly["Month"],
                                y=monthly["Profit"],
                                name="Profit",
                                mode="lines+markers",
                                line=dict(width=2.5),
                                marker=dict(size=6)
                            )
                        )

                        fig = create_chart_layout(fig)

                        fig.update_layout(
                            height=280,
                            yaxis_tickprefix="$",
                            hovermode="x unified"
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            config={"displayModeBar": False}
                        )

                    else:

                        monthly = (
                            temp
                            .groupby(
                                ["MonthNumber", "Month"]
                            )[sales_col]
                            .sum()
                            .reset_index()
                            .sort_values("MonthNumber")
                        )

                        fig = px.line(
                            monthly,
                            x="Month",
                            y=sales_col,
                            markers=True
                        )

                        fig = create_chart_layout(fig)

                        fig.update_layout(
                            height=280
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            config={"displayModeBar": False}
                        )

            else:

                st.info(
                    "A date and sales column are required "
                    "for the time-series chart."
                )

        # REVENUE BY REGION
        with chart_middle:

            st.markdown(
                """
                <div class="section-title">
                📍 Revenue by Region
                </div>
                """,
                unsafe_allow_html=True
            )

            if regional is not None and sales_col:

                chart_df = regional.reset_index()

                fig = px.pie(
                    chart_df,
                    names=cols["region"],
                    values="sales",
                    hole=0.55
                )

                fig.update_traces(
                    textinfo="percent",
                    textfont_size=10
                )

                fig.update_layout(
                    height=280,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        x=0.98,
                        y=0.5
                    )
                )

                fig = create_chart_layout(fig)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

            else:

                st.info(
                    "Region and sales columns required."
                )

        # REVENUE BY PRODUCT
        with chart_right:

            st.markdown(
                """
                <div class="section-title">
                📦 Revenue by Product
                </div>
                """,
                unsafe_allow_html=True
            )

            product_col = (
                cols.get("product")
                or cols.get("category")
                or cols.get("subcategory")
            )

            if product_col and sales_col:

                df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')

                product_chart = (
                    df.groupby(product_col)[sales_col]
                    .sum()
                    .sort_values(ascending=True)
                    .tail(7)
                    .reset_index()
                )

                product_chart.columns = [product_col, "Revenue"]

                product_chart = product_chart.sort_values("Revenue", ascending=True)

                fig = px.bar(
                    product_chart,
                    x="Revenue",
                    y=product_col,
                    orientation="h",
                    text="Revenue",
                    color="Revenue",
                    color_continuous_scale="Blues"
                )

                fig.update_traces(
                    texttemplate='$%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>'
                )

                fig = create_chart_layout(fig)

                fig.update_layout(
                    height=300,
                    showlegend=False,
                    xaxis_title="Revenue ($)",
                    yaxis_title="",
                    xaxis=dict(
                        tickprefix="$",
                        tickformat=",.0f"
                    ),
                    margin=dict(l=10, r=40, t=10, b=10)
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

            else:

                st.info(
                    "Product and sales columns required."
                )

        # AI BUSINESS ANALYST - Already shown here but also in its own tab
        st.markdown("<br>", unsafe_allow_html=True)

        ai_left, ai_right = st.columns(
            [2.2, 1],
            gap="small"
        )

        with ai_left:

            st.markdown(
                """
                <div class="section-title">
                🤖 AI Business Analyst
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="problem-card">

                <div class="problem-title">
                ⚠️ BIGGEST BUSINESS PROBLEM
                </div>

                <div class="problem-text">
                {insight}
                </div>

                <div class="insight-card">

                <div class="insight-title">
                🔎 Key Insight
                </div>

                <div class="insight-text">
                InsightOps analyzed the dataset using
                business KPIs, segment comparisons,
                anomaly detection and relationship analysis.
                </div>

                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        with ai_right:

            st.markdown(
                """
                <div class="section-title">
                💡 Top 3 Recommendations
                </div>
                """,
                unsafe_allow_html=True
            )

            for index, recommendation in enumerate(
                recommendations,
                start=1
            ):
                st.markdown(
                    f"""
                    <div class="recommendation">
                        <div class="rec-number">{index}</div>
                        <div class="rec-text">{recommendation}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # DATASET PREVIEW
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="section-title">
            👀 Dataset Preview
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander(
            "View Dataset",
            expanded=False
        ):

            st.dataframe(
                df.head(20),
                use_container_width=True,
                height=350
            )
    else:
        st.info("📊 Upload a CSV file and click 'Analyze Dataset' to see the dashboard.")

# ============================================================
# TAB 2: OVERVIEW
# ============================================================

elif current_tab == "📈 Overview":

    st.markdown(
        """
        <div class="section-title">
        📈 Dataset Overview
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete and df is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **Dataset Summary**
            - Total Records: {total_rows:,}
            - Total Columns: {total_columns}
            - Missing Values: {missing_values:,}
            - Duplicate Rows: {duplicates:,}
            """)

        with col2:
            if sales_col and profit_col:
                total_sales_val = safe_sum(df[sales_col])
                total_profit_val = safe_sum(df[profit_col])
                margin = (total_profit_val / total_sales_val * 100) if total_sales_val else 0
                st.markdown(f"""
                **Financial Summary**
                - Total Revenue: {money(total_sales_val)}
                - Total Profit: {money(total_profit_val)}
                - Profit Margin: {pct(margin)}
                """)

        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.info("📊 Upload a CSV file and click 'Analyze Dataset' to see the overview.")

# ============================================================
# TAB 3: AI BUSINESS ANALYST (Moved up)
# ============================================================

elif current_tab == "🤖 AI Business Analyst":

    st.markdown(
        """
        <div class="section-title">
        🤖 AI Business Analyst
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete:

        st.markdown(
            f"""
            <div class="problem-card">

            <div class="problem-title">
            ⚠️ BIGGEST BUSINESS PROBLEM
            </div>

            <div class="problem-text">
            {insight}
            </div>

            <div class="insight-card">

            <div class="insight-title">
            🔎 Key Insight
            </div>

            <div class="insight-text">
            InsightOps analyzed the dataset using
            business KPIs, segment comparisons,
            anomaly detection and relationship analysis.
            </div>

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="section-title">
            💡 Top 3 Recommendations
            </div>
            """,
            unsafe_allow_html=True
        )

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):
            st.markdown(
                f"""
                <div class="recommendation">
                    <div class="rec-number">{index}</div>
                    <div class="rec-text">{recommendation}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("🤖 Upload a CSV file and click 'Analyze Dataset' to get AI insights.")

# ============================================================
# TAB 4: SEGMENT ANALYSIS
# ============================================================

elif current_tab == "📊 Segment Analysis":

    st.markdown(
        """
        <div class="section-title">
        📊 Segment Analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete and regional is not None and "margin" in regional.columns:

        display_region = regional.reset_index()

        st.dataframe(
            display_region,
            use_container_width=True
        )

        fig = px.bar(
            display_region,
            x=cols["region"],
            y="margin",
            title="Profit Margin by Region",
            color="margin",
            color_continuous_scale="RdYlGn"
        )

        fig = create_chart_layout(fig)
        fig.update_layout(height=400)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    else:
        st.info("📊 Upload a CSV file and click 'Analyze Dataset' to see segment analysis.")

# ============================================================
# TAB 5: PRODUCT ANALYSIS
# ============================================================

elif current_tab == "📦 Product Analysis":

    st.markdown(
        """
        <div class="section-title">
        📦 Product Analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete and df is not None:

        product_col = (
            cols.get("product")
            or cols.get("category")
            or cols.get("subcategory")
        )

        if product_col and sales_col:

            df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
            if profit_col:
                df[profit_col] = pd.to_numeric(df[profit_col], errors='coerce')

            product_analysis_data = (
                df.groupby(product_col)
                .agg({
                    sales_col: "sum",
                    **({profit_col: "sum"} if profit_col else {})
                })
                .reset_index()
            )

            if profit_col and profit_col in product_analysis_data.columns:
                product_analysis_data["Margin"] = (
                    product_analysis_data[profit_col] / product_analysis_data[sales_col] * 100
                )

            st.dataframe(
                product_analysis_data,
                use_container_width=True
            )

            top_products = product_analysis_data.nlargest(10, sales_col)

            fig = px.bar(
                top_products,
                x=product_col,
                y=sales_col,
                title="Top 10 Products by Revenue"
            )

            fig = create_chart_layout(fig)
            fig.update_layout(height=400)

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        else:
            st.warning("Product data not available for analysis.")
    else:
        st.info("📊 Upload a CSV file and click 'Analyze Dataset' to see product analysis.")

# ============================================================
# TAB 6: DISCOUNT ANALYSIS
# ============================================================

elif current_tab == "♙ Discount Analysis":

    st.markdown(
        """
        <div class="section-title">
        ♙ Discount Analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete and discount_col and profit_col:

        df[discount_col] = pd.to_numeric(df[discount_col], errors='coerce')
        df[profit_col] = pd.to_numeric(df[profit_col], errors='coerce')

        scatter_df = df[
            [discount_col, profit_col]
        ].copy()

        scatter_df = scatter_df.dropna()

        if sales_col:
            df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
            scatter_df["Profit Margin"] = (
                scatter_df[profit_col] / df.loc[scatter_df.index, sales_col] * 100
            )

        fig = px.scatter(
            scatter_df,
            x=discount_col,
            y="Profit Margin" if sales_col else profit_col,
            opacity=0.55,
            trendline="ols",
            title="Discount vs Profitability"
        )

        fig = create_chart_layout(fig)
        fig.update_layout(height=400)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        if correlation is not None:
            st.metric("Discount-Profit Correlation", f"{correlation:.3f}")

    else:
        st.info("📊 Upload a CSV file and click 'Analyze Dataset' to see discount analysis.")

# ============================================================
# TAB 7: ANOMALY DETECTION
# ============================================================

elif current_tab == "△ Anomaly Detection":

    st.markdown(
        """
        <div class="section-title">
        △ Anomaly Detection
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete and len(anomalies) > 0:

        st.warning(f"Found {len(anomalies)} anomalies in the dataset.")

        st.dataframe(
            anomalies,
            use_container_width=True
        )

    elif st.session_state.analysis_complete:
        st.success("✅ No anomalies detected in the dataset.")
    else:
        st.info("📊 Upload a CSV file and click 'Analyze Dataset' to detect anomalies.")

# ============================================================
# TAB 8: CORRELATIONS
# ============================================================

elif current_tab == "♧ Correlations":

    st.markdown(
        """
        <div class="section-title">
        ♧ Correlation Analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete and df is not None:

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) > 1:

            corr_matrix = df[numeric_cols].corr()

            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title="Correlation Matrix"
            )

            fig = create_chart_layout(fig)
            fig.update_layout(height=500)

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        else:
            st.warning("Not enough numeric columns for correlation analysis.")
    else:
        st.info("📊 Upload a CSV file and click 'Analyze Dataset' to see correlations.")

# ============================================================
# TAB 9: REPORTS
# ============================================================

elif current_tab == "📄 Reports":

    st.markdown(
        """
        <div class="section-title">
        📄 Executive Report
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete:

        report_dir = "reports"

        os.makedirs(
            report_dir,
            exist_ok=True
        )

        report_path = os.path.join(
            report_dir,
            "insightops_executive_report.pdf"
        )

        summary = (
            f"InsightOps analyzed {total_rows:,} records and "
            f"{total_columns} columns. "
            f"The requested business objective was: "
            f"{st.session_state.objective}"
        )

        findings = [
            f"Dataset contains {total_rows:,} records.",
            f"Dataset contains {total_columns} columns.",
            f"Total missing values: {missing_values:,}.",
            f"Duplicate rows: {duplicates:,}."
        ]

        if regional is not None and "margin" in regional.columns:

            worst_region = regional["margin"].idxmin()

            findings.append(
                f"{worst_region} has the weakest regional "
                f"profit margin at "
                f"{regional.loc[worst_region, 'margin']:.2f}%."
            )

        if correlation is not None:

            findings.append(
                f"Discount vs profit correlation: "
                f"{correlation:.3f}."
            )

        try:

            create_report(
                report_path,
                "InsightOps Executive Business Report",
                summary,
                findings,
                recommendations
            )

            with open(
                report_path,
                "rb"
            ) as pdf_file:

                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_file,
                    file_name="insightops_executive_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:

            st.warning(
                f"Could not generate PDF report: {e}"
            )
    else:
        st.info("📄 Upload a CSV file and click 'Analyze Dataset' to generate reports.")

# ============================================================
# DATA QUALITY - Show on all tabs
# ============================================================

if st.session_state.analysis_complete and df is not None:

    st.markdown("<br>", unsafe_allow_html=True)

    quality_left, quality_right = st.columns(
        [1, 1],
        gap="small"
    )

    with quality_left:

        st.markdown(
            """
            <div class="section-title">
            🧹 Data Quality
            </div>
            """,
            unsafe_allow_html=True
        )

        quality = pd.DataFrame(
            {
                "Column": df.columns,
                "Missing": [
                    int(df[col].isnull().sum())
                    for col in df.columns
                ],
                "Type": [
                    str(df[col].dtype)
                    for col in df.columns
                ]
            }
        )

        st.dataframe(
            quality,
            use_container_width=True,
            hide_index=True,
            height=300
        )

    with quality_right:

        st.markdown(
            """
            <div class="section-title">
            🧠 Detected Business Columns
            </div>
            """,
            unsafe_allow_html=True
        )

        detected = []

        for key, value in cols.items():

            if value:

                detected.append(
                    {
                        "Business Role": key.title(),
                        "Detected Column": str(value)
                    }
                )

        if detected:

            st.dataframe(
                pd.DataFrame(detected),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "No standard business columns detected."
            )

    # LIMITATIONS
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="dashboard-card">

        <div class="section-title">
        ⚠️ Limitations
        </div>

        <div style="
            color:#8f97aa;
            font-size:11px;
            line-height:1.7;
        ">

        InsightOps identifies patterns and associations in the
        provided dataset. Correlation does not establish causation.
        Statistical conclusions should be validated with additional
        historical and operational data.

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
    InsightOps · Powered by Python, Pandas, Streamlit & Gemini AI ❤️
    </div>
    """,
    unsafe_allow_html=True
)