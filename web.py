from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver import ActionChains
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
PATH_TO_DRIVER="C:\\Users\\CHETAN\\OneDrive\\Desktop\\Stock_ market\\chromedriver.exe"
import mysql.connector
from mysql.connector import Error
from selenium.webdriver.chrome.options import Options
def create_connection():
    db_user = 'root'
    db_password = 'dimpu123'
    db_host = 'localhost'
    db_name = 'all_companies_data1'
    try:
        connection = mysql.connector.connect(
                        user=db_user,
                        password=db_password,
                        host=db_host,
                        database=db_name
                    )
        print("Connected to MySQL database")
        return connection
    except Error as e:
        print("Error connecting to MySQL database:", e)
        return None
    
def scrape_data_for_companies(csv_file):
    """Scrape data for companies and add to CSV and MySQL table."""
    # Read company symbols from CSV file
    df_companies = pd.read_csv(csv_file)
    companies = df_companies['Company Name'].tolist()

    for company, symbol in zip(companies, df_companies['Symbol'].tolist()):
        print(f"Scraping data for {company}...")
        service = Service(executable_path=PATH_TO_DRIVER)
        # options = webdriver.ChromeOptions()
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.moneycontrol.com/stocks/histstock.php?ex=B&sc_id=CI29&mycomp=")
        driver.maximize_window()
        action = ActionChains(driver)
        # notification_no = driver.find_element(By.XPATH, "//button[@class='No thanks']")
        # notification_no.click()
        company_search = driver.find_element(By.NAME, "mycomp")
        nse_selection = driver.find_element(By.NAME, "ex")
        from_day = driver.find_element(By.XPATH, "//select[@name='frm_dy']")
        from_month = driver.find_element(By.XPATH, "//select[@name='frm_mth']")
        time.sleep(1)
        from_year = driver.find_element(By.XPATH, "//select[@name='frm_yr']")
        to_day = driver.find_element(By.XPATH, "//select[@name='to_dy']")
        to_month = driver.find_element(By.XPATH, "//select[@name='to_mth']")
        to_year = driver.find_element(By.XPATH, "//select[@name='to_yr']")
        go_button = driver.find_element(By.XPATH, "(//input[@type='image'])[1]")
        action.move_to_element(nse_selection).perform()
        nse_selected = driver.find_element(By.XPATH, "//option[@value='N']")
        nse_selected.click()
        
        company_search.clear()
        company_search.send_keys(company)
        webdriver.ActionChains(driver).click(company_search).perform()
        time.sleep(2)

        # Wait for the dropdown options to appear
        dropdown_options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='suglist']/li"))
        )

        # Find the matching option and select it
        option_selected = False
        for option in dropdown_options:
            if option.text.strip() == company:
                option.click()
                option_selected = True
                break

        # from_day selection
        action.move_to_element(from_day).perform()
        from_day_selected = driver.find_element(By.XPATH, "(//option[@value='03'])[1]")
        from_day_selected.click()

        # from_month selection
        action.move_to_element(from_month).perform()
        from_month_selected = driver.find_element(By.XPATH, "(//option[@value='07'])[2]")
        from_month_selected.click()

        # from_year selection
        action.move_to_element(from_year).perform()
        from_year_selected = driver.find_element(By.XPATH, "(//option[@value='2023'])[1]")
        from_year_selected.click()

        # to_day selection
        time.sleep(1)
        action.move_to_element(to_day).perform()
        to_day_selected = driver.find_element(By.XPATH, "(//option)[144]")
        to_day_selected.click()

        # to_month selection
        action.move_to_element(to_month).perform()
        to_month_selected = driver.find_element(By.XPATH, "(//option)[156]")
        to_month_selected.click()

        # to_year selection
        time.sleep(1)
        action.move_to_element(to_year).perform()
        to_year_selected = driver.find_element(By.XPATH, "(//option)[157]")
        to_year_selected.click()
        action.move_to_element(go_button).perform()
        go_button.click()

        # Scrape data for the current company
        df_company = scrape_table_data(driver, company, symbol)

        # Append data to existing CSV file
        with open('final_company.csv', 'a', newline='') as file:
            df_company.to_csv(file, index=False, header=False)
        driver.quit()

        # Append data to MySQL table
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = "INSERT INTO data(Symbol, Company, Date, Open, High, Low, Close, Volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                data = df_company.values.tolist()
                cursor.executemany(query, data)
                connection.commit()
                print("Data inserted into MySQL table")
            except Error as e:
                print("Error inserting data into MySQL table:", e)
            finally:
                cursor.close                
                connection.close()

    print("Data scraping completed for all companies.")
    
def scrape_table_data(driver, company, symbol):
    """Scrape table data for a company."""
    data = []

    # Extract table data
    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[@class='tblchart']")))
    rows = table.find_elements(By.XPATH, "//tr")
    if len(rows) >= 5:
        row = rows[4]
        cells = row.find_elements(By.XPATH, ".//td")
        row_data = [cell.text for cell in cells[:-2]]

        if os.path.exists('final_company.csv') and os.path.getsize('final_company.csv') > 0:
            existing_data = pd.read_csv('final_company.csv')
            if 'Symbol' in existing_data.columns and 'Date' in existing_data.columns:
                existing_symbols_dates = existing_data[['Symbol', 'Date']].values.tolist()
                if [symbol, row_data[0]] not in existing_symbols_dates:
                    data.append(row_data)
            else:
                data.append(row_data)
        else:
            data.append(row_data)

    df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df.insert(0, 'Symbol', symbol)
    df.insert(1, 'Company', company)
    df.dropna(inplace=True)

    return df


csv_file = "test_output.csv"
scrape_data_for_companies(csv_file)
