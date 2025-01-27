from cds_data_fetch import *
import pandas as pd
from pandas.tseries.offsets import MonthEnd, YearEnd

import numpy as np
import wrds

import config
from pathlib import Path

OUTPUT_DIR = Path(config.OUTPUT_DIR)
DATA_DIR = Path(config.DATA_DIR)
WRDS_USERNAME = config.WRDS_USERNAME

def assign_quantiles(group, n_quantiles=20):
    """
    Assigns quantile rankings to a DataFrame based on the 'parspread' column.

    Parameters:
    - group (DataFrame): The input pandas DataFrame containing at least the 'parspread' column.
    - n_quantiles (int): The number of quantiles to divide the data into. Default is 20.

    Returns:
    - DataFrame: The modified input DataFrame with a new 'quantile' column indicating the quantile ranking of each 'parspread'.
    """
    group['quantile'] = pd.qcut(group['parspread'], n_quantiles, labels=False) + 1
    return group

# Create a function to resample and select the last value for each month
def resample_end_of_month(data):
    """
    Resamples a time series DataFrame to the end of each month, selecting the last available value for each month.

    Parameters:
    - data (DataFrame): The input pandas DataFrame with a DateTimeIndex.

    Returns:
    - DataFrame: A DataFrame resampled to the end of each month with the last value of the month.
    """
    return data.resample('M').last()

# Uncomment to pull fresh data
#cds_data_dict = get_cds_data()

def process_cds_data():
    """
    Processes the CDS data to prepare it for analysis. It consolidates CDS data from multiple years, 
    averages data by date and ticker, resamples to end of month, sorts, and assigns quantiles.

    Returns:
    - DataFrame: The processed CDS data with quantiles assigned and resampled to the end of each month.
    """
    cds_data = pd.concat(cds_data_dict.values(), axis=0)

    df = cds_data.groupby(['date','ticker']).mean().reset_index()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Apply the function to each group
    end_of_month_data = df.groupby('ticker').apply(resample_end_of_month)

    # Reset the index if needed
    end_of_month_data.reset_index(level=0, drop=True, inplace=True)

    # Ensure the 'date' column is the right datetime type
    end_of_month_data.reset_index(inplace=True)
    end_of_month_data['date'] = pd.to_datetime(end_of_month_data['date'])

    # Sort values by 'date' and 'parspread' to ensure proper quantile ranking
    end_of_month_data_sorted = end_of_month_data.sort_values(['date', 'parspread'])

    # Group by 'date' and apply the function to assign quantiles
    end_of_month_data_quantiled = end_of_month_data_sorted.groupby('date').apply(assign_quantiles)
    end_of_month_data_quantiled.rename(columns={'date': 'Date'}, inplace=True)


    end_of_month_data_quantiled.reset_index(inplace=True)
    #end_of_month_data_quantiled.drop(columns=['level_1','index','date'], inplace=True)
    return end_of_month_data_quantiled

def calc_cds_monthly(method = 'median'):
    """
    Calculates monthly CDS spreads based on the specified aggregation method (mean, median, or weighted).

    Parameters:
    - method (str): The aggregation method to use ('mean', 'median', or 'weighted'). Default is 'median'.

    Returns:
    - DataFrame: A pivot table of monthly CDS spreads with quantiles as columns and dates as rows.
    """
    if Path(OUTPUT_DIR / 'cds_monthly_spread_median.csv').exists() and method == 'median':
        return pd.read_csv(OUTPUT_DIR / 'cds_monthly_spread_median.csv')
    elif Path(OUTPUT_DIR / 'cds_monthly_spread_mean.csv').exists() and method == 'mean':
        return pd.read_csv(OUTPUT_DIR / 'cds_monthly_spread_mean.csv')
    elif Path(OUTPUT_DIR / 'cds_monthly_spread_weighted.csv').exists() and method == 'weighted':
        return pd.read_csv(OUTPUT_DIR / 'cds_monthly_spread_weighted.csv')
    
    df = process_cds_data()
    df.set_index('quantile', inplace = True)

    def weighted_mean(data):
        weights = data['parspread']
        return (data['parspread'] * weights).sum() / weights.sum()

    if method == 'mean':
        comb_spread = df.groupby(['quantile', 'Date'])['parspread'].mean().reset_index()
    elif method == 'median':
        comb_spread = df.groupby(['quantile', 'Date'])['parspread'].median().reset_index()
    elif method == 'weighted':
        comb_spread = df.groupby(['quantile', 'Date']).apply(weighted_mean).reset_index(name = 'parspread')

    # Pivot the table to have 'date' as index, 'quantile' as columns, and mean 'parspread' as values
    pivot_table = comb_spread.pivot_table(index='Date', columns='quantile', values='parspread')

    # Rename the columns to follow the 'cds_{quantile}' format
    pivot_table.columns = [f'cds_{int(col)}' for col in pivot_table.columns]
    if method == 'median':
        pivot_table.to_csv(OUTPUT_DIR / 'cds_monthly_spread_median.csv')
    elif method == 'mean':
        pivot_table.to_csv(OUTPUT_DIR / 'cds_monthly_spread_mean.csv')
    elif method == 'weighted':
        pivot_table.to_csv(OUTPUT_DIR / 'cds_monthly_spread_weighted.csv')
    return pivot_table

def process_cds_monthly(method = 'median'):
    """
    Processes monthly CDS data to replace outliers with a rolling median or the specified aggregation method.

    Parameters:
    - method (str): The aggregation method to use for calculating the monthly CDS spreads. Default is 'median'.

    Returns:
    - DataFrame: The processed monthly CDS data with outliers replaced according to the specified method.
    """
    df = calc_cds_monthly(method)
    #print(df['cds_20'].describe())
    mean = df['cds_20'].mean()
    std = df['cds_20'].std()
    cutoff = std * 3
    lower, upper = mean - cutoff, mean + cutoff

    # Calculate the median
    median = df['cds_20'].median()
    window_size = 15
    # Replace outliers with the median
    #df['cds_20'] = np.where((df['cds_20'] < lower) | (df['cds_20'] > upper), median, df['cds_20'])
    df['cds_20'] = df['cds_20'].rolling(window=window_size).median()
    #print(df['cds_20'].describe())
    return df
