import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os
from sql_connection import connect_to_database
from preprocess_code import preprocess_data

#get_ipython().run_line_magic('run', 'web.ipynb')

f=open("logfile.txt", "a")
f.write("\n")

f1=open("prediction_file.txt", "a")
f1.write("\n")


# In[5]:


csv_file = "test_output.csv" 
# scrape_data_for_companies(csv_file)
# f.write("Scraping new data for all companies.\n")


def train_model(ipweeks, threshold, symbol, addtosqlflag):
    cursor = connection.cursor()
    tobeexecuted=f"SELECT Symbol,Date,Open,High,Low,Close,Volume FROM all_companies_data1.companies_data where Symbol='{symbol}';"
    cursor.execute(tobeexecuted)
#     cursor.execute("SELECT Date,Open,High,Low,Close,Volume FROM all_companies_data.companies_data where Symbol='TCS';")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Symbol", "Date", "Open", "Low", "Close", "High","Volume"])
    df = preprocess_data(df, ipweeks, 1, addtosqlflag)
    targets = ["HighestInNext1Week", "HighestInNext2Weeks", "LowestInNext1Week", "LowestInNext2Weeks"]
    models = {}
    for target in targets:
        X = df.drop(["Date", "Open", "Low", "Close", "High", "Symbol"] + targets, axis=1)
        if "High" in target:
            X = X.drop(columns=X.filter(like='Low', axis=1).columns)
        if "Low" in target:
            X = X.drop(columns=X.filter(like='High', axis=1).columns)
        y = df[target]

        # Replace infinity values with NaN
        X = X.replace([np.inf, -np.inf], np.nan)
        y = y.replace([np.inf, -np.inf], np.nan)

        # Drop rows with NaN values in both X and y
        df_combined = pd.concat([X, y], axis=1).dropna()

        # Update X and y after dropping rows
        X = df_combined.drop(columns=[target])
        y = df_combined[target]

        model = GradientBoostingRegressor()
        model.fit(X, y)

        predictions = model.predict(X)
        rmse = np.sqrt(mean_squared_error(y, predictions))

        f.write("Training model for " + symbol + " " + target + " -> " + str(ipweeks) + ' input weeks' + " ---> RMSE: " + str(rmse))

        if rmse < threshold:
            model_filename = symbol + "_" + target + "_" + str(ipweeks) + '.joblib'
            joblib.dump(model, model_filename)
            models[f'{symbol}_{target}_{ipweeks}'] = (model_filename, rmse)

            f.write("\t MODEL ACCEPTED \n")
        else:
            f.write("\t MODEL REJE     CTED \n")
    return models


# In[9]:


def train_loop(minweeks, maxweeks, threshold, symbol):
    f.write(f"Training models with {minweeks} to {maxweeks} input weeks with RMSE threshold {threshold} for {symbol}.\n")
    models = {}
    addtosqlflag=0
    for i in range(minweeks, maxweeks+1):
        if i==minweeks:
            addtosqlflag=1
        else:
            addtosqlflag=0
        trained_model = train_model(i,threshold, symbol, addtosqlflag)

        # Store the trained models with appropriate names
        models.update(trained_model)
    return models


# In[16]:




def find_threshold(symbol,percentage):
    cursor = connection.cursor()
    tobeexecuted=f"SELECT Close FROM all_companies_data1.companies_data where Symbol='{symbol}';"
    cursor.execute(tobeexecuted)
#     cursor.execute("SELECT Date,Open,High,Low,Close,Volume FROM all_companies_data.companies_data where Symbol='TCS';")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Close"])
    df["Close"] = df["Close"].astype(float)
    avg=df["Close"].mean()
    threshold=(percentage/100)*avg
    return threshold


# In[12]:

connection = connect_to_database()

cursor = connection.cursor()
query = f"SELECT Symbol FROM all_companies_data1.parameters;"
cursor.execute(query)
symbols=[]
result = cursor.fetchall()
for symbol in result:
    symbols.append(symbol[0])


# In[13]:


# symbols=["TCS","HDFCBANK","KOTAKBANK","HINDUNILVR","INFY","ITC","SBIN","ADANIPORTS","COALINDIA","BHARTIARTL","BAJFINANCE"]


# In[14]:


all_trained_models={}
for symbol in symbols:
    print("\n\n\n",symbol,"\n\n\n")
    cursor = connection.cursor()

    # Execute the SELECT statement
    query = f"SELECT minweeks, maxweeks, threshold_percentage FROM all_companies_data1.parameters WHERE Symbol='{symbol}';"
    cursor.execute(query)

    result = cursor.fetchone()

    # Retrieve the values
    minweeks = result[0]
    maxweeks = result[1]
    threshold_percentage=result[2]

    try:
        threshold = find_threshold(symbol,threshold_percentage)
        all_trained_models[symbol]=train_loop(minweeks, maxweeks, threshold, symbol) 
    except Exception as e:
        print(f"An error occured: {e}\n")
     
    
# print(all_trained_models)
    for model, name_and_rmse in all_trained_models[symbol].items():
        print(f"{model}: {name_and_rmse}")
    print("\n-----------------------------------------------------------\n")
print("\n\n*********************************************************************\n\n")

joblib.dump(all_trained_models, 'all_trained_models.joblib')
