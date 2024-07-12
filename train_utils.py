import operator
import pandas as pd
import numpy as np
import io

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
                  '1': {'operators':(operator.ge,), 'bounds':(1,)},
                  '2': {'operators':(operator.ge,), 'bounds':(1,)},
                  '3': {'operators':(operator.ge,), 'bounds':(1,)},
                  '4': {'operators':(operator.ge,), 'bounds':(1,)},
                  '5': {'operators':(operator.ge,), 'bounds':(1,)},
                  '6': {'operators':(operator.ge,), 'bounds':(1,)},
                  '7': {'operators':(operator.ge,), 'bounds':(1,)},
                  '8': {'operators':(operator.ge,), 'bounds':(1,)},
                  '9': {'operators':(operator.ge,), 'bounds':(1,)}}

range_description_json = {'Selling Costs': 'float greater than 0 and less than 1', 
                           'Disposition Fee': 'float greater than 0 and less than 1', 
                           'Net Operating Income': 'float greater than or equal to 0', 
                           'Loan Assumption/Payoff': 'float less than or equal to 0', 
                           'Return of Forecasted Reserves': 'float less than or equal to 0', 
                           'CF Y 11': 'float greater than or equal to 0', 
                           'Return of Maximum Offering Amount': 'float less than or equal to 0', 
                           'Projected Terminal Cap Rate': 'float greater than 0 and less than 1',
                           '1': 'float greater than 1',
                           '2': 'float greater than 1',
                           '3': 'float greater than 1',
                           '4': 'float greater than 1',
                           '5': 'float greater than 1',
                           '6': 'float greater than 1',
                           '7': 'float greater than 1',
                           '8': 'float greater than 1',
                           '9': 'float greater than 1'}
