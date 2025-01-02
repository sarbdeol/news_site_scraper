

import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

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
driver = webdriver.Chrome(service=service, options=chrome_options)  # Ensure chromedriver is installed and in PATH

# Define the target URL
url = "https://hotel.hardrock.com/news/"  # Replace with the actual URL of the news page
driver.get(url)

# Wait for the first 'href' to load and navigate to the URL
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.blogPostReadMoreLink')))
driver.execute_script("""
    var firstLink = document.querySelector('a.blogPostReadMoreLink').getAttribute('href');
    window.location.href = firstLink;
""")

# Wait for the new page to load completely
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.blogPostTitleHeader')))

# Extract title, date, and image from the opened page
try:
    # Wait for the image URL to load
    image_url = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img.blogPostImage'))).get_attribute("src")
    
    img_name = generate_random_filename()

    download_image(image_url,img_name)

    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Extract date
    date = date_format(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.blogPostDate'))).get_attribute("data-date-format"))
    print(date)
    # Extract title text
    title_text = driver.execute_script("""
        var title = document.querySelector('.blogPostTitleHeader').textContent;
        return title;
    """)

    title_text = generate_title(title_text)
    print(title_text)
    # Extract paragraph text (content)
    paragraph_text = driver.execute_script("""
        var paragraphs = document.querySelectorAll('.blogPostBody p');
        var paragraphText = Array.from(paragraphs).map(p => p.textContent).join(' ');
        return paragraphText;
    """)
    paragraph_text = generate_news(paragraph_text)
    # Create a row of data
    row = [
        "1",  # You can set a unique ID for each entry
        title_text,
        generate_subtitle(title_text),  # Subtitle (not available in the current data, you can leave it blank)
        title_text.lower().replace(" ","-"),  # Slug (not available in the current data, you can leave it blank)
        "",  # Lead (not available in the current data, you can leave it blank)
        paragraph_text,
        "information/"+img_name,
        "",  # Type (not available in the current data, you can leave it blank)
        "",  # Custom field (not available in the current data, you can leave it blank)
        "",  # Parent ID (not available in the current data, you can leave it blank)
        date,
        datetime.now().today(),  # Assuming updated_at is the same as created_at for now
        date,  # Added timestamp (not available in the current data, you can leave it blank)
        "en",  # Assuming English language for now
        "",  # SEO Title (not available in the current data, you can leave it blank)
        "",  # SEO Content (not available in the current data, you can leave it blank)
        "",  # SEO Title Description (not available in the current data, you can leave it blank)
        "",  # SEO Content Description (not available in the current data, you can leave it blank)
        100   # Category ID (not available in the current data, you can leave it blank)
    ]

    # Check if the file exists, and write the header only if the file is empty
    file_exists = False
    try:
        with open("extracted_data.csv", "r", newline="", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        pass

    # Write the header if the file doesn't exist yet
    if not file_exists:
        with open("extracted_data.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write header

    # Write the data to the CSV file
    with open("extracted_data.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row)  # Write the row data

    print("Data successfully written to CSV.")

except Exception as e:
    print(f"Error extracting data: {e}")

# Quit the browser
driver.quit()

if date==date_format(datetime.now().today()):
    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    # append_unique_records("extracted_data.csv","combined_news_data.csv")
    insert_csv_data("extracted_data.csv",'informations')
else:
    print("WE DO NOT HAVE DATA FOR TODAY")