#-----------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from upload_and_reference import upload_photo_to_ftp
import time
import csv
import os
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
from insert_csv_into_sql_db import date_format,check_and_remove_file, generate_news, generate_subtitle, generate_title,insert_csv_data,generate_random_filename,append_unique_records

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disabling sandbox for headless mode
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the website
driver.get('https://news.groupbanyan.com/')
time.sleep(3)  # Wait for the page to load

# JavaScript to click on the article link
script = """
    var recentNewsLink = document.querySelector('div.article-section__text-holder h1 a');
    recentNewsLink.click();
"""

# Execute the JavaScript to click on the article
driver.execute_script(script)

# Wait for the article to load
time.sleep(3)

# JavaScript to extract article data
script = """
// Initialize an object to store the extracted data
var articleData = {};

// Extract the date
var dateElement = document.querySelector('time[datetime]');
articleData.date = dateElement ? dateElement.textContent.trim() : 'Date not found';

// Extract the title
var titleElement = document.querySelector('h1');
articleData.title = titleElement ? titleElement.textContent.trim() : 'Title not found';

// Extract the content (first paragraph and additional text)
var contentElement = document.querySelectorAll('.article-block__p p');
articleData.content = [];
contentElement.forEach(function (p) {
    articleData.content.push(p.textContent.trim());
});

// Extract the images (src of img elements)
var images = document.querySelectorAll('img.c-image__thumbnail');
articleData.images = [];
images.forEach(function (img) {
    articleData.images.push(img.src);
});

// Output the extracted data
return articleData;
"""

# Execute the script and get the extracted data
article_data = driver.execute_script(script)
print(article_data)

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
    "title": generate_title(article_data['title']),  # Use the extracted title
    "subtitle": generate_subtitle(article_data['title']),  # You can add subtitle if needed
    "slug": generate_title(article_data['title']).replace(" ","-").lower(),  # Example slug
    "lead": "",
    "content": generate_news(" ".join(article_data['content'])),
    "image": "information/"+ article_data['images'][0] if article_data['images'] else "",  # Only the first image URL
    "type": "news",  # Example type
    "custom_field": "N/A",  # Example custom field
    "parent_id": "0",  # Example parent_id
    "created_at": date_format(article_data['date'].split(',')[0]),  # Using the extracted date
    "updated_at": datetime.now().date(),  # Assuming updated_at is the same as created_at
    "added_timestamp": date_format(article_data['date'].split(',')[0]),  # Example timestamp, should be dynamic if needed
    "language": "en",  # Example language
    "seo_title": "",  # Example SEO title
    "seo_content": "",  # Example SEO content
    "seo_title_desc": "",  # Example SEO title description
    "seo_content_desc": "",  # Example SEO content description
    "category_id": "100"  # Example category ID
}

# Function to download and resize images
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
            image_name = generate_random_filename()
            image_path = os.path.join(folder, image_name)

            # upload_photo_to_ftp(image_name, "/public_html/storage/information/")

            # Save the resized image
            img.save(image_name)
            return image_name  # Return the local path of the image
        else:
            print(f"Failed to download image: {url}")
            return None
    except Exception as e:
        print(f"Error downloading or resizing image: {e}")
        return None

# Create a folder to store images
images_folder = "groupbanyan_images"
os.makedirs(images_folder, exist_ok=True)

# Ensure only the first image is downloaded
image_filenames = []    
if article_data['images']:
    # Download and process only the first image
    first_image_url = article_data['images'][0]
    image_filename = download_and_resize_image(first_image_url, images_folder)
    if image_filename:
        image_filenames.append(image_filename)

upload_photo_to_ftp(image_filename, "/public_html/storage/information/")

# Update the CSV data with the local image filename(s)
csv_data["image"] = "information/"+ image_filename

# Create CSV file and write the data
csv_file_path = "groupbanyan_data.csv"
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

# Close the browser after extracting the data
driver.quit()

if date_format(article_data['date'])==date_format(datetime.now().date()):
    print("Exeuction ended no new data")
    insert_csv_data(csv_file_path,"informations")
    append_unique_records(csv_file_path,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")