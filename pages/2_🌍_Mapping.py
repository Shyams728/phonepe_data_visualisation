"""
🌍 Geographic Maps - Enhanced with KPIs and Choropleth Maps
============================================================
Interactive choropleth maps with KPI metrics for Transaction, Insurance, and User data.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit_shadcn_ui as ui
import sys
sys.path.insert(0, '..')

from utils.config import (
    load_data_cached,
    render_breadcrumbs,
    format_currency,
    format_number,
    COLORS,
    PLOTLY_SCALES,
    INDIA_GEOJSON_URL
)

# Set Streamlit page configuration
st.set_page_config(
    layout="wide",
    initial_sidebar_state='collapsed',
    page_icon="🌍",
    page_title="PhonePe - Geographic Maps"
)

# Render breadcrumb navigation
render_breadcrumbs("Mapping")

# ***************************************Data Access*******************************

@st.cache_data(ttl=3600)
def load_data_from_db(query):
    """Load data with caching for better performance."""
    return load_data_cached(query)

def select_the_table(selected_tab):
    """Select table based on chosen tab."""
    tables = {
        'Transaction Data': 'map_transaction_hover_state',
        'Insurance Data': 'map_insurence_hover_state',
        'User Data': 'map_user_hover_state'
    }
    return tables.get(selected_tab, None)

def get_column_config(selected_tab):
    """Get column configuration based on data type."""
    if 'User' in selected_tab:
        return {
            'value_col': 'registered_users',
            'hover_cols': ['state', 'registered_users'],
            'color_scale': PLOTLY_SCALES['users'],
            'value_label': 'Registered Users',
            'icon': '👥'
        }
    elif 'Insurance' in selected_tab:
        return {
            'value_col': 'total_transactions_amount',
            'count_col': 'total_transactions_count',
            'hover_cols': ['state', 'total_transactions_amount', 'total_transactions_count'],
            'color_scale': PLOTLY_SCALES['insurance'],
            'value_label': 'Insurance Amount',
            'icon': '🛡️'
        }
    else:
        return {
            'value_col': 'total_transactions_amount',
            'count_col': 'total_transactions_count',
            'hover_cols': ['state', 'total_transactions_amount', 'total_transactions_count'],
            'color_scale': PLOTLY_SCALES['transactions'],
            'value_label': 'Transaction Amount',
            'icon': '💳'
        }

# ***************************************Data Exploration*******************************

# Tab Selection
st.markdown("### 📊 Select Data Category")
tab_container = st.container(border=True)
col1, col2 = tab_container.columns([4, 1])

with col1:
    selected_tab = ui.tabs(
        options=['Transaction Data', 'Insurance Data', 'User Data'],
        default_value='Transaction Data',
        key="map_tabs"
    )

with col2:
    filter_data = st.toggle('🔍 Filter', value=False)

# Load and process data
chosen_table = select_the_table(selected_tab)
config = get_column_config(selected_tab)

if chosen_table is None:
    st.warning("Please select a valid data category.")
    st.stop()

df = load_data_from_db(f'SELECT * FROM {chosen_table}')

if df.empty:
    st.error("No data available for the selected category.")
    st.stop()

# Standardize state names
df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', ' & '))

# ***************************************Filters*******************************

if filter_data:
    filter_container = st.container(border=True)
    col3, col4, col5 = filter_container.columns(3)

    with col3:
        selected_years = st.multiselect(
            'Select Year:',
            sorted(df['year'].unique()),
            default=[max(df['year'].unique())]
        )
    
    with col4:
        selected_quarters = st.multiselect(
            'Select Quarter:',
            sorted(df['quarter'].unique()),
            default=list(df['quarter'].unique())
        )
    
    with col5:
        all_states = sorted(df['state'].unique())
        selected_states = st.multiselect(
            'Select States:',
            all_states,
            default=[]
        )

    # Apply filters
    filtered_df = df[
        (df['year'].isin(selected_years)) & 
        (df['quarter'].isin(selected_quarters))
    ]
    
    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
else:
    filtered_df = df

# ***************************************KPI Section*******************************

st.markdown("---")
st.markdown(f"### {config['icon']} Key Performance Indicators - {selected_tab}")

# Aggregate data for KPIs
value_col = config['value_col']
agg_data = filtered_df.groupby('state')[value_col].sum().reset_index()

# Calculate KPIs
total_value = filtered_df[value_col].sum()
total_states = filtered_df['state'].nunique()
top_state = agg_data.loc[agg_data[value_col].idxmax(), 'state'] if len(agg_data) > 0 else "N/A"
top_state_value = agg_data[value_col].max() if len(agg_data) > 0 else 0
avg_per_state = total_value / total_states if total_states > 0 else 0

# Count column for transactions/insurance
if 'count_col' in config:
    count_col = config['count_col']
    total_count = filtered_df[count_col].sum() if count_col in filtered_df.columns else 0
else:
    total_count = total_value  # For users, total is the count

# Display KPIs
kpi_cols = st.columns(4)

with kpi_cols[0]:
    if 'User' in selected_tab:
        ui.metric_card(
            title="Total Users",
            content=format_number(total_value),
            description="Total registered users",
            key="map_kpi1"
        )
    else:
        ui.metric_card(
            title=f"Total {config['value_label']}",
            content=format_currency(total_value),
            description=f"Across all states",
            key="map_kpi1"
        )

with kpi_cols[1]:
    if 'User' not in selected_tab:
        ui.metric_card(
            title="Total Transactions",
            content=format_number(total_count),
            description="Number of transactions",
            key="map_kpi2"
        )
    else:
        ui.metric_card(
            title="Avg Users/State",
            content=format_number(avg_per_state),
            description="Average per state",
            key="map_kpi2"
        )

with kpi_cols[2]:
    ui.metric_card(
        title="States Covered",
        content=str(total_states),
        description="Active states in selection",
        key="map_kpi3"
    )

with kpi_cols[3]:
    ui.metric_card(
        title="Top Performing State",
        content=top_state[:12] + "..." if len(top_state) > 12 else top_state,
        description=format_currency(top_state_value) if 'User' not in selected_tab else format_number(top_state_value),
        key="map_kpi4"
    )

# ***************************************Choropleth Map*******************************

st.markdown("---")
st.markdown(f"### 🗺️ Geographic Distribution - {selected_tab}")

# Aggregate by state for map
map_data = filtered_df.groupby('state').agg({
    value_col: 'sum'
}).reset_index()

if 'count_col' in config and config['count_col'] in filtered_df.columns:
    count_agg = filtered_df.groupby('state')[config['count_col']].sum().reset_index()
    map_data = map_data.merge(count_agg, on='state', how='left')

# Create choropleth map
fig_map = px.choropleth(
    map_data,
    geojson=INDIA_GEOJSON_URL,
    featureidkey='properties.ST_NM',
    locations='state',
    color=value_col,
    hover_data=map_data.columns.tolist(),
    title=f"🌍 {selected_tab} by State",
    color_continuous_scale=config['color_scale']
)

fig_map.update_geos(fitbounds='locations', visible=False)
fig_map.update_layout(
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    height=600,
    coloraxis_colorbar=dict(title=config['value_label'])
)

st.plotly_chart(fig_map, theme="streamlit", use_container_width=True)

# ***************************************Additional Charts*******************************

st.markdown("---")
st.markdown("### 📊 Detailed Analysis")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Top 10 States Bar Chart
    top_10_states = map_data.nlargest(10, value_col)
    
    fig_bar = px.bar(
        top_10_states,
        y='state',
        x=value_col,
        orientation='h',
        title=f"🏆 Top 10 States by {config['value_label']}",
        color=value_col,
        color_continuous_scale=config['color_scale']
    )
    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    # Pie Chart for top states
    fig_pie = px.pie(
        top_10_states,
        values=value_col,
        names='state',
        title=f"📊 Top 10 States - Share Distribution",
        hole=0.4,
        color_discrete_sequence=COLORS['categorical']
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# ***************************************Trend Analysis*******************************

st.markdown("---")
st.markdown("### 📈 Trend Analysis")

# Yearly trend
if len(filtered_df['year'].unique()) > 1:
    yearly_trend = filtered_df.groupby('year')[value_col].sum().reset_index()
    
    trend_col1, trend_col2 = st.columns(2)
    
    with trend_col1:
        fig_trend = px.line(
            yearly_trend,
            x='year',
            y=value_col,
            markers=True,
            title=f"📈 {config['value_label']} Trend by Year",
            labels={value_col: config['value_label'], 'year': 'Year'}
        )
        fig_trend.update_traces(line=dict(width=3, color=COLORS['primary']), marker=dict(size=12))
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with trend_col2:
        # Quarterly breakdown
        quarterly_trend = filtered_df.groupby(['year', 'quarter'])[value_col].sum().reset_index()
        quarterly_trend['period'] = quarterly_trend['year'].astype(str) + '-Q' + quarterly_trend['quarter'].astype(str)
        
        fig_quarterly = px.bar(
            quarterly_trend,
            x='period',
            y=value_col,
            color='year',
            title=f"📅 Quarterly {config['value_label']}",
            labels={value_col: config['value_label'], 'period': 'Period'}
        )
        fig_quarterly.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_quarterly, use_container_width=True)
else:
    st.info("Select multiple years to see trend analysis.")

# ***************************************Data Table*******************************

st.markdown("---")
with st.expander("📋 View Detailed Data", expanded=False):
    display_df = map_data.copy()
    display_df[value_col] = display_df[value_col].apply(
        lambda x: format_currency(x) if 'User' not in selected_tab else format_number(x)
    )
    display_df = display_df.sort_values(value_col.replace('₹', '').replace(',', ''), ascending=False)
    ui.table(data=display_df, maxHeight=400, key="map_detailed_table")
