#this is with new logic extract title date and then contnent of news and image

import os
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import check_and_remove_file,generate_news,generate_title,generate_subtitle,insert_csv_data,append_unique_records
import shutil
from insert_csv_into_sql_db import date_format
import time
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

# Open the target URL
url = "https://www.amarahotels.com/press-room"  # Replace with your actual URL
driver.get(url)

# Wait until the page is fully loaded
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "node__content"))
    )
except Exception as e:
    print(f"Error waiting for elements: {e}")
    driver.quit()
    exit()

# JavaScript code to scrape the data
js_code = """
let extractedData = [];

document.querySelectorAll('.node__content').forEach(card => {
    let title = card.querySelector('.field--name-title a')?.textContent.trim() || 'No title';
    let dateText = card.querySelector('.field--name-field-image + div')?.textContent.trim() || 'No date';
    let imageUrl = card.querySelector('.field--name-field-image img')?.src || 'No image';
    
    extractedData.push({ title, date: dateText, image: imageUrl });
});

return extractedData;
"""

# Execute JavaScript to extract data
data = driver.execute_script(js_code)

# Debugging: Print extracted data
print("Extracted Data:", data)

# Close the driver after data extraction
driver.quit()

# Check if data is empty
if not data:
    print("No data extracted. Check the selectors or webpage structure.")
    exit()

# Prepare output folder for images
output_folder = "amarahotels_scraped_images"

if os.path.exists(output_folder):
    print(f"Folder '{output_folder}' exists. Deleting and creating a new one...")
    shutil.rmtree(output_folder)  # Remove the folder and its contents
os.makedirs(output_folder, exist_ok=True) 

# Prepare CSV file and headers
csv_file = "amarahotels_scraped_data.csv"
check_and_remove_file(csv_file)

headers = [
    "id", "title", "subtitle","slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# User-Agent to mimic a browser for image downloading
headers_for_requests = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# Save data to CSV and download images
with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    for idx, item in enumerate(data):
        title = generate_news(item.get("title", "No title"))
        date = date_format(item.get("date", "No date"))
        image_url = item.get("image", "No image")
        
        # Image download logic
        image_path = "No image"
        if image_url and image_url != "No image":
            try:
                # Handle relative image URLs
                if image_url.startswith("/"):
                    image_url = url + image_url  # Update the base URL
                
                # Send the request with headers for image download
                response = requests.get(image_url, headers=headers_for_requests, stream=True)
                if response.status_code == 200:
                    # Generate a unique filename for the image
                    image_name = f"image_{idx + 1}.jpg"
                    image_path = os.path.join(output_folder, image_name)
                    
                    # Save the image locally
                    with open(image_path, "wb") as img_file:
                        for chunk in response.iter_content(1024):
                            img_file.write(chunk)
                    print(f"Image saved: {image_path}")
                else:
                    print(f"Failed to download image: {image_url} (status code {response.status_code})")
            except Exception as e:
                print(f"Error downloading image {image_url}: {e}")

        # Write the data to CSV file, including all fields
        writer.writerow({
            "id": idx + 1,
            "title": generate_title(title),
            "subtitle":generate_subtitle(title),
            "slug":title.lower().replace(" ","-"),
            "lead":"",
            "content":generate_news(title),
            "image":image_path,
            "type":"news",
            "custom_field":"",
            "parent_id":"",
            "created_at":date,
            "updated_at":time.time(),
            "added_timestamp":date,
            "language":'EN',
            "seo_title":'',
            "seo_content":"",
            "seo_title_desc":"",
            "seo_title_desc":"",
            "category_id":100
        })

print(f"Data saved to {csv_file}. Images saved in the '{output_folder}' folder.")

# insert_into_db(csv_file)

if date_format(datetime.now().today())==date:

    insert_csv_data(csv_file,"informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")

