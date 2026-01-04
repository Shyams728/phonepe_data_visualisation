import plotly.express as px
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import sys
sys.path.insert(0, '..')

from utils.config import (
    load_insurance_state_data,
    load_data_cached,
    format_currency,
    format_number,
    render_breadcrumbs,
    COLORS,
    PLOTLY_SCALES
)

# Set Streamlit page configuration
st.set_page_config(
    page_title="PhonePe - Visualizations",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📈",
)

# Render breadcrumb navigation
render_breadcrumbs("visual")


# Use cached data loading function
@st.cache_data(ttl=3600)
def load_data_from_db(query):
    """Load data with caching for better performance."""
    return load_data_cached(query)





# # Fetch data from SQLite based on user selection from dropdown
# dropdown_options = {
#     '---': None,
#     "Nationwise Aggregated User Data": "aggregated_user_counry",
#     "Nationwise Aggregated Insurence Data": "aggregated_insurence_counry",
#     "Statewise Map Transaction Data": "map_transaction_hover_state",
#     "Nationwise Top Transaction Data": "top_transaction_country",
#     "Statewise Top Insurence Data": "top_insurence_state",
#     "Statewise Aggregated Transaction Data": "aggregated_transaction_state",
#     "Nationwise Map User Data": "map_user_hover_contry",
#     "Nationwise Map Insurence Data": "map_insurence_hover_counry",
#     "Statewise Aggregated User Data": "aggregated_user_state",
#     "Statewise Map User Data": "map_user_hover_state",
#     "Nationwise Map Transaction Data": "map_transaction_hover_counry",
#     "Nationwise Top Insurence Data": "top_insurence_country",
#     "Statewise Aggregated Insurence Data": "aggregated_insurence_state",
#     "Nationwise Aggregated Transaction Data": "aggregated_transaction_country",
#     "Nationwise Top User Data": "top_user_country",
#     "Statewise Top User Data": "top_user_state",
#     "Top Ten States Transactions": "your_table_name WHERE ...",
#     "Top Ten Districts": "your_table_name WHERE ...",
#     "Top Ten Pincodes": "your_table_name WHERE ...",
# }

# # Streamlit app
# st.title("SQL Table Visualization")


query = 'SELECT * FROM aggregated_insurence_state;'
df = load_data_from_db(query)

# Replace hyphens with spaces and title-case the elements in the 'state' column
df['state'] = df['state'].apply(lambda x: x.replace('-', ' ').title().replace(' And ', '& '))

# Aggregate data by summing quarter amounts and transactions per year
agg_df = df.groupby(["state", "year"]).agg({
    "number_of_transactions": "sum",
    "total_amount": "sum"
}).reset_index()


# Calculate KPI values
total_amount = df.total_amount.sum()
total_transactions = df.number_of_transactions.sum()
avg_transaction_value = total_amount / total_transactions if total_transactions > 0 else 0

# Year-over-Year Growth calculation
yearly_data = df.groupby('year')['total_amount'].sum().sort_index()
if len(yearly_data) >= 2:
    latest_year = yearly_data.iloc[-1]
    previous_year = yearly_data.iloc[-2]
    yoy_growth = ((latest_year - previous_year) / previous_year * 100) if previous_year > 0 else 0
else:
    yoy_growth = 0

# Top performing state
state_totals = df.groupby('state')['total_amount'].sum()
top_state = state_totals.idxmax() if len(state_totals) > 0 else "N/A"
top_state_amount = state_totals.max() if len(state_totals) > 0 else 0

# Total unique states
total_states = df['state'].nunique()

# Best performing quarter
quarterly_data = df.groupby('quarter')['total_amount'].sum()
best_quarter = quarterly_data.idxmax() if len(quarterly_data) > 0 else "N/A"

# State with highest average transaction value
state_avg_txn = df.groupby('state').apply(lambda x: x['total_amount'].sum() / x['number_of_transactions'].sum() if x['number_of_transactions'].sum() > 0 else 0)
highest_avg_state = state_avg_txn.idxmax() if len(state_avg_txn) > 0 else "N/A"
highest_avg_value = state_avg_txn.max() if len(state_avg_txn) > 0 else 0

# Format large numbers for display
def format_currency(value):
    if value >= 1e9:
        return f"₹{value/1e9:.2f}B"
    elif value >= 1e7:
        return f"₹{value/1e7:.2f}Cr"
    elif value >= 1e5:
        return f"₹{value/1e5:.2f}L"
    else:
        return f"₹{value:,.2f}"

def format_number(value):
    if value >= 1e9:
        return f"{value/1e9:.2f}B"
    elif value >= 1e7:
        return f"{value/1e7:.2f}Cr"
    elif value >= 1e5:
        return f"{value/1e5:.2f}L"
    else:
        return f"{value:,.0f}"

# Display KPI metrics in organized rows
st.markdown("### 📊 Key Performance Indicators")

# Row 1: Primary Metrics
cols_row1 = st.columns(4)
with cols_row1[0]:
    ui.metric_card(
        title="Total Insurance Amount", 
        content=format_currency(total_amount), 
        description="Total insurance amount from state transactions", 
        key="card1"
    )
with cols_row1[1]:
    ui.metric_card(
        title="Total Transactions", 
        content=format_number(total_transactions), 
        description="Total number of insurance transactions", 
        key="card2"
    )
with cols_row1[2]:
    ui.metric_card(
        title="Avg Transaction Value", 
        content=format_currency(avg_transaction_value), 
        description="Average value per transaction", 
        key="card3"
    )
with cols_row1[3]:
    yoy_indicator = "📈" if yoy_growth > 0 else "📉" if yoy_growth < 0 else "➡️"
    ui.metric_card(
        title="YoY Growth", 
        content=f"{yoy_indicator} {yoy_growth:.1f}%", 
        description="Year-over-year growth in amount", 
        key="card4"
    )

# Row 2: Secondary Metrics
cols_row2 = st.columns(4)
with cols_row2[0]:
    ui.metric_card(
        title="Top Performing State", 
        content=top_state, 
        description=f"Amount: {format_currency(top_state_amount)}", 
        key="card5"
    )
with cols_row2[1]:
    ui.metric_card(
        title="States Covered", 
        content=str(total_states), 
        description="Total number of states in dataset", 
        key="card6"
    )
with cols_row2[2]:
    ui.metric_card(
        title="Best Quarter", 
        content=f"Q{best_quarter}", 
        description="Quarter with highest amount", 
        key="card7"
    )
with cols_row2[3]:
    ui.metric_card(
        title="Highest Avg Txn State", 
        content=highest_avg_state, 
        description=f"Avg: {format_currency(highest_avg_value)}", 
        key="card8"
    )

st.markdown("---")

# Trend Analysis Section
st.markdown("### 📈 Trend Analysis")

# Create yearly trend data
yearly_trend = df.groupby('year').agg({
    'total_amount': 'sum',
    'number_of_transactions': 'sum'
}).reset_index()
yearly_trend['avg_transaction'] = yearly_trend['total_amount'] / yearly_trend['number_of_transactions']

# Create quarterly trend data
quarterly_trend = df.groupby(['year', 'quarter']).agg({
    'total_amount': 'sum',
    'number_of_transactions': 'sum'
}).reset_index()
quarterly_trend['period'] = quarterly_trend['year'].astype(str) + '-Q' + quarterly_trend['quarter'].astype(str)

# Display trend charts side by side
trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    # Yearly Trend Line Chart
    fig_yearly = px.line(
        yearly_trend,
        x='year',
        y='total_amount',
        markers=True,
        title='📊 Yearly Insurance Amount Trend',
        labels={'total_amount': 'Total Amount (₹)', 'year': 'Year'}
    )
    fig_yearly.update_traces(line=dict(width=3), marker=dict(size=10))
    fig_yearly.update_layout(hovermode='x unified')
    st.plotly_chart(fig_yearly, theme="streamlit", use_container_width=True)

with trend_col2:
    # Quarterly Comparison Bar Chart
    fig_quarterly = px.bar(
        quarterly_trend,
        x='period',
        y='total_amount',
        color='year',
        title='📅 Quarterly Performance',
        labels={'total_amount': 'Total Amount (₹)', 'period': 'Period'}
    )
    fig_quarterly.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_quarterly, theme="streamlit", use_container_width=True)

# Growth metrics row
st.markdown("#### 📊 Growth Metrics")
growth_cols = st.columns(3)

# Calculate growth metrics
if len(yearly_trend) >= 2:
    amount_cagr = ((yearly_trend['total_amount'].iloc[-1] / yearly_trend['total_amount'].iloc[0]) ** (1 / (len(yearly_trend) - 1)) - 1) * 100
    txn_cagr = ((yearly_trend['number_of_transactions'].iloc[-1] / yearly_trend['number_of_transactions'].iloc[0]) ** (1 / (len(yearly_trend) - 1)) - 1) * 100
else:
    amount_cagr = 0
    txn_cagr = 0

# Get latest quarter growth
if len(quarterly_trend) >= 2:
    latest_q_amount = quarterly_trend['total_amount'].iloc[-1]
    prev_q_amount = quarterly_trend['total_amount'].iloc[-2]
    qoq_growth = ((latest_q_amount - prev_q_amount) / prev_q_amount * 100) if prev_q_amount > 0 else 0
else:
    qoq_growth = 0

with growth_cols[0]:
    cagr_indicator = "📈" if amount_cagr > 0 else "📉" if amount_cagr < 0 else "➡️"
    ui.metric_card(
        title="Amount CAGR",
        content=f"{cagr_indicator} {amount_cagr:.1f}%",
        description="Compound Annual Growth Rate for amount",
        key="card_cagr"
    )

with growth_cols[1]:
    txn_indicator = "📈" if txn_cagr > 0 else "📉" if txn_cagr < 0 else "➡️"
    ui.metric_card(
        title="Transaction CAGR",
        content=f"{txn_indicator} {txn_cagr:.1f}%",
        description="Compound Annual Growth Rate for transactions",
        key="card_txn_cagr"
    )

with growth_cols[2]:
    qoq_indicator = "📈" if qoq_growth > 0 else "📉" if qoq_growth < 0 else "➡️"
    ui.metric_card(
        title="QoQ Growth",
        content=f"{qoq_indicator} {qoq_growth:.1f}%",
        description="Quarter-over-Quarter growth (latest)",
        key="card_qoq"
    )

st.markdown("---")

# Aggregate data by summing quarter amounts and transactions per year
agg_df2 = df.groupby(["state"]).agg({
    "number_of_transactions": "sum",
    "total_amount": "sum"
}).reset_index()

# Sort the aggregated DataFrame by 'total_amount' in descending order
agg_df_sorted = agg_df2.sort_values(by="total_amount", ascending=False)
# Add a new column with the formatted total_amount
agg_df_sorted["total_amount"] = "₹ " + agg_df_sorted["total_amount"].apply(lambda x: f"{x:,.2f}")


first_box = st.container(border=True)
with first_box:
    st.markdown('###### Top 5 states by total transactions amount')
    ui.table(data=agg_df_sorted.head(5), maxHeight=300)
    

# Create a scatter plot using Plotly Express
fig1 = px.scatter(
    agg_df2,
    x="number_of_transactions",
    y="total_amount",
    size='total_amount',  # Use 'total_amount' for size
    color="state",
    hover_name="state",
    log_x=True,
    size_max=50,
    title='Total Distribution of Insurance Amount & Counts',
)

# Update the hover template to display ₹ symbol with the total_amount
fig1.update_traces(hovertemplate='<b>%{hovertext}</b><br><br>Transactions: %{x}<br>Amount: ₹%{y}')

# Customize the y-axis to show the ₹ symbol
fig1.update_layout(
    yaxis_title='Total Amount (₹)',
    xaxis_title='Number of Transactions',
)


# Display the scatter plot
st.plotly_chart(fig1, theme="streamlit", use_container_width=True)



# Create pie charts
fig2 = px.pie(df, values='total_amount', names='year',title='Insurence Amount by year')
fig3 = px.pie(df, values='total_amount', names='state', hole=.6, hover_data=['number_of_transactions'], title='Total Insurence Amount by State')

# Display the pie charts in columns
col1, col2 = st.columns([1, 3])

with col1:
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

with col2:
    st.plotly_chart(fig3, theme="streamlit", use_container_width=True)

fig4 = px.bar(df, x="state", y="number_of_transactions", color="state", title="Total Transactions by State",labels = None)


st.plotly_chart(fig4, theme="streamlit", use_container_width=True)


fig5 = px.pie(df, values='total_amount', names='state', hole=.6, hover_data=['number_of_transactions'],title='Total Number of Insurence counts')
fig12 = px.sunburst(
    df,
    path=["state", "year"],
    values="number_of_transactions",
    title="Hierarchical Transactions by State and Year"
)

col4, col5 = st.columns([5, 3])

with col4:
    st.plotly_chart(fig5, theme="streamlit", use_container_width=True)

with col5:
    st.plotly_chart(fig12, theme="streamlit", use_container_width=True)



# fig8 = px.imshow(
#     agg_df.pivot(index="state", columns="year", values="number_of_transactions"),
#     title="Heatmap of Transactions by State and Year"
# )
# st.plotly_chart(fig8, theme="streamlit", use_container_width=True)



fig13 = px.treemap(
    df,
    path=["state", "year","quarter"],
    values="number_of_transactions",
    # color= "total_amount",
    title="Transaction Distribution by State and Year"
)
st.plotly_chart(fig13, theme="streamlit", use_container_width=True)


fig9 = px.choropleth(
    df,
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
    featureidkey='properties.ST_NM',
    locations='state',
    color='total_amount',
    hover_data=['total_amount','number_of_transactions'],
    title="Insurance Amount by State",
    color_continuous_scale='Viridis_r'
)
fig9.update_geos(fitbounds='locations', visible=False)
st.plotly_chart(fig9, theme="streamlit", use_container_width=True)

    
