import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
from selenium.webdriver.chrome.options import Options
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


# Open the page URL
driver.get("https://nordichotels.com/news")  # Replace with the actual URL

# JavaScript code to extract the href and navigate to it
js_code = """
const linkElement = document.querySelector('.block-block__inner a');
if (linkElement) {
    const href = linkElement.href;
    window.location.href = href;    // Navigate to the link in the same tab
    return href;  // Return the href for verification or logging
} else {
    return "No link found";  // In case no link is found
}
"""

# Execute the JavaScript code in Selenium and retrieve the result
href = driver.execute_script(js_code)

# JavaScript code to extract most recent date, title, image URL, and <p> content
js_code = """
var result = {};

// Extract the most recent date (first <p> element found with date text)
var date = document.querySelector("div.block-block__inner.block-column__inner p");
if (date) {
    result.date = date.innerText.trim();
}

// Extract the most recent title (first <h1> element found)
var title = document.querySelector("div.block-block__inner.block-column__inner h1");
if (title) {
    result.title = title.innerText.trim();
}

// Extract the most recent image URL (first <img> tag found)
var image = document.querySelector("div.block-block__inner.block-column__inner img");
if (image) {
    result.image_url = image.src;
}

// Extract the first <p> content that isn't the date
var pTags = document.querySelectorAll("div.block-block__inner.block-column__inner p");
for (var i = 0; i < pTags.length; i++) {
    var pTag = pTags[i];
    if (pTag.innerText.trim() !== result.date) {  // Ensure it's not the date
        result.p_content = pTag.innerText.trim();
        break;  // Exit the loop once we find the first relevant <p> tag
    }
}

return result;
"""

# Execute the JavaScript code in the browser and get the result
result = driver.execute_script(js_code)

# Define headers for the CSV
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]
title =generate_title(result.get('title', ''))
date = date_format(result.get('date', ''))
print(date)
img_name = generate_random_filename()
download_image(result.get('image_url', ''),img_name)
upload_photo_to_ftp(img_name,"/public_html/storage/information/")
# Generate a new row of data to save in CSV (example data for fields)
row = [
    1,  # id
    title,  # title
    generate_subtitle(title),  # subtitle
    title.lower().replace(" ","-"),  # slug
    '',  # lead
   '',  # content
    "information/"+img_name ,  # image URL
    '',  # type
    '',  # custom_field
    '',  # parent_id
   date,  # created_at (using date as created_at for example)
    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # updated_at
    date,  # added_timestamp
    'en',  # language (assuming English for this example)
    '',  # seo_title
    '',  # seo_content
    '',  # seo_title_desc
    '',  # seo_content_desc
    '100'  # category_id
]
csv_file = "scraped_data.csv"
# Open the CSV file and append the row of data
with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write the headers if the file is empty
    file.seek(0, 2)  # Move to the end of file to check if it's empty
    if file.tell() == 0:  # If file is empty, write headers
        writer.writerow(headers)
    
    # Write the scraped data row
    writer.writerow(row)

# Close the browser when done
driver.quit()


if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data(csv_file, "informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")