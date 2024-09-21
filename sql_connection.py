import mysql.connector

f=open("logfile.txt", "a")
f.write("\n")

def connect_to_database():
    f.write("Connecting to MySQL database.\n")
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='dimpu123',
            database='all_companies_data1'
        )
        return connection
    except mysql.connector.Error as error:
        print("Error connecting to MySQL database:", error)
        return None

# Call the connect_to_database function to establish the connection
connection = connect_to_database()
