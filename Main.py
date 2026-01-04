import plotly.express as px
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import sys
sys.path.insert(0, '.')

from utils.config import (
    load_data_cached,
    load_insurance_state_data,
    render_breadcrumbs,
    format_currency,
    format_number,
    COLORS,
    PLOTLY_SCALES
)

# Set Streamlit page configuration
st.set_page_config(
    page_title="PhonePe - Home",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏠",
)

# Render breadcrumb navigation
render_breadcrumbs("Main")


# Create a cached function to load data from the SQLite database
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

# # Create dropdown for selecting a table
# selected_option = st.selectbox("Select an option:", list(dropdown_options.keys()))

# # Fetch data based on the selected option
# if selected_option != '---':
#     if "Statewise" in selected_option:
#         show_all_states = st.checkbox("Show data for all states")

#         available_states = [
#         "dadra-&-nagar-haveli-&-daman-&-diu",
#         "west-bengal",
#         "arunachal-pradesh",
#         "puducherry",
#         "kerala",
#         "uttar-pradesh",
#         "mizoram",
#         "meghalaya",
#         "goa",
#         "bihar",
#         "tripura",
#         "nagaland",
#         "delhi",
#         "chandigarh",
#         "tamil-nadu",
#         "jharkhand",
#         "sikkim",
#         "maharashtra",
#         "uttarakhand",
#         "ladakh",
#         "rajasthan",
#         "madhya-pradesh",
#         "manipur",
#         "andaman-and-nicobar-islands",
#         "assam",
#         "punjab",
#         "odisha",
#         "telangana",
#         "jammu-and-kashmir",
#         "himachal-pradesh",
#         "karnataka",
#         "andhra-pradesh",
#         "haryana",
#         "lakshadweep",
#         "gujarat",
#         "chhattisgarh",
#         ]

#         # Check if selected option involves statewise data
#         if not show_all_states:
#             selected_state = st.selectbox("Select a state:", available_states)
#             query = f"SELECT * FROM {selected_option.replace(' ', '_').lower()} WHERE state = '{selected_state}';"
#         else:
#             query = f"SELECT * FROM {selected_option.replace(' ', '_').lower()};"
#     else:
#         query = f'SELECT * FROM {dropdown_options[selected_option]};'

#     # Load data from the database
#     df = load_data_from_db(query)

#     # Display the selected data
#     st.write(f"Displaying data based on {selected_option}:")

query = 'SELECT * FROM aggregated_insurence_state;'
df = load_data_from_db(query)

# Aggregate data by summing quarter amounts and transactions per year
agg_df = df.groupby(["state", "year"]).agg({
    "number_of_transactions": "sum",
    "total_amount": "sum"
}).reset_index()


# Display metrics in two columns
cols = st.columns(2)
with cols[0]:
    ui.metric_card(title="Total Insurence Amount ", content=f"₹{df.total_amount.sum()}", description="Total insurence amount from state transactions", key="card1")
with cols[1]:
    ui.metric_card(title="Total Number of Transactions", content=f"{df.number_of_transactions.sum()}", description="Total Number of Transactions from state insurence", key="card2")
# st.markdown('---')
ui.table(data=df.head(), maxHeight=300)
# Create a scatter plot using Plotly Express
fig1 = px.scatter(
    df,
    x="number_of_transactions",
    y="total_amount",
    size="total_amount",  # Use 'total_amount' for size
    color="state",
    hover_name="state",
    log_x=True,
    size_max=60,
)

# Display the scatter plot
st.plotly_chart(fig1, theme="streamlit", use_container_width=True)

# Load data for pie charts
query1 = 'SELECT * FROM aggregated_insurence_state;'
df1 = load_data_from_db(query1)

# Create pie charts
fig2 = px.pie(df1, values='total_amount', names='year')
fig3 = px.pie(df1, values='total_amount', names='state', hole=.6, hover_data=['number_of_transactions'], title='Total Insurence Amount')

# Display the pie charts in columns
col1, col2 = st.columns([1, 3])

with col1:
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)

with col2:
    st.plotly_chart(fig3, theme="streamlit", use_container_width=True)

charts= st.container(border=True)
charts.write("Total transaction proportion by year")
charts.plotly_chart(fig2, theme="streamlit", use_container_width=True)
charts.header('container check')




# Showing metric data
temp = st.container()
col1, col2, col3 = temp.columns(3)
one = col1.container(border=True)
two = col2.container(border=True)
three = col3.container(border=True)

# Metrics for column one
one.metric(label= "__Total Insurence Amount__", value=f"₹{df.total_amount.sum()}", delta="Total insurence amount from state transactions", delta_color = 'off')
# Metrics for column two
two.metric(label="Wind", value="17 mph", delta="-8%")
# Metrics for column three
three.metric(label="Humidity", value="86%", delta="4%")
