import pandas as pd
df=pd.read_csv("final_company.csv")

import mysql.connector
from sqlalchemy import create_engine

db_user = 'root'
db_password = 'dimpu123'
db_host = 'localhost'
db_name = 'all_companies_data1'
connection = mysql.connector.connect(
    user=db_user,
    password=db_password,
    host=db_host,
    database=db_name
)

if connection.is_connected():
    print("Connected to MySQL database")

engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')
table_name = 'companies_data'
df.to_sql(table_name, con=engine, if_exists='append', index=False)

engine.dispose()
connection.close()