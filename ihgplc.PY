

import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp



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


# Open the page
driver.get("https://www.ihgplc.com/en/news-and-media/news-releases")  # Replace with your actual URL

# JavaScript to find the first link and open it
script = """
    var link = document.querySelector('.c-card__title a');  // Select the <a> inside .c-card__title
    if (link) {
        window.location.href = link.href;  // Open the href in the browser
    }
"""

# Execute the script to open the link in the browser
driver.execute_script(script)

# JavaScript to get the date from the <p class="news-date">
script = """
    var dateElement = document.querySelector('.news-date');
    return dateElement ? dateElement.innerText : null;
"""

# Execute the script to get the date
date = date_format(driver.execute_script(script))
print(date)

# JavaScript to get the title from the <h1> element
script = """
    var titleElement = document.querySelector('h1');
    return titleElement ? titleElement.innerText : null;
"""

# Execute the script to get the title
title = generate_title(driver.execute_script(script))

# JavaScript to get the image URL from the <img> element

script = """
    var linkElement = document.querySelector('.caption a');  // Select the <a> tag inside .caption
    return linkElement ? linkElement.getAttribute('href') : null;  // Get the href attribute
"""

# Execute the script to get the image URL
image_url = driver.execute_script(script)

# If the image URL is a relative path, prepend the base URL
base_url = "https://www.ihgplc.com"
if image_url:
    full_image_url = base_url + image_url if image_url.startswith('/') else image_url
else:
    full_image_url = "Image not found"

# JavaScript to get all <p> tags and concatenate their text into a single string
script = """
    var pTags = document.querySelectorAll('p');  // Select all <p> tags
    var pTexts = [];
    pTags.forEach(function(p) {
        pTexts.push(p.innerText);  // Push each <p>'s inner text into an array
    });
    return pTexts.join(' ');  // Join all texts into a single string with a space separator
"""

# Execute the script to get all <p> tags' text as a single string
p_text_string = generate_news(driver.execute_script(script))

# Wait for the page to load
time.sleep(5)

# Close the browser
driver.quit()

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

img_name = generate_random_filename()

download_image(full_image_url,img_name)


# Data to save in CSV format (fill the fields based on your extracted content)
data = [
    "1",  # Example ID (you can generate or extract as needed)
    title,  # Title
    generate_subtitle(title),  # Subtitle (if any, leave empty or set appropriately)
    title.lower().replace(" ","-"),  # Slug (if any, leave empty or set appropriately)
    "",  # Lead (or date)
    p_text_string,  # Content
    "information/"+img_name,  # Image URL
    "news",  # Type (you can change this value if required)
    "",  # Custom Field (if any)
    "",  # Parent ID (if applicable)
    date,  # Created At (you can use current timestamp if needed)
    datetime.now().today(),  # Updated At (you can use current timestamp if needed)
    date,  # Added Timestamp (you can use current timestamp if needed)
    "en",  # Language (use appropriate language code)
    "",  # SEO Title (leave empty or fill with SEO data)
    "",  # SEO Content (leave empty or fill with SEO content)
    "",  # SEO Title Desc (leave empty or fill with SEO title description)
    "",  # SEO Content Desc (leave empty or fill with SEO content description)
    100,  # Category ID (you can set this if needed)
]

check_and_remove_file("ihgplc_output.csv") 

csvfile='ihgplc_output.csv'

# Write data to CSV
with open(csvfile, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write headers
    writer.writerow(data)  # Write the data row

print("Data saved to output.csv")

if date==date_format(datetime.now().today()):
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    append_unique_records(csvfile,"combined_news_data.csv")
    insert_csv_data(csvfile,"information")
else:
    print("---------------------WE DO NOT HAVE NEW DATA FOR TODAY----------------------------------------")