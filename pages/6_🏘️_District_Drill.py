"""
🏘️ District-Level Drill-Down Analysis
======================================
Analyze transactions, insurance, and user data at the district level.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit_shadcn_ui as ui
import sys
sys.path.insert(0, '..')

from utils.config import (
    load_data_cached,
    load_top_transaction_data,
    format_currency,
    format_number,
    render_breadcrumbs,
    COLORS,
    PLOTLY_SCALES,
    INDIA_GEOJSON_URL
)

# Page Configuration
st.set_page_config(
    page_title="PhonePe - District Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏘️",
)

render_breadcrumbs("District_Drill")

# =============================================================================
# Load Data
# =============================================================================
@st.cache_data(ttl=3600)
def get_district_data():
    """Load district-level transaction data."""
    df = load_data_cached('SELECT * FROM top_transaction_state')
    if not df.empty:
        df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))
    return df

@st.cache_data(ttl=3600)
def get_district_insurance_data():
    """Load district-level insurance data."""
    df = load_data_cached('SELECT * FROM top_insurance_state')
    if not df.empty:
        df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))
    return df

@st.cache_data(ttl=3600)
def get_district_user_data():
    """Load district-level user data."""
    df = load_data_cached('SELECT * FROM top_user_state')
    if not df.empty:
        df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))
    return df

# Load all data
transaction_df = get_district_data()
insurance_df = get_district_insurance_data()
user_df = get_district_user_data()

if transaction_df.empty:
    st.error("No district transaction data available.")
    st.stop()

# =============================================================================
# Data Type Selection
# =============================================================================
st.markdown("### 📊 Select Analysis Type")

data_type = st.radio(
    "Choose data to analyze:",
    options=["Transactions", "Insurance", "Users"],
    horizontal=True
)

# Select appropriate dataset
if data_type == "Transactions":
    df = transaction_df
    value_col = 'amount'
    count_col = 'count'
    icon = "💳"
elif data_type == "Insurance":
    df = insurance_df if not insurance_df.empty else transaction_df
    value_col = 'amount' if 'amount' in df.columns else 'count'
    count_col = 'count'
    icon = "🛡️"
else:
    df = user_df if not user_df.empty else transaction_df
    value_col = 'registeredUsers' if 'registeredUsers' in df.columns else 'count'
    count_col = 'count'
    icon = "👥"

# =============================================================================
# Filters
# =============================================================================
st.markdown("---")
st.markdown("### 🎛️ Filters")

filter_container = st.container(border=True)
col1, col2, col3, col4 = filter_container.columns(4)

with col1:
    selected_state = st.selectbox(
        "Select State",
        options=["All States"] + sorted(df['state'].unique().tolist())
    )

with col2:
    selected_years = st.multiselect(
        "Select Years",
        options=sorted(df['year'].unique()),
        default=[max(df['year'].unique())] if len(df['year'].unique()) > 0 else []
    )

with col3:
    selected_quarters = st.multiselect(
        "Select Quarters",
        options=sorted(df['quarter'].unique()),
        default=list(df['quarter'].unique())
    )

with col4:
    entity_types = df['entity_type'].unique().tolist() if 'entity_type' in df.columns else ['districts']
    selected_entity = st.selectbox(
        "Entity Type",
        options=entity_types,
        index=0 if 'districts' in entity_types else 0
    )

# Apply filters
filtered_df = df[
    (df['year'].isin(selected_years)) & 
    (df['quarter'].isin(selected_quarters))
]

if selected_state != "All States":
    filtered_df = filtered_df[filtered_df['state'] == selected_state]

if 'entity_type' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['entity_type'] == selected_entity]

# =============================================================================
# KPI Section
# =============================================================================
st.markdown("---")
st.markdown(f"### {icon} Key Metrics - {data_type}")

if value_col in filtered_df.columns:
    total_value = filtered_df[value_col].sum()
else:
    total_value = 0

if count_col in filtered_df.columns:
    total_count = filtered_df[count_col].sum()
else:
    total_count = 0

unique_entities = filtered_df['entity_name'].nunique() if 'entity_name' in filtered_df.columns else 0
avg_value = total_value / unique_entities if unique_entities > 0 else 0

# Top entity
if 'entity_name' in filtered_df.columns and value_col in filtered_df.columns:
    entity_totals = filtered_df.groupby('entity_name')[value_col].sum()
    top_entity = entity_totals.idxmax() if len(entity_totals) > 0 else "N/A"
    top_entity_value = entity_totals.max() if len(entity_totals) > 0 else 0
else:
    top_entity = "N/A"
    top_entity_value = 0

kpi_cols = st.columns(4)

with kpi_cols[0]:
    if data_type == "Users":
        ui.metric_card(
            title="Total Users",
            content=format_number(total_value),
            description=f"Registered users in {selected_entity}",
            key="district_kpi1"
        )
    else:
        ui.metric_card(
            title="Total Amount",
            content=format_currency(total_value),
            description=f"Total {data_type.lower()} amount",
            key="district_kpi1"
        )

with kpi_cols[1]:
    ui.metric_card(
        title="Total Transactions",
        content=format_number(total_count),
        description=f"Number of {data_type.lower()} transactions",
        key="district_kpi2"
    )

with kpi_cols[2]:
    ui.metric_card(
        title=f"Total {selected_entity.title()}",
        content=str(unique_entities),
        description=f"Unique {selected_entity} in selection",
        key="district_kpi3"
    )

with kpi_cols[3]:
    ui.metric_card(
        title=f"Top {selected_entity.title()[:-1] if selected_entity.endswith('s') else selected_entity}",
        content=top_entity[:15] + "..." if len(top_entity) > 15 else top_entity,
        description=format_currency(top_entity_value) if data_type != "Users" else format_number(top_entity_value),
        key="district_kpi4"
    )

# =============================================================================
# Top Districts/Pincodes Analysis
# =============================================================================
st.markdown("---")
st.markdown(f"### 🏆 Top {selected_entity.title()} Analysis")

if 'entity_name' in filtered_df.columns and value_col in filtered_df.columns:
    # Aggregate by entity
    agg_dict = {value_col: 'sum'}
    if count_col in filtered_df.columns:
        agg_dict[count_col] = 'sum'
        
    entity_agg = filtered_df.groupby('entity_name').agg(agg_dict).reset_index()
    entity_agg = entity_agg.sort_values(value_col, ascending=False)
    
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Top 10 bar chart
        top_10 = entity_agg.head(10)
        fig_bar = px.bar(
            top_10,
            y='entity_name',
            x=value_col,
            orientation='h',
            title=f'🏅 Top 10 {selected_entity.title()} by {"Amount" if data_type != "Users" else "Users"}',
            color=value_col,
            color_continuous_scale=PLOTLY_SCALES['transactions']
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        # Pie chart for top 10 share
        fig_pie = px.pie(
            top_10,
            values=value_col,
            names='entity_name',
            title=f'📊 Top 10 {selected_entity.title()} - Share Distribution',
            hole=0.4,
            color_discrete_sequence=COLORS['categorical']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # =============================================================================
    # State-wise Breakdown (if All States selected)
    # =============================================================================
    if selected_state == "All States":
        st.markdown("---")
        st.markdown("### 🗺️ State-wise Distribution")

        agg_dict = {
            value_col: 'sum',
            'entity_name': 'nunique'
        }
        if count_col in filtered_df.columns:
            agg_dict[count_col] = 'sum'
            
        state_agg = filtered_df.groupby('state').agg(agg_dict).reset_index()
        
        cols = ['State', 'Total Amount' if data_type != "Users" else 'Total Users']
        if count_col in filtered_df.columns:
            cols.append('Transaction Count')
        cols.append(f'{selected_entity.title()} Count')
        
        state_agg.columns = cols
        state_agg = state_agg.sort_values(state_agg.columns[1], ascending=False)

        map_col, table_col = st.columns([3, 2])

        with map_col:
            # Choropleth map
            fig_map = px.choropleth(
                state_agg,
                geojson=INDIA_GEOJSON_URL,
                featureidkey='properties.ST_NM',
                locations='State',
                color=state_agg.columns[1],
                hover_data=list(state_agg.columns),
                title=f"🗺️ {data_type} Distribution by State",
                color_continuous_scale=PLOTLY_SCALES['transactions']
            )
            fig_map.update_geos(fitbounds='locations', visible=False)
            fig_map.update_layout(height=500)
            st.plotly_chart(fig_map, use_container_width=True)

        with table_col:
            st.markdown(f"**State Rankings - Top 10**")
            display_state = state_agg.head(10).copy()
            if data_type != "Users":
                display_state['Total Amount'] = display_state['Total Amount'].apply(format_currency)
            else:
                display_state['Total Users'] = display_state['Total Users'].apply(format_number)
            if 'Transaction Count' in display_state.columns:
                display_state['Transaction Count'] = display_state['Transaction Count'].apply(format_number)
            ui.table(data=display_state, maxHeight=450, key="state_ranking_table")

    # =============================================================================
    # Quarterly Trends
    # =============================================================================
    if len(selected_years) >= 1:
        st.markdown("---")
        st.markdown("### 📈 Quarterly Trends")

        agg_dict = {value_col: 'sum'}
        if count_col in filtered_df.columns:
            agg_dict[count_col] = 'sum'
            
        quarterly_agg = filtered_df.groupby(['year', 'quarter']).agg(agg_dict).reset_index()
        quarterly_agg['period'] = quarterly_agg['year'].astype(str) + '-Q' + quarterly_agg['quarter'].astype(str)

        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:
            fig_trend = px.line(
                quarterly_agg,
                x='period',
                y=value_col,
                markers=True,
                title=f'📊 {"Amount" if data_type != "Users" else "Users"} Trend by Quarter',
                labels={value_col: 'Amount' if data_type != "Users" else 'Users', 'period': 'Period'}
            )
            fig_trend.update_traces(line=dict(width=3, color=COLORS['primary']), marker=dict(size=10))
            st.plotly_chart(fig_trend, use_container_width=True)

        with trend_col2:
            if count_col in quarterly_agg.columns:
                fig_trend_count = px.bar(
                    quarterly_agg,
                    x='period',
                    y=count_col,
                    title='📊 Transaction Count by Quarter',
                    labels={count_col: 'Transaction Count', 'period': 'Period'},
                    color='year',
                    color_discrete_sequence=COLORS['categorical']
                )
                st.plotly_chart(fig_trend_count, use_container_width=True)
            else:
                st.info("Transaction count data not available for this category.")

    # =============================================================================
    # Detailed Table
    # =============================================================================
    st.markdown("---")
    st.markdown(f"### 📋 Detailed {selected_entity.title()} Data")

    display_df = entity_agg.head(20).copy()
    
    label = 'Amount' if data_type != "Users" else 'Users'
    cols = [selected_entity.title()[:-1] if selected_entity.endswith('s') else selected_entity, label]
    
    if data_type != "Users":
        display_df[value_col] = display_df[value_col].apply(format_currency)
    else:
        display_df[value_col] = display_df[value_col].apply(format_number)
    
    if count_col in display_df.columns:
        display_df[count_col] = display_df[count_col].apply(format_number)
        cols.append('Transactions')
        
    display_df.columns = cols

    with st.expander("📊 View Detailed Data", expanded=True):
        ui.table(data=display_df, maxHeight=400, key="detailed_entity_table")

else:
    st.warning("Required data columns not available for analysis.")
