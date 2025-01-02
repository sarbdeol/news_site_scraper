

import os
import csv
import requests
from selenium import webdriver
import time
from datetime import datetime
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# from PIL import Image
from io import BytesIO
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
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

# Navigate to the target website
driver.get("https://www.discoverasr.com/en/the-ascott-limited/newsroom")

# Wait for the page to load
time.sleep(5)

# Extract all news item links
news_links = driver.execute_script("""
    const items = document.querySelectorAll('.news-listing-item .news-image a');
    return Array.from(items).map(item => item.href);
""")

# Directory to save images
image_dir = "discoverasr_images"
os.makedirs(image_dir, exist_ok=True)

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Initialize a list to store the results
results = []

# Process each news link (adjust the range as needed)
if news_links:  # Limit to 5 links for this example
    link = news_links[0]
    driver.get(link)
    time.sleep(3)  # Adjust sleep as needed for page load

    # Extract title, date, content, and image
    data = driver.execute_script("""
        const title = document.querySelector('meta[property="og:title"]')?.content 
                      || document.querySelector('title')?.innerText;

        const date = document.querySelector('.cmp-article-content-block_publishdatetime')?.innerText;

        const content = Array.from(
            document.querySelectorAll('div#text-3d74b7f7bb.cmp-text p')
        ).slice(0, 5).map(p => p.innerHTML).join(" ");

        const imageElement = document.querySelector('div.cmp-image__image img');
        const image = imageElement ? imageElement.src : null;

        return { title, date, content, image };
    """)

    # Download the image if it exists
    image_path = None
    if data.get("image"):
        try:
            # Get the image name from the URL
            image_name = generate_random_filename() + ".jpg"
            image_path = os.path.join(image_dir, image_name)

            # Download and save the image locally
            img_data = requests.get(data["image"]).content
            with open(image_name, "wb") as img_file:
                img_file.write(img_data)
            
            # Upload to FTP
            # upload_photo_to_ftp(image_name, "/public_html/storage/information/")
        except Exception as e:
            print(f"Failed to download image: {e}")

    # Organize the data into the specified format
    title =  generate_title(data.get("title", ""))
    # title =  data.get("title", "")
    news_entry = {
        "id": 1,
        "title": title,
        "subtitle": generate_subtitle(title),
        "slug": title.replace(" ", "-").lower(),
        "lead": '',
        "content": generate_news(data.get("content", "")),
        "image": "information/" + image_name if image_path else "",  # FTP path
        "type": "news",
        "custom_field": "",
        "parent_id": None,
        "created_at": date_format(data.get("date", "")),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "added_timestamp": date_format(data.get("date", "")),
        "language": "en",
        "seo_title": '',
        "seo_content": '',
        "seo_title_desc": "",
        "seo_content_desc": "",
        "category_id": "100"
    }
    #pd.to_datetime(data['added_timestamp'], format='%d %b %Y').dt.strftime('%Y-%m-%d')

    # Append the entry to results
    results.append(news_entry)

# Quit the driver
driver.quit()

# Save the data to a CSV file
csv_filename = "discoverasr_news.csv"
check_and_remove_file(csv_filename)
with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(results)

print(f"Data saved to {csv_filename} and images saved to {image_dir}/")


if date_format(data.get("date", ""))==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    upload_photo_to_ftp(image_name, "/public_html/storage/information/")
    insert_csv_data(csv_filename, "informations")
    append_unique_records(csv_filename,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")

