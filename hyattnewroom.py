

import csv
import time
import os
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from insert_csv_into_sql_db import generate_news,generate_subtitle,append_unique_records,generate_random_filename,generate_title,check_and_remove_file
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import insert_csv_data,date_format


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


# Function to download and resize the image
def download_and_resize_image(url, folder, width=865, height=590):
    try:
        # Get the image response
        response = requests.get(url)
        if response.status_code == 200:
            # Open the image using PIL
            img = Image.open(BytesIO(response.content))
            
            # Resize the image to the desired dimensions
            img = img.resize((width, height), Image.Resampling.LANCZOS)  # Corrected line
            
            # Extract image filename from the URL
            image_name = url.split("/")[-1]
            image_path = os.path.join(folder, image_name)

            # Save the resized image
            img.save(image_name)
            return image_name  # Return the local path of the image
        else:
            print(f"Failed to download image: {url}")
            return None
    except Exception as e:
        print(f"Error downloading or resizing image: {e}")
        return None

# # Set up Chrome options for headless mode (optional)
# chrome_options = Options()
# chrome_options.add_argument("--headless")

# Set up the WebDriver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the target webpage
url = "https://newsroom.hyatt.com"  # Replace with the actual URL of the page
driver.get(url)

# Give the page some time to load
time.sleep(2)

# Get the most recent href link (you may customize this based on your needs)
latest_link = driver.find_element(By.XPATH, "(//a[contains(@href, '2024-')])[1]").get_attribute("href")

# Open the link
driver.get(latest_link)
time.sleep(2)

# Extract the title, date, and news content using JavaScript executed via Selenium
title = driver.execute_script("return document.querySelector('h1').innerText")
date = driver.execute_script("return document.querySelector('.wd_date').innerText")
content = driver.execute_script("""
var paragraphs = document.querySelectorAll('div.wd_body.wd_news_body p');
var textContent = [];
for (var i = 0; i < paragraphs.length; i++) {
    textContent.push(paragraphs[i].innerText);
}
return textContent.join('\\n');  // Join the paragraph texts with line breaks
""")
image_url = driver.execute_script("""
var imgElement = document.querySelector('img');  // Modify the selector if needed
if (imgElement) {
    return imgElement.src;  // Return the image URL
} else {
    return 'Image not found';
}
""")

# Close the browser
driver.quit()

# Define the headers for the CSV file
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Prepare the data to be written to CSV
csv_data = {
    "id": "1",  # Example ID, should be dynamically generated if needed
    "title": generate_title(title),  # Use the extracted title
    "subtitle": generate_subtitle(title),  # You can add subtitle if needed
    "slug": generate_title(generate_title(title)).lower().replace(" ", "-"),  # Example slug (you can customize this)
    "lead": "",  # Use the first line of the content as lead
    "content": generate_news(content),
    "image": "",  # Placeholder for image URL or local path
    "type": "news",  # Example type
    "custom_field": "N/A",  # Example custom field
    "parent_id": "0",  # Example parent_id
    "created_at": datetime.strptime(date, '%b %d, %Y').strftime('%d %B %Y').lstrip('0'),  # Using the extracted date
    "updated_at": datetime.now().today(),  # Assuming updated_at is the same as created_at
    "added_timestamp": datetime.strptime(date, '%b %d, %Y').strftime('%d %B %Y').lstrip('0'),  # Example timestamp, should be dynamic if needed
    "language": "en",  # Example language
    "seo_title": "",  # Example SEO title
    "seo_content": "",  # Example SEO content
    "seo_title_desc": "",  # Example SEO title description
    "seo_content_desc": "",  # Example SEO content description
    "category_id": "100"  # Example category ID
}

# Create a folder to store images
images_folder = "hyatt_images"
os.makedirs(images_folder, exist_ok=True)

# Download and resize the image
image_filename = download_and_resize_image(image_url, images_folder)

# upload_photo_to_ftp(image_filename,"/public_html/storage/information/")
# If an image was successfully downloaded, update the image field in the CSV data
if image_filename:
    csv_data["image"] = f"information/{image_filename}"

# Create the CSV file and write the data
csv_file_path = "hyatt_newsroom.csv"

check_and_remove_file(csv_file_path)


# Check if the file exists
file_exists = os.path.isfile(csv_file_path)

# Open the CSV file in append mode (or create it if it doesn't exist)
with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    
    # If the file doesn't exist, write the header
    if not file_exists:
        writer.writeheader()
    
    # Write the extracted article data
    writer.writerow(csv_data)

print("CSV file has been created/updated with the extracted data.")




if date_format(date)==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    upload_photo_to_ftp(image_filename,"/public_html/storage/information/")
    insert_csv_data(csv_file_path,"informations")
    append_unique_records(csv_file_path,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")
