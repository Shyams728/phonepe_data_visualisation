import extra_streamlit_components as stx
import streamlit as st
import streamlit_shadcn_ui as ui
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px

st.set_page_config(
    layout="wide",
    initial_sidebar_state='collapsed',
    page_title="📈 Tables",
    page_icon= ':chart:'  
)

st.title("📈 Tables")

# ***************************************Data Access*******************************

# Create a function to load data from the SQLite database
def load_data_from_db(query):
    sqlite_file = 'test.sqlite'
    # Use a context manager to ensure proper resource management
    with create_engine(f'sqlite:///{sqlite_file}').connect() as engine:
        df = pd.read_sql(query, engine)
    return df

def select_the_table(selected_tab):
    # Execute different queries based on the chosen tab
    tables = {
        'Transaction Data': 'agregated_transaction_country',
        'Transaction State Data': 'aggregated_transaction_state',
        'Insurance Data': 'aggregated_insurence_country',
        'Insurance State Data': 'aggregated_insurence_state',
        'User Country Data': 'aggregated_user_counry',
        'User State Data': 'agregated_user_state'
    }
    return tables.get(selected_tab, None)

# ***************************************Data Exploration*******************************

first_box = st.container(border=True)
col1, col2 = first_box.columns([7, 1])

with col1:
    # Create tabs
    selected_tab = ui.tabs(
        options=['Transaction Data', 'Transaction State Data', 'Insurance Data', 'Insurance State Data',
                 'User Country Data', 'User State Data'], default_value='User State Data', key="two_birds")
with col2:
    filter_data = st.toggle('Filter Data')

chosen_table = select_the_table(selected_tab)
if chosen_table is None:
    st.warning("Please select a valid table.")
else:
    df = load_data_from_db(f'SELECT * FROM {chosen_table}')
    
    filtered_df = None

    filter_box = st.container(border=True)

if filter_data:
    # Create columns
    col3, col4, col5, col6 = filter_box.columns(4)

    # Sidebar input widgets
    selected_years = col3.multiselect('Select Year:', sorted(df['year'].unique()), default=[2022],
                                      help='Select the Year')
    selected_quarters = col4.multiselect('Select Quarter:', sorted(df['quarter'].unique()), default=[1, 2, 3, 4])

    # Check if 'state' is a column in the DataFrame
    if 'state' in df.columns:
        selected_state = col5.multiselect('Select State/UT:', sorted(df['state'].unique()), default= ['karnataka'])
        
        if 'type_of_transaction' in df.columns:
            entity_type = col6.multiselect('Select Transaction Type:', sorted(df['type_of_transaction'].unique()))
            # Filter the DataFrame based on user inputs
            filtered_df = df[(df['state'].isin(selected_state)) & (df['year'].isin(selected_years)) & (
                        df['quarter'].isin(selected_quarters)) & (df['type_of_transaction'].isin(entity_type))]
        else:
            entity_type = col6.multiselect('Select Phone Brand:', sorted(df['phone_brand'].unique()))
            # Filter the DataFrame based on user inputs
            filtered_df = df[(df['state'].isin(selected_state)) & (df['year'].isin(selected_years)) & (
                        df['quarter'].isin(selected_quarters)) & (df['phone_brand'].isin(entity_type))]
    else:
        if 'type_of_transaction' in df.columns:
            entity_type = col5.multiselect('Select Transaction Type:', sorted(df['type_of_transaction'].unique()))
            # Filter the DataFrame based on user inputs
            filtered_df = df[(df['year'].isin(selected_years)) & (df['quarter'].isin(selected_quarters)) & (
                        df['type_of_transaction'].isin(entity_type))]
        else:
            entity_type = col5.multiselect('Select Phone Brand:', sorted(df['phone_brand'].unique()))
            # Filter the DataFrame based on user inputs
            filtered_df = df[(df['year'].isin(selected_years)) & (df['quarter'].isin(selected_quarters)) & (
                        df['phone_brand'].isin(entity_type))]
   
    # Show filtered data using an expander
    with st.expander('Show Filtered Full Data'):
        st.dataframe(filtered_df, use_container_width=True)

else:
    filtered_df = df
    with st.expander('Show Full Data'):
        st.dataframe(df, use_container_width=True)
        
if selected_tab == 'User Country Data':
    # Aggregate data by year and phone brand 
    agg_df = df.groupby(["year",'phone_brand']).agg({
        "phone_count": "sum",
        "Percentage": "sum"
    }).reset_index()
    data = agg_df
    


    # Bar chart of Tracsaction data
    fig1 = px.bar(
        df,
        x="name",
        y="count",
        title="Total Transaction Count by Category",
        labels={"count": "Total Transaction Count", "name": "Category"}
    )

    st.plotly_chart(fig1, use_container_width=True)
    

else:
    data = filtered_df.head()    
    
    

    
ui.table(data=data, maxHeight=500, key="filtered_data_table")


# # Bar chart for total transaction amount by year and quarter
# fig1 = px.bar(
#     df,
#     x="year",
#     y="amount",
#     color="name",
#     barmode="group",
#     title="Total Transaction Amount by Year and Quarter"
# )
# fig1.update_layout(xaxis_title="Year", yaxis_title="Total Amount")
# st.plotly_chart(fig1, theme="streamlit", use_container_width=True)

# # Pie chart for transaction distribution by category
# fig4 = px.pie(
#     df,
#     values="amount",
#     names="name",
#     title="Transaction Distribution by Category"
# )
# st.plotly_chart(fig4, theme="streamlit", use_container_width=True)


# # Sunburst chart for hierarchical data
# fig6 = px.sunburst(
#     df,
#     path=["year", "quarter", "name"],
#     values="amount",
#     title="Hierarchical Data (Year, Quarter, Category)"
# )
# st.plotly_chart(fig6, theme="streamlit", use_container_width=True)

# # Density heatmap for transaction amount
# fig9 = px.density_heatmap(
#     df,
#     x="quarter",
#     y="name",
#     z="amount",
#     title="Density Heatmap for Transaction Amount"
# )
# st.plotly_chart(fig9, theme="streamlit", use_container_width=True)


# # Parallel coordinates for multi-dimensional analysis
# fig10 = px.parallel_coordinates(
#     df,
#     color="amount",
#     dimensions=["year", "quarter", "count", "amount"],
#     title="Parallel Coordinates for Multi-Dimensional Analysis"
# )
# st.plotly_chart(fig10, theme="streamlit", use_container_width=True)