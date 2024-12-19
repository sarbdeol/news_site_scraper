import mysql.connector
from mysql.connector import Error
import pandas as pd
import csv
import mysql.connector
from mysql.connector import Error
import string
import random
import pytz
from datetime import datetime
import csv
import os



auth = ""


def insert_into_db(csv_file_path):
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

#insert_into_db(csv_file_path)


import os

def check_and_remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' has been removed.")
    else:
        print(f"File '{file_path}' does not exist.")

# Example usage:
# check_and_remove_file("example.txt")

import requests
import json

def generate_news(short_sentence):
    # OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Payload for the API request
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a new writter engaging and well-researched news articles."
            },
            {
                "role": "user",
                "content": f"Rewrite following news in HTML paragramph fomrat upto 25 lines and remove html keyword and ''''''' : {short_sentence}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    })

    # API headers
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': '',  # Replace with your actual API key
        'Authorization': auth,  # Replace with your actual API key
    }

    # Making the request to OpenAI API
    response = requests.post(url, headers=headers, data=payload)
    
    # Parsing and returning the response
    if response.status_code == 200:
        news_content = response.json().get("choices")[0].get("message").get("content")
        # print("Generated News Article:\n")
        # print(news_content)
        return news_content
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    

def generate_subtitle(short_sentence):
    # OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Payload for the API request
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a new writter engaging and well-researched news articles."
            },
            {
                "role": "user",
                "content": f"Rewrite following title as subtitle upto 3 sentences in HTML paragraph format which should not be matched with given short sentences.Then remove HTML keyword and ''' : {short_sentence}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    })

    # API headers
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': '',  # Replace with your actual API key
        'Authorization': '',  # Replace with your actual API key
    }

    # Making the request to OpenAI API
    response = requests.post(url, headers=headers, data=payload)
    
    # Parsing and returning the response
    if response.status_code == 200:
        news_content = response.json().get("choices")[0].get("message").get("content")
        # print("Generated News Article:\n")
        # print(news_content)
        return news_content
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Example Usage
short_sentence = "A new park has opened in downtown with eco-friendly facilities."
# generate_news(short_sentence)

def generate_title(short_sentence):
    # OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Payload for the API request
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a new writter engaging and well-researched news articles."
            },
            {
                "role": "user",
                "content": f"Rewrite title in keep similar meaning but word should be more impactfully in one line: {short_sentence}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    })

    # API headers
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': '',  # Replace with your actual API key
        'Authorization': auth,  # Replace with your actual API key
    }

    # Making the request to OpenAI API
    response = requests.post(url, headers=headers, data=payload)
    
    # Parsing and returning the response
    if response.status_code == 200:
        news_content = response.json().get("choices")[0].get("message").get("content")
        # print("Generated News Article:\n")
        # print(news_content)
        return news_content
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


#_______________________________________________________



import csv
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Default values for columns that can be empty in the CSV but should have a default
default_values = {
    "image_credit": None,
    "category_id": 0,
    "views": None,
    "active": 1,
    "active_from": "0001-01-01",
    "active_to": "9999-01-01",
    "slug": "",  # Empty string for slug if not provided
    "content": "",  # Empty string for content if not provided
    "created_at": None,  # Will use current timestamp if not provided
    "updated_at": None,  # Will use current timestamp if not provided
}

# def format_date(date_str):
#     """
#     Formats the given date string into the desired 'YYYY-MM-DD HH:MM:SS' format.
    
#     :param date_str: The input date string.
#     :return: Formatted date string in 'YYYY-MM-DD HH:MM:SS' format.
#     """
#     try:
#         # If the date is already in the correct format (e.g., '2021-08-09 10:26:49')
#         return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
#     except ValueError:
#         # If the date is not in the correct format, return the current timestamp
#         return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def convert_to_unix_timestamp(date_str):
    """
    Converts a date string to Unix timestamp (seconds since epoch).
    
    :param date_str: The input date string.
    :return: Unix timestamp.
    """
    try:
        date_object = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return int(date_object.timestamp())  # Convert to Unix time
    except ValueError:
        # If the date is invalid, return the current Unix timestamp
        return int(datetime.now().timestamp())

def get_max_id_from_db(cursor, table_name):
    """
    Get the maximum ID currently in the database for the specified table.
    
    :param cursor: MySQL cursor object.
    :param table_name: Name of the table to check.
    :return: Maximum ID value in the table.
    """
    cursor.execute(f"SELECT MAX(id) FROM {table_name}")
    result = cursor.fetchone()
    return result[0] if result[0] is not None else 0


def insert_csv_data(csv_file_path, table_name):
    """
    Inserts data from a CSV file into a specified database table.
    
    :param csv_file_path: Path to the CSV file
    :param table_name: Name of the table where data will be inserted
    """
    db_schema = [
        "id", "title","subtitle", "slug", "content", "image", "image_credit", 
        "category_id", "created_at", "updated_at", "added_timestamp", "language", 
        "views", "seo_title", "seo_content", "seo_title_desc", "seo_content_desc", 
        "active", "active_from", "active_to"
    ]
    
    # Read the CSV file and prepare data
    records = []
    try:
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Skip header row if detected (e.g., "id" matches column names)
                if row.get("id", "").lower() == "id":
                    print("Skipping header row")
                    continue
                
                data = {}
                for column in db_schema:
                    if column in row:
                        # Handle specific column logic
                        # if column == "title" and row.get("title"):
                        #     data["subtitle"] = row["title"]

                                                # Get today's date in the local timezone
                        # local_timezone = pytz.timezone("Europe/Berlin")  # Replace with your local time zone
                        # now_local = datetime.now(local_timezone)

                        if column in ["added_timestamp"] and row[column]:
                            data[column] = int(datetime.strptime(row[column], '%d %b %Y').timestamp())
                        else:
                            data[column] = row[column].strip() if row[column].strip() else default_values.get(column)
                        
                        # Convert `created_at` to Unix timestamp and assign it to `added_timestamp`
                        # if column == "created_at" and row[column]:
                        #     added_timestamp = convert_to_unix(row[column])
                        #     data["added_timestamp"] = added_timestamp
                        # elif column == "created_at" and not row[column]:
                        #     added_timestamp = convert_to_unix(row[column])
                        #     data["added_timestamp"] = added_timestamp
                    else:
                        data[column] = default_values.get(column)
                
                # Append the record if it's not the header
                records.append(data)
    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Connect to the database and insert the data
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            port=3306,
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        if connection.is_connected():
            cursor = connection.cursor()

            # Get the current max ID in the table for incremental ID
            max_id = get_max_id_from_db(cursor, table_name)

            # Prepare SQL query for insertion
            columns = ", ".join(db_schema)
            placeholders = ", ".join(["%s"] * len(db_schema))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # Prepare values to insert (incrementing IDs starting from max_id + 1)
            values = []
            for index, record in enumerate(records, start=max_id + 1):
                # if 'added_timestamp' not in record or record['added_timestamp'] is None:
                #     # record["added_timestamp"] = convert_to_unix(row[column])
                #     record["added_timestamp"] = int(datetime.strptime(row[column], '%d %B %Y').timestamp())
                record["id"] = index
                values.append(tuple(record[col] for col in db_schema))

            # Batch insert data
            cursor.executemany(sql, values)

            # Commit the transaction
            connection.commit()
            print(f"All records inserted successfully. Total records: {cursor.rowcount}")

    except Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error inserting data into database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")


# Example usage
csv_file_path = "frasershospitality_data.csv"
table_name = "informations"
db_config = {
    "host": "hotelexplorer.net",
    "user": "",
    "password": "",
    "database": "",
}

# Call the function
# insert_csv_data(csv_file_path, table_name)

# Function to save extracted data to CSV
def save_to_csv(data, idx, csv_file, headers):
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow({
            "id": idx,
            "title": data['title'],
            "subtitle": "",  # Empty, assuming no subtitle
            "slug": data['slug'],
            "lead": data['lead'],
            "content": data['content'],
            "image": data['image'],
            "type": data['type'],
            "custom_field": data['custom_field'],
            "parent_id": data['parent_id'],
            "created_at": data['created_at'],
            "updated_at": data['updated_at'],
            "added_timestamp": data['added_timestamp'],
            "language": data['language'],
            "seo_title": data['seo_title'],
            "seo_content": data['seo_content'],
            "seo_title_desc": data['seo_title_desc'],
            "seo_content_desc": data['seo_content_desc'],
            "category_id": data['category_id']
        })

# Function to generate a random filename for the image
def generate_random_filename(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length)) + '.jpg'


def date_format(date):
    # OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Payload for the API request
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a new writter engaging and well-researched news articles."
            },
            {
                "role": "user",
                "content": f"Give me given date into this format %d %b %Y: {date}. Do not include in text.I need clean date"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    })

    # API headers
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': '',  # Replace with your actual API key
        'Authorization': auth,  # Replace with your actual API key
    }

    # Making the request to OpenAI API
    response = requests.post(url, headers=headers, data=payload)
    
    # Parsing and returning the response
    if response.status_code == 200:
        news_content = response.json().get("choices")[0].get("message").get("content")
        # print("Generated News Article:\n")
        # print(news_content)
        return news_content
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    

# date_format('October 17th, 2023')


import requests

def download_image(image_url, save_path):
    """
    Downloads an image from the given URL and saves it to the specified path.

    :param image_url: str - The URL of the image to download.
    :param save_path: str - The local file path to save the image (e.g., 'image.jpg').
    :return: None
    """
    try:
        # Send a GET request to the image URL
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an error for bad HTTP response

        # Write the image content to a file
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image successfully downloaded: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image: {e}")




def check_today_news_date_eqaul(date):
    # OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Payload for the API request
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a new writter engaging and well-researched news articles."
            },
            {
                "role": "user",
                "content": f"Please check given {date} is today's date or not.Give me respond in either true or false"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    })

    # API headers
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': '',  # Replace with your actual API key
        'Authorization': auth,  # Replace with your actual API key
    }

    # Making the request to OpenAI API
    response = requests.post(url, headers=headers, data=payload)
    
    # Parsing and returning the response
    if response.status_code == 200:
        news_content = response.json().get("choices")[0].get("message").get("content")
        # print("Generated News Article:\n")
        print(news_content)
        return news_content
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    
# 
# check_today_news_date_eqaul('04-Dec-24')


import pandas as pd
import os

def append_unique_records(new_data_file, existing_data_file):
    # Load new data
    new_data = pd.read_csv(new_data_file)

    # Check if the existing file exists
    if os.path.exists(existing_data_file):
        # Load existing data
        existing_data = pd.read_csv(existing_data_file)

        # Combine data, ensuring only unique records are retained
        combined_data = pd.concat([existing_data, new_data]).drop_duplicates()
    else:
        # If the file doesn't exist, treat all new data as unique
        combined_data = new_data

    # Save back to the existing CSgit push -u origin mainV file
    combined_data.to_csv(existing_data_file, index=False)
    print(f"Updated {existing_data_file} with unique records.")

# File paths
new_data_file = "scraped_data.csv"  # Replace with your new data file
existing_data_file = "news_data.csv"  # Replace with your existing data file

# Call the function
# append_unique_records(new_data_file, existing_data_file)



