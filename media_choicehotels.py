




import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime

# Set up Chrome options for headless mode (optional)

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
driver.maximize_window()

# Open the target URL
driver.get("https://media.choicehotels.com/international-press-releases")  # Replace with the actual URL where the HTML content is located

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Extract date
js_code = """
let dateElement = document.querySelector('.wd_date');  // Select the .wd_date div
let date = dateElement ? dateElement.innerText : null;  // Get the text content (date)
return date;  // Return the extracted date
"""
date = date_format(driver.execute_script(js_code))

# Extract title
js_code = """
let titleElement = document.querySelector('.wd_title');  // Select the .wd_title div
let title = titleElement ? titleElement.innerText : null;  // Get the text content
return title;  // Return the extracted title
"""
title = generate_title(driver.execute_script(js_code))

time.sleep(10)

# Extract image URL
js_code = """
    let imageElement = document.querySelector('.wd_asset_gallery_container img');  // Select the first image
    let imageUrl = imageElement ? imageElement.src : null;  // Get the src of the image
    return imageUrl;  // Return the extracted image URL
    """

# Execute the JavaScript code to extract the image URL
image_url = driver.execute_script(js_code)

img_name = generate_random_filename()
download_image(image_url,img_name)
# upload_photo_to_ftp(img_name,"/public_html/storage/information/")

# Extract paragraphs text
js_code = """
let paragraphs = document.querySelectorAll('.wd_body p');  // Select all <p> tags inside .wd_body
let allText = Array.from(paragraphs).map(p => p.innerText).join(" ");  // Join all text into one string
return allText;  // Return the concatenated string
"""
all_paragraphs_text = generate_news(driver.execute_script(js_code))

# Prepare the data to be saved in CSV
data = [
    {
        "id": 1,  # Replace with dynamic ID if needed
        "title": title,
        "subtitle": generate_subtitle(title),  # No subtitle provided, keep empty
        "slug": title.lower().replace(" ", "-"),
        "lead": "",  # First 100 characters as lead
        "content": all_paragraphs_text,
        "image": "information"+img_name,
        "type": "",  # Assuming type is "press_release"
        "custom_field": "",
        "parent_id": "",
        "created_at": date,  # Use the extracted date as created_at
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "added_timestamp": date,
        "language": "en",
        "seo_title":"" ,
        "seo_content": "",
        "seo_title_desc": "",
        "seo_content_desc": "",
        "category_id": "100"  # Assuming category_id is "1"
    }
]

# Create a DataFrame
df = pd.DataFrame(data, columns=headers)

# Save data to CSV
output_file = "choice_hotels_press_releases.csv"
check_and_remove_file(output_file)
df.to_csv(output_file, index=False)

print(f"Data saved to {output_file}")

# Optionally, wait for the page to load if needed
time.sleep(5)

# Close the browser

driver.quit()


if date == date_format(datetime.now().today()):
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    append_unique_records(output_file,"")
    insert_csv_data(output_file,"informations")

else:
    print("WE DO NOT HAVE DATA FOR TODAY")