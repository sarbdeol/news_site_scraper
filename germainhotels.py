



import csv
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from insert_csv_into_sql_db import date_format
from datetime import datetime
from insert_csv_into_sql_db import generate_news, generate_subtitle, generate_title, insert_csv_data,append_unique_records
from selenium.webdriver.chrome.options import Options
from upload_and_reference import upload_photo_to_ftp

from insert_csv_into_sql_db import date_format,download_image

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
driver.get('https://www.germainhotels.com/en/about/mediaroom')

# Wait for the page to load
time.sleep(3)

# Create image folder if not exists
image_folder = "germainhotels_images"
os.makedirs(image_folder, exist_ok=True)

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Define CSV output file
output_file = "germainhotels_data.csv"

# Define function to write rows
def write_row_to_csv(writer, row_data):
    writer.writerow(row_data)

# Open the CSV for writing
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)  # Write headers

    rows = driver.find_elements(By.CSS_SELECTOR, 'tr[role="link"]')
    for idx, row in enumerate(rows, start=1):
        try:
            # Extract data
            title = row.find_element(By.CSS_SELECTOR, 'td.css-stz03g').text
            date = row.find_element(By.CSS_SELECTOR, 'span.css-tlj14j').text
            location = row.find_element(By.CSS_SELECTOR, 'td.css-ruc5cq').text

            # Click Details link
            row.find_element(By.CSS_SELECTOR, 'td.css-uknx5e').click()
            time.sleep(3)

            # Get image URL
            image_url = driver.execute_script("""
                var img = document.querySelector('figure img');
                return img ? img.src : null;
            """)
            image_path = None
            if image_url:
                image_name = f"{idx}.jpg"
                image_path = os.path.join(image_folder, image_name)
                img_data = requests.get(image_url).content
                with open(image_path, "wb") as img_file:
                    img_file.write(img_data)
                upload_photo_to_ftp(image_name, "/public_html/storage/information/")

            # Get page content
            content = driver.execute_script("""
                return Array.from(document.querySelectorAll('p'))
                           .map(p => p.innerText)
                           .join(' ');
            """)

            # Generate data
            formatted_date = date_format(date)
            title = generate_title(title)
            row_data = [
                idx, title, generate_subtitle(title), title.replace(" ", "-"), "",
                generate_news(content), f"information/{os.path.basename(image_path)}" if image_path else "",
                "", "", "", formatted_date, datetime.now().date(), formatted_date, "en", '', '', '', '', '100'
            ]

            # Write to CSV
            write_row_to_csv(writer, row_data)

            # Go back to the main page
            driver.back()
            time.sleep(3)

        except Exception as e:
            print(f"Error processing row {idx}: {e}")

# Close the driver and insert data
driver.quit()
if date_format(date) == date_format(datetime.now().today()):
    insert_csv_data(output_file, 'informations')
    append_unique_records(output_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")



# print(f"Data saved to {output_file}. Images saved in {image_folder}.")
