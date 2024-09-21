import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os
import mysql.connector
from mysql.connector import Error
from sql_connection import connect_to_database
# from web import create_connection, scrape_data_for_companies
from preprocess_code import preprocess_data

f=open("logfile.txt", "a")
f.write("\n")

f1=open("prediction_file.txt", "a")
f1.write("\n")

csv_file = "test_output1.csv" 
#scrape_data_for_companies(csv_file)
f.write("Scraping new data for all companies.\n")



def predict(target, ipweeks, best_model, symbol):
    connection = connect_to_database()
    cursor = connection.cursor()
    tobeexecuted = f"SELECT Symbol, Date, Open, High, Low, Close, Volume FROM all_companies_data1.companies_data WHERE Symbol = '{symbol}';"
    cursor.execute(tobeexecuted)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Symbol", "Date", "Open", "Low", "Close", "High", "Volume"])
    df = preprocess_data(df, ipweeks, 0, 0)
    
    TwoWeeksAgo = df.iloc[-11:-10]
    TwoWeeksAgoDate = TwoWeeksAgo["Date"]
    
    OneWeeksAgo = df.iloc[-6:-5]
    OneWeeksAgoDate = OneWeeksAgo["Date"]

    newdate = pd.to_datetime(TwoWeeksAgoDate.iloc[0])  
    dfnew = df[df['Date'] >= newdate]
    dfnew = preprocess_data(dfnew, ipweeks, 1, 1)
    
    df = df.tail(1)
    
    dateprint = "For the date: " + df["Date"].iloc[0].strftime("%Y-%m-%d")
    if target=="HighestInNext1Week":
        print(dateprint)
    f1.write("\n\n\n" + dateprint + "\n")
    predictions = {}

    model = joblib.load(best_model)

    X_pred = df.drop(["Date", "Open", "Low", "Close", "High", "Symbol"], axis=1)
    if "High" in target:
        X_pred = X_pred.drop(columns=X_pred.filter(like='Low', axis=1).columns)
    if "Low" in target:
        X_pred = X_pred.drop(columns=X_pred.filter(like='High', axis=1).columns)
        
    f.write("Making predictions.\n")
    
    # Perform predictions using the loaded model
    predictions[target] = model.predict(X_pred)
    
    query = f"UPDATE all_companies_data1.companies_data SET {target}_P = {predictions[target][0]} WHERE Date = '{df['Date'].iloc[0].strftime('%Y-%m-%d')}' AND Symbol = '{df['Symbol'].iloc[0]}' AND {target}_P IS NULL;"
    cursor.execute(query)
    connection.commit()
    
    return predictions


connection = connect_to_database()

cursor = connection.cursor()
query = f"SELECT Symbol FROM all_companies_data1.parameters;"
cursor.execute(query)
symbols = []
result = cursor.fetchall()
for symbol in result:
    symbols.append(symbol[0])


all_trained_models = joblib.load('all_trained_models.joblib')

predictionstring = ""
f1.write("\n\n")
print("PREDICTIONS:\n\n")
for symbol in symbols:
    symbol_preds={}
    print("\n\n\n", symbol, "\n\n\n")
    predictionstring += f"\n\n{symbol}\n\n"
    targets = ["HighestInNext1Week", "HighestInNext2Weeks", "LowestInNext1Week", "LowestInNext2Weeks"]
    try:
        avg_rmse_dict={}
        filtered_dict = {}
        for key, value in all_trained_models[symbol].items():
            if symbol in key:
                filtered_dict[key] = value
        key_of_min_value = min(filtered_dict, key=lambda k: filtered_dict[k])
        filename_ipweeks = key_of_min_value.split("_")
        ipweeks = int(filename_ipweeks[-1])

        for target in targets:
            preds = predict(target, ipweeks, f"{symbol}_{target}_{ipweeks}.joblib", symbol)
            for key, value in preds.items():
                symbol_preds[key]=value[0]
                """
                predictionstring += f"{key}: {value[0]}\n"
                f1.write(predictionstring)
                print(f"{key}: {value[0]}")
                print()
                """
        if symbol_preds["HighestInNext2Weeks"]<symbol_preds["HighestInNext1Week"]:
            symbol_preds["HighestInNext2Weeks"]=symbol_preds["HighestInNext1Week"]

        if symbol_preds["LowestInNext2Weeks"]>symbol_preds["LowestInNext1Week"]:
            symbol_preds["LowestInNext2Weeks"]=symbol_preds["LowestInNext1Week"]

        if (symbol_preds["LowestInNext1Week"]>symbol_preds["HighestInNext1Week"]) or (symbol_preds["LowestInNext1Week"]>symbol_preds["HighestInNext2Weeks"]) or (symbol_preds["LowestInNext2Weeks"]>symbol_preds["HighestInNext1Week"]) or (symbol_preds["LowestInNext2Weeks"]>symbol_preds["HighestInNext2Weeks"]):
            symbol_preds["LowestInNext1Week"]=symbol_preds["HighestInNext1Week"]
            symbol_preds["LowestInNext2Weeks"]=symbol_preds["HighestInNext1Week"]


        for key, value in symbol_preds.items():
            predictionstring += f"{key}: {value: .2f}\n"
            f1.write(predictionstring)
            print(f"{key}: {value: .2f}")

                   
    except mysql.connector.Error as e:
        print(f"An error occurred: {e}\n")
            
    print("\n-----------------------------------------------------------\n")
print("\n\n*********************************************************************\n\n")



