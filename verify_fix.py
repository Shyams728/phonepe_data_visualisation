import pandas as pd
import numpy as np

def test_aggregation_logic():
    # Mock data without 'count' column (simulating User Data)
    df_no_count = pd.DataFrame({
        'entity_name': ['A', 'A', 'B', 'C'],
        'state': ['S1', 'S1', 'S1', 'S2'],
        'year': [2022, 2022, 2022, 2022],
        'quarter': [1, 2, 1, 2],
        'registeredUsers': [100, 200, 300, 400]
    })
    
    value_col = 'registeredUsers'
    count_col = 'count'
    data_type = 'Users'
    selected_entity = 'districts'
    
    print("Testing with MISSING 'count' column...")
    agg_dict = {value_col: 'sum', 'entity_name': 'nunique'}
    if count_col in df_no_count.columns:
        agg_dict[count_col] = 'sum'
    
    state_agg = df_no_count.groupby('state').agg(agg_dict).reset_index()
    
    # Test the fix for District Drill line 279
    cols = ['State', 'Total Amount' if data_type != "Users" else 'Total Users']
    if count_col in df_no_count.columns:
        cols.append('Transaction Count')
    cols.append(f'{selected_entity.title()} Count')
    
    print(f"Assigning columns: {cols}")
    state_agg.columns = cols
    print("State Aggregation Result:")
    print(state_agg)
    assert len(state_agg.columns) == 3
    
    # Mock data WITH 'count' column (simulating Transaction Data)
    df_with_count = pd.DataFrame({
        'entity_name': ['A', 'A', 'B', 'C'],
        'state': ['S1', 'S1', 'S1', 'S2'],
        'year': [2022, 2022, 2022, 2022],
        'quarter': [1, 2, 1, 2],
        'amount': [1000, 2000, 3000, 4000],
        'count': [10, 20, 30, 40]
    })
    
    value_col = 'amount'
    data_type = 'Transactions'
    
    print("\nTesting with EXISTING 'count' column...")
    agg_dict = {value_col: 'sum', 'entity_name': 'nunique'}
    if count_col in df_with_count.columns:
        agg_dict[count_col] = 'sum'
        
    state_agg_w = df_with_count.groupby('state').agg(agg_dict).reset_index()
    
    cols = ['State', 'Total Amount' if data_type != "Users" else 'Total Users']
    if count_col in df_with_count.columns:
        cols.append('Transaction Count')
    cols.append(f'{selected_entity.title()} Count')
    
    print(f"Assigning columns: {cols}")
    state_agg_w.columns = cols
    
    # Test formatting logic
    display_state = state_agg_w.head(10).copy()
    if data_type != "Users":
        display_state['Total Amount' if 'Total Amount' in display_state.columns else 'Total Users'] = 100 # Simulating formatting
    
    if 'Transaction Count' in display_state.columns:
        display_state['Transaction Count'] = display_state['Transaction Count'].apply(lambda x: f"{x}")
        
    print("State Aggregation Result:")
    print(display_state)
    assert len(state_agg_w.columns) == 4
    
    print("\nVerification SUCCESSFUL!")

if __name__ == "__main__":
    test_aggregation_logic()
