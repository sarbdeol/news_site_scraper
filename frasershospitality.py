#this is with new logic extract title date and then contnent of news and image
import shutil
import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from insert_csv_into_sql_db import generate_news,generate_title,generate_subtitle,date_format,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd

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

# Open the main page containing the news items
driver.get('https://www.frasershospitality.com/en/about-us/newsroom/')  # Replace with your actual page URL

# Wait for the page to load and for dynamic content to appear
time.sleep(5)  # Increase sleep time to allow dynamic content to load fully

# JS code to extract href links, date, title, and content of the news
js_code = """
    const newsItems = document.querySelectorAll('.newsroom-info');
    const newsData = [];

    newsItems.forEach(item => {
        const date = item.querySelector('.news-date') ? item.querySelector('.news-date').innerText : '';
        const title = item.querySelector('h3') ? item.querySelector('h3').innerText : '';
        const href = item.querySelector('a') ? item.querySelector('a').getAttribute('href') : '';
        
        newsData.push({date, title, href});
    });

    return newsData;
"""

# Execute JS to get the data
news_data = driver.execute_script(js_code)

# Define CSV headers
headers = [
    "id", "title", "subtitle","slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at","added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open CSV file for writing
# Open CSV file for writing
csv_file =  "frasershospitality_data.csv"


with open('frasershospitality_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the header row

    base_url = 'https://www.frasershospitality.com'

    # Manage the images folder
    image_folder = "frasershospitality_data_images"
    remote_folder = "/public_html/storage/information/"
    if os.path.exists(image_folder):
        print(f"Folder '{image_folder}' exists. Deleting and creating a new one...")
        shutil.rmtree(image_folder)  # Remove the folder and its contents
    os.makedirs(image_folder, exist_ok=True)  # Create a new folder
    # os.makedirs("frasershospitality_images", exist_ok=True)

    # Extract and process each news item
    for index, news in enumerate(news_data):
        # print(f"Processing: {news['title']}")

        # Check if the href is relative and update it to be absolute
        if news['href'].startswith('/'):
            news['href'] = base_url + news['href']
        
        try:
            # Now navigate to the "Read More" link to fetch the content
            driver.get(news['href'])

            # Wait for the news content to load
            time.sleep(5)  # Wait longer to ensure content loads

            # JS code to extract the image with class 'hide-on-mobile'
            image_js = """
                const image = document.querySelector('img.hide-on-mobile');
                return image ? image.getAttribute('src') : null;
            """
            image_url = driver.execute_script(image_js)

            if image_url:
                # Check if the image URL is absolute or relative and fix if necessary
                if image_url.startswith('/'):
                    image_url = base_url + image_url
                
                # Save image with the news title as the filename
                # image_name = f"{news['title'].replace(' ', '_').replace('/', '_')}.jpg"  # Image name based on article title
                image_name = f"{news['title'].replace(' ', '_').replace('/', '_')}.webp"  # Image name based on article title
                image_path = os.path.join('frasershospitality_data_images', image_name)
                image_path = image_path.replace(os.sep, '/')

                # Download the image
                img_data = requests.get(image_url).content
                with open(image_path, 'wb') as img_file:
                    img_file.write(img_data)

                # upload_photo_to_ftp(image_path,remote_folder)

                print(f"Image saved: {image_path}")
            else:
                image_path = 'No image available'

            # JS code to extract the first 5 paragraphs of the article
            paragraphs_js = """
                const paragraphs = document.querySelectorAll('.cmp-text p');
                const firstFiveParagraphs = [];

                for (let i = 0; i < 5 && i < paragraphs.length; i++) {
                    firstFiveParagraphs.push(paragraphs[i].innerText);
                }

                return firstFiveParagraphs.join('\\n');
            """

            first_five_paragraphs = driver.execute_script(paragraphs_js)

                    # Wait for the <p> element to be present
            wait = WebDriverWait(driver, 10)  # Timeout after 10 seconds
            element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "p")))

            js_code = """
return document.querySelector('.article-detail-info__publish-date p').innerText.trim();
"""

            news_date = driver.execute_script(js_code)

            print(news_date)

            if not first_five_paragraphs:
                first_five_paragraphs = 'No paragraphs available or failed to load.'

            # Prepare data for CSV (fill with dummy or actual values where needed)
            row = [
                index + 1,  # id
                generate_title(news['title']),  # title,
                generate_subtitle(news["title"]),
                news['title'].replace(" ","-").lower(),  # slug (or you can define another way to create slug)
                "",  # lead (Add actual lead text extraction logic if available)
                generate_news(first_five_paragraphs),  # content (first 5 paragraphs)
                "information/"+image_name,  # image path (local image file path or 'No image available')
                "news",  # type
                "",  # custom_field (dummy, or replace with actual data)
                0,  # parent_id (or add logic to get this info)
                date_format(news_date),  # created_at (add actual date handling logic if available)
                date.today(),
                date_format(news_date),  # updated_at (same as created_at in this case)
                "en",  # language
                "",  # seo_title (Add actual SEO title if available)
                "",  # seo_content (Add actual SEO content if available)
                "",  # seo_title_desc (Add SEO title description if available)
                "",  # seo_content_desc (Add SEO content description if available)
                "100"  # category_id (Add category logic if available)
            ]

            # Write the row to CSV
            writer.writerow(row)

            
            print(f"Data for {news['title']} stored in CSV.")

        except Exception as e:
            print(f"Error processing {news['title']}:{e}")

# Close the browser after processing
driver.quit()

# if os.path.exists(csv_file):
#     # Read the existing CSV to avoid duplicate records
#     existing_titles = set()
#     with open(csv_file, 'r', encoding='utf-8') as file:
#         reader = csv.reader(file)
#         next(reader)  # Skip header row
#         for row in reader:
#             existing_titles.add(row[1])  # Assuming 'title' is at index 1'
#             print(existing_titles.add(row[1]) )
# else:
#     existing_titles = set()

from insert_csv_into_sql_db import insert_csv_data

if date_format(time.time())==date_format(news_date):
    csv_file  = pd.read_csv(r"csv_file")
    csv_file  = csv_file.head(1)
    upload_photo_to_ftp(image_path,remote_folder)
    insert_csv_data(csv_file,'informations')
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")