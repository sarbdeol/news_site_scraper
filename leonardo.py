# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import pandas as pd
# import os
# import requests
# import shutil
# from insert_csv_into_sql_db import insert_into_db, check_and_remove_file, generate_news

# # Set up Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
# chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
# chrome_options.add_argument("--no-sandbox")  # Disable sandbox for headless mode
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
# )  # Set user-agent to mimic a real browser

# # Initialize WebDriver
# driver = webdriver.Chrome(options=chrome_options)
# url = "https://www.leonardo-hotels.com/press"  # Target page URL
# driver.get(url)

# # JavaScript code to extract titles, dates, and image URLs
# js_code = """
# const articles = document.querySelectorAll('a.press__release');
# const data = Array.from(articles).map((article, index) => {
#     const title = article.querySelector('h5')?.innerText || '';
#     const date = article.querySelector('small > span')?.innerText || '';
#     const img = article.querySelector('img')?.src || '';
#     return { id: index + 1, title, date, img };
# });
# return data;
# """

# # Execute JavaScript to get data
# news_data = driver.execute_script(js_code)

# # Prepare image folder
# image_folder = "leonardo_news_data_images"
# if os.path.exists(image_folder):
#     print(f"Folder '{image_folder}' exists. Deleting and creating a new one...")
#     shutil.rmtree(image_folder)  # Remove the folder and its contents
# os.makedirs(image_folder, exist_ok=True)

# # Prepare data for CSV
# data = []

# for item in news_data:
#     title = generate_news(item['title'])
#     date = item['date']
#     img_url = item['img']
#     image_filename = None

#     # Save image locally
#     if img_url:
#         try:
#             # Log the image URL
#             print(f"Downloading image from URL: {img_url}")
            
#             # Validate and sanitize filename
#             if img_url.startswith('http'):
#                 sanitized_title = title.replace(' ', '_').replace('/', '_')
#                 image_filename = os.path.join(image_folder, f"{sanitized_title}.jpg")
                
#                 # Download image
#                 img_data = requests.get(img_url, timeout=10)
#                 img_data.raise_for_status()  # Ensure valid HTTP response
                
#                 # Save image
#                 with open(image_filename, 'wb') as img_file:
#                     img_file.write(img_data.content)
#                 print(f"Image saved as: {image_filename}")
#             else:
#                 print(f"Invalid image URL: {img_url}")
#         except requests.exceptions.RequestException as e:
#             print(f"Failed to download image from {img_url}. Error: {e}")
#             image_filename = None

#     # Add data row in the expected format
#     data.append([
#         item['id'],  # id
#         title,  # title
#         title.replace(" ", "-").lower(),  # slug
#         "",  # lead
#         "",  # content
#         image_filename or "",  # image
#         "news",  # type
#         "",  # custom_field
#         "",  # parent_id
#         date,  # created_at
#         date,  # updated_at
#         "en",  # language
#         title,  # seo_title
#         "",  # seo_content
#         title,  # seo_title_desc
#         "",  # seo_content_desc
#         "1"  # category_id
#     ])

# # Define CSV headers
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at",
#     "language", "seo_title", "seo_content", "seo_title_desc",
#     "seo_content_desc", "category_id"
# ]

# # Save data to a CSV
# output_file = "leonardo_news_data.csv"
# check_and_remove_file(output_file)  # Remove file if it exists
# df = pd.DataFrame(data, columns=headers)  # Add headers explicitly
# df.to_csv(output_file, index=False, header=True)  # Include headers in the CSV

# print(f"Scraping completed. Data saved to '{output_file}'. Images stored in '{image_folder}/'.")

# # Quit WebDriver
# driver.quit()

# # Insert data into the database
# # insert_into_db(output_file)









import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,insert_csv_data
from insert_csv_into_sql_db import generate_random_filename,download_image,date_format,append_unique_records
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


# Add headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.rotana.com",  # Set a referer from the same domain if needed
}
# Setup Selenium WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Set up WebDriver (replace with the path to your ChromeDriver)

wait = WebDriverWait(driver, 30)  # Increase the wait time

# Navigate to the webpage
driver.get("https://www.leonardo-hotels.com/press")  # Replace with the target URL

# Define headers for CSV
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Sample data to write, you can populate these dynamically with your scraped content
data = {
    "id": "1",  # For example, could be dynamically generated or scraped
    "title": None,
    "subtitle":None,
    "slug": None,
    "lead": None,
    "content": None,
    "image": None,
    "type": None,
    "custom_field": None,
    "parent_id": None,
    "created_at": None,
    "updated_at": None,
    "added_timestamp": None, 
    "language": None,
    "seo_title": None,
    "seo_content": None,
    "seo_title_desc": None,
    "seo_content_desc": None,
    "category_id": None
}

try:
    # Wait until the link is visible (use the appropriate CSS selector to find the <a> tag)
    press_release_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".press__release")))

    # Use JavaScript to click on the link (to open the href)
    driver.execute_script('arguments[0].click();', press_release_link)

    # Optionally, you can wait for the new page to load
    # wait.until(EC.url_changes(driver.current_url))

    # Wait until the image is visible
    img_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='leonardo-hotels-employees']")))

    # Extract the src URL using JavaScript
    image_url = driver.execute_script('return arguments[0].src;', img_element)
      # Save the image URL

    img_name = generate_random_filename()

    download_image(data['image'],img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Wait for the article to load
    article_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.col-12.w-lg-75.mx-auto.my-5.images_fix")))

    # Extract Title using JavaScript
    title = driver.execute_script("""
        var titleElement = document.querySelector('article p strong');
        return titleElement ? titleElement.innerText.trim() : null;
    """)
     # Save the title

    # Extract Date using JavaScript (it's assumed to be in a <small> element inside the article)
    date = driver.execute_script("""
        var pTags = document.querySelectorAll('article p');
        var date = null;

        pTags.forEach(function(p) {
            var text = p.innerText;
            // Use regex to search for a date pattern
            var match = text.match(/\\d{1,2}\\. [A-Za-z]+ \\d{4}/);  // Matches "19. November 2024"
            if (match) {
                date = match[0];  // Save the matched date
            }
        });

        return date;
    """)
      # Save the date as the creation date

    # Extract all <p> tags inside the article and concatenate their content
    paragraphs = driver.execute_script("""
        var pTags = document.querySelectorAll('article p');
        var text = '';
        pTags.forEach(function(p) {
            text += p.innerText + '\\n';  // Add newline after each paragraph for readability
        });
        return text;
    """)  # Save the article content

    # Set other data fields as needed
    title=generate_title(title) 
    data['id']=1
    data['title']=title
    data['subtitle']=generate_subtitle(title)
    data['slug'] = title.lower().replace(" ","-")  # Assign dynamically if possible
    data['lead'] = ""  # Assign dynamically if possible
    data['content'] = generate_news(paragraphs)
    data['image'] = 'information/'+img_name
    data['type'] = ""  # Example, assign based on actual content
    data['custom_field'] = ""  # Optional, assign if applicable
    data['parent_id'] = ""  # Optional, assign if applicable
    data['created_at'] = date_format(date)
    data['updated_at'] = datetime.now().today() # If not available, use created_at
    date['added_timestamp'] = date_format(date)
    data['language'] = ""  # Optional, assign the language
    data['seo_title'] = ""  # Optional, assign dynamically if applicable
    data['seo_content'] = ""  # Optional, assign dynamically if applicable
    data['seo_title_desc'] = ""  # Optional, assign dynamically if applicable
    data['seo_content_desc'] = ""  # Optional, assign dynamically if applicable
    data['category_id'] = 100  # Example, assign dynamically if applicable


    csv_file = "Scraped_data.csv"
    # Write the data to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(data)  # Write the scraped data

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()

if date ==  datetime.now().today():
    insert_csv_data(csv_file,"informations")
    append_unique_records(csv_file,"combined_news_data.csv")
else:
    print("WE DO NOT HAVE DATA FOR TODAY")