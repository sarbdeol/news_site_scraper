import mysql.connector
from mysql.connector import Error

try:
    # Use your credentials to establish a connection
    connection = mysql.connector.connect(
        host='hotelexplorer.net',           # Replace with your database host
        port=3306,                          # Default MySQL port
        user='aktywwwni_hotelexplorer_en',  # Your username
        password=')Jz4UR1Z-PsB-e@l',         # Your password
        database='aktywwwni_hotelexplorer_en'       # Replace with your database name
    )

    if connection.is_connected():
        print("Connected to MySQL database")

        # Example query to test the connection
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        print("Databases:", databases)

except Error as e:
    print("Error while connecting to MySQL:", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("MySQL connection is closed")