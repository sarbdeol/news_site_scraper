# from selenium import webdriver
# driver = webdriver.Chrome()
# driver.get("https://www.panpacific.com/en/newsroom.html#/latest_news")
# print(driver.title)
# driver.quit()

import mysql
import mysql.connector


# Establish a connection to the MySQL database
connection = mysql.connector.connect(
host='hotelexplorer.net',           # Replace with your database host
port=3306,                          # Default MySQL port
user='aktywwwni_hotelexplorer_en',  # Your username
password=')Jz4UR1Z-PsB-e@l',        # Your password
database='aktywwwni_hotelexplorer_en')  # Replace with your database name


if connection.is_connected():
    print("Connected to MySQL database")