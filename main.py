import pandas as pd
# import datetime as dt

def read_file() -> pd.DataFrame:
    df = pd.read_excel('input_data.xlsx')
    return df


def get_tax_rate(state):
    state_rates = {'IL': .0251, 'TN': .01766, }
    return state_rates[state]


def write_new_file(aggregated_data_frame: pd.DataFrame, report_date: str):
    aggregated_data_frame.to_excel(f'aggregated_report-{report_date}.xlsx')
    return

def fix_data_entry_mistakes(df):
    cols = ['Effective Date', 'Expiration Date', 'Annual GWP'] # columns of interest
    for col in cols:
        if df[col].astype(str).str.contains('O').any(): # if column contains str "O"
            df[col] = df[col].astype(str).str.replace('O','0') # replace with zero
            if 'date' in col.lower(): # if column is a date column
                df[col] = pd.to_datetime(df[col]) # convert from temporary string type to datetime
            else:
                df[col] = pd.to_numeric(df[col]) # convert from temporary string type to a numeric type
        
def calc_pro_rata_gwp(df):
    df['Pro-Rata GWP'] = (df['Annual GWP']/365)*(df['Expiration Date']-df['Effective Date']).dt.days

def calc_earned_unearned_premium(df):
    df['Earned Premium'] = df['Pro-Rata GWP']/(df['Expiration Date']-df['Effective Date']).dt.days # daily GWP
    df['Unearned Premium'] = 
    
def main():
    report_date = '2022-08-01'
    df = read_file()
    # your processing here
    fix_data_entry_mistakes(df)
    calc_pro_rata_gwp(df)
    # calc_earned_unearned_premium(df)
    
    write_new_file(df, report_date)
    return df

