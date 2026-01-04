"""
📱 Phone Brand Market Share Analysis
=====================================
Analyze phone brand distribution and market share across states and time periods.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit_shadcn_ui as ui
import sys
sys.path.insert(0, '..')

from utils.config import (
    load_user_state_data,
    load_data_cached,
    format_number,
    format_percentage,
    render_breadcrumbs,
    COLORS,
    PLOTLY_SCALES
)

# Page Configuration
st.set_page_config(
    page_title="PhonePe - Phone Brand Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📱",
)

render_breadcrumbs("Phone_Brands")

# =============================================================================
# Load Data
# =============================================================================
@st.cache_data(ttl=3600)
def get_phone_brand_data():
    """Load and preprocess phone brand data."""
    df = load_data_cached('SELECT * FROM agregated_user_state')
    if not df.empty:
        df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))
    return df

df = get_phone_brand_data()

if df.empty:
    st.error("No phone brand data available.")
    st.stop()

# =============================================================================
# Filters
# =============================================================================
st.markdown("### 🎛️ Filters")
filter_container = st.container(border=True)
col1, col2, col3 = filter_container.columns(3)

with col1:
    selected_years = st.multiselect(
        "Select Years",
        options=sorted(df['year'].unique()),
        default=sorted(df['year'].unique())[-2:] if len(df['year'].unique()) >= 2 else list(df['year'].unique())
    )

with col2:
    selected_quarters = st.multiselect(
        "Select Quarters",
        options=sorted(df['quarter'].unique()),
        default=list(df['quarter'].unique())
    )

with col3:
    selected_states = st.multiselect(
        "Select States",
        options=sorted(df['state'].unique()),
        default=[]
    )

# Apply filters
filtered_df = df[
    (df['year'].isin(selected_years)) & 
    (df['quarter'].isin(selected_quarters))
]

if selected_states:
    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

# =============================================================================
# KPI Section
# =============================================================================
st.markdown("---")
st.markdown("### 📊 Key Metrics")

# Calculate KPIs
total_users = filtered_df['registered_users'].sum() if 'registered_users' in filtered_df.columns else 0
unique_brands = filtered_df['phone_brand'].nunique() if 'phone_brand' in filtered_df.columns else 0
total_phone_count = filtered_df['phone_count'].sum() if 'phone_count' in filtered_df.columns else 0

# Get top brand
if 'phone_brand' in filtered_df.columns and 'phone_count' in filtered_df.columns:
    brand_totals = filtered_df.groupby('phone_brand')['phone_count'].sum()
    top_brand = brand_totals.idxmax() if len(brand_totals) > 0 else "N/A"
    top_brand_share = (brand_totals.max() / brand_totals.sum() * 100) if brand_totals.sum() > 0 else 0
else:
    top_brand = "N/A"
    top_brand_share = 0

kpi_cols = st.columns(4)
with kpi_cols[0]:
    ui.metric_card(
        title="Total Registered Users",
        content=format_number(total_users),
        description="Across selected filters",
        key="phone_kpi1"
    )

with kpi_cols[1]:
    ui.metric_card(
        title="Phone Brands Tracked",
        content=str(unique_brands),
        description="Unique brands in data",
        key="phone_kpi2"
    )

with kpi_cols[2]:
    ui.metric_card(
        title="Market Leader",
        content=top_brand,
        description=f"Share: {top_brand_share:.1f}%",
        key="phone_kpi3"
    )

with kpi_cols[3]:
    ui.metric_card(
        title="Total Device Count",
        content=format_number(total_phone_count),
        description="Total phones tracked",
        key="phone_kpi4"
    )

# =============================================================================
# Market Share Analysis
# =============================================================================
st.markdown("---")
st.markdown("### 📱 Brand Market Share Analysis")

if 'phone_brand' in filtered_df.columns and 'phone_count' in filtered_df.columns:
    # Aggregate by brand
    brand_share = filtered_df.groupby('phone_brand').agg({
        'phone_count': 'sum',
        'Percentage': 'mean'
    }).reset_index()
    brand_share = brand_share.sort_values('phone_count', ascending=False)
    brand_share['market_share'] = brand_share['phone_count'] / brand_share['phone_count'].sum() * 100

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Donut chart for market share
        fig_donut = px.pie(
            brand_share.head(10),
            values='phone_count',
            names='phone_brand',
            hole=0.5,
            title='📊 Top 10 Phone Brands - Market Share',
            color_discrete_sequence=COLORS['categorical']
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        # Horizontal bar chart
        fig_bar = px.bar(
            brand_share.head(10),
            y='phone_brand',
            x='phone_count',
            orientation='h',
            title='📈 Top 10 Phone Brands by Device Count',
            color='phone_count',
            color_continuous_scale=PLOTLY_SCALES['users']
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # =============================================================================
    # Brand Trends Over Time
    # =============================================================================
    st.markdown("---")
    st.markdown("### 📈 Brand Trends Over Time")

    # Get top 5 brands for trend analysis
    top_5_brands = brand_share.head(5)['phone_brand'].tolist()
    trend_df = filtered_df[filtered_df['phone_brand'].isin(top_5_brands)]
    
    # Aggregate by year and brand
    yearly_trend = trend_df.groupby(['year', 'phone_brand'])['phone_count'].sum().reset_index()
    
    fig_trend = px.line(
        yearly_trend,
        x='year',
        y='phone_count',
        color='phone_brand',
        markers=True,
        title='📊 Top 5 Brand Trends by Year',
        labels={'phone_count': 'Device Count', 'year': 'Year', 'phone_brand': 'Brand'}
    )
    fig_trend.update_traces(line=dict(width=3), marker=dict(size=10))
    st.plotly_chart(fig_trend, use_container_width=True)

    # =============================================================================
    # State-wise Brand Distribution
    # =============================================================================
    st.markdown("---")
    st.markdown("### 🗺️ State-wise Brand Distribution")

    # Heatmap: Brand vs State
    state_brand = filtered_df.groupby(['state', 'phone_brand'])['phone_count'].sum().reset_index()
    state_brand_pivot = state_brand.pivot(index='phone_brand', columns='state', values='phone_count').fillna(0)
    
    # Get top brands for heatmap
    top_brands_for_heatmap = brand_share.head(8)['phone_brand'].tolist()
    state_brand_pivot_filtered = state_brand_pivot.loc[state_brand_pivot.index.isin(top_brands_for_heatmap)]
    
    # Get top states by total count
    top_states = state_brand.groupby('state')['phone_count'].sum().nlargest(15).index.tolist()
    state_brand_pivot_filtered = state_brand_pivot_filtered[
        [col for col in state_brand_pivot_filtered.columns if col in top_states]
    ]

    if not state_brand_pivot_filtered.empty:
        fig_heatmap = px.imshow(
            state_brand_pivot_filtered,
            title='🔥 Brand Distribution Heatmap (Top 8 Brands × Top 15 States)',
            labels=dict(x="State", y="Phone Brand", color="Device Count"),
            aspect="auto",
            color_continuous_scale=PLOTLY_SCALES['heatmap']
        )
        fig_heatmap.update_layout(height=500)
        fig_heatmap.update_xaxes(tickangle=45)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # =============================================================================
    # Brand Competition Analysis
    # =============================================================================
    st.markdown("---")
    st.markdown("### 🏆 Brand Competition Analysis")

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        # Treemap
        fig_treemap = px.treemap(
            brand_share.head(15),
            path=['phone_brand'],
            values='phone_count',
            title='📊 Market Share Treemap',
            color='market_share',
            color_continuous_scale=PLOTLY_SCALES['users']
        )
        st.plotly_chart(fig_treemap, use_container_width=True)

    with comp_col2:
        # Sunburst by Year > Brand
        if len(selected_years) > 1:
            sunburst_df = filtered_df.groupby(['year', 'phone_brand'])['phone_count'].sum().reset_index()
            sunburst_df = sunburst_df[sunburst_df['phone_brand'].isin(top_5_brands)]
            
            fig_sunburst = px.sunburst(
                sunburst_df,
                path=['year', 'phone_brand'],
                values='phone_count',
                title='🎯 Brand Distribution by Year',
                color='phone_count',
                color_continuous_scale=PLOTLY_SCALES['users']
            )
            st.plotly_chart(fig_sunburst, use_container_width=True)
        else:
            st.info("Select multiple years to see the sunburst chart.")

    # =============================================================================
    # Detailed Brand Table
    # =============================================================================
    st.markdown("---")
    st.markdown("### 📋 Detailed Brand Statistics")

    brand_stats = brand_share.copy()
    brand_stats['phone_count_formatted'] = brand_stats['phone_count'].apply(format_number)
    brand_stats['market_share_formatted'] = brand_stats['market_share'].apply(lambda x: f"{x:.2f}%")
    
    display_df = brand_stats[['phone_brand', 'phone_count_formatted', 'market_share_formatted']].head(15)
    display_df.columns = ['Phone Brand', 'Device Count', 'Market Share']
    
    ui.table(data=display_df, maxHeight=400, key="brand_stats_table")

else:
    st.warning("Phone brand data not available in the expected format.")
