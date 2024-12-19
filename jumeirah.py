# # import os
# # import csv
# # import requests
# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service
# # from selenium.webdriver.chrome.options import Options
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC

# # # Set up Selenium WebDriver in headless mode
# # chrome_options = Options()
# # chrome_options.add_argument("--headless")
# # chrome_options.add_argument("--disable-gpu")
# # chrome_options.add_argument("--no-sandbox")
# # chrome_options.add_argument("--disable-dev-shm-usage")
# # from insert_csv_into_sql_db import insert_into_db,check_and_remove_file,generate_news
# # import shutil

# # # Path to ChromeDriver (adjust this path if necessary)
# # driver = webdriver.Chrome(options=chrome_options)

# # # Target URL
# # url = "https://www.jumeirah.com/en/jumeirah-group/press-centre"  # Replace with the actual URL containing the HTML
# # driver.get(url)

# # # Wait for the page to load completely
# # try:
# #     WebDriverWait(driver, 10).until(
# #         EC.presence_of_all_elements_located((By.CLASS_NAME, "card"))
# #     )
# # except Exception as e:
# #     print(f"Error waiting for elements: {e}")
# #     driver.quit()
# #     exit()

# # # Execute JavaScript to scrape the data
# # js_code = """
# # let extractedData = [];
# # document.querySelectorAll('.card').forEach(card => {
# #     let title = card.querySelector('.card-title')?.textContent.trim() || 'No title';
# #     let dateText = card.querySelector('.card-text')?.textContent.match(/\\d{1,2}\\s\\w+\\s\\d{4}/)?.[0] || 'No date';
# #     let image = card.querySelector('.card-img')?.src || 'No image';
    
# #     extractedData.push({ title, date: dateText, image });
# # });
# # return extractedData;
# # """

# # data = driver.execute_script(js_code)

# # # Debugging: Print extracted data
# # print("Extracted Data:", data)

# # # Close the browser
# # driver.quit()

# # # Check if data is empty
# # if not data:
# #     print("No data extracted. Check the selectors or webpage structure.")
# #     exit()

# # # Prepare output folders
# # output_folder = "jumeirah_scraped_images"

# # if os.path.exists(output_folder):
# #     print(f"Folder '{output_folder}' exists. Deleting and creating a new one...")
# #     shutil.rmtree(output_folder)  # Remove the folder and its contents
# # os.makedirs(output_folder, exist_ok=True)  # Create a new folder


# # # Prepare CSV file with the required headers
# # csv_file = "jumeirah_news_data.csv"

# # check_and_remove_file(csv_file)

# # headers = [
# #     "id", "title", "slug", "lead", "content", "image", "type",
# #     "custom_field", "parent_id", "created_at", "updated_at", 
# #     "language", "seo_title", "seo_content", "seo_title_desc", 
# #     "seo_content_desc", "category_id"
# # ]

# # # Save data to CSV and download images
# # with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
# #     writer = csv.DictWriter(file, fieldnames=headers)
# #     writer.writeheader()

# #     for idx, item in enumerate(data):
# #         title = generate_news(item.get("title", "No title"))
# #         date = item.get("date", "No date")
# #         image_url = item.get("image", "No image")
        
# #         # Download and save the image
# #         image_path = "No image"
# #         if image_url and image_url != "No image":
# #             try:
# #                 response = requests.get(image_url, stream=True)
# #                 if response.status_code == 200:
# #                     # Generate a unique filename for the image
# #                     image_name = f"news_image_{idx + 1}.jpg"
# #                     image_path = os.path.join(output_folder, image_name)
                    
# #                     # Save the image locally
# #                     with open(image_path, "wb") as img_file:
# #                         for chunk in response.iter_content(1024):
# #                             img_file.write(chunk)
# #                     print(f"Image saved: {image_path}")
# #             except Exception as e:
# #                 print(f"Error downloading image {image_url}: {e}")

# #         # Prepare other fields (placeholders as we don't have them from the page)
# #         slug = title.lower().replace(" ", "-")  # Example: generate slug from title
# #         lead = "No lead"  # Placeholder
# #         content = "No content"  # Placeholder
# #         news_type = "press-release"  # Example: default type
# #         custom_field = "No custom field"  # Placeholder
# #         parent_id = "1"  # Placeholder
# #         created_at = date  # Use date as created_at
# #         updated_at = date  # Use date as updated_at
# #         language = "en"  # Example: English
# #         seo_title = title  # Same as title for SEO
# #         seo_content = "No seo content"  # Placeholder
# #         seo_title_desc = "No seo title desc"  # Placeholder
# #         seo_content_desc = "No seo content desc"  # Placeholder
# #         category_id = "1"  # Placeholder for category_id

# #         # Write row to CSV
# #         writer.writerow({
# #             "id": idx + 1,
# #             "title": title,
# #             "slug": slug,
# #             "lead": lead,
# #             "content": content,
# #             "image": image_path,
# #             "type": news_type,
# #             "custom_field": custom_field,
# #             "parent_id": parent_id,
# #             "created_at": created_at,
# #             "updated_at": updated_at,
# #             "language": language,
# #             "seo_title": seo_title,
# #             "seo_content": seo_content,
# #             "seo_title_desc": seo_title_desc,
# #             "seo_content_desc": seo_content_desc,
# #             "category_id": category_id
# #         })

# # print(f"Data saved to {csv_file}. Images saved in the '{output_folder}' folder.")


# # # # insert_into_db(csv_file)
# # import os
# # import csv
# # import requests
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from datetime import datetime
# # from urllib.parse import urlparse

# # # Initialize WebDriver
# # driver = webdriver.Chrome()

# # # Open the website
# # driver.get('https://www.jumeirah.com/en/jumeirah-group/press-centre')

# # # Execute JavaScript to extract the news data
# # news_data = driver.execute_script("""
# # var newsItems = document.querySelectorAll('.flex-row.card');
# # var extractedData = [];

# # newsItems.forEach(function(item) {
# #     var title = item.querySelector('.card-title') ? item.querySelector('.card-title').innerText : null;
# #     var content = item.querySelector('.card-text') ? item.querySelector('.card-text').innerText : null;
# #     var image = item.querySelector('.image-wrapper img') ? item.querySelector('.image-wrapper img').src : null;
    
# #     extractedData.push({
# #         title: title,
# #         content: content,
# #         image: image
# #     });
# # });

# # return extractedData;
# # """)

# # # Folder to save images locally
# # image_folder = "downloaded_images"
# # os.makedirs(image_folder, exist_ok=True)

# # # Prepare CSV file
# # csv_filename = "news_data.csv"
# # headers = [
# #     "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
# #     "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
# #     "language", "seo_title", "seo_content", "seo_title_desc", 
# #     "seo_content_desc", "category_id"
# # ]

# # # Function to write a row to the CSV
# # def write_to_csv(csv_filename, row_data):
# #     with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
# #         writer = csv.DictWriter(file, fieldnames=headers)
# #         writer.writerow(row_data)

# # # Initialize the CSV with headers (only once)
# # with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
# #     writer = csv.DictWriter(file, fieldnames=headers)
# #     writer.writeheader()

# # # Loop through the scraped news data and save it to CSV
# # for idx, news in enumerate(news_data):
# #     title = news['title']
# #     content = news['content']
# #     image_url = news['image']

# #     # Generate an ID for the entry (based on index)
# #     id = f"news_{idx+1}"
    
# #     # Download the image locally
# #     image_path = None
# #     if image_url:
# #         image_filename = os.path.join(image_folder, os.path.basename(urlparse(image_url).path))
# #         try:
# #             # Download the image
# #             img_data = requests.get(image_url).content
# #             with open(image_filename, 'wb') as img_file:
# #                 img_file.write(img_data)
# #             image_path = image_filename  # Save the local path of the image
# #         except Exception as e:
# #             print(f"Error downloading image {image_url}: {e}")
# #             image_path = None

# #     # Prepare data for CSV
# #     row_data = {
# #         "id": id,
# #         "title": title,
# #         "subtitle": None,
# #         "slug": None,
# #         "lead": None,
# #         "content": content,
# #         "image": image_path if image_path else "No image",
# #         "type": None,
# #         "custom_field": None,
# #         "parent_id": None,
# #         "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# #         "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# #         "added_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# #         "language": "en",
# #         "seo_title": None,
# #         "seo_content": None,
# #         "seo_title_desc": None,
# #         "seo_content_desc": None,
# #         "category_id": None
# #     }

# #     # Call the function to write each row to CSV
# #     write_to_csv(csv_filename, row_data)

# # # Close the WebDriver
# # driver.quit()

# # print(f"Scraped data has been saved to {csv_filename}")






# from selenium import webdriver
# import time
# from urllib.parse import urljoin  # For joining relative URLs with the base URL

# # Initialize WebDriver
# driver = webdriver.Chrome()

# # Open the main page where "READ MORE" links are located
# driver.get('https://www.jumeirah.com/en/jumeirah-group/press-centre')

# # Execute JavaScript to get all "READ MORE" links by class selector
# read_more_links = driver.execute_script("""
#     var links = [];
#     var readMoreElements = document.querySelectorAll('a.arrow-link-molecule[title="READ MORE"]');
#     readMoreElements.forEach(function(element) {
#         links.push({
#             href: element.getAttribute('href'),
#             title: element.innerText
#         });
#     });
#     return links;
# """)

# # Check if we found any links
# if read_more_links:
#     # Iterate over the links
#     for link in read_more_links:
#         href = link['href']
#         title = link['title']

#         # Create the full URL using the base URL
#         base_url = 'https://www.jumeirah.com'
#         full_url = urljoin(base_url, href)

#         # Print the link for debugging
#         print(f"Visiting: {full_url} (Title: {title})")

#         # Open the link
#         driver.get(full_url)
#         time.sleep(3)  # Wait for the page to load

#         # Extract data from the new page using class selectors
#         try:
#             # Extract the title, content, and image using class selectors
#             page_title = driver.find_element_by_class_name('card-title').text if driver.find_elements_by_class_name('card-title') else None
#             content = driver.find_element_by_class_name('card-text').text if driver.find_elements_by_class_name('card-text') else None
#             image = driver.find_element_by_class_name('image-wrapper').find_element_by_tag_name('img').get_attribute('src') if driver.find_elements_by_class_name('image-wrapper') else None

#             # Print the extracted data
#             print(f"Page Title: {page_title}")
#             print(f"Content: {content}")
#             print(f"Image: {image}")
#         except Exception as e:
#             print(f"Error occurred while extracting data from {full_url}: {e}")
        
#         # Optionally, wait a bit before moving to the next link
#         time.sleep(2)

# else:
#     print("No 'READ MORE' links found.")

# # Close the WebDriver
# driver.quit()





import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp

# Initialize the WebDriver
driver = webdriver.Chrome()

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Prepare CSV file
csv_filename = "scraped_data.csv"
check_and_remove_file(csv_filename)

# Initialize the CSV with headers (only once)
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

try:
    driver.maximize_window()

    # Navigate to the target webpage
    driver.get("https://www.jumeirah.com/en/jumeirah-group/press-centre")

    # Wait until the 'READ MORE' anchor tag is clickable
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "arrow-link-molecule"))
    )

    # Locate the 'READ MORE' anchor tag
    read_more_element = driver.find_element(By.CLASS_NAME, "arrow-link-molecule")

    # Get the href attribute using JavaScript
    href = driver.execute_script("return arguments[0].getAttribute('href');", read_more_element)
    print(f"Href found: {href}")

    # Open the href link in a new tab
    driver.execute_script(f"window.open('{href}', '_blank');")

    # Switch to the new tab (assuming it's the last opened tab)
    driver.switch_to.window(driver.window_handles[-1])

    # Wait for the <h1> tag to be present in the new tab
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Execute JavaScript to get the text inside the <h1> tag
    title = generate_title(driver.execute_script("return document.querySelector('h1').innerText;"))
    print(f"Text inside <h1>: {title}")

    time.sleep(20)

     # Wait until the div with the background image is visible
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-background"))
    )

    image_url = driver.execute_script("""
    let div = document.querySelector('.video-background');
    let style = div.style.background;
    let imageUrl = style.match(/url\("([^"]+)"\)/);
    return imageUrl ? imageUrl[1] : "NONE";
""")

    print(image_url)
    img_name=generate_random_filename()
    download_image(image_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Execute JavaScript to get the text inside the <strong> tag
    # date = date_format(driver.execute_script("return document.querySelector('strong').innerText;"))
    # print(f"Text inside <strong>: {date}")

    # JavaScript to extract text from the first few <p> tags
    js_code = """
    return Array.from(document.querySelectorAll('div.richtext-container p'))
        .slice(0, 5)  // Number of <p> tags to fetch
        .map(p => p.innerText.trim());
    """
    
    # Execute JavaScript in the browser
    p_texts = driver.execute_script(js_code)
    print(p_texts)

    # Prepare the data row
    row_data = {
        "id": 1,  # You can generate a unique ID or increment it
        "title": title,
        "subtitle": (title),
        "slug": title,  # Example: generate slug from title
        "lead": None,  # Placeholder
        "content": " ".join(p_texts),  # Combine the first few paragraphs
        "image": image_url,  # Placeholder for image (you can extract an image URL if needed)
        "type": "press-release",  # Example: default type
        "custom_field": None,  # Placeholder
        "parent_id": None,  # Placeholder
        "created_at": "",  # Use date as created_at
        "updated_at": datetime.now().today(),  # Use date as updated_at
        "added_timestamp": "",
        "language": "en",  # Example: English
        "seo_title": '',  # Same as title for SEO
        "seo_content": None,  # Placeholder
        "seo_title_desc": None,  # Placeholder
        "seo_content_desc": None,  # Placeholder
        "category_id": 100  # Placeholder
    }

    # Append the row data to the CSV
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(row_data)

    print(f"Data saved to {csv_filename}")

finally:
    # Close the browser
    driver.quit()

# if date==date_format(datetime.now().today()):
#     insert_csv_data(csv_filename,"informations")
#     append_unique_records(csv_filename,"combined_news_data.csv")
# else:
#     print("WE DO NOT HAVE DATA FOR TODAY")