# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # import os
# # import urllib.request
# # import csv
# # from datetime import datetime

# # # Setup the Selenium WebDriver (use appropriate WebDriver for your browser)
# # driver = webdriver.Chrome()  # Make sure chromedriver is installed and in PATH

# # # Navigate to the webpage containing the HTML content
# # driver.get("https://www.germainhotels.com/en/about/mediaroom/")  # Change this to the URL you need

# # # Wait for the table to be visible
# # wait = WebDriverWait(driver, 10)
# # press_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.css-8atqhb')))

# # # Locate all press release rows in the table
# # press_rows = driver.find_elements(By.CSS_SELECTOR, 'table.css-8atqhb tbody tr')

# # # Create a directory to save the images
# # os.makedirs("germainhotels_images", exist_ok=True)

# # # Define CSV headers
# # headers = [
# #     "id", "title","subtitle", "slug", "lead", "content", "image", "type", 
# #     "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp"
# #     "language", "seo_title", "seo_content", "seo_title_desc", 
# #     "seo_content_desc", "category_id"
# # ]

# # # Open CSV file to write the data
# # csv_file = "germainhotels_news.csv"
# # with open(csv_file, "w", newline="", encoding="utf-8") as file:
# #     writer = csv.writer(file)
# #     writer.writerow(headers)  # Write header row

# #     # Iterate through the rows and extract details
# #     for idx, row in enumerate(press_rows, start=1):
# #         try:
# #             # Extract title
# #             title_element = row.find_element(By.CSS_SELECTOR, '.css-stz03g')
# #             title = title_element.text if title_element else "No Title"

# #             # Extract date
# #             # Locate the table cell element
# #             element = driver.find_element(By.CLASS_NAME, 'css-wk7ht')
# #             # Execute JavaScript to extract the content
# #             js_script = "document.querySelector('.css-1asonfv').innerText;"
# #             date = driver.execute_script(js_script, element)

# #             if date==datetime.now().date():

# #                 date_element = row.find_element(By.CSS_SELECTOR, '.css-tlj14j')
# #                 date = date_element.text if date_element else "No Date"

# #                 # Extract city
# #                 city_element = row.find_element(By.CSS_SELECTOR, '.css-ruc5cq')
# #                 city = city_element.text if city_element else "No City"

# #                 # Image URL (If available, otherwise set a default)
# #                 img_url = "default_image_url_here"  # Set a default image URL if none is found
# #                 img_filename = f"germainhotels_images/{title.replace(' ', '_')}.jpg"
                
# #                 # Download the image if the URL is valid
# #                 if img_url != "default_image_url_here":
# #                     urllib.request.urlretrieve(img_url, img_filename)
# #                     print(f"Saved: {img_filename}")
# #                 else:
# #                     print("No image found, skipping download.")

# #                 # Populate other fields based on provided HTML
# #                 slug = title.lower().replace(" ", "-")
# #                 lead = date  # Using date as lead for simplicity
# #                 content = lead  # Using lead as content for simplicity
# #                 type_ = "press_release"  # Assuming press release type
# #                 custom_field = None  # No custom field provided, set as None
# #                 parent_id = None  # No parent_id provided, set as None
# #                 created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Using current timestamp
# #                 language = "en"  # Assuming English language
# #                 seo_title = title
# #                 seo_content = lead
# #                 seo_title_desc = title
# #                 seo_content_desc = lead
# #                 category_id = None  # No category_id provided, set as None

# #                 # Write the data to the CSV
# #                 writer.writerow([
# #                     idx,             # id
# #                     title,           # title
# #                     slug,            # slug
# #                     lead,            # lead
# #                     content,         # content (using lead as content for simplicity)
# #                     img_url,    # image (local file path)
# #                     type_,           # type (hardcoded as press_release)
# #                     custom_field,    # custom_field
# #                     parent_id,       # parent_id
# #                     created_at,      # created_at
# #                     updated_at,      # updated_at
# #                     language,        # language
# #                     seo_title,       # seo_title
# #                     seo_content,     # seo_content
# #                     seo_title_desc,  # seo_title_desc
# #                     seo_content_desc, # seo_content_desc
# #                     category_id,     # category_id
# #                 ])

# #         except Exception as e:
# #             print(f"Error processing row {idx}: {e}")

# # # Close the browser
# # driver.quit()

# # print(f"Data saved to {csv_file}. Images saved in the 'germainhotels_images' folder.")





# #_______________________________________________________________________________________________



# import os
# import csv
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from datetime import datetime
# from PIL import Image
# from io import BytesIO
# from urllib.parse import urljoin

# # Function to initialize the WebDriver in headless mode
# def initialize_driver():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Enable headless mode
#     chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
#     chrome_options.add_argument("--no-sandbox")  # Ensure it runs on systems without a display

#     # Setup the WebDriver (adjust path to your chromedriver if necessary)
#     driver = webdriver.Chrome(options=chrome_options)
#     return driver

# # Function to save extracted data to CSV
# def save_to_csv(data, idx, csv_file, headers):
#     with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
#         writer = csv.DictWriter(file, fieldnames=headers)
#         writer.writerow({
#             "id": idx,
#             "title": data['title'],
#             "subtitle": "",  # Empty, assuming no subtitle
#             "slug": data['slug'],
#             "lead": data['lead'],
#             "content": data['content'],
#             "image": data['image'],
#             "type": data['type'],
#             "custom_field": data['custom_field'],
#             "parent_id": data['parent_id'],
#             "created_at": data['created_at'],
#             "updated_at": data['updated_at'],
#             "added_timestamp": data['added_timestamp'],
#             "language": data['language'],
#             "seo_title": data['seo_title'],
#             "seo_content": data['seo_content'],
#             "seo_title_desc": data['seo_title_desc'],
#             "seo_content_desc": data['seo_content_desc'],
#             "category_id": data['category_id']
#         })

# # Function to extract content and images from a news article page
# def extract_article_content_and_images(driver, article_url):
#     # Navigate to the article page
#     driver.get(article_url)
    
#     # Extract the content
#     content = ""
#     try:
#         content_element = driver.find_element(By.CSS_SELECTOR, '.article-content')  # Replace with actual selector
#         content = content_element.text.strip()
#     except Exception as e:
#         print(f"Error extracting content from {article_url}: {e}")

#     # Extract images from the article
#     images = []
#     try:
#         img_elements = driver.find_elements(By.TAG_NAME, 'img')  # Get all images
#         for img_element in img_elements:
#             img_url = img_element.get_attribute('src')
#             if img_url:
#                 images.append(img_url)
#     except Exception as e:
#         print(f"Error extracting images from {article_url}: {e}")
    
#     return content, images

# # Initialize WebDriver in headless mode
# driver = initialize_driver()

# # Directory to save images
# image_dir = "germainhotels_images"
# os.makedirs(image_dir, exist_ok=True)

# # CSV file to store data
# csv_file = "germainhotels_news.csv"
# headers = [
#     "id", "title", "subtitle", "slug", "lead", "content", "image", "type", 
#     "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Create and write header row to CSV
# with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()

# # Navigate to the target page
# driver.get('https://www.germainhotels.com/en/about/mediaroom')  # Replace with the correct URL

# # Locate all rows with the target class (update this based on actual HTML structure)
# rows = driver.find_elements(By.CLASS_NAME, 'css-17zgd0x')

# # Loop through each row and extract data
# for idx, row in enumerate(rows, start=1):
#     try:
#         js_script = """
#         let row = arguments[0];
#         let href = row.getAttribute('href') || row.closest('[role="link"]').getAttribute('href');
#         let title = row.querySelector('.css-stz03g').innerText;
#         let date = row.querySelector('.css-1asonfv').innerText;
#         let image = row.querySelector('img') ? row.querySelector('img').src : null;
#         return { href, title, date, image };
#         """
#         data = driver.execute_script(js_script, row)

#         # Open the link to extract content and images
#         content = ""
#         images = []

#         if data['href']:
#             # Open the article page
#             content, images = extract_article_content_and_images(driver, data['href'])

#         # Save images locally
#         image_names = []
#         for img_url in images:
#             image_name = f"{data['title'].replace(' ', '_')}_{images.index(img_url)}.jpg"
#             image_path = os.path.join(image_dir, image_name)

#             # Check if the image URL is valid
#             response = requests.get(img_url)
#             if response.status_code == 200:
#                 # Open the image and resize it
#                 image = Image.open(BytesIO(response.content))

#                 # Resize the image to 865x590
#                 image_resized = image.resize((865, 590))

#                 # Save the resized image
#                 image_resized.save(image_path)
#                 image_names.append(image_name)
#                 print(f"Image saved: {image_name}")
#             else:
#                 print(f"Failed to download image: {img_url}")

#         # Prepare the data for saving
#         slug = data['title'].lower().replace(" ", "-")
#         lead = data['date']  # Using the date as the lead for simplicity
#         content = content if content else lead  # Use the scraped content or fallback to lead
#         type_ = "press_release"  # Assuming press release type
#         custom_field = None  # No custom field provided
#         parent_id = None  # No parent_id provided
#         created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
#         added_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Same as created_at
#         language = "en"  # Assuming English language
#         seo_title = data['title']
#         seo_content = lead
#         seo_title_desc = data['title']
#         seo_content_desc = lead
#         category_id = None  # No category_id provided

#         # Collect data to save to CSV
#         data_to_save = {
#             "title": data['title'],
#             "slug": slug,
#             "lead": lead,
#             "content": content,
#             "image": ', '.join(image_names),  # Save multiple image names
#             "type": type_,
#             "custom_field": custom_field,
#             "parent_id": parent_id,
#             "created_at": created_at,
#             "updated_at": updated_at,
#             "added_timestamp": added_timestamp,
#             "language": language,
#             "seo_title": seo_title,
#             "seo_content": seo_content,
#             "seo_title_desc": seo_title_desc,
#             "seo_content_desc": seo_content_desc,
#             "category_id": category_id
#         }

#         # Save the extracted data to CSV
#         save_to_csv(data_to_save, idx, csv_file, headers)

#     except Exception as e:
#         print(f"Error processing row {idx}: {e}")

# # Close the WebDriver
# driver.quit()

# print(f"Data extraction completed. CSV saved to {csv_file}, and images saved in {image_dir}/")



import csv
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from insert_csv_into_sql_db import date_format
from datetime import datetime
from insert_csv_into_sql_db import generate_news, generate_subtitle, generate_title, insert_csv_data,append_unique_records
from selenium.webdriver.chrome.options import Options
from upload_and_reference import upload_photo_to_ftp

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--no-sandbox")  # Disable sandbox
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)

# Start the WebDriver
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.germainhotels.com/en/about/mediaroom')

# Wait for the page to load
time.sleep(3)

# Create image folder if not exists
image_folder = "germainhotels_images"
os.makedirs(image_folder, exist_ok=True)

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Define CSV output file
output_file = "germainhotels_data.csv"

# Define function to write rows
def write_row_to_csv(writer, row_data):
    writer.writerow(row_data)

# Open the CSV for writing
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)  # Write headers

    rows = driver.find_elements(By.CSS_SELECTOR, 'tr[role="link"]')
    for idx, row in enumerate(rows, start=1):
        try:
            # Extract data
            title = row.find_element(By.CSS_SELECTOR, 'td.css-stz03g').text
            date = row.find_element(By.CSS_SELECTOR, 'span.css-tlj14j').text
            location = row.find_element(By.CSS_SELECTOR, 'td.css-ruc5cq').text

            # Click Details link
            row.find_element(By.CSS_SELECTOR, 'td.css-uknx5e').click()
            time.sleep(3)

            # Get image URL
            image_url = driver.execute_script("""
                var img = document.querySelector('figure img');
                return img ? img.src : null;
            """)
            image_path = None
            if image_url:
                image_name = f"{idx}.jpg"
                image_path = os.path.join(image_folder, image_name)
                img_data = requests.get(image_url).content
                with open(image_path, "wb") as img_file:
                    img_file.write(img_data)
                upload_photo_to_ftp(image_name, "/public_html/storage/information/")

            # Get page content
            content = driver.execute_script("""
                return Array.from(document.querySelectorAll('p'))
                           .map(p => p.innerText)
                           .join(' ');
            """)

            # Generate data
            formatted_date = date_format(date)
            title = generate_title(title)
            row_data = [
                idx, title, generate_subtitle(title), title.replace(" ", "-"), "",
                generate_news(content), f"information/{os.path.basename(image_path)}" if image_path else "",
                "", "", "", formatted_date, datetime.now().date(), formatted_date, "en", '', '', '', '', '100'
            ]

            # Write to CSV
            write_row_to_csv(writer, row_data)

            # Go back to the main page
            driver.back()
            time.sleep(3)

        except Exception as e:
            print(f"Error processing row {idx}: {e}")

# Close the driver and insert data
driver.quit()
if date_format(date) == date_format(datetime.now().today()):
    insert_csv_data(output_file, 'informations')
    append_unique_records(output_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")



# print(f"Data saved to {output_file}. Images saved in {image_folder}.")
