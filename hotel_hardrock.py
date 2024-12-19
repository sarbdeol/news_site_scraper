# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # import urllib.request
# # import os
# # import base64
# # import csv
# # from datetime import datetime

# # # Setup the Selenium WebDriver (Make sure chromedriver is installed and in PATH)
# # driver = webdriver.Chrome()  # Make sure chromedriver is in the PATH

# # # Open the target page
# # driver.get("https://hotel.hardrock.com/news/")

# # # Wait for the content to load (adjust timeout if needed)
# # driver.implicitly_wait(10)

# # # Create a directory to save the images
# # os.makedirs("hardrock_images", exist_ok=True)

# # # Define CSV headers
# # headers = [
# #     "id", "title", "slug", "lead", "content", "image_data", "type", 
# #     "custom_field", "parent_id", "created_at", "updated_at", 
# #     "language", "seo_title", "seo_content", "seo_title_desc", 
# #     "seo_content_desc", "category_id"
# # ]

# # # Open CSV file to write the data
# # csv_file = "hardrock_news.csv"
# # with open(csv_file, "w", newline="", encoding="utf-8") as file:
# #     writer = csv.writer(file)
# #     writer.writerow(headers)  # Write header row

# #     # Locate all blog post items
# #     blog_items = driver.find_elements(By.CSS_SELECTOR, ".blogPost")

# #     # Iterate through each blog post item
# #     for idx, item in enumerate(blog_items, start=1):
# #         try:
# #             # Extract title and URL
# #             title = item.find_element(By.CSS_SELECTOR, '.blogPostTitleLink').text
# #             url = item.find_element(By.CSS_SELECTOR, '.blogPostTitleLink').get_attribute('href')

# #             # Extract publication date
# #             date = item.find_element(By.CSS_SELECTOR, '.blogPostDate').text

# #             # Extract image URL (background-image from the style)
# #             img_element = item.find_element(By.CSS_SELECTOR, '.blogPostImagePreview')
# #             img_url = img_element.get_attribute('style').split('url(')[1].split(')')[0]

# #             # Download and save the image
# #             img_filename = f"hardrock_images/{title.replace(' ', '_')}.jpg"
# #             urllib.request.urlretrieve(img_url, img_filename)

# #             # Convert the image to base64
# #             with open(img_filename, "rb") as img_file:
# #                 img_data = base64.b64encode(img_file.read()).decode('utf-8')

# #             # Generate slug and content for SEO purposes
# #             slug = title.lower().replace(" ", "-")
# #             lead = f"Press release for {title} on {date}"
# #             content = lead  # Simple placeholder content
# #             type_ = "press_release"
# #             custom_field = None  # No custom field
# #             parent_id = None  # No parent ID
# #             created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #             language = "en"  # Assuming English language
# #             seo_title = title
# #             seo_content = lead
# #             seo_title_desc = title
# #             seo_content_desc = lead
# #             category_id = None  # No category ID

# #             # Write the data to the CSV file
# #             writer.writerow([
# #                 idx,             # id
# #                 title,           # title
# #                 slug,            # slug
# #                 lead,            # lead
# #                 content,         # content
# #                 img_data,        # image data (base64 encoded)
# #                 type_,           # type
# #                 custom_field,    # custom_field
# #                 parent_id,       # parent_id
# #                 created_at,      # created_at
# #                 updated_at,      # updated_at
# #                 language,        # language
# #                 seo_title,       # seo_title
# #                 seo_content,     # seo_content
# #                 seo_title_desc,  # seo_title_desc
# #                 seo_content_desc, # seo_content_desc
# #                 category_id,     # category_id
# #             ])

# #         except Exception as e:
# #             print(f"Error processing blog post {idx}: {e}")

# # # Close the browser
# # driver.quit()

# # print(f"Data saved to {csv_file}. Images saved in the 'hardrock_images' folder.")





# # # import os
# # # import requests
# # # import csv
# # # import time
# # # from datetime import datetime
# # # from selenium import webdriver
# # # from selenium.webdriver.chrome.options import Options
# # # from upload_and_reference import upload_photo_to_ftp
# # # from insert_csv_into_sql_db import insert_csv_data,generate_news,generate_random_filename,generate_subtitle,generate_title,check_and_remove_file

# # # # Set up Selenium WebDriver
# # # chrome_options = Options()
# # # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
# # # driver = webdriver.Chrome(options=chrome_options)

# # # # Base URL of the website
# # # base_url = "https://hotel.hardrock.com/news/"

# # # # Create a CSV file to store the data
# # # csv_file = "hardrock_scraped_data.csv"
# # # check_and_remove_file(csv_file)
# # # headers = [
# # #     "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
# # #     "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
# # #     "language", "seo_title", "seo_content", "seo_title_desc", 
# # #     "seo_content_desc", "category_id"
# # # ]

# # # # Open the CSV file and write headers if it doesn't exist
# # # if not os.path.exists(csv_file):
# # #     with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
# # #         writer = csv.writer(file)
# # #         writer.writerow(headers)

# # # # Load the main page
# # # driver.get(base_url)

# # # # JavaScript code to extract the href of the news article
# # # js_code = """
# # #     // Find the first <a> tag inside the blogPostTitleLink
# # #     let element = document.querySelector('.blogPostTitleLink');
# # #     return element ? element.getAttribute('href') : null;
# # # """

# # # # Execute the JavaScript code
# # # news_url = driver.execute_script(js_code)

# # # if news_url:
# # #     # Open the news article link in the browser
# # #     driver.get(news_url)

# # #     # Extract the title
# # #     title = driver.execute_script("""
# # #         let titleElement = document.querySelector('h3.blogPostTitleHeader');
# # #         return titleElement ? titleElement.innerHTML.trim().replace(/\\s+/g, ' ') : null;
# # #     """)

# # #     # Extract the publication date
# # #     date = driver.execute_script("""
# # #         let dateElement = document.querySelector('.blogPostDate');
# # #         return dateElement ? dateElement.textContent.trim() : null;
# # #     """)

# # #     # Extract the news content
# # #     js_code_content = """
# # #     let blogPostBody = document.querySelector('div.blogPostBody');
# # #     return blogPostBody ? blogPostBody.innerHTML : null;
# # #     """
# # #     p_content = driver.execute_script(js_code_content)

# # #     # Extract the image URL
# # #     js_script = """
# # #         return document.querySelector('img.blogPostImage').src;
# # #     """
# # #     image_url = driver.execute_script(js_script)

# # #     # Generate a unique ID for each record
# # #     unique_id = int(time.time())  # Use current timestamp as unique ID

# # #     # Generate image file name and path
# # #     image_folder = "hardrock_images"
# # #     os.makedirs(image_folder, exist_ok=True)
# # #     image_filename = f"news_image_{unique_id}.jpg"
# # #     image_path = os.path.join(image_folder, image_filename)

# # #     # Download the image locally
# # #     if image_url:
# # #         response = requests.get(image_url, stream=True)
# # #         if response.status_code == 200:
# # #             with open(image_filename, "wb") as file:
# # #                 for chunk in response.iter_content(1024):
# # #                     file.write(chunk)
# # #             print(f"Image saved at: {image_filename}")
# # #         else:
# # #             print("Failed to download the image.")
# # #     else:
# # #         print("No image URL found.")

# # #     # Prepare the row data
# # #     row = [
# # #         1, generate_title(title), generate_title(title), generate_title(title).replace(" ", "-").lower(), "", generate_news(p_content), "information/"+image_filename, "news",
# # #         "", "", datetime.strptime(date, '%B %d, %Y').strftime('%d %B %Y'), datetime.now().date(), time.strftime("%Y-%m-%d %H:%M:%S"), 
# # #         "en", "", "", "", "", "100"
# # #     ]
# # #     #datetime.strptime(str(date),'%d %b %Y').strftime('%d %B %Y')
# # #     # Append the row to the CSV file
# # #     with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
# # #         writer = csv.writer(file)
# # #         writer.writerow(row)

# # #     upload_photo_to_ftp(image_filename,"/public_html/storage/information/")
    
# # #     # Print the extracted data
# # #     # print("Title:", title)
# # #     # print("Date:", date)
# # #     # print("Content:", p_content)
# # #     # print("Image URL:", image_url)

# # # else:
# # #     print("No news URL found.")

# # # # Quit the browser
# # # driver.quit()


# # # insert_csv_data(csv_file,"informations")




# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import json
# import time

# # Set up the Chrome WebDriver (make sure you have chromedriver installed)
# driver = webdriver.Chrome()

# # Step 1: Navigate to the Hard Rock News page
# driver.get('https://hotel.hardrock.com/news')

# # Step 2: Extract the href of the first blog post
# first_post_link = driver.find_element(By.CSS_SELECTOR, '.blogPostTitleLink').get_attribute('href')
# print('Post link:', first_post_link)

# # Step 3: Navigate to the post page
# driver.get(first_post_link)

# # Step 4: Extract the title
# title = driver.find_element(By.CSS_SELECTOR, '.blogPostTitleHeader h1').text
# print('Title:', title)

# # Step 5: Extract the date
# date = driver.find_element(By.CSS_SELECTOR, '.blogPostDate').text
# print('Date:', date)

# # Step 6: Extract the content (news excerpt)
# content = driver.find_element(By.CSS_SELECTOR, '.blogPostExcerpt').text
# print('Content:', content)

# # Step 7: Extract image URL from JSON-LD script
# script_tag = driver.find_element(By.CSS_SELECTOR, 'script[type="application/ld+json"]').get_attribute('innerHTML')
# json_data = json.loads(script_tag)
# image_url = json_data['image'][0]  # Extracting the image URL from the JSON-LD data
# print('Image URL:', image_url)

# # Give time to load content properly before quitting
# time.sleep(3)

# # Close the WebDriver
# driver.quit()







import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Setup Chrome in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Uncomment to run headlessly
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)  # Ensure chromedriver is installed and in PATH

# Define the target URL
url = "https://hotel.hardrock.com/news/"  # Replace with the actual URL of the news page
driver.get(url)

# Wait for the first 'href' to load and navigate to the URL
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.blogPostReadMoreLink')))
driver.execute_script("""
    var firstLink = document.querySelector('a.blogPostReadMoreLink').getAttribute('href');
    window.location.href = firstLink;
""")

# Wait for the new page to load completely
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.blogPostTitleHeader')))

# Extract title, date, and image from the opened page
try:
    # Wait for the image URL to load
    image_url = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img.blogPostImage'))).get_attribute("src")
    
    img_name = generate_random_filename()

    download_image(image_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Extract date
    date = date_format(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.blogPostDate'))).get_attribute("data-date-format"))

    # Extract title text
    title_text = driver.execute_script("""
        var title = document.querySelector('.blogPostTitleHeader').textContent;
        return title;
    """)

    title_text = generate_title(title_text)
    print(title_text)
    # Extract paragraph text (content)
    paragraph_text = driver.execute_script("""
        var paragraphs = document.querySelectorAll('.blogPostBody p');
        var paragraphText = Array.from(paragraphs).map(p => p.textContent).join(' ');
        return paragraphText;
    """)
    paragraph_text = generate_news(paragraph_text)
    # Create a row of data
    row = [
        "1",  # You can set a unique ID for each entry
        title_text,
        generate_subtitle(title_text),  # Subtitle (not available in the current data, you can leave it blank)
        title_text.lower().replace(" ","-"),  # Slug (not available in the current data, you can leave it blank)
        "",  # Lead (not available in the current data, you can leave it blank)
        paragraph_text,
        "information/"+img_name,
        "",  # Type (not available in the current data, you can leave it blank)
        "",  # Custom field (not available in the current data, you can leave it blank)
        "",  # Parent ID (not available in the current data, you can leave it blank)
        date,
        datetime.now().today(),  # Assuming updated_at is the same as created_at for now
        date,  # Added timestamp (not available in the current data, you can leave it blank)
        "en",  # Assuming English language for now
        "",  # SEO Title (not available in the current data, you can leave it blank)
        "",  # SEO Content (not available in the current data, you can leave it blank)
        "",  # SEO Title Description (not available in the current data, you can leave it blank)
        "",  # SEO Content Description (not available in the current data, you can leave it blank)
        100   # Category ID (not available in the current data, you can leave it blank)
    ]

    # Check if the file exists, and write the header only if the file is empty
    file_exists = False
    try:
        with open("extracted_data.csv", "r", newline="", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        pass

    # Write the header if the file doesn't exist yet
    if not file_exists:
        with open("extracted_data.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write header

    # Write the data to the CSV file
    with open("extracted_data.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(row)  # Write the row data

    print("Data successfully written to CSV.")

except Exception as e:
    print(f"Error extracting data: {e}")

# Quit the browser
driver.quit()

if date==date_format(datetime.now().today()):
    append_unique_records("extracted_data.csv","combined_news_data.csv")
    insert_csv_data("extracted_data.csv",'informations')
else:
    print("WE DO NOT HAVE DATA FOR TODAY")