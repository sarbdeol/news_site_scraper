# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # import csv
# # import os
# # import requests
# # from datetime import datetime

# # # Configure Selenium WebDriver
# # driver = webdriver.Chrome()  # Ensure the appropriate WebDriver is installed
# # url = "https://www.dusit-international.com/en/updates/press-releases"  # Replace with the actual URL
# # driver.get(url)

# # # Define CSV headers as per your requested format
# # headers = [
# #     "id", "title", "slug", "lead", "content", "image", "type", 
# #     "custom_field", "parent_id", "created_at", "updated_at", 
# #     "language", "seo_title", "seo_content", "seo_title_desc", 
# #     "seo_content_desc", "category_id"
# # ]

# # # Create a CSV file for saving the data
# # csv_file = "dusit_press_releases.csv"
# # with open(csv_file, "w", newline="", encoding="utf-8") as file:
# #     writer = csv.writer(file)
# #     writer.writerow(headers)  # Write the header row

# #     # Find all cards containing press release information
# #     cards = driver.find_elements(By.CSS_SELECTOR, ".card--news-horizontal")

# #     for idx, card in enumerate(cards, start=1):
# #         try:
# #             # Extract the title
# #             title = card.find_element(By.CSS_SELECTOR, ".card__title").text
# #             slug = title.lower().replace(" ", "-")  # Generate a slug from the title

# #             # Extract the description (lead)
# #             lead = card.find_element(By.CSS_SELECTOR, ".card__body").text

# #             # Extract the link
# #             link = card.get_attribute("href")

# #             # Extract the publication date
# #             date = card.find_element(By.CSS_SELECTOR, ".card__date").text
# #             created_at = updated_at = datetime.strptime(date, "%d %B %Y").strftime("%Y-%m-%d %H:%M:%S")

# #             # Extract the image URL
# #             try:
# #                 image_url = card.find_element(By.CSS_SELECTOR, ".card__img").get_attribute("style")
# #                 image_url = image_url.split("url('")[1].split("')")[0]  # Parse the URL
# #                 image_name = f"images/{slug}.jpg"

# #                 # Download the image
# #                 os.makedirs("images", exist_ok=True)
# #                 img_response = requests.get(image_url)
# #                 if img_response.status_code == 200:
# #                     with open(image_name, "wb") as img_file:
# #                         img_file.write(img_response.content)
# #             except:
# #                 image_url = None
# #                 image_name = None

# #             # Write the data to the CSV file
# #             writer.writerow([
# #                 idx,             # id
# #                 title,           # title
# #                 slug,            # slug
# #                 lead,            # lead
# #                 "",              # content (not available)
# #                 image_name,      # image (local path)
# #                 "news",          # type
# #                 "",              # custom_field
# #                 None,            # parent_id
# #                 created_at,      # created_at
# #                 updated_at,      # updated_at
# #                 "en",            # language (assumed English)
# #                 title,           # seo_title
# #                 lead,            # seo_content
# #                 title,           # seo_title_desc
# #                 lead,            # seo_content_desc
# #                 None             # category_id (not available)
# #             ])

# #         except Exception as e:
# #             print(f"Error processing card {idx}: {e}")

# # # Close the browser
# # driver.quit()

# # print(f"Data saved to {csv_file}. Images saved to the 'images' folder.")
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode (no UI)

# # Initialize WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Open the page containing the <a> tag with class "card--news-horizontal"
# driver.get("https://www.dusit-international.com/en/updates/")  # Replace with the actual URL

# # Wait for the link element to be present (e.g., wait for the first news card to load)
# # WebDriverWait(driver, 10).until(
# #     EC.presence_of_element_located((By.CSS_SELECTOR, 'a.card.card--news-horizontal'))
# # )

# # JavaScript to get the href attribute from the <a> tag
# js_code = """
# var links = document.querySelectorAll('a.card.card--news-horizontal');
# if (links.length > 0) {
#     return links[0].href;
# } else {
#     return null;
# }
# """

# # Execute the JavaScript to get the href
# href = driver.execute_script(js_code)

# if href:
#     print("Extracted href:", href)
    
#     # Now open the href link in the browser
#     driver.get(href)
    
#     # Wait for the page to load
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, 'h5.card__title'))
#     )
    
#     # Extract title, date, and image from the opened page
#     title = driver.find_element_by_css_selector('h5.card__title').text
#     date = driver.find_element_by_css_selector('time.card__date').text
#     image_url = driver.find_element_by_css_selector('div.card__img').get_attribute('style')
    
#     # Extract image URL from the background-image style attribute
#     start_idx = image_url.find("url('") + 5
#     end_idx = image_url.find("')", start_idx)
#     image_url = image_url[start_idx:end_idx]

#     print(f"Title: {title}")
#     print(f"Date: {date}")
#     print(f"Image URL: {image_url}")
# else:
#     print("Href link not found.")

# # Close the WebDriver
# driver.quit()

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
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

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open the target webpage
driver.get('https://www.dusit-international.com/en/updates/press-releases')

# Wait for the page to load
time.sleep(5)

# Find all <a> tags with the class 'card card--news-horizontal'
cards = driver.find_elements(By.CLASS_NAME, 'card--news-horizontal')

# Extract hrefs from the <a> tags
hrefs = [card.get_attribute('href') for card in cards if card.get_attribute('href')]

# # Print the hrefs
# print("Extracted hrefs from cards:")
# for href in hrefs:
#     print(href)
csv_file = 'output.csv'
# Open a CSV file to store the extracted data
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    # Open each href in the same browser tab one after another
    for href in hrefs[:1]:
        driver.get(href)
        time.sleep(5)  # Wait for 5 seconds to view the page

        # Initialize data row
        data_row = {key: '' for key in headers}
        data_row['id'] = 1

        # Find and extract the date from the specified div
        try:
            date_element = driver.find_element(By.CLASS_NAME, 'media-detail__date')
            date_text = date_element.find_element(By.TAG_NAME, 'time').text
            # data_row['created_at'] = date_text
            date_text= date_format(date_text)
        except Exception as e:
            print(f"Error extracting date: {e}")

        # Find and extract the title from the specified div
        try:
            title_element = driver.find_element(By.CLASS_NAME, 'media-detail__title')
            title_text = title_element.find_element(By.TAG_NAME, 'h1').text
            data_row['title'] = generate_title(title_text)
        except Exception as e:
            print(f"Error extracting title: {e}")

        img_name = generate_random_filename()
        data_row['subtitle'] = generate_subtitle(title_text)
        data_row['slug'] = title_text.lower().replace(" ","-")
        data_row['lead'] = ""
        # Find and extract the image and paragraphs from the specified div
        try:

            # Extract all paragraphs
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            all_text = " ".join([p.text for p in paragraphs])
            data_row['content'] = generate_news(all_text)

            body_element = driver.find_element(By.CLASS_NAME, 'media-detail__body')

            # Extract the image source
            image_element = body_element.find_element(By.TAG_NAME, 'img')
            image_src = image_element.get_attribute('src')
            data_row['image'] = 'information/'+img_name
            download_image(image_src,img_name)
            upload_photo_to_ftp(img_name,"/public_html/storage/information/")

            data_row['type']=""
            data_row['custom_field']=""
            data_row['parent_id']=""
            data_row['created_at']=date_text
            data_row['updated_at']=datetime.now().today()
            data_row['added_timestamp']=date_text
            data_row['language']="en"
            data_row['seo_title']=""
            data_row['seo_content']=""
            data_row['seo_title_desc']=""
            data_row['seo_content_desc']=""
            data_row['category_id']=100

        except Exception as e:
            print(f"Error extracting body content: {e}")

        # Write data to the CSV file
        writer.writerow(data_row)

# Optional: Close the browser after interaction
driver.quit()

if date_text == date_format(datetime.now().today()):
    append_unique_records(csv_file,"combined_news_data.csv")
    insert_csv_data(csv_file,"informations")
else:
    print("WE DO NOT HAVE DATA FOR TODAY")