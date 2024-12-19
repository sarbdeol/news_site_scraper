# import os
# import requests
# import csv
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from insert_csv_into_sql_db import insert_into_db,check_and_remove_file,generate_news
# import shutil

# # Set up Selenium WebDriver in headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Initialize WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Open the target URL
# url = "https://www.ihgplc.com/en/news-and-media/news-releases"  # Replace with your URL
# driver.get(url)

# # Wait until the page is fully loaded
# try:
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_all_elements_located((By.CLASS_NAME, "c-card"))
#     )
# except Exception as e:
#     print(f"Error waiting for elements: {e}")
#     driver.quit()
#     exit()

# # JavaScript to execute for scraping data
# js_code = """
# let extractedData = [];

# document.querySelectorAll('.c-card').forEach(card => {
#     let title = card.querySelector('.c-card__title')?.textContent.trim() || 'No title';
#     let dateText = card.querySelector('.c-card__date')?.textContent.trim() || 'No date';
#     let imageUrl = card.querySelector('.c-card__image img')?.src || 'No image';
    
#     extractedData.push({ title, date: dateText, image: imageUrl });
# });

# return extractedData;
# """

# # Execute JavaScript to extract data
# data = driver.execute_script(js_code)

# # Debugging: Print extracted data
# print("Extracted Data:", data)

# # Close the driver after data extraction
# driver.quit()

# # Check if data is empty
# if not data:
#     print("No data extracted. Check the selectors or webpage structure.")
#     exit()

# # Prepare output folder for images
# output_folder = "ihgplc_scraped_images"

# if os.path.exists(output_folder):
#     print(f"Folder '{output_folder}' exists. Deleting and creating a new one...")
#     shutil.rmtree(output_folder)  # Remove the folder and its contents
# os.makedirs(output_folder, exist_ok=True) 


# # Prepare CSV file and headers
# csv_file = "ihgplc_scraped_data.csv"
# check_and_remove_file(csv_file)

# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # User-Agent to mimic a browser
# headers_for_requests = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
# }

# # Save data to CSV and download images
# with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()

#     for idx, item in enumerate(data):
#         title = generate_news(item.get("title", "No title"))
#         date = item.get("date", "No date")
#         image_url = item.get("image", "No image")
        
#         # Fill in the placeholders for the missing fields
#         slug = "No slug"
#         lead = "No lead"
#         content = "No content"
#         image_path = "No image"
#         content_type = "No type"
#         custom_field = "No custom field"
#         parent_id = "No parent"
#         created_at = date  # Using the date as a placeholder for created_at
#         updated_at = date  # Same for updated_at
#         language = "en"  # Assuming English as the default language
#         seo_title = "No SEO Title"
#         seo_content = "No SEO Content"
#         seo_title_desc = "No SEO Title Description"
#         seo_content_desc = "No SEO Content Description"
#         category_id = "No category"
        
#         # Download and save the image
#         if image_url and image_url != "No image":
#             try:
#                 # Handle relative image URLs
#                 if image_url.startswith("/"):
#                     image_url = "https://www.ihgplc.com" + image_url.split('?')[0]  # Clean URL
                
#                 # Send the request with the headers
#                 response = requests.get(image_url, headers=headers_for_requests, stream=True)
#                 if response.status_code == 200:
#                     # Generate a unique filename for the image
#                     image_name = f"image_{idx + 1}.jpg"
#                     image_path = os.path.join(output_folder, image_name)
                    
#                     # Save the image locally
#                     with open(image_path, "wb") as img_file:
#                         for chunk in response.iter_content(1024):
#                             img_file.write(chunk)
#                     print(f"Image saved: {image_path}")
#                 else:
#                     print(f"Failed to download image: {image_url} (status code {response.status_code})")
#             except Exception as e:
#                 print(f"Error downloading image {image_url}: {e}")

#         # Write the data to CSV file, including all fields
#         writer.writerow({
#             "id": idx + 1,
#             "title": title,
#             "slug": slug,
#             "lead": lead,
#             "content": content,
#             "image": image_url,
#             "type": content_type,
#             "custom_field": custom_field,
#             "parent_id": parent_id,
#             "created_at": created_at,
#             "updated_at": updated_at,
#             "language": language,
#             "seo_title": seo_title,
#             "seo_content": seo_content,
#             "seo_title_desc": seo_title_desc,
#             "seo_content_desc": seo_content_desc,
#             "category_id": category_id,
#         })

# print(f"Data saved to {csv_file}. Images saved in the '{output_folder}' folder.")

# # insert_into_db(csv_file)



import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
# Set up Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disable sandbox for headless mode
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp

# Path to chromedriver (ensure chromedriver is installed and accessible)
driver = webdriver.Chrome(options=chrome_options)

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

upload_photo_to_ftp(img_name,"/public_html/storage/information/")

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

check_and_remove_file("output.csv") 

csvfile='output.csv'

# Write data to CSV
with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write headers
    writer.writerow(data)  # Write the data row

print("Data saved to output.csv")

if date==date_format(datetime.now().today()):
    append_unique_records(csvfile,"combined_news_data.csv")
    insert_csv_data(csvfile,"information")
else:
    print("---------------------WE DO NOT HAVE NEW DATA FOR TODAY----------------------------------------")