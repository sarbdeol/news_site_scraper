# import os
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# import csv
# import uuid
# import time
# import shutil
# from insert_csv_into_sql_db import insert_into_db,generate_news,check_and_remove_file

# # Configure WebDriver
# options = Options()
# # options.add_argument("--headless")  # Disable for debugging
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# # Set up Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
# chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
# chrome_options.add_argument("--no-sandbox")  # Disabling sandbox for headless mode
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
# )  # Set user-agent to mimic a real browser

# # Path to chromedriver (ensure chromedriver is installed and accessible)
# driver = webdriver.Chrome(options=chrome_options)

# # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # URL to scrape
# URL = "https://www.louvrehotels.com/en-us/news/"
# driver.get(URL)

# # Wait for elements to load
# try:
#     WebDriverWait(driver, 20).until(
#         EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ConfigurableMediaAndTextBlock-styled__Wrapper-lhg__sc-8d273b9a-0'))
#     )
# except Exception as e:
#     print(f"Error waiting for elements: {e}")

# # Scroll to the bottom to load all content
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# time.sleep(3)  # Wait a few seconds for content to load

# # JavaScript to extract data
# script = """
# let articles = document.querySelectorAll('.ConfigurableMediaAndTextBlock-styled__Wrapper-lhg__sc-8d273b9a-0');
# let data = [];
# articles.forEach(article => {
#     let title = article.querySelector('.ConfigurableMediaAndTextBlock-styled__Title-lhg__sc-8d273b9a-4')?.innerText || '';
#     let date = article.querySelector('.ConfigurableMediaAndTextBlock-styled__Tagline-lhg__sc-8d273b9a-5')?.innerText || '';
#     let description = article.querySelector('.ConfigurableMediaAndTextBlock-styled__Description-lhg__sc-8d273b9a-6')?.innerText || '';
#     let image = article.querySelector('.ConfigurableMediaAndTextBlock-styled__Image-lhg__sc-8d273b9a-18')?.src || '';
#     let link = article.querySelector('.ConfigurableMediaAndTextBlock-styled__CtaButton-lhg__sc-8d273b9a-10')?.href || '';
#     data.push({ title, date, description, image, link });
# });
# return data;
# """

# # Execute JavaScript
# news_data = driver.execute_script(script)

# # Prepare data with specified headers
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Create a directory to store images
# image_dir = "lourehotels_images"
# os.makedirs(image_dir, exist_ok=True)

# # Process each article and add data in the format specified
# processed_data = []
# for article in news_data:
#     # Simulate the data extraction and filling in placeholders
#     image_url = article.get("image", "")
    
#     # Download the image and save it locally
#     if image_url:
#         try:
#             image_name = os.path.basename(image_url)  # Extract the image filename
#             image_path = os.path.join(image_dir, image_name)
#             # Download the image
#             img_data = requests.get(image_url).content
#             with open(image_path, 'wb') as img_file:
#                 img_file.write(img_data)
#         except Exception as e:
#             print(f"Error downloading image: {e}")
#             image_path = ""  # If there's an error, leave the image path empty
#     else:
#         image_path = ""
    
#     processed_article = {
#         "id": str(uuid.uuid4()),  # Generate a unique ID for each article
#         "title": generate_news(article.get("title", "")),
#         "slug": article.get("title", "").lower().replace(" ", "-"),  # Create a slug from the title
#         "lead": article.get("description", ""),
#         "content": article.get("description", ""),
#         "image": image_path,  # Save the local image path
#         "type": "news",  # Assuming it's news type
#         "custom_field": "",  # Empty field for custom data
#         "parent_id": "",  # Empty field for parent ID
#         "created_at": article.get("date", ""),
#         "updated_at": article.get("date", ""),
#         "language": "en",  # Assuming English content
#         "seo_title": article.get("title", ""),
#         "seo_content": article.get("description", ""),
#         "seo_title_desc": article.get("title", ""),
#         "seo_content_desc": article.get("description", ""),
#         "category_id": "1"  # Assuming category ID 1 for news
#     }
#     processed_data.append(processed_article)

# # Save to CSV
# csv_file = "lourehotels_news_data.csv"

# check_and_remove_file(csv_file)

# if processed_data:
#     with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.DictWriter(file, fieldnames=headers)
#         writer.writeheader()
#         writer.writerows(processed_data)
#     print(f"Data saved to {csv_file}")
# else:
#     print("No data to save.")

# # Close the driver
# driver.quit()


# # insert_into_db(csv_file)










import time
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,check_and_remove_file,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import download_image,date_format,insert_csv_data
from datetime import datetime

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Set up WebDriver with headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Uncomment for headless mode
driver = webdriver.Chrome(options=chrome_options)

# Prepare data to save in CSV
news_data = []

try:
    # Load the webpage
    driver.get("https://www.louvrehotels.com/en-us/news/")  # Replace with the actual URL
    time.sleep(2)  # Wait for the page to load

    # Execute JavaScript to click the "Accept All" button

    time.sleep(20)

    try:
        driver.execute_script("""
            document.getElementById('onetrust-accept-btn-handler').click();
        """)

    except:

        # Wait for the page to load fully after accepting the cookies
        time.sleep(20)

        # Execute JavaScript to extract the title
        title = driver.execute_script("""
            return document.querySelector(".ConfigurableMediaAndTextBlock-styled__Title-lhg__sc-8d273b9a-4").textContent;
        """)

        # Execute JavaScript to extract the date
        date = driver.execute_script("""
            return document.querySelector(".ConfigurableMediaAndTextBlock-styled__Tagline-lhg__sc-8d273b9a-5").textContent;
        """)

        # Execute JavaScript to extract the image URL
        image_url = driver.execute_script("""
            return document.querySelector("img.ConfigurableMediaAndTextBlock-styled__Image-lhg__sc-8d273b9a-18.cTASBf").src;
        """)

        # Execute JavaScript to extract the paragraph content
        paragraph_content = driver.execute_script("""
            return document.querySelector("div.ConfigurableMediaAndTextBlock-styled__Description-lhg__sc-8d273b9a-6.hUsutH p").textContent;
        """)


        title = generate_title(title).replace('"', '').replace("'", '')
        date = date_format(date)
        img_name = generate_random_filename()
        download_image(image_url,img_name)

        upload_photo_to_ftp(img_name,"/public_html/storage/information/")


        # Gather data in the required format
        news_item = {
            "id": "1",  # You can adjust the ID as per your logic
            "title": title,
            "subtitle": generate_subtitle(title),  # Add if there is a subtitle
            "slug": title.lower().replace('"',"").replace(" ","-"),  # Add if there's a slug
            "lead": "",  # Add lead if applicable
            "content": generate_news(paragraph_content),
            "image": "information/"+img_name,
            "type": "",  # Add if type is present
            "custom_field": "",  # Add custom field if applicable
            "parent_id": "",  # Add if parent ID is available
            "created_at": date,
            "updated_at": datetime.now().today(),  # Add if updated_at is available
            "added_timestamp": date,  # Add timestamp if applicable
            "language": "en",  # You can adjust based on language
            "seo_title": "",  # Add SEO title if applicable
            "seo_content": "",  # Add SEO content if applicable
            "seo_title_desc": "",  # Add SEO title description if applicable
            "seo_content_desc": "",  # Add SEO content description if applicable
            "category_id":  100# Add category ID if applicable
        }

        # Append the data
        news_data.append(news_item)

        # Define CSV file path
        csv_file_path = "louvrehotl_news_data.csv"
        check_and_remove_file(csv_file_path)
        # Write data to CSV
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()  # Write headers
            writer.writerows(news_data)  # Write data rows

        print("Data saved to CSV successfully!")

        if date ==  date_format(datetime.now().today()):
            insert_csv_data(csv_file_path,'informations')
            append_unique_records(csv_file_path,"combined_news_data.csv")
        else:
            print("--------WE DO NOT HAVE DATA FOR TODAY--------")

finally:
    driver.quit()


