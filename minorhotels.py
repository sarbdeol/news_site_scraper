# import json
# import csv
# import os
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import shutil
# from insert_csv_into_sql_db import generate_news,insert_into_db,check_and_remove_file
# # Configure Selenium WebDriver
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# driver = webdriver.Chrome(service=Service(), options=chrome_options)

# # Output paths
# output_csv = "minorhotels_news_data.csv"
# check_and_remove_file(output_csv)

# image_folder = "minorhotels_news_images"


# if os.path.exists(image_folder):
#     print(f"Folder '{image_folder}' exists. Deleting and creating a new one...")
#     shutil.rmtree(image_folder)  # Remove the folder and its contents
# os.makedirs(image_folder, exist_ok=True)

# # JavaScript to extract the data
# js_code = """
# return Array.from(document.querySelectorAll(".c-card")).map(card => {
#     const titleElement = card.querySelector(".c-card__title a");
#     const timeElement = card.querySelector("time.c-card__time");
#     const linkElement = card.querySelector("a.c-card__img-holder");
#     const imageElement = card.querySelector(".bg-retina");

#     const title = titleElement ? titleElement.innerText.trim() : null;
#     const date = timeElement ? timeElement.getAttribute("datetime") : null;
#     const url = linkElement ? linkElement.href : null;

#     // Extract background image URL from inline style
#     const image = imageElement && imageElement.style.backgroundImage
#         ? imageElement.style.backgroundImage.replace(/url\\(["']?(.+?)["']?\\)/, '$1')
#         : null;

#     return { title, date, url, image };
# });
# """

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

# # Open the target website and extract data
# def scrape_news(url):
#     driver.get(url)

#     # Execute the JavaScript to extract data
#     results = driver.execute_script(js_code)
#     return results

# # Save data to CSV
# def save_to_csv(data, output_csv):
#     headers = ["title", "date", "url", "image"]
#     with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.DictWriter(file, fieldnames=headers)
#         writer.writeheader()
#         writer.writerows(data)

# # Main script
# target_url = "https://media.minorhotels.com/en-GLO/"  # Replace with the actual URL
# scraped_data = scrape_news(target_url)

# # Process and download images
# processed_data = []
# for idx, item in enumerate(scraped_data, start=1):
#     if item["image"]:
#         image_name = f"news_{idx}.jpg"
#         item["image"] = download_image(item["image"], image_name)
#     processed_data.append(item)

# # Save the processed data to CSV
# save_to_csv(processed_data, output_csv)

# print(f"Scraping complete. Data saved in {output_csv} and images in {image_folder}")

# # Quit the driver
# driver.quit()










import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from insert_csv_into_sql_db import download_image,check_and_remove_file,insert_csv_data
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,append_unique_records
from insert_csv_into_sql_db import generate_random_filename,date_format
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime

# Set up WebDriver (replace with the path to your ChromeDriver)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Uncomment if you want to run headless
driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 20)  # Increase the wait time

# Define the headers for the CSV
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

def scrape_news():
    try:
        # Navigate to the webpage
        driver.get("https://media.minorhotels.com/en-GLO/")  # Replace with the target URL

        # Wait for the news card to load
        card = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "c-card")))

        # Extract the title using JavaScript
        title = driver.execute_script(""" 
            return document.querySelector('h2.c-card__title a').textContent.trim();
        """)
        print("Title:", title)

        # Extract the date
        date_element = card.find_element(By.CSS_SELECTOR, "time.c-card__time")
        date = date_element.get_attribute("datetime")

        # Click the link to navigate to the article
        driver.execute_script('document.querySelector("h2.h5.c-card__title a").click();')

        # Extract the image URL
        image_url = driver.execute_script('return document.querySelector(".c-image-wrap .c-image__thumbnail").src;')
        print("Image URL:", image_url)

        img_name = generate_random_filename()

        download_image(image_url,img_name)
        upload_photo_to_ftp(img_name,"/public_html/storage/information/")
        # Wait for the article content to load
        time.sleep(2)  # Added delay to ensure page content is loaded

        # Execute JavaScript to extract paragraph text as a single string
        paragraphs_text = driver.execute_script('''
            var paragraphs = document.getElementsByTagName('p');
            var result = '';
            for (var i = 0; i < paragraphs.length; i++) {
                result += paragraphs[i].innerText + '\\n';  // Adding newline for separation
            }
            return result;
        ''')

        # Print the content
        # print("Content:", paragraphs_text)

        title = generate_title(title)

        date  = date_format(date)

        # Prepare the data for CSV
        data = [
            "1",  # id, placeholder for example
            title,  # title
            generate_subtitle(title),  # subtitle, placeholder as the structure doesn't provide it
            title.lower().replace(" ","-"),  # slug, placeholder
            "",  # lead, placeholder
            generate_news(paragraphs_text),  # content
            "information/"+img_name,  # image URL
            "",  # type, placeholder (assuming it's an article)
            "",  # custom_field, placeholder
            "",  # parent_id, placeholder
            date,  # created_at
            datetime.now().today(),  # updated_at
            date,  # added_timestamp (current time in UNIX format)
            "en",  # language (hardcoded for now)
            "",  # seo_title, placeholder
            "",  # seo_content, placeholder
            "",  # seo_title_desc, placeholder
            "",  # seo_content_desc, placeholder
            100   # category_id, placeholder
        ]
        csv_file = 'scraped_data.csv'

        check_and_remove_file(csv_file)
        # Save data to CSV
        with open(csv_file,'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Write headers if the file is empty
                writer.writerow(headers)
            writer.writerow(data)

        print("Data saved to CSV.")

    except TimeoutException:
        print("Failed to load the page or locate elements.")
    finally:
        driver.quit()

    if date == date_format(datetime.now().today()):
        insert_csv_data(csv_file,"informations")
        append_unique_records(csv_file,"combined_news_data.csv")

    else:
        print("--------WE DO NOT HAVE DATA FOR TODAY--------")

# Execute the scraping function
scrape_news()
