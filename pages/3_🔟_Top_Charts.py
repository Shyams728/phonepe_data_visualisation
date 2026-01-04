"""
🏆 Top Charts - Enhanced with Choropleth Maps and KPIs
=======================================================
Comprehensive rankings with geographic visualization and key metrics.
"""

import plotly.express as px
import streamlit as st
import pandas as pd
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
    page_title="PhonePe - Top Charts",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏆",
)

# Render breadcrumb navigation
render_breadcrumbs("Top_Charts")

st.markdown('### 🏆 Top Charts & Rankings')

# ***************************************Data Access*******************************

@st.cache_data(ttl=3600)
def load_data_from_db(query):
    """Load data with caching for better performance."""
    return load_data_cached(query)

def select_the_table(selected_tab):
    """Get query for selected tab."""
    table_queries = {
        'Transaction Data': 'SELECT * FROM top_transaction_country;',
        'Insurance Data': 'SELECT * FROM top_insurence_country;',
        'User Data': 'SELECT * FROM top_user_country;',
        'Statewise Transaction': 'SELECT * FROM top_transaction_state;',
        'Statewise Insurance': 'SELECT * FROM top_insurance_state;',
        'Statewise User': 'SELECT * FROM top_user_state;'
    }
    return table_queries.get(selected_tab, None)

def get_config(selected_tab):
    """Get configuration based on data type."""
    if 'User' in selected_tab:
        return {
            'value_col': 'registeredUsers',
            'count_col': 'count',
            'color_scale': PLOTLY_SCALES['users'],
            'value_label': 'Registered Users',
            'icon': '👥',
            'is_user': True
        }
    elif 'Insurance' in selected_tab:
        return {
            'value_col': 'amount',
            'count_col': 'count',
            'color_scale': PLOTLY_SCALES['insurance'],
            'value_label': 'Insurance Amount',
            'icon': '🛡️',
            'is_user': False
        }
    else:
        return {
            'value_col': 'amount',
            'count_col': 'count',
            'color_scale': PLOTLY_SCALES['transactions'],
            'value_label': 'Transaction Amount',
            'icon': '💳',
            'is_user': False
        }

# ***************************************Tab Selection*******************************

st.markdown("### 📊 Select Data Category")
tab_container = st.container(border=True)
col1, col2 = tab_container.columns([5, 1])

with col1:
    selected_tab = ui.tabs(
        options=['Transaction Data', 'Insurance Data', 'User Data', 
                 'Statewise Transaction', 'Statewise Insurance', 'Statewise User'],
        default_value='Transaction Data',
        key="top_charts_tabs"
    )

with col2:
    filter_data = st.toggle('🔍 Filter', value=False)

# Load data
chosen_query = select_the_table(selected_tab)
config = get_config(selected_tab)

if chosen_query is None:
    st.warning("Please select a valid data category.")
    st.stop()

df = load_data_from_db(chosen_query)

if df.empty:
    st.error("No data available for the selected category.")
    st.stop()

# Standardize state names if present
if 'state' in df.columns:
    df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', ' & '))

# ***************************************Filters*******************************

filtered_df = df.copy()

if filter_data:
    filter_container = st.container(border=True)
    cols = filter_container.columns(4 if 'state' in df.columns else 3)

    with cols[0]:
        selected_years = st.multiselect(
            'Select Year:',
            sorted(df['year'].unique()),
            default=[max(df['year'].unique())]
        )

    with cols[1]:
        selected_quarters = st.multiselect(
            'Select Quarter:',
            sorted(df['quarter'].unique()),
            default=list(df['quarter'].unique())
        )

    with cols[2]:
        if 'entity_type' in df.columns:
            entity_types = sorted(df['entity_type'].unique())
            selected_entity = st.selectbox('Entity Type:', entity_types)
        else:
            selected_entity = None

    if 'state' in df.columns and len(cols) > 3:
        with cols[3]:
            selected_states = st.multiselect(
                'Select States:',
                sorted(df['state'].unique()),
                default=[]
            )
    else:
        selected_states = []

    # Apply filters
    filtered_df = df[
        (df['year'].isin(selected_years)) & 
        (df['quarter'].isin(selected_quarters))
    ]
    
    if selected_entity and 'entity_type' in df.columns:
        filtered_df = filtered_df[filtered_df['entity_type'] == selected_entity]
    
    if selected_states and 'state' in df.columns:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

# ***************************************KPI Section*******************************

st.markdown("---")
st.markdown(f"### {config['icon']} Key Performance Indicators")

value_col = config['value_col']
count_col = config['count_col']

# Calculate KPIs
if value_col in filtered_df.columns:
    total_value = filtered_df[value_col].sum()
else:
    total_value = 0

if count_col in filtered_df.columns:
    total_count = filtered_df[count_col].sum()
else:
    total_count = 0

unique_entities = filtered_df['entity_name'].nunique() if 'entity_name' in filtered_df.columns else 0

# Top entity
if 'entity_name' in filtered_df.columns and value_col in filtered_df.columns:
    entity_totals = filtered_df.groupby('entity_name')[value_col].sum()
    if len(entity_totals) > 0:
        top_entity = entity_totals.idxmax()
        top_entity_value = entity_totals.max()
        top_entity_share = (top_entity_value / total_value * 100) if total_value > 0 else 0
    else:
        top_entity, top_entity_value, top_entity_share = "N/A", 0, 0
else:
    top_entity, top_entity_value, top_entity_share = "N/A", 0, 0

# Display KPIs
kpi_cols = st.columns(4)

with kpi_cols[0]:
    if config['is_user']:
        ui.metric_card(
            title="Total Users",
            content=format_number(total_value),
            description="Registered users in selection",
            key="top_kpi1"
        )
    else:
        ui.metric_card(
            title=f"Total {config['value_label']}",
            content=format_currency(total_value),
            description="Across all entities",
            key="top_kpi1"
        )

with kpi_cols[1]:
    ui.metric_card(
        title="Total Transactions",
        content=format_number(total_count),
        description="Number of transactions",
        key="top_kpi2"
    )

with kpi_cols[2]:
    ui.metric_card(
        title="Unique Entities",
        content=str(unique_entities),
        description="Districts/Pincodes/States",
        key="top_kpi3"
    )

with kpi_cols[3]:
    ui.metric_card(
        title="🥇 Top Entity",
        content=top_entity[:15] + "..." if len(top_entity) > 15 else top_entity,
        description=f"Share: {top_entity_share:.1f}%",
        key="top_kpi4"
    )

# ***************************************Choropleth Map (for statewise data)*******************************

if 'Statewise' in selected_tab and 'state' in filtered_df.columns:
    st.markdown("---")
    st.markdown("### 🗺️ Geographic Distribution")
    
    # Aggregate by state
    state_data = filtered_df.groupby('state').agg({
        value_col: 'sum',
        count_col: 'sum'
    }).reset_index()
    
    map_col, stats_col = st.columns([3, 2])
    
    with map_col:
        fig_map = px.choropleth(
            state_data,
            geojson=INDIA_GEOJSON_URL,
            featureidkey='properties.ST_NM',
            locations='state',
            color=value_col,
            hover_data=['state', value_col, count_col],
            title=f"🌍 {selected_tab} by State",
            color_continuous_scale=config['color_scale']
        )
        fig_map.update_geos(fitbounds='locations', visible=False)
        fig_map.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0}, height=500)
        st.plotly_chart(fig_map, use_container_width=True)
    
    with stats_col:
        st.markdown("#### 📊 State Rankings")
        top_states = state_data.nlargest(10, value_col).copy()
        
        if config['is_user']:
            top_states[value_col] = top_states[value_col].apply(format_number)
        else:
            top_states[value_col] = top_states[value_col].apply(format_currency)
        
        top_states[count_col] = top_states[count_col].apply(format_number)
        top_states.columns = ['State', config['value_label'], 'Transactions']
        
        ui.table(data=top_states, maxHeight=450, key="state_rankings")

# ***************************************Top Entities Charts*******************************

st.markdown("---")
st.markdown("### 🏅 Top Entities Ranking")

if 'entity_name' in filtered_df.columns and value_col in filtered_df.columns:
    # Aggregate by entity
    entity_data = filtered_df.groupby('entity_name').agg({
        value_col: 'sum',
        count_col: 'sum'
    }).reset_index()
    entity_data = entity_data.sort_values(value_col, ascending=False)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Top 15 horizontal bar chart
        top_15 = entity_data.head(15)
        
        fig_bar = px.bar(
            top_15,
            y='entity_name',
            x=value_col,
            orientation='h',
            title=f"🏆 Top 15 by {config['value_label']}",
            color=value_col,
            color_continuous_scale=config['color_scale']
        )
        fig_bar.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with chart_col2:
        # Treemap for top entities
        fig_treemap = px.treemap(
            top_15,
            path=['entity_name'],
            values=value_col,
            title=f"📊 Market Share Distribution",
            color=value_col,
            color_continuous_scale=config['color_scale']
        )
        fig_treemap.update_layout(height=500)
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    # ***************************************Comparison Charts*******************************
    
    st.markdown("---")
    st.markdown("### 📈 Additional Analysis")
    
    analysis_col1, analysis_col2 = st.columns(2)
    
    with analysis_col1:
        # Pie chart
        fig_pie = px.pie(
            top_15.head(10),
            values=value_col,
            names='entity_name',
            title=f"📊 Top 10 Share Distribution",
            hole=0.4,
            color_discrete_sequence=COLORS['categorical']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with analysis_col2:
        # Scatter plot: Value vs Count
        if count_col in entity_data.columns:
            fig_scatter = px.scatter(
                entity_data.head(30),
                x=count_col,
                y=value_col,
                size=value_col,
                color='entity_name',
                title=f"💹 {config['value_label']} vs Transaction Count",
                labels={value_col: config['value_label'], count_col: 'Transaction Count'},
                hover_name='entity_name'
            )
            fig_scatter.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)

# ***************************************Data Table*******************************

st.markdown("---")

with st.expander("📋 View Complete Data", expanded=False):
    display_df = entity_data.head(50).copy() if 'entity_data' in dir() else filtered_df.head(50).copy()
    
    if value_col in display_df.columns:
        if config['is_user']:
            display_df[value_col] = display_df[value_col].apply(format_number)
        else:
            display_df[value_col] = display_df[value_col].apply(format_currency)
    
    if count_col in display_df.columns:
        display_df[count_col] = display_df[count_col].apply(format_number)
    
    st.dataframe(display_df, use_container_width=True, height=400)
