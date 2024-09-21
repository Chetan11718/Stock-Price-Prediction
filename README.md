                                        Instructions

->Install mysql workbench
->Install chromedriver from the website according to your chrome version
    https://chromedriver.chromium.org/downloads

->First run 
pip install -r requirements.txt

->Then run 
python inserting_database.py

->Load the sql file into the database 
mysql -u root -p path/to/your/database.sql

-->First run training_code.py
python training_code.py

-->Once the training is done,run web.py to get the prediction of highest and lowest data for upcoming wweks     current day.
python web.py

-->Everyday run prediction file 
python prediction_code.py




