import warnings
warnings.filterwarnings('ignore')


# In[2]:


import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os
from sql_connection import connect_to_database
# from web import create_connection, scrape_data_for_companies

# In[3]:


f=open("logfile.txt", "a")
f.write("\n")

connection = connect_to_database()

def preprocess_data(df, ipweeks, calcflag, addtosqlflag):
    cursor=connection.cursor()
    f.write("Preprocessing data.\n")
    df = df.drop_duplicates()
    df=df[["Symbol", "Date", "Open", "High", "Close", "Low"]]
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df = df.sort_values('Date').reset_index(drop=True)

    df['Open'] = df['Open'].astype('float64')
    df['High'] = df['High'].astype('float64')
    df['Low'] = df['Low'].astype('float64')
    df = df[pd.to_numeric(df['Close'], errors='coerce').notnull()]
    df['Close'] = df['Close'].astype('float64')
    df['Symbol'] = df['Symbol'].astype('object')
    df = df[["Symbol","Date","Open","Low","Close","High"]]
    
    df["Change"] = df['Close'].diff()
    df["Gain"] = df["Change"].apply(lambda x: x if x >= 0 else 0)
    df["Loss"] = df["Change"].apply(lambda x: -x if x < 0 else 0)
    df["AvgGain"] = df["Gain"].rolling(window=10, min_periods=1).mean()
    df["AvgLoss"] = df["Loss"].rolling(window=10, min_periods=1).mean()
    df["RS"] = df["AvgGain"] / df["AvgLoss"]
    df["RSI"] = 100 - (100 / (1 + df["RS"]))
    
    df['MovingAvg'] = df['Close'].rolling(window=10, min_periods=1).mean()
    df['Standard Deviation'] = df['Close'].rolling(window=10, min_periods=1).std()
    df['UpperBand'] = df['MovingAvg'] + 2 * df['Standard Deviation']
    df['LowerBand'] = df['MovingAvg'] - 2 * df['Standard Deviation']   
    df['CrossAbove'] = df.apply(lambda row: 1 if row['High'] > row['UpperBand'] else 0, axis=1)
    df['CrossBelow'] = df.apply(lambda row: 1 if row['Low'] < row['LowerBand'] else 0, axis=1)
        
    if calcflag == 1:
        df['HighestInNext1Week'] = df['Close'].rolling(window=5+1).apply(
            lambda x: x.max() if len(x) == 5+1 else np.nan,
            raw=True
        ).shift(-5)
        df['HighestInNext2Weeks'] = df['Close'].rolling(window=10+1).apply(
            lambda x: x.max() if len(x) == 10+1 else np.nan,
            raw=True
        ).shift(-10)
        df['LowestInNext1Week'] = df['Close'].rolling(window=5+1).apply(
            lambda x: x.min() if len(x) == 5+1 else np.nan,
            raw=True
        ).shift(-5)
        df['LowestInNext2Weeks'] = df['Close'].rolling(window=10+1).apply(
            lambda x: x.min() if len(x) == 10+1 else np.nan,
            raw=True
        ).shift(-10)
        i=0
        if addtosqlflag==1:
            for index, row in df.iterrows():
    #             print(i,"\n")
    #             i+=1;
                update_query = """
                UPDATE all_companies_data1.companies_data
                SET HighestInNext1Week_A = %s,
                    HighestInNext2Weeks_A = %s,
                    LowestInNext1Week_A = %s,
                    LowestInNext2Weeks_A = %s
                WHERE Date = %s AND Symbol = %s AND (HighestInNext1Week_A IS NULL OR HighestInNext2Weeks_A IS NULL OR LowestInNext1Week_A IS NULL OR LowestInNext2Weeks_A IS NULL)
                """

                # Extract the values from the DataFrame row
                values = (
                    row['HighestInNext1Week'],
                    row['HighestInNext2Weeks'],
                    row['LowestInNext1Week'],
                    row['LowestInNext2Weeks'],
                    row['Date'].strftime('%d-%m-%Y'),
                    row['Symbol']
                )

                cursor.execute(update_query, values)
                connection.commit()


    for i in range(0, (ipweeks)*5):
        for col in ['Open', 'Close', 'High', 'Low']:
            df[f'{col}-{i}'] = df[col].shift(i)
            
    df = df.dropna()
    return df
