"""
📊 Tables & Plotting - Comprehensive Data Analysis
===================================================
Detailed visualizations and analysis for Transaction, Insurance, and User data.
"""

import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import plotly.express as px
import sys
sys.path.insert(0, '..')

from utils.config import (
    load_data_cached,
    render_breadcrumbs,
    format_currency,
    format_number,
    COLORS,
    PLOTLY_SCALES
)

st.set_page_config(
    layout="wide",
    initial_sidebar_state='collapsed',
    page_title="PhonePe - Data Analysis",
    page_icon='📊'
)

# Render breadcrumb navigation
render_breadcrumbs("Plotting")

st.markdown("### 📊 Detailed Data Analysis")

# ***************************************Data Access*******************************

@st.cache_data(ttl=3600)
def load_data_from_db(query):
    """Load data with caching for better performance."""
    return load_data_cached(query)

def select_the_table(selected_tab):
    """Execute different queries based on the chosen tab."""
    tables = {
        'Transaction Data': 'agregated_transaction_country',
        'Transaction State': 'aggregated_transaction_state',
        'Insurance Data': 'aggregated_insurence_country',
        'Insurance State': 'aggregated_insurence_state',
        'User Data': 'aggregated_user_counry',
        'User State': 'agregated_user_state'
    }
    return tables.get(selected_tab, None)

def get_config(selected_tab):
    """Get configuration for the selected data type."""
    if 'User' in selected_tab:
        return {
            'has_phone_brand': True,
            'value_col': 'phone_count',
            'icon': '👥',
            'color_scale': PLOTLY_SCALES['users']
        }
    elif 'Insurance' in selected_tab:
        return {
            'has_phone_brand': False,
            'value_col': 'total_amount' if 'State' in selected_tab else 'amount',
            'count_col': 'number_of_transactions' if 'State' in selected_tab else 'count',
            'icon': '🛡️',
            'color_scale': PLOTLY_SCALES['insurance']
        }
    else:
        return {
            'has_phone_brand': False,
            'value_col': 'total_amount' if 'State' in selected_tab else 'amount',
            'count_col': 'number_of_transactions' if 'State' in selected_tab else 'count',
            'icon': '💳',
            'color_scale': PLOTLY_SCALES['transactions']
        }

# ***************************************Data Exploration*******************************

# Tab Selection
tab_container = st.container(border=True)
col1, col2 = tab_container.columns([6, 1])

with col1:
    selected_tab = ui.tabs(
        options=['Transaction State', 'Insurance State', 'User State',
                 'Transaction Data', 'Insurance Data', 'User Data'],
        default_value='Transaction State',
        key="plotting_tabs"
    )

with col2:
    filter_data = st.toggle('🔍 Filter', value=False)

# Load data
chosen_table = select_the_table(selected_tab)
config = get_config(selected_tab)

if chosen_table is None:
    st.warning("Please select a valid data category.")
    st.stop()

df = load_data_from_db(f'SELECT * FROM {chosen_table}')

if df.empty:
    st.error("No data available for the selected category.")
    st.stop()

# Standardize state names if present
if 'state' in df.columns:
    df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', ' & '))

# ***************************************Filters*******************************

filtered_df = df.copy()

if filter_data:
    filter_box = st.container(border=True)
    cols = filter_box.columns(4)

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

    # Apply year and quarter filters first
    filtered_df = df[
        (df['year'].isin(selected_years)) & 
        (df['quarter'].isin(selected_quarters))
    ]

    with cols[2]:
        if 'state' in filtered_df.columns:
            states = sorted(filtered_df['state'].unique())
            selected_states = st.multiselect('Select States:', states, default=[])
            if selected_states:
                filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
        elif 'phone_brand' in filtered_df.columns:
            brands = sorted(filtered_df['phone_brand'].unique())
            selected_brands = st.multiselect('Select Brands:', brands, default=[])
            if selected_brands:
                filtered_df = filtered_df[filtered_df['phone_brand'].isin(selected_brands)]

    with cols[3]:
        if 'type_of_transaction' in filtered_df.columns:
            types = sorted(filtered_df['type_of_transaction'].unique())
            selected_types = st.multiselect('Transaction Type:', types, default=[])
            if selected_types:
                filtered_df = filtered_df[filtered_df['type_of_transaction'].isin(selected_types)]

# ***************************************KPI Section*******************************

st.markdown("---")
st.markdown(f"### {config['icon']} Key Metrics - {selected_tab}")

# Calculate KPIs based on data type
if config.get('has_phone_brand'):
    total_users = filtered_df['registered_users'].sum() if 'registered_users' in filtered_df.columns else 0
    total_phones = filtered_df['phone_count'].sum() if 'phone_count' in filtered_df.columns else 0
    unique_brands = filtered_df['phone_brand'].nunique() if 'phone_brand' in filtered_df.columns else 0
    
    if 'phone_brand' in filtered_df.columns and 'phone_count' in filtered_df.columns:
        brand_totals = filtered_df.groupby('phone_brand')['phone_count'].sum()
        top_brand = brand_totals.idxmax() if len(brand_totals) > 0 else "N/A"
    else:
        top_brand = "N/A"
    
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        ui.metric_card(title="Total Users", content=format_number(total_users), description="Registered users", key="plot_kpi1")
    with kpi_cols[1]:
        ui.metric_card(title="Total Devices", content=format_number(total_phones), description="Phone count", key="plot_kpi2")
    with kpi_cols[2]:
        ui.metric_card(title="Unique Brands", content=str(unique_brands), description="Phone brands", key="plot_kpi3")
    with kpi_cols[3]:
        ui.metric_card(title="Top Brand", content=top_brand, description="Most popular", key="plot_kpi4")
else:
    value_col = config.get('value_col', 'total_amount')
    count_col = config.get('count_col', 'number_of_transactions')
    
    total_amount = filtered_df[value_col].sum() if value_col in filtered_df.columns else 0
    total_count = filtered_df[count_col].sum() if count_col in filtered_df.columns else 0
    avg_value = total_amount / total_count if total_count > 0 else 0
    
    if 'state' in filtered_df.columns:
        unique_states = filtered_df['state'].nunique()
        state_totals = filtered_df.groupby('state')[value_col].sum()
        top_state = state_totals.idxmax() if len(state_totals) > 0 else "N/A"
    else:
        unique_states = 0
        top_state = "N/A"
    
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        ui.metric_card(title="Total Amount", content=format_currency(total_amount), description="Total value", key="plot_kpi1")
    with kpi_cols[1]:
        ui.metric_card(title="Transactions", content=format_number(total_count), description="Total count", key="plot_kpi2")
    with kpi_cols[2]:
        ui.metric_card(title="Avg Transaction", content=format_currency(avg_value), description="Per transaction", key="plot_kpi3")
    with kpi_cols[3]:
        if 'state' in filtered_df.columns:
            ui.metric_card(title="Top State", content=top_state[:12], description=f"{unique_states} states", key="plot_kpi4")
        else:
            ui.metric_card(title="Data Points", content=str(len(filtered_df)), description="Records", key="plot_kpi4")

# ***************************************Data Preview*******************************

with st.expander('📋 View Data', expanded=False):
    st.dataframe(filtered_df.head(100), use_container_width=True, height=300)

# ***************************************Charts*******************************

st.markdown("---")
st.markdown("### 📈 Visualizations")

# Transaction State Data Charts
if selected_tab == 'Transaction State' and 'state' in filtered_df.columns:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if 'type_of_transaction' in filtered_df.columns:
            fig1 = px.bar(
                filtered_df.groupby(['state', 'type_of_transaction'])['number_of_transactions'].sum().reset_index(),
                x="state", y="number_of_transactions", color="type_of_transaction",
                barmode="group", title="📊 Transactions by State & Type"
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        if 'type_of_transaction' in filtered_df.columns:
            fig2 = px.bar(
                filtered_df.groupby(['state', 'type_of_transaction'])['total_amount'].sum().reset_index(),
                x="state", y="total_amount", color="type_of_transaction",
                barmode="group", title="💰 Amount by State & Type"
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Treemap
    if 'type_of_transaction' in filtered_df.columns:
        fig_tree = px.treemap(
            filtered_df.groupby(['state', 'type_of_transaction'])['number_of_transactions'].sum().reset_index(),
            path=["state", "type_of_transaction"], values="number_of_transactions",
            title="🌳 Transaction Distribution by State & Type",
            color="number_of_transactions", color_continuous_scale=config['color_scale']
        )
        st.plotly_chart(fig_tree, use_container_width=True)

# Insurance State Data Charts
elif selected_tab == 'Insurance State' and 'state' in filtered_df.columns:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        state_data = filtered_df.groupby('state')['number_of_transactions'].sum().reset_index()
        fig1 = px.bar(state_data.nlargest(15, 'number_of_transactions'),
            x='state', y='number_of_transactions',
            title="📊 Top 15 States by Insurance Transactions",
            color='number_of_transactions', color_continuous_scale=config['color_scale']
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        state_amount = filtered_df.groupby('state')['total_amount'].sum().reset_index()
        fig2 = px.bar(state_amount.nlargest(15, 'total_amount'),
            x='state', y='total_amount',
            title="💰 Top 15 States by Insurance Amount",
            color='total_amount', color_continuous_scale=config['color_scale']
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Scatter plot
    fig_scatter = px.scatter(
        filtered_df.groupby('state').agg({'number_of_transactions': 'sum', 'total_amount': 'sum'}).reset_index(),
        x='number_of_transactions', y='total_amount', color='state',
        size='total_amount', hover_name='state',
        title="📈 Transactions vs Amount by State"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# User State Data Charts
elif selected_tab == 'User State' and 'phone_brand' in filtered_df.columns:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        brand_data = filtered_df.groupby('phone_brand')['phone_count'].sum().reset_index()
        fig1 = px.pie(brand_data.nlargest(10, 'phone_count'),
            values='phone_count', names='phone_brand', hole=0.4,
            title="📱 Top 10 Phone Brands Market Share"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        fig2 = px.bar(brand_data.nlargest(10, 'phone_count'),
            y='phone_brand', x='phone_count', orientation='h',
            title="📊 Top 10 Brands by Device Count",
            color='phone_count', color_continuous_scale=config['color_scale']
        )
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)
    
    # State-wise user distribution
    if 'state' in filtered_df.columns:
        state_users = filtered_df.groupby('state')['registered_users'].sum().reset_index()
        fig_state = px.bar(state_users.nlargest(15, 'registered_users'),
            x='state', y='registered_users',
            title="👥 Top 15 States by Registered Users",
            color='registered_users', color_continuous_scale=config['color_scale']
        )
        st.plotly_chart(fig_state, use_container_width=True)

# Country-level data
else:
    if 'amount' in filtered_df.columns or 'count' in filtered_df.columns:
        yearly_data = filtered_df.groupby('year').agg({
            col: 'sum' for col in filtered_df.columns if col in ['amount', 'count', 'phone_count']
        }).reset_index()
        
        if not yearly_data.empty:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                value_col = 'amount' if 'amount' in yearly_data.columns else 'phone_count'
                if value_col in yearly_data.columns:
                    fig1 = px.line(yearly_data, x='year', y=value_col, markers=True,
                        title=f"📈 Yearly Trend", labels={value_col: 'Value'}
                    )
                    fig1.update_traces(line=dict(width=3), marker=dict(size=10))
                    st.plotly_chart(fig1, use_container_width=True)
            
            with chart_col2:
                if 'count' in yearly_data.columns:
                    fig2 = px.bar(yearly_data, x='year', y='count',
                        title="📊 Transactions by Year",
                        color='count', color_continuous_scale=config['color_scale']
                    )
                    st.plotly_chart(fig2, use_container_width=True)

# ***************************************Quarterly Trends*******************************

st.markdown("---")
st.markdown("### 📅 Quarterly Analysis")

if 'year' in filtered_df.columns and 'quarter' in filtered_df.columns:
    quarterly = filtered_df.groupby(['year', 'quarter']).agg({
        col: 'sum' for col in filtered_df.columns 
        if col in ['total_amount', 'number_of_transactions', 'amount', 'count', 'phone_count', 'registered_users']
    }).reset_index()
    quarterly['period'] = quarterly['year'].astype(str) + '-Q' + quarterly['quarter'].astype(str)
    
    if not quarterly.empty:
        # Determine value column
        for val_col in ['total_amount', 'amount', 'phone_count', 'registered_users']:
            if val_col in quarterly.columns:
                fig_quarterly = px.bar(quarterly, x='period', y=val_col, color='year',
                    title="📅 Quarterly Performance",
                    labels={val_col: 'Value'}
                )
                fig_quarterly.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_quarterly, use_container_width=True)
                break