

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import download_image, generate_random_filename,date_format,check_and_remove_file
from upload_and_reference import upload_photo_to_ftp
import os
import time
from datetime import datetime
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,insert_csv_data,append_unique_records


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
driver = webdriver.Chrome(service=service, options=chrome_options)  # Replace with your WebDriver, e.g., FirefoxDriver if using Firefox
url = "https://press.roccofortehotels.com/"
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# Locate news containers
news_elements = driver.find_elements(By.CSS_SELECTOR, "div.post-info a.img-wrapper")

# Extract href links
news_links = [element.get_attribute("href") for element in news_elements]

news_data = []

# Ensure the directory for saving images exists
os.makedirs("roccofortehotels_images", exist_ok=True)

# Save the data to CSV
csv_file = "roccofortehotels_news_data.csv"

check_and_remove_file(csv_file)


# Visit each link and extract details
for link in news_links[:1]:
    driver.get(link)
    try:
        # Wait for the title element to be visible
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text
        
        # Extract the main image
        image_element = driver.find_element(By.CSS_SELECTOR, "img")
        image_url = image_element.get_attribute("src") if image_element else None

        # Generate random image filename
        image_file = generate_random_filename()
        image_local_path = f"downloaded_images/{image_file}"

        # Extract content
        js_code = """
            let contentElement = document.querySelector("div.entry-content");
            return contentElement ? contentElement.innerHTML.trim() : "Content not found";
        """
        content = driver.execute_script(js_code)

        # Extract date
        js_code = """
            let dateElement = document.querySelector("div.entry-date");
            return dateElement ? dateElement.textContent.trim() : "Date not found";
        """
        date = driver.execute_script(js_code)

        print(date)

        if date.strip() == datetime.now().date():
            print(f"Scraped date is today ({date.strip()}). Exiting script.")
            break  # Exit the loop if the date is today's date

                # Download the image locally
        download_image(image_url, image_local_path)

        # Upload image to FTP
        upload_photo_to_ftp(image_local_path, "/public_html/storage/information/")

        # Create slug (a URL-friendly version of the title)
        # slug = title.lower().replace(" ", "-").replace(",", "").replace(".", "")

        time.sleep(20)

        # Generate current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        title = generate_title(title)

        # Store data for CSV
        news_data.append({
            "id": "1",  # You can populate this if needed
            "title": title,
            "subtitle":generate_subtitle(title),  # Add subtitle if available or leave empty
            "slug": title.replace(" ","-").lower(),
            "lead": "",  # Add lead if available or leave empty
            "content": generate_news(content),
            "image": "information/"+image_file,  # Use the image filename here
            "type": "news",  # You can customize this if needed
            "custom_field": "",  # Add custom fields if needed
            "parent_id": "",  # Add parent ID if needed
            "created_at": date_format(date),
            "updated_at": timestamp,
            "added_timestamp": date_format(date),
            "language": "en",  # Modify as needed
            "seo_title": "",
            "seo_content": "",
            "seo_title_desc": "",
            "seo_content_desc": "",
            "category_id": "100"  # Add category ID if available
        })
    except Exception as e:
        print(f"Error scraping {link}: {e}")

# Quit the driver
driver.quit()

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]



with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    for row in news_data:
        writer.writerow(row)

print(f"Data saved to {csv_file}")

if date_format(date) == datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
    insert_csv_data(csv_file,"informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("WE DO NOT HAVE DATA FOR TODAY")

