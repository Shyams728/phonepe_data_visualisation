import streamlit as st
import plotly.express as px
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import streamlit_shadcn_ui as ui
import extra_streamlit_components as stx

# Set Streamlit page configuration
st.set_page_config(
    page_title="Dash Board",
    layout="wide",
    initial_sidebar_state = "collapsed",
    page_icon=":graph:",
)
#***************************************Data Access*******************************
# Create a function to load data from the SQLite database
def load_data_from_db(query):
    sqlite_file = 'test.sqlite'
    engine = create_engine(f'sqlite:///{sqlite_file}')
    df = pd.read_sql(query, engine)
    return df


def select_the_table(selected_tab):
    # Execute different queries based on the chosen tab
    if selected_tab == 'Transaction Data':
        query = 'SELECT * FROM top_transaction_country;'
    elif selected_tab == 'Insurance Data':
        query = 'SELECT * FROM top_insurence_country;'
    elif selected_tab == 'User Data':
        query = 'SELECT * FROM top_user_country;'
    elif selected_tab == 'Statewise Transaction Data':
        query = 'SELECT * FROM top_transaction_state;'
    elif selected_tab == 'Statewise Insurance Data':
        query = 'SELECT * FROM top_insurance_state;'
    elif selected_tab == 'Statewise User Data':
        query = 'SELECT * FROM top_user_state;'
    return query


#***********************************plots*********************************************

def plot_barchart_top(df, x, y, title):
    # Plotly bar chart
    fig = px.bar(
        df,
        y=x,
        x=y,
        orientation='h',
        color="entity_name",
        labels={'amount': 'Amount', 'count': 'Transactions', 'quarter': 'Quar'},
        title=title,
    )
    # Show the plot using Plotly chart in Streamlit
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)



#***************************************Data Exploration*******************************





def main():

    # Create container for choices
    choice_box = st.container(border=True)
    with choice_box:
        selected_tab = st.selectbox(label='Choice of chart',
                                    options=['Transaction Data', 'Insurance Data', 'User Data',
                                                'Statewise Transaction Data', 'Statewise Insurance Data',
                                                'Statewise User Data'])
    choosen_table = select_the_table(selected_tab)
    df = load_data_from_db(choosen_table)

    # Create container for info box
    info_box = st.container()
    
    # Create main container
    main_box = st.container(border=True)

    # Create columns
    col2, col3 = main_box.columns([2, 3])


    # Access data from container1 in col2
    with col2:
        container2 = st.container()
        with container2:
            # Display the filtered DataFrame
            st.dataframe(df, height=480, use_container_width=True)
            # ui.table(data=df.head(), maxHeight=500,key="filtered_data_table")


    # Create containers within each column
    with col3:
        container3 = st.container()
        with container3:
            # Plotly bar chart
            # Check if 'registeredUsers' column exists in the DataFrame
            if 'registeredUsers' in df.columns:
                plot_barchart_top(df, 'entity_name', 'registeredUsers', f'Top {selected_tab} Chart')
            else:
                plot_barchart_top(df, 'entity_name', 'amount', f'Top {selected_tab} Chart')

    # info_box = st.container(border=True)
    col5, col6 = info_box.columns([1, 1])
        # Create containers within each column
    with col5:
        container1 = st.container(border=True)
        with container1:
            if 'User' in selected_tab:
                total_users = df.registeredUsers.sum()
                st.metric(f"Total Users", f"{total_users}", "Year on year")
            else:
                st.metric(f"{selected_tab} Amount", f"₹{df.amount.sum()}", "Year on year")
                
    with col6:
        container3 = st.container(border=True)
        with container3:
            st.metric(f"{selected_tab} Counts", f"{df['count'].sum()}", "Year on year")    


# Run the main script
if __name__ == "__main__":
    main()
