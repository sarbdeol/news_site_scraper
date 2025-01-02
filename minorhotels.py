

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from insert_csv_into_sql_db import download_image,check_and_remove_file,insert_csv_data
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,append_unique_records
from insert_csv_into_sql_db import generate_random_filename,date_format
from upload_and_reference import upload_photo_to_ftp
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

wait = WebDriverWait(driver, 20)  # Increase the wait time

# Define the headers for the CSV
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

def scrape_news():
    try:
        # Navigate to the webpage
        driver.get("https://media.minorhotels.com/en-GLO/")  # Replace with the target URL

        # Wait for the news card to load
        card = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "c-card")))

        # Extract the title using JavaScript
        title = driver.execute_script(""" 
            return document.querySelector('h2.c-card__title a').textContent.trim();
        """)
        print("Title:", title)

        # Extract the date
        date_element = card.find_element(By.CSS_SELECTOR, "time.c-card__time")
        date = date_element.get_attribute("datetime")

        # Click the link to navigate to the article
        driver.execute_script('document.querySelector("h2.h5.c-card__title a").click();')

        # Extract the image URL
        image_url = driver.execute_script('return document.querySelector(".c-image-wrap .c-image__thumbnail").src;')
        print("Image URL:", image_url)

        img_name = generate_random_filename()

        download_image(image_url,img_name)
        # upload_photo_to_ftp(img_name,"/public_html/storage/information/")
        # Wait for the article content to load
        time.sleep(2)  # Added delay to ensure page content is loaded

        # Execute JavaScript to extract paragraph text as a single string
        paragraphs_text = driver.execute_script('''
            var paragraphs = document.getElementsByTagName('p');
            var result = '';
            for (var i = 0; i < paragraphs.length; i++) {
                result += paragraphs[i].innerText + '\\n';  // Adding newline for separation
            }
            return result;
        ''')

        # Print the content
        # print("Content:", paragraphs_text)

        title = generate_title(title)

        date  = date_format(date)

        print(date)

        # Prepare the data for CSV
        data = [
            "1",  # id, placeholder for example
            title,  # title
            generate_subtitle(title),  # subtitle, placeholder as the structure doesn't provide it
            title.lower().replace(" ","-"),  # slug, placeholder
            "",  # lead, placeholder
            generate_news(paragraphs_text),  # content
            "information/"+img_name,  # image URL
            "",  # type, placeholder (assuming it's an article)
            "",  # custom_field, placeholder
            "",  # parent_id, placeholder
            date,  # created_at
            datetime.now().today(),  # updated_at
            date,  # added_timestamp (current time in UNIX format)
            "en",  # language (hardcoded for now)
            "",  # seo_title, placeholder
            "",  # seo_content, placeholder
            "",  # seo_title_desc, placeholder
            "",  # seo_content_desc, placeholder
            100   # category_id, placeholder
        ]
        csv_file = 'minorhotels_scraped_data.csv'

        check_and_remove_file(csv_file)
        # Save data to CSV
        with open(csv_file,'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Write headers if the file is empty
                writer.writerow(headers)
            writer.writerow(data)

        print("Data saved to CSV.")

    except TimeoutException:
        print("Failed to load the page or locate elements.")
    finally:
        driver.quit()

    if date == date_format(datetime.now().today()):
        upload_photo_to_ftp(img_name,"/public_html/storage/information/")
        insert_csv_data(csv_file,"informations")
        append_unique_records(csv_file,"combined_news_data.csv")

    else:
        print("--------WE DO NOT HAVE DATA FOR TODAY--------")

# Execute the scraping function
scrape_news()
