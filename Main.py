"""Main entry point for the PhonePe Pulse Data Visualization Streamlit app.

This dashboard visualizes PhonePe transaction, user, and insurance metrics across India.
Run with: `streamlit run Main.py`
"""

import streamlit as st
import streamlit_shadcn_ui as ui
import sys
sys.path.insert(0, '.')

from utils.config import (
    render_breadcrumbs
)

# Set Streamlit page configuration
st.set_page_config(
    page_title="PhonePe Pulse - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏠",
)

# Custom CSS for enhanced aesthetics
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .hero-section {
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .hero-section h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        color: white !important;
    }
    .hero-section p {
        font-size: 1.4rem;
        opacity: 0.95;
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        height: 100%;
        transition: all 0.3s ease;
        border: 1px solid #eee;
    }
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.1);
        border-color: #2575fc;
    }
    .feature-card h4 {
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .step-number {
        background: #2575fc;
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .guide-item {
        margin-bottom: 2rem;
        display: flex;
        align-items: flex-start;
    }
</style>
""", unsafe_allow_html=True)

# Render breadcrumb navigation
render_breadcrumbs("Main")

# --- Hero Section ---
st.markdown("""
<div class="hero-section">
    <h1>🚀 PhonePe Pulse Visualization</h1>
    <p>
        Unveiling the power of digital payments and financial trends across the diverse landscape of India.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Project Summary ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("### 📊 Project Overview")
    st.write("""
    Welcome to the **PhonePe Pulse Data Visualization Dashboard**. This interactive platform transforms raw transaction 
    and user data from the PhonePe Pulse repository into meaningful insights. 
    
    Whether you're looking for macro-level state trends or micro-level district performance, this dashboard 
    provides the tools to visualize the growth of digital transactions, insurance adoption, and user demographics 
    since 2018.
    """)
    
    st.markdown("### 🛠 Explore Dashboard Modules")
    
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📈 Visualizations</h4>
            <p>Deep dive into transaction counts, amounts, and growth metrics with interactive Plotly charts.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h4>🗺️ Geospatial Mapping</h4>
            <p>Visualize the distribution of financial activity across Indian states and districts using choropleth maps.</p>
        </div>
        """, unsafe_allow_html=True)

    with f_col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🔟 Top Charts</h4>
            <p>Identify the leaders! See top performing states, districts, and pincodes at a glance.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h4>🏘️ District Drill-down</h4>
            <p>Grasp the granular details by exploring data down to the specific district level within any state.</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.image("https://raw.githubusercontent.com/Shyams728/phonepe_data_visualisation/main/visualization.png")
    
    st.markdown("### 🚦 Quick Stats")
    ui_cols = st.columns(2)
    with ui_cols[0]:
        ui.metric_card(title="States", content="36", description="States & UTs Covered", key="main_states")
    with ui_cols[1]:
        ui.metric_card(title="Years", content="2018-24", description="Temporal Coverage", key="main_range")
    
    st.info("💡 **Tip:** All charts are interactive. You can hover, zoom, and even download them as PNGs!")

st.markdown("---")

# --- User Guide ---
st.markdown("### 📖 How to Get Started")
guide_col1, guide_col2 = st.columns(2)

with guide_col1:
    st.markdown("""
    <div class="guide-item">
        <span class="step-number">1</span>
        <div>
            <strong>Select a Module</strong><br>
            Use the sidebar on the left to navigate between different pages like Mapping, Visualizations, or Top Charts.
        </div>
    </div>
    <div class="guide-item">
        <span class="step-number">2</span>
        <div>
            <strong>Adjust Filters</strong><br>
            Use the dropdown menus at the top of each page to select the Year, Quarter, or Metric you want to analyze.
        </div>
    </div>
    """, unsafe_allow_html=True)

with guide_col2:
    st.markdown("""
    <div class="guide-item">
        <span class="step-number">3</span>
        <div>
            <strong>Drill into Details</strong><br>
            Click on map regions or bar elements to get more specific information about those areas.
        </div>
    </div>
    <div class="guide-item">
        <span class="step-number">4</span>
        <div>
            <strong>Analyze Trends</strong><br>
            Observe the Year-over-Year (YoY) growth and CAGR metrics to understand how digital payments are evolving.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Tech Stack ---
st.markdown("### 💻 Powered By")
tech_cols = st.columns(4)
with tech_cols[0]: st.markdown("**Streamlit** (UI Framework)")
with tech_cols[1]: st.markdown("**Plotly** (Interactive Charts)")
with tech_cols[2]: st.markdown("**Pandas** (Data Processing)")
with tech_cols[3]: st.markdown("**SQLite** (Data Storage)")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding-bottom: 2rem;">
    PhonePe Pulse Data Visualization Dashboard • MIT License • 2026
</div>
""", unsafe_allow_html=True)
