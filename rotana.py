
import csv
import time
import os
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from insert_csv_into_sql_db import generate_random_filename
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import date_format,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime
from selenium.webdriver.chrome.options import Options
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


# Initialize WebDriver (make sure the driver is in your PATH)
# driver = webdriver.Chrome()

# CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Directory to save images
# image_dir = "rotana_images"
# os.makedirs(image_dir, exist_ok=True)
csv_file_name = "rotana_news_data.csv"
# Open the CSV file to write the extracted data
with open(csv_file_name, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    try:
        # Open the target webpage
        driver.get("https://www.rotana.com/newsroom")
        
        # Wait for the page to load completely
        time.sleep(2)
        
        # Execute JavaScript to extract title, href, and date
        news_data = driver.execute_script("""
            return Array.from(document.querySelectorAll('div[style*="padding:8px;"]')).map(news => {
                const titleElement = news.querySelector('.BrandTitling a');
                const href = titleElement ? titleElement.href : null;
                const title = titleElement ? titleElement.textContent.trim() : null;
                const dateElement = news.querySelector('.PageSmall'); // Assuming date is in this class
                const date = dateElement ? dateElement.textContent.trim() : null;
                
                return { title, href, date };
            });
        """)

        # Loop through the news_data and extract further details
        # for item in news_data:
            # Navigate to the article page
        driver.get(news_data[0]['href'])

        title  = news_data[0]['title']

        # Execute the JavaScript to extract the date
        date_text = driver.execute_script("""
            const dateElement = document.querySelector('td.PageText');
            const dateText = dateElement ? dateElement.textContent.trim() : null;
            return dateText ? dateText.replace('Published: ', '').trim() : null;
        """)

        print(date_text)

        # Extract all paragraphs
        all_paragraphs = driver.execute_script("""
            const paragraphs = Array.from(document.querySelectorAll('p'));
            return paragraphs.map(p => p.textContent.trim()).join('\\n');
        """)

        # Extract image URL
        image_url = driver.execute_script("""
            const img = document.querySelector('p img');
            return img ? img.src : null;
        """)


        image_name =  generate_random_filename()
        # Download the image and resize it
        if image_url:
            try:
                img_data = requests.get(image_url).content
                with open(image_name, 'wb') as img_file:
                    img_file.write(img_data)
                # response = requests.get(image_url,headers)
                # img = Image.open(BytesIO(response.content))
                # img = img.resize((865, 590))  # Resize the image to 865x590
                # image_name = image_name+".jpg"  # Using the first 50 chars of the title for image name
                # img_path = os.path.join(image_dir, image_name)
                # img.save(image_name)  # Save the image locally
            except Exception as e:
                print(f"Error downloading or resizing image: {e}")
                image_name = None
        else:
            image_name = None
        
        upload_photo_to_ftp(image_name,"/public_html/storage/information/")
        
        title = generate_title(title)
        # Write the extracted data to the CSV file
        writer.writerow([1, title,
                          generate_subtitle(title),
                            title.replace(" ","-").lower(),
                              None, generate_news(all_paragraphs), 
                              "information/"+image_name, None,
                            None, None,date_format(date_text), 
                            time.strftime("%Y-%m-%d %H:%M:%S"), 
                            date_format(date_text),None, None, None,None,None, 100])

        # Optionally, print the extracted data for debugging
        print(f"Title: {title}")
        print(f"Date: {date_text}")
        print(f"Image saved at: {image_name}\n")

    finally:
        # Close the browser
        driver.quit()

if date_format(date_text)==date_format(datetime.now().today()):
    append_unique_records("news_data.csv","combined_news_data.csv")
    insert_csv_data(csv_file_name,"informations")

else:
    print("SKIPPING")


