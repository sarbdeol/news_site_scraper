


import time
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,check_and_remove_file,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import download_image,date_format,insert_csv_data
from datetime import datetime


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

# Set up WebDriver with headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment for headless mode

# Prepare data to save in CSV
news_data = []

try:
    # Load the webpage
    driver.get("https://www.louvrehotels.com/en-us/news/")  # Replace with the actual URL
    time.sleep(2)  # Wait for the page to load

    # Execute JavaScript to click the "Accept All" button

    time.sleep(20)

    try:
        driver.execute_script("""
            document.getElementById('onetrust-accept-btn-handler').click();
        """)

    except:

        # Wait for the page to load fully after accepting the cookies
        time.sleep(20)

        # Execute JavaScript to extract the title
        title = driver.execute_script("""
            return document.querySelector(".ConfigurableMediaAndTextBlock-styled__Title-lhg__sc-8d273b9a-4").textContent;
        """)

        # Execute JavaScript to extract the date
        date = driver.execute_script("""
            return document.querySelector(".ConfigurableMediaAndTextBlock-styled__Tagline-lhg__sc-8d273b9a-5").textContent;
        """)

        # Execute JavaScript to extract the image URL
        image_url = driver.execute_script("""
            return document.querySelector("img.ConfigurableMediaAndTextBlock-styled__Image-lhg__sc-8d273b9a-18.cTASBf").src;
        """)

        # Execute JavaScript to extract the paragraph content
        paragraph_content = driver.execute_script("""
            return document.querySelector("div.ConfigurableMediaAndTextBlock-styled__Description-lhg__sc-8d273b9a-6.hUsutH p").textContent;
        """)


        title = generate_title(title).replace('"', '').replace("'", '')
        date = date_format(date)
        img_name = generate_random_filename()
        download_image(image_url,img_name)

        # upload_photo_to_ftp(img_name,"/public_html/storage/information/")


        # Gather data in the required format
        news_item = {
            "id": "1",  # You can adjust the ID as per your logic
            "title": title,
            "subtitle": generate_subtitle(title),  # Add if there is a subtitle
            "slug": title.lower().replace('"',"").replace(" ","-"),  # Add if there's a slug
            "lead": "",  # Add lead if applicable
            "content": generate_news(paragraph_content),
            "image": "information/"+img_name,
            "type": "",  # Add if type is present
            "custom_field": "",  # Add custom field if applicable
            "parent_id": "",  # Add if parent ID is available
            "created_at": date,
            "updated_at": datetime.now().today(),  # Add if updated_at is available
            "added_timestamp": date,  # Add timestamp if applicable
            "language": "en",  # You can adjust based on language
            "seo_title": "",  # Add SEO title if applicable
            "seo_content": "",  # Add SEO content if applicable
            "seo_title_desc": "",  # Add SEO title description if applicable
            "seo_content_desc": "",  # Add SEO content description if applicable
            "category_id":  100# Add category ID if applicable
        }

        # Append the data
        news_data.append(news_item)

        # Define CSV file path
        csv_file_path = "louvrehotl_news_data.csv"
        check_and_remove_file(csv_file_path)
        # Write data to CSV
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()  # Write headers
            writer.writerows(news_data)  # Write data rows

        print("Data saved to CSV successfully!")

        if date ==  date_format(datetime.now().today()):
            upload_photo_to_ftp(img_name,"/public_html/storage/information/")
            insert_csv_data(csv_file_path,'informations')
            append_unique_records(csv_file_path,"combined_news_data.csv")
        else:
            print("--------WE DO NOT HAVE DATA FOR TODAY--------")

finally:
    driver.quit()


