# #this is with new logic extract title date and then contnent of news and image


# import os
# import time
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from PIL import Image
# from io import BytesIO
# import csv
# from insert_csv_into_sql_db import *
# import shutil
# # Set up Chrome options for headless browsing
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Initialize the WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Open the main blog page
# url = "https://www.corinthia.com/en-gb/latest-news/"
# driver.get(url)

# # Wait for the page to load
# time.sleep(3)

# # List to hold article data
# articles_data = []

# # Function to download image
# def download_image(image_url, image_name):
#     try:
#         # Only download if it's a valid image URL (HTTP/HTTPS)
#         if image_url.startswith('http') or image_url.startswith('https'):
#             response = requests.get(image_url)
#             img = Image.open(BytesIO(response.content))
#             img_format = img.format.lower()
#             img.save(f"corinthia_images/{image_name}.{img_format}")
#             print(f"Downloaded corinthia_image: {image_name}.{img_format}")
#         else:
#             print(f"Skipping invalid image URL: {image_url}")
#     except Exception as e:
#         print(f"Error downloading image {image_name}: {e}")

# # Function to extract article information from the opened article link
# def extract_article_data(article_link):
#     driver.get(article_link)
#     time.sleep(3)  # Wait for the article page to load

#     try:
#         # Extract title, content, and images
#         title = driver.find_element(By.CSS_SELECTOR, 'h1').text
#         # date = driver.find_element(By.CSS_SELECTOR, 'time').text
#         date = driver.execute_script("""
#             let dateElement = document.querySelector('.generic-content-block__body strong');
#             let dateText = dateElement ? dateElement.textContent : null;
#             if (dateText) {
#                 let date = dateText.split(' - ')[1];
#                 return date;
#             } else {
#                 return null;
#             }
#         """)

#         content = driver.execute_script("""
#            let paragraphs = document.querySelectorAll('p');
#     let paragraphTexts = Array.from(paragraphs).map(p => p.textContent);
#     // Join all paragraphs with a space and remove 'Light' and 'Dark' words
#     let fullContent = paragraphTexts.join(' ');  
#     fullContent = fullContent.replace(/Light\s*/g, "").replace(/Dark\s*/g, "");  // Remove unwanted words
#     fullContent = fullContent.replace(/\s+/g, " ").trim();  // Remove extra spaces
#     return fullContent;
#         """)

#         # Download images
#         image_elements = driver.find_elements(By.CSS_SELECTOR, 'article img')
#         image_names = []
#         for idx, img_elem in enumerate(image_elements):
#             img_url = img_elem.get_attribute('src')
#             image_name = f"{title.replace(' ', '_').lower()}_image_{idx+1}"
#             download_image(img_url, image_name)
#             image_names.append(image_name)

#         return title, date, content, image_names
#     except Exception as e:
#         print(f"Error extracting data from {article_link}: {e}")
#         return None

# # Create a directory for saving images if it doesn't exist
# image_folder = "corinthia_images"
# if os.path.exists(image_folder):
#     print(f"Folder '{image_folder}' exists. Deleting and creating a new one...")
#     shutil.rmtree(image_folder)  # Remove the folder and its contents
# os.makedirs(image_folder, exist_ok=True) 
# # if not os.path.exists("corinthia_images"):
# #     os.makedirs("corinthia_images")

# # Find all article links
# article_links = [a.get_attribute('href') for a in driver.find_elements(By.CSS_SELECTOR, '.listing-result-card__content a')]

# # Loop through each article link, extract data and save it
# for article_link in article_links:
#     print(f"Processing article: {article_link}")
#     article_data = extract_article_data(article_link)
#     if article_data:
#         title, date, content, image_names = article_data
#         articles_data.append([title, date, content, ', '.join(image_names)])

# # Define headers for the CSV file
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Save the extracted data into a CSV file
# check_and_remove_file('corinthia_news.csv')

# with open('corinthia_news.csv', mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(headers)  # Write the headers
    
#     # Add the article data to the CSV
#     article_id = 1  # Starting article ID
#     for article in articles_data:
#         # Assuming slug is derived from the title, lead is the first paragraph, and using placeholders for other fields
#         title = generate_title(article[0])
#         slug = title.replace(" ", "-").lower()
#         lead = ""  # Lead is the first paragraph of the content
#         content = ' '.join(generate_news(article[2]))
#         image = article[3]
#         type = "news"
#         custom_field = parent_id = ""
#         created_at = updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
#         language = "en"
#         seo_title = seo_content = seo_title_desc = seo_content_desc = ""
#         category_id = 100  # Placeholder for category ID

#         writer.writerow([
#             article_id, title, slug, lead, content, image, type,
#             custom_field, parent_id, created_at, updated_at, 
#             language, seo_title, seo_content, seo_title_desc, 
#             seo_content_desc, category_id
#         ])
#         article_id += 1  # Increment article ID for each new article

# # Close the driver after scraping
# driver.quit()

# print("Scraping completed and data saved to 'corinthia_news.csv'")

# # insert_csv_data('corinthia_news.csv')


# ------------------------------------


import os
import requests
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,append_unique_records,generate_title,check_and_remove_file,insert_csv_data,date_format
from upload_and_reference import upload_photo_to_ftp

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Necessary for some environments like Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # For some systems with limited resources

# Set up the WebDriver (e.g., using Chrome with headless option)
driver = webdriver.Chrome(options=chrome_options)  # Update path to your chromedriver if needed

# Navigate to the page with the "Read more" link
driver.get('https://www.corinthia.com/en-gb/latest-news/')  # Replace with the URL of the page containing the news links

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "listing-result-card__content")))

# Step 1: Execute JavaScript to click the "Read more" link
script = """
    // Find the 'Read more' link and click it
    let readMoreLink = document.querySelector('a.link--underlined');
    if (readMoreLink) {
        readMoreLink.click();
    }
"""

# Execute JavaScript to click the "Read more" link
driver.execute_script(script)

# Wait for the new page to load
# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "article")))

# Execute JavaScript to extract the title
script = """
    let title = document.querySelector('h1.text').textContent.trim();
    return title;
"""
title = driver.execute_script(script)

# Execute JavaScript to extract the date
script = """
    const element = document.querySelector('em > strong');
    return element ? element.textContent.trim() : null;
"""
date = driver.execute_script(script)

# Execute JavaScript to extract the paragraphs
script = """
    let paragraphs = document.querySelectorAll('div.generic-content-block__body.rich-text p');
    let textContent = Array.from(paragraphs).map(p => p.textContent.trim());
    return textContent;
"""
paragraphs = driver.execute_script(script)

# Execute JavaScript to get the image URL
script = """
       let img = document.querySelector('picture img');
    if (img) {
        return img.src;
    }
    return null;
"""
image_url = driver.execute_script(script)

# Check if the image URL is relative or absolute
base_url = "https://www.corinthia.com"  # The base URL of the website
if not image_url.startswith("http"):
    image_url = base_url + image_url  # Convert relative URL to absolute URL

# Create folder to save the image
if not os.path.exists("corinthia_images"):
    os.makedirs("corinthia_images")

# Download the image and save it
image_name = image_url.split("/")[-1].split("?")[0]  # Extract the image file name
image_path = os.path.join("corinthia_images", image_name)

# Download image and save it locally
try:
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(image_name, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image saved at: {image_name}")
        upload_photo_to_ftp(image_name,"/public_html/storage/information/")
    else:
        print(f"Failed to download image: {image_url}, Status code: {response.status_code}")
except Exception as e:
    print(f"Error downloading image: {e}")

# Prepare data for saving
data = {
    "id": 1,  # You can set a value or leave it empty
    "title": generate_title(title),
    "subtitle": generate_subtitle(title),  # You can set a subtitle if needed
    "slug": generate_title(title.lower().replace(" ", "-")).replace(" ","-").lower().strip('"'),  # Example slug, can be customized
    "lead": "",  # Lead as the first paragraph
    "content": generate_news(" ".join(paragraphs)),
    "image": "information/"+image_name,  # Save the image file name
    "type": "news",  # You can define a type if needed
    "custom_field": "",  # Custom field if any
    "parent_id": "",  # Parent ID if any
    "created_at":date_format(date),
    "updated_at": date,
    "added_timestamp": date_format(date),
    "language": "en",  # Assuming the language is English
    "seo_title": "",  # Example SEO title
    "seo_content": "",  # Example SEO content
    "seo_title_desc": "",  # Example SEO description
    "seo_content_desc": "",  # Example SEO content description
    "category_id": 101  # Category ID if any
}

# Define the headers for the CSV
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Save data to CSV file
csv_filename = "corinthia_news.csv"
check_and_remove_file(csv_filename)

# Check if the file exists, if not, write headers
file_exists = os.path.isfile(csv_filename)
with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    
    if not file_exists:
        writer.writeheader()  # Write headers only if file doesn't exist

    # Write the data to CSV
    writer.writerow(data)

# Close the browser
driver.quit()

if date_format(datetime.now().date())==date_format(date):
    print("Data is sending.......")
    insert_csv_data(csv_filename,"informations")
    append_unique_records(csv_filename,"combined_news_data.csv")

else:
    print("---------------WE DO NOT HAVE DATA FOR TODAY---------------------")


