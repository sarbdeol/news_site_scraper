import mysql.connector
from mysql.connector import Error
import pandas as pd

# File path to the updated CSV
csv_file_path = "frasershospitality_news.csv"

try:
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host='hotelexplorer.net',           # Replace with your database host
        port=3306,                          # Default MySQL port
        user='aktywwwni_hotelexplorer_en',  # Your username
        password=')Jz4UR1Z-PsB-e@l',        # Your password
        database='aktywwwni_hotelexplorer_en'  # Replace with your database name
    )

    if connection.is_connected():
        print("Connected to MySQL database")

        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file_path)

        # Clean the data by replacing NaN with None (for SQL NULL)
        df = df.fillna(value="NA")

        # Ensure all rows have the required columns
        required_columns = ['title', 'image', 'content']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns: {required_columns}")

        # Create a cursor object
        cursor = connection.cursor()

        # Iterate through the DataFrame and insert rows into the table
        for index, row in df.iterrows():
            insert_query = """
                INSERT INTO pages (title, image, content) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    image = VALUES(image),
                    content = VALUES(content)
            """
            cursor.execute(insert_query, (row['title'], row['image'], row['content']))

        # Commit the transaction
        connection.commit()
        print("Data has been successfully inserted/updated.")

except Error as e:
    print("Error while connecting to MySQL:", e)

except ValueError as ve:
    print("Error in CSV data:", ve)

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("MySQL connection is closed.")
