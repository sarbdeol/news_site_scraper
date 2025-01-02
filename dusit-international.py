

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage (optional, improves performance)
chrome_options.add_argument("--no-sandbox")  # Recommended for headless mode in some environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues
chrome_options.add_argument("--window-size=1920,1080")  # Set the window size for screenshots

# Specify the path to your ChromeDriver executable
chromedriver_path = "/usr/local/bin/chromedriver"  # Replace with the actual path to ChromeDriver

# Set up the WebDriver with Chrome options
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open the target webpage
driver.get('https://www.dusit-international.com/en/updates/press-releases')

# Wait for the page to load
time.sleep(5)

# # Find all <a> tags with the class 'card card--news-horizontal'
# cards = driver.find_elements(By.CLASS_NAME, 'card--news-horizontal')

# # Extract hrefs from the <a> tags
# hrefs = [card.get_attribute('href') for card in cards if card.get_attribute('href')]

# # Execute JavaScript to get the href attribute from the <a> tag
# js_code = """
# var card = document.querySelector('.card.card--news-horizontal');
# return card ? card.href : null;
# """

# # Execute the script to get the href value
# hrefs = driver.execute_script(js_code)

# # Print the hrefs
# print("Extracted hrefs from cards:")
# for href in hrefs:
#     print(href)

 # Wait for the presence of the <a> element with class 'card--news-horizontal'
# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.card.card--news-horizontal')))


# JavaScript to extract date
js_date = """
var card = document.querySelector('.card.card--news-horizontal');
return card ? card.querySelector('.card__date').textContent.trim() : 'Date not found';
"""
date = driver.execute_script(js_date)
print(f"Date: {date}")

# JavaScript to extract title
js_title = """
var card = document.querySelector('.card.card--news-horizontal');
return card ? card.querySelector('.card__title').textContent.trim() : 'Title not found';
"""
title = driver.execute_script(js_title)
print(f"Title: {title}")

# JavaScript to extract href
js_href = """
var card = document.querySelector('.card.card--news-horizontal');
return card ? card.href : 'URL not found';
"""
href = driver.execute_script(js_href)
print(f"URL: {href}")


csv_file = 'output.csv'
# Open a CSV file to store the extracted data
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    # Open each href in the same browser tab one after another
    # for href in hrefs[:1]:
    if href:
        driver.get(href)
        time.sleep(5)  # Wait for 5 seconds to view the page

        # Initialize data row
        data_row = {key: '' for key in headers}
        data_row['id'] = 1

        # Find and extract the date from the specified div
        try:
            date_element = driver.find_element(By.CLASS_NAME, 'media-detail__date')
            date_text = date_element.find_element(By.TAG_NAME, 'time').text
            # data_row['created_at'] = date_text
            date_text= date_format(date_text)
            print(date_text)
        except Exception as e:
            print(f"Error extracting date: {e}")

        # Find and extract the title from the specified div
        try:
            title_element = driver.find_element(By.CLASS_NAME, 'media-detail__title')
            title_text = title_element.find_element(By.TAG_NAME, 'h1').text
            data_row['title'] = generate_title(title_text)
        except Exception as e:
            print(f"Error extracting title: {e}")

        img_name = generate_random_filename()
        data_row['subtitle'] = generate_subtitle(title_text)
        data_row['slug'] = title_text.lower().replace(" ","-")
        data_row['lead'] = ""
        # Find and extract the image and paragraphs from the specified div
        try:

            # Extract all paragraphs
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            all_text = " ".join([p.text for p in paragraphs])
            data_row['content'] = generate_news(all_text)

            body_element = driver.find_element(By.CLASS_NAME, 'media-detail__body')

            # Extract the image source
            image_element = body_element.find_element(By.TAG_NAME, 'img')
            image_src = image_element.get_attribute('src')
            data_row['image'] = 'information/'+img_name
            download_image(image_src,img_name)
            # upload_photo_to_ftp(img_name,"/public_html/storage/information/")

            data_row['type']=""
            data_row['custom_field']=""
            data_row['parent_id']=""
            data_row['created_at']=date_text
            data_row['updated_at']=datetime.now().today()
            data_row['added_timestamp']=date_text
            data_row['language']="en"
            data_row['seo_title']=""
            data_row['seo_content']=""
            data_row['seo_title_desc']=""
            data_row['seo_content_desc']=""
            data_row['category_id']=100

        except Exception as e:
            print(f"Error extracting body content: {e}")

        # Write data to the CSV file
        writer.writerow(data_row)

# Optional: Close the browser after interaction
driver.quit()

if date_text == date_format(datetime.now().today()):
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    append_unique_records(csv_file,"combined_news_data.csv")
    insert_csv_data(csv_file,"informations")
else:
    print("WE DO NOT HAVE DATA FOR TODAY")