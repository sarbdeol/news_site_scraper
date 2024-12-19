# import os
# import csv
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from insert_csv_into_sql_db import insert_into_db,generate_news,check_and_remove_file
# import shutil

# # Setup Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")

# # Initialize the Selenium WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # URL to scrapea
# url = "https://www.peninsula.com/en/newsroom/news"  # Replace with your actual URL
# driver.get(url)

# # Wait for the articles to load
# try:
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, '.articleListing-articles'))
#     )
#     print("Page loaded successfully.")
# except Exception as e:
#     print(f"Error: {e}")
#     driver.quit()
#     exit()

# # Initialize CSV file and image directory
# output_csv = "peninsula_scraped_news.csv"

# check_and_remove_file(output_csv)

# image_folder = "peninsula_images"

# if os.path.exists(image_folder):
#     print(f"Folder '{image_folder}' exists. Deleting and creating a new one...")
#     shutil.rmtree(image_folder)  # Remove the folder and its contents
# os.makedirs(image_folder, exist_ok=True)
# # os.makedirs(image_dir, exist_ok=True)

# # Define CSV headers
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Open CSV for writing
# with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(headers)

#     # Find all news articles
#     articles = driver.find_elements(By.CSS_SELECTOR, '.featuredNewsList-column')

#     for idx, article in enumerate(articles, start=1):
#         try:
#             # Extract title
#             title_element = article.find_element(By.CSS_SELECTOR, '.cardContainerless-headline a')
#             title = title_element.text.strip()
#             slug = title.replace(" ", "-").lower()
#             link = title_element.get_attribute("href")

#             # Extract date
#             date_element = article.find_element(By.CSS_SELECTOR, '.cardContainerless-title')
#             date = date_element.text.strip()

#             # Extract image URL
#             try:
#                 style_attribute = article.find_element(By.CSS_SELECTOR, '.imageWrapper').get_attribute("style")
#                 start = style_attribute.find("url(") + 4
#                 end = style_attribute.find(")", start)
#                 image_url = style_attribute[start:end].strip('"').strip("'")
#                 if not image_url.startswith("http"):
#                     image_url = f"https://www.example.com{image_url}"
#             except Exception as e:
#                 image_url = "N/A"

#             # Download the image
#             image_path = "N/A"
#             if image_url != "N/A":
#                 image_name = image_url.split("/")[-1]
#                 image_path = os.path.join(image_folder, image_name)

#                 try:
#                     response = requests.get(image_url, stream=True)
#                     if response.status_code == 200:
#                         with open(image_path, "wb") as img_file:
#                             for chunk in response.iter_content(1024):
#                                 img_file.write(chunk)
#                     else:
#                         image_path = "Failed to download"
#                 except Exception as e:
#                     image_path = f"Error: {e}"

#             title  = generate_news(title)
#             # Placeholder values for non-available fields
#             lead = "N/A"
#             content = "N/A"
#             type_ = "News Article"
#             custom_field = "N/A"
#             parent_id = "N/A"
#             created_at = date
#             updated_at = date
#             language = "en"
#             seo_title = title
#             seo_content = "N/A"
#             seo_title_desc = "N/A"
#             seo_content_desc = "N/A"
#             category_id = "N/A"

#             # Write the data into CSV
#             writer.writerow([idx, title, slug, lead, content, image_path, type_, custom_field, parent_id, created_at, updated_at, language, seo_title, seo_content, seo_title_desc, seo_content_desc, category_id])
#             print(f"Scraped: {title}, {date}, Image Path: {image_path}")

#         except Exception as e:
#             print(f"Error processing article: {e}")

# # Close the browser
# driver.quit()

# print(f"Scraping completed. Data saved to {output_csv} and images saved in {image_folder}.")

# # insert_into_db(output_csv)



import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename
from insert_csv_into_sql_db import check_and_remove_file,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import download_image,date_format
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

url = "https://www.peninsula.com/en/newsroom/news"  # Replace with your target URL
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# JavaScript to get the most recent news URL
js_code = """
    let links = document.querySelectorAll('.cardContainerlessNews-text h3.cardContainerless-headline a');
    
    let newsData = Array.from(links).map(link => {
        return {
            url: link.href,
            date: link.closest('.cardContainerlessNews').querySelector('h4.cardContainerless-title').innerText,
            title: link.innerText
        };
    });

    newsData.sort((a, b) => {
        let dateA = new Date(a.date.split('/').reverse().join('-'));
        let dateB = new Date(b.date.split('/').reverse().join('-'));
        return dateB - dateA;
    });

    return newsData.length > 0 ? newsData[0].url : null;
"""

# Get the most recent news URL
recent_news_url = driver.execute_script(js_code)

# Save the data to CSV
csv_file = "pennnisula_news.csv"
check_and_remove_file(csv_file)

# Print the most recent news URL
print("Recent News URL:", recent_news_url)

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# List to store data to save into CSV
news_data = []

# If a URL is found, navigate to it and extract title, content, and images
if recent_news_url:
    driver.get(recent_news_url)  # Open the recent news link
    
    # Wait for the page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))  # Assuming title is in <h1>
    
    # Extract title
    title = driver.find_element(By.TAG_NAME, "h1").text
    
    # Extract content (assuming content is within <div class="content">, update as per actual structure)
    js_code = """
    let paragraphs = document.querySelectorAll('p');
    let paragraphTexts = Array.from(paragraphs).map(p => p.innerText);
    let paragraphString = paragraphTexts.join('\\n');
    return paragraphString;
"""
    # Execute the JavaScript code to get all paragraph content in a single string
    paragraph_content = driver.execute_script(js_code)
    
    # Extract image URL (assuming image is in <img> tag)
    js_code = """
    let imageUrl = document.querySelector('div.imageWrapper img').getAttribute('src');
    return imageUrl;
"""

# Execute the JavaScript code to get the image URL
    image_url = driver.execute_script(js_code)

    image_url = "https://www.peninsula.com/"+image_url

    img_name = generate_random_filename()

    download_image(image_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    
    # Extract date (assuming date is in <p> tag with class 'date')
    js_code = """
    let date = document.querySelector('div.headline-footnote').innerText;
    return date;
"""
    # Execute the JavaScript code to get the date
    date = driver.execute_script(js_code)  # Adjust the selector for the date
    
    title = generate_title(title)

    date = date_format(date)
    # Prepare the data for CSV
    news_item = {
        "id": "",  # You can populate this if needed
        "title": title,
        "subtitle": generate_subtitle(title),  # Add subtitle if available or leave empty
        "slug": title.lower().replace(" ", "-").replace(",", "").replace(".", ""),  # Slug generated from title
        "lead": "",  # Add lead if available or leave empty
        "content": generate_news(paragraph_content),
        "image": "information/"+img_name,
        "type": "news",  # You can customize this if needed
        "custom_field": "",  # Add custom fields if needed
        "parent_id": "",  # Add parent ID if needed
        "created_at": date,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "added_timestamp": date,
        "language": "en",  # Modify as needed
        "seo_title": "",
        "seo_content": "",
        "seo_title_desc": "",
        "seo_content_desc": "",
        "category_id": "100"  # Add category ID if available
    }

    # Append the data to the list
    news_data.append(news_item)

# Quit the driver
driver.quit()


with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    for row in news_data:
        writer.writerow(row)

print(f"Data saved to {csv_file}")

if date == date_format(datetime.now().today()):
    
    insert_csv_data(csv_file,'informations')
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("WE DO NOT HAVE DATA FOR TODAY")