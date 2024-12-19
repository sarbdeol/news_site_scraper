# import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select
# import time
# from urllib.parse import urljoin  # To handle relative URLs
# from selenium.webdriver.chrome.options import Options



# # Setup Chrome in headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Set up the WebDriver

# driver = webdriver.Chrome(options=chrome_options)   # Or another WebDriver (e.g., Firefox)
# driver.get('https://newsroom.caesars.com/press-releases/default.aspx')  # URL of the page

# # Wait for the page to load (add explicit waits as needed)
# time.sleep(2)

# # Select a year from the dropdown
# year_dropdown = driver.find_element(By.ID, "newsYear")
# select = Select(year_dropdown)
# select.select_by_visible_text('2024')  # Replace '2024' with desired year

# # Wait for the content to update
# time.sleep(2)

# # Extract news headlines and associated images
# news_items = driver.find_elements(By.CSS_SELECTOR, '.module_item')

# # Define CSV structure and initialize the file
# csv_file = "scraped_newsroom.caesars_images.csv"
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type", 
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Write to CSV file
# with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()

#     for idx, item in enumerate(news_items, start=1):
#         headline_element = item.find_element(By.CSS_SELECTOR, '.module_headline-link')
#         image_element = item.find_element(By.CSS_SELECTOR, 'img') if item.find_elements(By.CSS_SELECTOR, 'img') else None
        
#         # Ensure the image URL is absolute
#         image_url = ""
#         if image_element:
#             image_url = image_element.get_attribute('src')
#             # Convert relative URLs to absolute URLs
#             image_url_1 = urljoin(driver.current_url, image_url)
        
#         writer.writerow({
#             "id": idx,
#             "title": headline_element.text,
#             "slug": headline_element.get_attribute('href').split('/')[-1],
#             "lead": "",  # Placeholder for "lead"
#             "content": headline_element.text,
#             "image": image_url,  # Use absolute image URL
#             "type": "press-release",  # Default type
#             "custom_field": "",  # Placeholder
#             "parent_id": "",  # Placeholder
#             "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
#             "updated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
#             "language": "en",
#             "seo_title": headline_element.text,
#             "seo_content": headline_element.text,
#             "seo_title_desc": headline_element.text[:60],
#             "seo_content_desc": headline_element.text[:160],
#             "category_id": "news"
#         })

# # Close the WebDriver
# driver.quit()

# print(f"Scraped data with images has been saved to {csv_file}")


import time
import os
import requests
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import PyPDF2
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,append_unique_records
from insert_csv_into_sql_db import generate_random_filename,insert_csv_data,download_image,date_format,check_and_remove_file
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime

from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disabling sandbox for headless mode
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)  # Set user-agent to mimic a real browser

# Setup Selenium WebDriver
driver = webdriver.Chrome(options=chrome_options)


# Function to download the PDF file
def download_pdf(pdf_url, download_path):
    response = requests.get(pdf_url)
    with open(download_path, 'wb') as file:
        file.write(response.content)

# Function to extract text from PDF
def extract_pdf_content(pdf_path):
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        content = ""
        for page in range(len(pdf_reader.pages)):
            content += pdf_reader.pages[page].extract_text()
        return content

# Set up WebDriver (make sure to replace the path with the actual path of the driver)
# driver = webdriver.Chrome()

# Open the target webpage
url = "https://newsroom.caesars.com/press-releases/default.aspx"
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# JavaScript to get date, title, and image
js_code = """
let dateElement = document.querySelector('.module_date-time');
let titleElement = document.querySelector('.module_headline a');
let imageElement = document.querySelector('img');

let date = dateElement ? dateElement.textContent.trim() : "Date not found";
let title = titleElement ? titleElement.textContent.trim() : "Title not found";
let imageUrl = imageElement ? imageElement.getAttribute('src') : "Image not found";

return { date: date, title: title, imageUrl: imageUrl };
"""

# Execute the JavaScript code to get date, title, and image
result = driver.execute_script(js_code)

date = result['date']
title = result['title']
img_url = result['imageUrl']

# Wait for the specific element to be visible and extract the download link for the PDF
download_link_element = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".module_links .module_related-document a"))
)

# Get the PDF link URL
pdf_url = download_link_element.get_attribute("href")
print("PDF URL:", pdf_url)

# Download the PDF file to a specified path (Make sure you set a correct path)
download_path = result['title']+".pdf"
download_pdf(pdf_url, download_path)
print(f"PDF downloaded to {download_path}")

# Wait for the download to finish
time.sleep(2)

# Extract content from the downloaded PDF
pdf_content = extract_pdf_content(download_path)

img_name = generate_random_filename()

download_image(img_url,img_name)

upload_photo_to_ftp(img_name,"/public_html/storage/information/")

# Print the extracted content
print("PDF Content:\n", pdf_content)

title =  generate_title(title)

date = date_format(date)

# Prepare data to save in CSV
data = {
    "id": "1",  # For simplicity, id is hardcoded as "1". You can modify this for unique ids.
    "title": title,
    "subtitle": generate_subtitle(title),  # You can add a subtitle extraction if needed.
    "slug": title.replace(" ","-").lower(),  # Slug can be extracted or generated if needed.
    "lead": "",  # Lead information can be extracted from another source.
    "content": generate_news(pdf_content),  # Content extracted from the PDF.
    "image": "information/"+img_name,
    "type": "",  # Add type if relevant.
    "custom_field": "",  # Add any custom fields if relevant.
    "parent_id": "",  # Parent ID can be added if relevant.
    "created_at": date,  # Date extracted from the webpage.
    "updated_at": datetime.now().today(),  # Set if applicable.
    "added_timestamp": date,  # You can add the current timestamp if needed.
    "language": "en",  # Assuming English language for simplicity.
    "seo_title": "",  # SEO title if relevant.
    "seo_content": "",  # SEO content if relevant.
    "seo_title_desc": "",  # SEO title description if relevant.
    "seo_content_desc": "",  # SEO content description if relevant.
    "category_id": 100  # Add category if relevant.
}

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Write data to CSV file
csv_filename = "caesars_news_data.csv"
check_and_remove_file(csv_filename)
file_exists = os.path.isfile(csv_filename)

# Open the CSV file in append mode
with open(csv_filename, mode="a", newline='', encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    
    # If the file doesn't exist, write the header first
    if not file_exists:
        writer.writeheader()

    # Write the extracted data to the CSV
    writer.writerow(data)

print("Data saved to CSV successfully.")

# Quit the driver
driver.quit()


if date == date_format(datetime.now().today()):
    insert_csv_data(csv_filename,"informations")
    append_unique_records(csv_filename,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY-----------------------")