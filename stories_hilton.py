

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,check_and_remove_file,download_image
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,insert_csv_data,append_unique_records
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

# CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Placeholder for data rows
data_rows = []

try:
    # Load the page
    driver.get("https://stories.hilton.com/releases")  # Replace with the actual URL
    
    # Wait for the page to load (adjust as necessary for your use case)
    time.sleep(5)
    
    # Locate the most recent card
    card = driver.find_element(By.CLASS_NAME, "card-grid-item__title-contain")
    
    # Extract the details
    latest_href = card.find_element(By.CSS_SELECTOR, "a.card-grid-item__title-link").get_attribute("href")
    latest_title = card.find_element(By.CSS_SELECTOR, "h2.card-grid-item__title").text
    latest_date = card.find_element(By.CSS_SELECTOR, "time.card-grid-item__date").get_attribute("datetime")
    
    print(f"Latest href: {latest_href}")
    print(f"Title: {latest_title}")
    print(f"Date: {latest_date}")
    
    # Navigate to the latest link
    driver.get(latest_href)
    
    # Extract title and other details from the loaded page
    time.sleep(3)  # Wait for the new page to load
    page_title = driver.title
    print(f"Page Title: {page_title}")

    # Execute the JavaScript in Selenium
    all_text = driver.execute_script("""
        const paragraphs = Array.from(document.querySelectorAll('p'));
        return paragraphs.map(p => p.innerText).join('\\n\\n');
    """)
    print(all_text)

    # (Optional) Extract other elements like images

    js_script = """
// Select the image element by its class or any other attribute
const imageElement = document.querySelector('.article-hero__image');

// Extract the `src` attribute for the main image
const mainImageUrl = imageElement.getAttribute('src');

// Alternatively, extract the `srcset` attribute if you want all sizes
const srcset = imageElement.getAttribute('srcset');

// Log the values
console.log('Main Image URL:', mainImageUrl);
console.log('Srcset:', srcset);

return mainImageUrl


"""
    # try:
    #     image_element = driver.find_element(By.TAG_NAME, "img")
    #     image_url = image_element.get_attribute("src")
    #     print(f"Image URL: {image_url}")
    # except Exception as e:
    #     print("No image found:", e)
    #     image_url = None
    img_name = generate_random_filename()

    img_url = driver.execute_script(js_script)

    download_image(img_url,img_name)

    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    latest_title= generate_title(latest_title)
    date = date_format(latest_date)

    # Prepare a row for the CSV
    row = {
        "id": "1",  # Assuming static ID or generated elsewhere
        "title": latest_title,
        "subtitle": generate_subtitle(latest_title),  # Adjust as needed
        "slug": latest_title.lower().replace(" ","-"),
        "lead": "",  # Adjust as needed
        "content": generate_news(all_text),
        "image": "information/"+img_name,
        "type": "news",  # Example type
        "custom_field": None,
        "parent_id": None,
        "created_at": date,
        "updated_at": datetime.now().today(),
        "added_timestamp": date,
        "language": "en",  # Assuming English
        "seo_title": '',
        "seo_content": None,  # Adjust as needed
        "seo_title_desc": None,
        "seo_content_desc": None,
        "category_id": 100
    }
    data_rows.append(row)

finally:
    # Close the browser
    driver.quit()

# Save the data to a CSV file
csv_file = "stories_hilton.csv"
check_and_remove_file(csv_file)
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data_rows)

print(f"Data saved to {csv_file}")

# append_unique_records(csv_file,"combined_news_data.csv")

if date==date_format(datetime.now().today()):
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    append_unique_records(csv_file,"combined_news_data.csv")
    insert_csv_data(csv_file,"informations")
else:
     print("WE DO NOT HAVE DATA FOR TODAY")