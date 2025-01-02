import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from dotenv import load_dotenv

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Initialize CSV file
csv_file = "int_hworld_extracted_data.csv"
check_and_remove_file(csv_file)

# Write headers to the CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)


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


# Open the desired webpage
driver.get("https://int.hworld.com/press")

# Use JavaScript to extract the href from the 'a' element and open it
script = """
    var link = document.querySelector('a[href="/press/2024/rebranding-h-world-international"]');
    if (link) {
        window.location.href = link.href;
    }
"""
driver.execute_script(script)

# Wait for the page to load
time.sleep(10)

# Use JavaScript to get the image URL from the <img> element
image_url = driver.execute_script("""
    var imgElement = document.querySelector('img.lazyautosizes');
    return imgElement ? imgElement.getAttribute('src') : null;
""")

# If the image URL is a relative path, prepend the base URL
base_url = "https://int.hworld.com"
if image_url:
    full_image_url = base_url + image_url if image_url.startswith('/') else image_url
else:
    full_image_url = "Image not found"

# Extract other required data using JavaScript

# Extract the date
date = driver.execute_script("""
    var dateElement = document.querySelector('.date');
    return dateElement ? dateElement.innerText : null;
""")

# Extract the title (headline)
title = driver.execute_script("""
    var h1Element = document.querySelector('h1');
    return h1Element ? h1Element.innerText : null;
""")

# Extract content
content = driver.execute_script("""
    var pTags = document.querySelectorAll('p');
    var textContent = '';
    pTags.forEach(function(p) {
        textContent += p.innerText + ' ';
    });
    return textContent.trim();
""")
title = generate_title(title)
date = date_format(date)
print(date)
img_nam = generate_random_filename()
download_image(full_image_url,img_nam)
# upload_photo_to_ftp(img_nam,"/public_html/storage/information/")


# Define a dummy row of data (you can replace this with actual extracted data)
data_row = [
    "1",  # id
    title,  # title
    generate_subtitle(title),  # subtitle (if available)
    title.lower().replace(" ","-"),  # slug
    "",  # lead
    generate_news(content),  # content
    "information/"+img_nam,  # image
    "Press",  # type
    "",  # custom_field
    "",  # parent_id
    date,  # created_at (you can replace with actual creation date if available)
    time.time(),  # updated_at
    date,   # added_timestamp
    "en",  # language (you can adjust this based on the language of the content)
    "",  # seo_title
    "",  # seo_content
    "",  # seo_title_desc
    "",  # seo_content_desc
    100  # category_id
]

# Append the extracted data to the CSV file
with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(data_row)

# Close the browser
driver.quit()

print(f"Data has been saved to {csv_file}")


if date==date_format(time.time()):
    upload_photo_to_ftp(img_nam,"/public_html/storage/information/")
    append_unique_records(csv_file,"combined_news_data.csv")
    insert_csv_data(csv_file,"informations")
else:
    print("WE DO NOT HAVE DATA FOR TODAY")
