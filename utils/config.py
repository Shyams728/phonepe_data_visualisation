"""
Shared Configuration and Utilities for PhonePe Dashboard
=========================================================
This module provides centralized configuration, caching, and common components.
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from functools import lru_cache
import os

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_CONFIG = {
    'sqlite_file': 'test.sqlite',
    'connection_string': 'sqlite:///test.sqlite'
}

# =============================================================================
# COLOR SCHEMES - PhonePe Inspired
# =============================================================================
COLORS = {
    # Primary PhonePe colors
    'primary': '#5f259f',          # PhonePe Purple
    'primary_light': '#7b3fa0',
    'primary_dark': '#4a1d7a',
    'secondary': '#00baf2',        # PhonePe Blue
    'accent': '#ff6b6b',           # Accent Red
    
    # Chart color palettes
    'sequential': ['#5f259f', '#7b3fa0', '#9659b8', '#b17dd0', '#cca1e8', '#e8c5ff'],
    'diverging': ['#ff6b6b', '#ffa5a5', '#ffffff', '#b17dd0', '#5f259f'],
    'categorical': [
        '#5f259f', '#00baf2', '#ff6b6b', '#4ecdc4', '#ffe66d', 
        '#95e1d3', '#f38181', '#aa96da', '#fcbad3', '#a8d8ea'
    ],
    
    # Status colors
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    
    # Growth indicators
    'positive_growth': '#28a745',
    'negative_growth': '#dc3545',
    'neutral': '#6c757d'
}

# Plotly color scales
PLOTLY_SCALES = {
    'transactions': 'Plasma_r',
    'insurance': 'Viridis_r',
    'users': 'Purples',
    'growth': 'RdYlGn',
    'heatmap': 'YlOrRd'
}

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
PAGE_CONFIG = {
    'Main': {'icon': '🏠', 'title': 'Home'},
    'visual': {'icon': '📈', 'title': 'Visualizations'},
    'Plotting': {'icon': '📊', 'title': 'Plotting'},
    'Mapping': {'icon': '🌍', 'title': 'Geographic Maps'},
    'Top_Charts': {'icon': '🔟', 'title': 'Top Charts'},
    'Dash_Board': {'icon': '📋', 'title': 'Dashboard'},
    'Phone_Brands': {'icon': '📱', 'title': 'Phone Brand Analysis'},
    'District_Drill': {'icon': '🏘️', 'title': 'District Analysis'}
}

# =============================================================================
# CACHED DATA LOADING FUNCTIONS
# =============================================================================
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_cached(query: str) -> pd.DataFrame:
    """
    Load data from SQLite database with caching.
    
    Args:
        query: SQL query string
        
    Returns:
        DataFrame with query results
    """
    try:
        engine = create_engine(DATABASE_CONFIG['connection_string'])
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_all_tables() -> list:
    """Get list of all tables in the database."""
    try:
        engine = create_engine(DATABASE_CONFIG['connection_string'])
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")
        return []


@st.cache_data(ttl=3600)
def load_insurance_state_data() -> pd.DataFrame:
    """Load and preprocess insurance state data."""
    df = load_data_cached('SELECT * FROM aggregated_insurence_state')
    if not df.empty:
        df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))
    return df


@st.cache_data(ttl=3600)
def load_transaction_state_data() -> pd.DataFrame:
    """Load and preprocess transaction state data."""
    df = load_data_cached('SELECT * FROM aggregated_transaction_state')
    if not df.empty:
        df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))
    return df


@st.cache_data(ttl=3600)
def load_user_state_data() -> pd.DataFrame:
    """Load and preprocess user state data with phone brand info."""
    df = load_data_cached('SELECT * FROM agregated_user_state')
    if not df.empty:
        df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))
    return df


@st.cache_data(ttl=3600)
def load_top_transaction_data() -> pd.DataFrame:
    """Load top transaction data including district information."""
    return load_data_cached('SELECT * FROM top_transaction_state')


@st.cache_data(ttl=3600)
def load_top_insurance_data() -> pd.DataFrame:
    """Load top insurance state data."""
    return load_data_cached('SELECT * FROM top_insurance_state')


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================
def format_currency(value: float, use_indian_system: bool = True) -> str:
    """
    Format number as Indian currency with appropriate units.
    
    Args:
        value: Numeric value to format
        use_indian_system: Use Crore/Lakh notation if True
        
    Returns:
        Formatted currency string
    """
    if value >= 1e9:
        return f"₹{value/1e9:.2f}B" if not use_indian_system else f"₹{value/1e7:.2f}Cr"
    elif value >= 1e7:
        return f"₹{value/1e7:.2f}Cr"
    elif value >= 1e5:
        return f"₹{value/1e5:.2f}L"
    elif value >= 1e3:
        return f"₹{value/1e3:.2f}K"
    else:
        return f"₹{value:,.2f}"


def format_number(value: float) -> str:
    """Format large numbers with appropriate units."""
    if value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e7:
        return f"{value/1e7:.2f}Cr"
    elif value >= 1e5:
        return f"{value/1e5:.2f}L"
    elif value >= 1e3:
        return f"{value/1e3:.2f}K"
    else:
        return f"{value:,.0f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage with indicator."""
    indicator = "📈" if value > 0 else "📉" if value < 0 else "➡️"
    return f"{indicator} {value:.{decimals}f}%"


def get_growth_color(value: float) -> str:
    """Get color based on growth value."""
    if value > 0:
        return COLORS['positive_growth']
    elif value < 0:
        return COLORS['negative_growth']
    return COLORS['neutral']


# =============================================================================
# BREADCRUMB NAVIGATION COMPONENT
# =============================================================================
def render_breadcrumbs(current_page: str, show_home: bool = True):
    """
    Render navigation breadcrumbs.
    
    Args:
        current_page: Name of the current page
        show_home: Whether to include home link
    """
    page_info = PAGE_CONFIG.get(current_page, {'icon': '📄', 'title': current_page})
    
    breadcrumb_style = """
    <style>
    .breadcrumb-container {
        background: linear-gradient(135deg, #5f259f22 0%, #00baf222 100%);
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #5f259f;
    }
    .breadcrumb-nav {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #333;
    }
    .breadcrumb-item {
        color: #5f259f;
        text-decoration: none;
        font-weight: 500;
    }
    .breadcrumb-separator {
        color: #999;
        margin: 0 4px;
    }
    .breadcrumb-current {
        color: #333;
        font-weight: 600;
    }
    .page-header {
        font-size: 28px;
        font-weight: 700;
        color: #5f259f;
        margin-top: 10px;
    }
    </style>
    """
    
    breadcrumb_html = f"""
    {breadcrumb_style}
    <div class="breadcrumb-container">
        <div class="breadcrumb-nav">
            {'<span class="breadcrumb-item">🏠 Home</span><span class="breadcrumb-separator">›</span>' if show_home else ''}
            <span class="breadcrumb-current">{page_info['icon']} {page_info['title']}</span>
        </div>
        <div class="page-header">{page_info['title']}</div>
    </div>
    """
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)


# =============================================================================
# COMMON PAGE SETUP
# =============================================================================
def setup_page(page_name: str, layout: str = "wide"):
    """
    Common page setup with configuration.
    
    Args:
        page_name: Name of the page
        layout: Page layout ('wide' or 'centered')
    """
    page_info = PAGE_CONFIG.get(page_name, {'icon': '📄', 'title': page_name})
    
    st.set_page_config(
        page_title=f"PhonePe - {page_info['title']}",
        layout=layout,
        initial_sidebar_state="collapsed",
        page_icon=page_info['icon'],
    )
    
    render_breadcrumbs(page_name)


# =============================================================================
# METRIC CARD HELPERS
# =============================================================================
def get_growth_indicator(value: float) -> str:
    """Get emoji indicator based on growth value."""
    if value > 10:
        return "🚀"
    elif value > 0:
        return "📈"
    elif value < -10:
        return "📉"
    elif value < 0:
        return "📉"
    return "➡️"


# =============================================================================
# STATE NAME STANDARDIZATION
# =============================================================================
def standardize_state_name(state: str) -> str:
    """Standardize state names for consistency."""
    return state.replace('-', ' ').title().replace(' And ', ' & ')


# =============================================================================
# GEOJSON URL FOR INDIA MAP
# =============================================================================
INDIA_GEOJSON_URL = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
