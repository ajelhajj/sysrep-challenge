import os
import pandas as pd
import numpy as np
from datetime import datetime

def is_empty(file_path):
    """Check if file is empty by confirming if its size is 0 bytes. Returns 0 if false, 1 if true."""
    return (os.path.exists(file_path) and os.stat(file_path).st_size == 0) 

def read_file() -> pd.DataFrame:
    """Check if file is empty. If so, print message to console. If not, read file as pandas DataFrame.""" 
    path = 'input_data.xlsx'
    if is_empty(path): # if function returns true (ie empty file)
        print('File is empty')
    else:
        df = pd.read_excel(path)
    return df

def get_tax_rate(state):
    """Returns the tax rate for Illinois or Tennessee given their abbreviations.""" 
    state_rates = {'IL': .0251, 'TN': .01766, }
    return state_rates[state.upper()]

def write_new_file(aggregated_data_frame: pd.DataFrame, report_date: str):
    """Writes the aggregated datadrame to an xlsx file with the report date in the filename.""" 
    aggregated_data_frame.to_excel(f'aggregated_report-{report_date}.xlsx')
    return

def fix_data_entry_mistakes(df): 
    """Corrects the data entry mistake in which O exists in place of 0. """ 
    cols = ['Effective Date', 'Expiration Date', 'Annual GWP'] # columns of interest
    for col in cols:
        if df[col].astype(str).str.contains('O').any(): # if column contains str "O"
            df[col] = df[col].astype(str).str.replace('O','0') # replace with zero
            if 'date' in col.lower(): # if column is a date column
                df[col] = pd.to_datetime(df[col]) # convert from temporary string type to datetime
            else:
                df[col] = pd.to_numeric(df[col]) # convert from temporary string type to a numeric type
    return

def calc_pro_rata_gwp(df):
    """Create calculated column for Pro-Rate GWP."""
    df['Total Effective Days'] = (df['Expiration Date']-df['Effective Date']).dt.days
    df['Pro-Rata GWP'] = (df['Annual GWP']/365)*df['Total Effective Days']
    return

def report_str_datetime(report_date):
    """Converts report date from type string to datetime object."""
    return datetime.strptime(report_date, '%Y-%m-%d')

def calc_earned_premium(df, report_date):
    """Create calculated column for earned premium."""
    # calc_pro_rata_gwp(df) # dependency on this function b/c we need 'Effective Days' column and we don't want to recalculate

    # report date may fall before effective date, after effective date but before expiration, or after expiration
    # handle all cases appropriately to calclate current days effective:
    conds = [(report_date <= df['Effective Date']),
             ((report_date < df['Expiration Date']) & (report_date > df['Effective Date'])),
             (report_date >= df['Expiration Date'])]
             
    choice = [0,
              (report_date-df['Effective Date']).dt.days,
              (df['Expiration Date']-df['Effective Date']).dt.days]
    
    df['Current Days Effective']= np.select(conds, choice)
    df['Earned Premium'] = (df['Pro-Rata GWP']/df['Total Effective Days'])*df['Current Days Effective']
    return

def calc_unearned_premium(df, report_date):
    """Create calculated column for unearned premium."""
    conds = [(report_date <= df['Effective Date']),
             ((report_date < df['Expiration Date']) & (report_date > df['Effective Date'])),
             (report_date >= df['Expiration Date'])]

    choice = [(df['Expiration Date']-df['Effective Date']).dt.days,
                (df['Expiration Date']-report_date).dt.days,
                0]
    
    df['Days Remaining'] = np.select(conds, choice)
    df['Unearned Premium'] = (df['Pro-Rata GWP']/df['Total Effective Days'])*df['Days Remaining']
    return

def calc_taxes(df):
    """Create calculated column for taxes depending on State column."""
    conds = [df['State'] == 'IL',
             df['State'] == 'TN']
    choice = [df['Pro-Rata GWP'] * get_tax_rate('IL'),
              df['Pro-Rata GWP'] * get_tax_rate('TN')]
    df['Taxes'] = np.select(conds, choice)
    return

def report_date(df, report_date):
    """Create column in second position to store report_date."""
    df['Report Date'] = report_date
    return

# def aggregate_company(df):
#     """Aggregate by Company Name to count number of vehicles/VINs and sum vehicle pro-rata GWP, earned premium, unearned premium, and taxes."""
#     df.groupby('Company Name')['Fee'].agg(['sum','count'])
    
#     names = {
#         'Total_Count': x['Type'].count(),
#         'Total_Number': x['Number'].sum(),
#         'Count_Status=Y': x[x['Status']=='Y']['Type'].count(),
#         'Number_Status=Y': x[x['Status']=='Y']['Number'].sum(),
#         'Count_Status=N': x[x['Status']=='N']['Type'].count(),
#         'Number_Status=N': x[x['Status']=='N']['Number'].sum()}

#     return pd.Series(names)

# df.groupby('Type').apply(my_agg)

def company_agg(x):
    names = {
        'Total Count of Vehicles': x['VIN'].count(),
        'Total Annual GWP': x['Annual GWP'].sum(),
        'Total Pro_Rata GWP': x['Pro-Rata GWP'].sum(),
        'Total Earned Premium': x['Earned Premium'].sum(),
        'Total Unearned Premium': x['Unearned Premium'].sum(),
        'Total Taxes': x['Total Taxes'].sum()
        }
    return pd.Series(names)
    
def aggregate(df):
    df = df.groupby('Company Name').apply(company_agg)
    
def main():
    report_date = '2022-08-01'
    df = read_file()
    
    # your processing here
    report_date = report_str_datetime(report_date)
    fix_data_entry_mistakes(df)
    calc_pro_rata_gwp(df)
    calc_earned_premium(df, report_date)
    calc_unearned_premium(df, report_date)
    calc_taxes(df)
    report_date(df, report_date)
    # aggregate(df)
    
    write_new_file(df, report_date)
    return 
