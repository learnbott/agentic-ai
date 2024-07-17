import operator
import pandas as pd
import numpy as np
import io


def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )

# Function to split DataFrame by empty columns
def split_df_by_empty_columns(df):
    # Identify indices of empty columns
    empty_cols = df.columns[df.isna().all()].tolist()
    # Split DataFrame by empty columns
    sub_dfs = np.split(df, df.columns.get_indexer(empty_cols) + 1, axis=1)
    # Filter out the empty DataFrames (which correspond to the empty columns)
    sub_dfs = [sub_df.dropna(axis=1, how='all') for sub_df in sub_dfs]
    return sub_dfs

# Function to split a DataFrame by empty rows
def split_df_by_empty_rows(df):
    # Identify indices of empty rows
    empty_rows = df.index[df.isna().all(axis=1)].tolist()
    # Split DataFrame by empty rows
    sub_dfs = np.split(df, df.index.get_indexer(empty_rows) + 1, axis=0)
    # Filter out the empty DataFrames (which correspond to the empty rows)
    sub_dfs = [sub_df.dropna(axis=0, how='all') for sub_df in sub_dfs]
    return sub_dfs


# Displaying the final split DataFrames
# for i, final_df in enumerate(final_split_dfs, 1):
#     print(f"DataFrame {i}:\n{final_df}\n")

def randomize_row_values(dfs: pd.DataFrame, ground_truth: pd.DataFrame, n_samples: int = None) -> pd.DataFrame:
    """
    Randomly placing values in a dataframe
    """
    dfs_copy = dfs.copy()
    if n_samples is None:
        n_samples = np.random.randint(1,len(ground_truth),1)[0]
        
    testvalues = ground_truth.sample(n=n_samples)
    testidx = testvalues.index

    dfscolumns = dfs_copy.columns
    for row in testvalues.loc[testidx].iterrows():
        random_row = np.random.choice(dfs_copy.index,1)[0]
        random_col = np.random.choice(np.arange(len(dfscolumns)-1)[2:],1)[0]
        random_col1 = dfscolumns[random_col]
        random_col2 = dfscolumns[random_col+1]
        dfs_copy.loc[testidx, :2]=np.nan
        dfs_copy.loc[random_row, [random_col1, random_col2]] = row[1].values
    return dfs_copy

def get_csv_string(dfs: pd.DataFrame) -> str:
    """
    Convert a DataFrame to a CSV formatted string
    """
    # Create a string buffer
    buffer = io.StringIO()

    # Convert the DataFrame to CSV format and write to the buffer
    dfs.to_csv(buffer, index=False)

    # Get the CSV as a string
    csv_string = buffer.getvalue()

    return csv_string

operators_dict = {'Selling Costs': {'operators':(operator.ge, operator.le), 'bounds':(0,1)}, 
                  'Disposition Fee': {'operators':(operator.ge, operator.le), 'bounds':(0,1)}, 
                  'Net Operating Income': {'operators':(operator.ge,), 'bounds':(0,)}, 
                  'Loan Assumption/Payoff': {'operators':(operator.le,), 'bounds':(0,)}, 
                  'Return of Forecasted Reserves': {'operators':(operator.le,), 'bounds':(0,)}, 
                  'CF Y 11': {'operators':(operator.ge,), 'bounds':(0,)}, 
                  'Return of Maximum Offering Amount': {'operators':(operator.le,), 'bounds':(0,)}, 
                  'Projected Terminal Cap Rate': {'operators':(operator.ge, operator.le), 'bounds':(0,1)},
                  'Cashflows 1': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 2': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 3': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 4': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 5': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 6': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 7': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 8': {'operators':(operator.ge,), 'bounds':(1,)},
                  'Cashflows 9': {'operators':(operator.ge,), 'bounds':(1,)}}

range_description_json = {'Selling Costs': 'float greater than 0 and less than 1', 
                           'Disposition Fee': 'float greater than 0 and less than 1', 
                           'Net Operating Income': 'float greater than or equal to 0', 
                           'Loan Assumption/Payoff': 'float less than or equal to 0', 
                           'Return of Forecasted Reserves': 'float less than or equal to 0', 
                           'CF Y 11': 'float greater than or equal to 0', 
                           'Return of Maximum Offering Amount': 'float less than or equal to 0', 
                           'Projected Terminal Cap Rate': 'float greater than 0 and less than 1',
                           'Cashflows 1': 'float greater than 1',
                           'Cashflows 2': 'float greater than 1',
                           'Cashflows 3': 'float greater than 1',
                           'Cashflows 4': 'float greater than 1',
                           'Cashflows 5': 'float greater than 1',
                           'Cashflows 6': 'float greater than 1',
                           'Cashflows 7': 'float greater than 1',
                           'Cashflows 8': 'float greater than 1',
                           'Cashflows 9': 'float greater than 1'}
