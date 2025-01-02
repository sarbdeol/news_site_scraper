# import os
# import csv
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from insert_csv_into_sql_db import insert_into_db,check_and_remove_file,generate_news
# import shutil
# # Setup Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")

# # Path to your ChromeDriver
# driver = webdriver.Chrome(options=chrome_options)

# # URL to scrape
# url = "https://www.omnihotels.com/media-center"  # Replace with the actual URL
# driver.get(url)

# # Wait for the page to load
# try:
#     WebDriverWait(driver, 30).until(
#         EC.presence_of_all_elements_located((By.CLASS_NAME, 'row.margin-top-bottom-15'))
#     )
#     print("Page loaded successfully.")
# except Exception as e:
#     print(f"Error: {e}")
#     driver.quit()
#     exit()

# # Execute JavaScript to extract the data
# news_data = driver.execute_script("""
#     let data = [];
    
#     document.querySelectorAll('.row.margin-top-bottom-15').forEach(article => {
#         let titleElement = article.querySelector('h4');
#         let title = titleElement ? titleElement.textContent.trim() : 'N/A';
        
#         let dateElement = article.querySelector('.col-xs-2.text-right');
#         let date = dateElement ? dateElement.textContent.trim() : 'N/A';
        
#         let imageElement = article.querySelector('.col-xs-10 .btn3');
#         let imageUrl = imageElement ? imageElement.getAttribute('href') : 'N/A';
        
#         data.push({
#             title: title,
#             date: date,
#             image: imageUrl
#         });
#     });
    
#     return data;
# """)

# # Output directory for CSV and images
# output_csv = "omnihotels_scraped_news.csv"

# check_and_remove_file(output_csv)

# image_folder = "omnihotels_scraped_images"
# if os.path.exists(image_folder):
#     print(f"Folder '{image_folder}' exists. Deleting and creating a new one...")
#     shutil.rmtree(image_folder)
# os.makedirs(image_folder, exist_ok=True)

# # Define custom headers
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Save data to CSV
# with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(headers)  # Write the header row

#     for index, news in enumerate(news_data, start=1):
#         title = news['title']
#         title = generate_news(title)
#         date = news['date']
#         image_url = news['image']

#         # Prepare the row data
#         row = {
#             "id": index,
#             "title": title,
#             "slug": title.lower().replace(" ", "-"),
#             "lead": 'N/A',  # Placeholder
#             "content": 'N/A',  # Placeholder
#             "image": image_url,
#             "type": 'N/A',  # Placeholder
#             "custom_field": 'N/A',  # Placeholder
#             "parent_id": 'N/A',  # Placeholder
#             "created_at": date,
#             "updated_at": date,  # Assuming the same date for created and updated
#             "language": 'en',  # Assuming English
#             "seo_title": title,
#             "seo_content": 'N/A',  # Placeholder
#             "seo_title_desc": 'N/A',  # Placeholder
#             "seo_content_desc": 'N/A',  # Placeholder
#             "category_id": 'N/A'  # Placeholder
#         }

#         # Write the row to the CSV
#         writer.writerow([row[field] for field in headers])

#         # Optional: Download image
#         if image_url != 'N/A':
#             try:
#                 # Assuming the image URL is relative, build the full URL
#                 full_image_url = "https://www.omnihotels.com" + image_url
#                 image_name = image_url.split("/")[-1]
#                 image_path = os.path.join(image_folder, image_name)

#                 # Download the image
#                 response = requests.get(full_image_url, stream=True)
#                 if response.status_code == 200:
#                     with open(image_path, "wb") as img_file:
#                         for chunk in response.iter_content(1024):
#                             img_file.write(chunk)
#                     print(f"Downloaded: {image_path}")
#                 else:
#                     print(f"Failed to download image: {full_image_url}")
#             except Exception as e:
#                 print(f"Failed to download image: {e}")

# # Clean up and close the browser
# driver.quit()

# print(f"Scraping completed. Data saved to {output_csv} and images saved in {image_folder}.")





import csv
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,append_unique_records
from insert_csv_into_sql_db import insert_csv_data
from insert_csv_into_sql_db import date_format
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import generate_random_filename
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


# Initialize WebDriver
url = "https://www.omnihotels.com/media-center"  # Replace with your actual URL
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# Ensure the element is loaded
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-xs-2.padding-right-30.text-right')))

# JavaScript to get the date from the <div>
js_code = """
    let dateElement = document.querySelector('div.col-xs-2.padding-right-30.text-right');
    return dateElement ? dateElement.textContent.trim() : null;
"""
date = driver.execute_script(js_code)

# JavaScript to get all recent hrefs from <a> tags with class 'btn3'
js_code = """
    let links = document.querySelectorAll('a.btn3');
    return Array.from(links).map(link => link.getAttribute('href'));
"""
# Execute JavaScript to extract all hrefs
recent_hrefs = driver.execute_script(js_code)

if recent_hrefs:
    print(f"Found {len(recent_hrefs)} links:")
    print("\n".join(recent_hrefs))
else:
    print("No recent links found.")
    driver.quit()
    exit()

# List to store news data
news_data = []

# Loop through each href
for href in recent_hrefs[:1]:
    try:
        js_code = """
        let linkElement = document.querySelector('a.btn3');
        if (linkElement) {
            linkElement.click();
            return "Hyperlink clicked successfully.";
        } else {
            return "Hyperlink not found.";
        }
        """
        result = driver.execute_script(js_code)
    
        # Wait for the main content to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))  # Adjust selector as needed
        
        # Extract title (assuming it's in an <h1> tag)
        title = driver.find_element(By.TAG_NAME, "h1").text
        
        # Extract content (assuming it's in <p> tags)
        content_elements = driver.find_elements(By.TAG_NAME, "p")
        content = " ".join([element.text for element in content_elements])
        
        # Extract image URL (assuming the main image is in the first <img> tag)
        try:
            image_element = driver.find_element(By.TAG_NAME, "img")
            image_url = image_element.get_attribute("src")
        except Exception:
            image_url = "Image not found"
        
        img_name = generate_random_filename()

        # Generate a random ID for the record
        record_id = str(uuid.uuid4())

        title = generate_title(title)

        date =  date_format(date)

        print(date)
        
        # Store the extracted data
        news_data.append({
            "id": 1,
            "title": title,
            "subtitle": generate_subtitle(title),
            "slug": title.replace(" ","-").lower(),
            "lead": "",
            "content":generate_news(content),
            "image": "information/"+image_url,
            "type": "news",
            "custom_field": "",
            "parent_id": "",
            "created_at": date,
            "updated_at": datetime.now().isoformat(),
            "added_timestamp":date,
            "language": "en",
            "seo_title": '',
            "seo_content":"" ,
            "seo_title_desc": "",
            "seo_content_desc": "",
            "category_id": 100
        })
        
        # Navigate back to the main page
        driver.back()
        
        # Wait for the page to reload
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h4")))  # Adjust selector to ensure main page reloads
    
    except Exception as e:
        print(f"Error processing link {href}: {e}")
        driver.get(url)  # Reload the main page in case of an error
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h4")))  # Adjust selector

# Quit the driver
driver.quit()

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Save data to a CSV file
output_file = "omnihotels_news.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(news_data)

print(f"\n--- All News Data Saved to {output_file} ---")

if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    insert_csv_data(output_file,'informations')
    append_unique_records(output_file,"combined_news_data.csv")

else:
    print("WE DO NOT HAVE DATA FOR TODAY")




