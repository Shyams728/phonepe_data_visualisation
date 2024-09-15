import plotly.express as px
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import streamlit_shadcn_ui as ui

# Set Streamlit page configuration
st.set_page_config(
    page_title="Visualisation",
    layout="wide",
    initial_sidebar_state = "collapsed",
    page_icon=":graph:",
)


# Create a function to load data from the SQLite database
def load_data_from_db(query):
    sqlite_file = 'test.sqlite'
    engine = create_engine(f'sqlite:///{sqlite_file}')
    df = pd.read_sql(query, engine)
    return df





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


# Display metrics in two columns
cols = st.columns(2)
with cols[0]:
    ui.metric_card(title="Total Insurence Amount", content=f"₹{df.total_amount.sum()}", description="Total insurence amount from state transactions", key="card1")
with cols[1]:
    ui.metric_card(title="Total Number of Transactions", content=f"{df.number_of_transactions.sum()}", description="Total Number of Transactions from state insurence", key="card2")
# st.markdown('---')

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

    
