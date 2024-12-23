# import os
# import csv
# import time
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from insert_csv_into_sql_db import insert_into_db, check_and_remove_file, generate_news

# # Define CSV headers
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at",
#     "language", "seo_title", "seo_content", "seo_title_desc",
#     "seo_content_desc", "category_id"
# ]

# # Configure Selenium WebDriver
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# driver = webdriver.Chrome(service=Service(), options=chrome_options)

# # Output CSV file and image folder
# output_csv = "okura_news.csv"
# image_folder = "okura_images"

# # Ensure the image folder exists
# if not os.path.exists(image_folder):
#     os.makedirs(image_folder)

# # Remove the output CSV if it already exists
# check_and_remove_file(output_csv)

# # Function to download an image and save it locally
# def download_image(image_url, file_name):
#     try:
#         response = requests.get(image_url, stream=True, timeout=10)
#         if response.status_code == 200:
#             image_path = os.path.join(image_folder, file_name)
#             with open(image_path, "wb") as file:
#                 file.write(response.content)
#             return image_path
#     except Exception as e:
#         print(f"Failed to download image: {image_url}, Error: {e}")
#     return ""

# # Function to scrape data
# def scrape_okura_news(url):
#     driver.get(url)
#     time.sleep(2)  # Allow the page to load

#     # Find all accordion parent elements
#     accordion_parents = driver.find_elements(By.CLASS_NAME, "press_brand__accordion-parent")

#     data = []
#     item_id = 1

#     # Loop through each accordion section
#     for parent in accordion_parents:
#         # Use JavaScript to expand the accordion
#         driver.execute_script("arguments[0].click();", parent)
#         time.sleep(1)  # Allow content to load

#         # Get the associated child container
#         child_id = parent.get_attribute("data-dropdown-target")
#         child_container = driver.find_element(By.CSS_SELECTOR, child_id)

#         # Find all news items within this section
#         news_items = child_container.find_elements(By.CLASS_NAME, "press-list__item")
#         for news_item in news_items:
#             # Extract title, URL, and month/year
#             link_element = news_item.find_element(By.TAG_NAME, "a")
#             title = link_element.text.strip()
#             url = link_element.get_attribute("href")

#             # Extract date from the parent month/year element
#             date_element = news_item.find_element(By.XPATH, "../../..")
#             date = date_element.find_element(By.CLASS_NAME, "press-list__month").text.strip()

#             # Generate slug and content
#             slug = title.lower().replace(" ", "-").replace(",", "")
#             content = f"Read more at {url}"

#             # Download image if an image URL exists
#             try:
#                 image_element = news_item.find_element(By.TAG_NAME, "img")
#                 image_url = image_element.get_attribute("src")
#                 image_name = f"{slug}.jpg"
#                 image_path = download_image(image_url, image_name)
#             except:
#                 image_path = ""  # No image found

#             # Generate title using your custom function
#             title = generate_news(title)

#             # Append data to the list
#             data.append({
#                 "id": item_id,
#                 "title": title,
#                 "slug": slug,
#                 "lead": "",
#                 "content": content,
#                 "image": image_path,
#                 "type": "article",
#                 "custom_field": "",
#                 "parent_id": "",
#                 "created_at": date,
#                 "updated_at": date,
#                 "language": "en",
#                 "seo_title": title,
#                 "seo_content": content,
#                 "seo_title_desc": title,
#                 "seo_content_desc": content,
#                 "category_id": ""
#             })
#             item_id += 1

#     return data

# # Scrape data
# target_url = "https://www.okura-nikko.com/press-room/press-release/"  # Replace with the actual target URL
# news_data = scrape_okura_news(target_url)

# # Save data to CSV
# with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()
#     writer.writerows(news_data)

# print(f"Scraping complete. Data saved in {output_csv} and images in {image_folder}")

# # Quit the driver
# driver.quit()

# # Insert data into the database
# # insert_into_db(output_csv)





import csv
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,check_and_remove_file
from insert_csv_into_sql_db import date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
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


# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Initialize WebDriver
url = "https://www.okura-nikko.com/press-room/press-release/"  # Replace with your actual URL
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# JavaScript code to extract the date from the <div class="press-list__month">
js_code = """
    let dateElement = document.querySelector('.press-list__month');
    return dateElement ? dateElement.textContent.trim() : "Date not found";
"""

# Execute the JavaScript to get the date
date = driver.execute_script(js_code)

# JavaScript code to get the most recent hyperlink
js_code = """
    let newsItems = Array.from(document.querySelectorAll('.press-list__item__a')).map(link => {
        let dateElement = link.closest('.press-list__item').querySelector('.press-list__month'); // Adjust selector for date
        let dateText = dateElement ? new Date(dateElement.textContent.trim()) : new Date(0); // Default to epoch if no date found
        return { link: link.getAttribute('href'), date: dateText };
    });

    // Sort news items by date (descending)
    newsItems.sort((a, b) => b.date - a.date);

    // Return the most recent link
    return newsItems.length > 0 ? newsItems[0].link : "No recent news found";
"""

# Execute the JavaScript to get the most recent hyperlink
recent_link = driver.execute_script(js_code)

# List to store news data
news_data = []

if recent_link != "No recent news found":
    # Open the most recent news page
    driver.get(recent_link)

    # Wait for the page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))  # Assuming the title is in <h1> tag

    # Extract the title (assuming it's in an <h1> tag)
    title = driver.find_element(By.TAG_NAME, "h1").text

    # Extract content (assuming it's in <p> tags)
    content_elements = driver.find_elements(By.TAG_NAME, "p")
    content = " ".join([element.text for element in content_elements])

    # Extract image URL (assuming it's in an <img> tag)
    js_code = """
    let imageElement = document.querySelector('div.pure-u-1 img');
    let imageUrl = imageElement ? imageElement.getAttribute('src') : "Image not found";

    let textElement = document.querySelector('div.pure-u-1 p');
    let textContent = textElement ? textElement.textContent.trim() : "Text not found";

    return { imageUrl: imageUrl};
""" 

    image_url= driver.execute_script(js_code)

    img_name = generate_random_filename()

    download_image(image_url['imageUrl'],img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    
    # Generate unique ID for the record
    record_id = str(uuid.uuid4())

    # Current timestamp
    current_timestamp = datetime.now().isoformat()

    title = generate_title(title)

    date=date_format(date)
    
    # Store the extracted data
    news_data.append({
        "id": 1,
        "title": title,
        "subtitle": generate_subtitle(title),  # Assuming you have no subtitle
        # "subtitle": title,  # Assuming you have no subtitle
        "slug": title.lower().replace(" ","-"),  # Assuming you don't have slug
        "lead": "",  # Assuming no lead
        "content": content,
        "image": "information/"+img_name,
        "type": "",  # Adjust if you have a type
        "custom_field": "",  # Adjust if you have custom fields
        "parent_id": "",  # Adjust if you have a parent_id
        "created_at": date,
        "updated_at": current_timestamp,
        "added_timestamp": date,
        "language": "en",
        "seo_title": '',
        "seo_content": '',
        "seo_title_desc": "",  # Assuming no SEO title description
        "seo_content_desc": "",  # Assuming no SEO content description
        "category_id": 100  # Assuming no category
    })

    # # Print the extracted data
    # print("\n--- News Data ---")
    # print(f"Title: {title}")
    # print(f"Content: {content}")
    print(f"Date: {date}")
    print(f"Image URL: {image_url}")
else:
    print("No recent news found.")

# Quit the driver
driver.quit()

# Save data to a CSV file
output_file = "okura_news_data.csv"

check_and_remove_file(output_file)

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(news_data)

print(f"\n--- All News Data Saved to {output_file} ---")


if date == date_format(current_timestamp):
    insert_csv_data(output_file,"informations")
    append_unique_records(output_file,"combined_news_data.csv")

else:

    print("------WE DO NOT HAVE DATA FOR TODAY--------")