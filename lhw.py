# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import pandas as pd
# import os
# import requests
# from insert_csv_into_sql_db import insert_into_db, check_and_remove_file, generate_news
# import shutil

# # Set up Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
# )

# # Initialize WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Load the target URL
# url = "https://www.lhw.com/press-center"  # Replace with the actual URL containing the HTML structure
# driver.get(url)

# # JavaScript code to extract news title, date, and image URL
# js_code = """
# const articles = document.querySelectorAll('.press-release');
# const data = Array.from(articles).map((article, index) => {
#     const title = article.querySelector('.details .title a').innerText.trim();  // Title of the news
#     const date = article.querySelector('.date').innerText.trim();  // Date of the news
#     const img = article.querySelector('.col-12 .pr-img')?.src || '';  // Image URL
#     return { id: index + 1, title, date, img };
# });
# return data;
# """

# # Execute JavaScript and get the results
# news_data = driver.execute_script(js_code)

# # Close the browser
# driver.quit()

# # Create a folder to store images
# image_folder = "lhw_news_data_images"
# if not os.path.exists(image_folder):
#     os.makedirs(image_folder)

# # Format the data for the CSV and download images
# formatted_data = []
# for item in news_data:
#     title = generate_news(item['title'])
#     date = item['date']
#     img_url = item['img']
    
#     image_filename = None
#     # If an image URL is available, download and save the image
#     if img_url:
#         try:
#             # Create sanitized filename
#             image_filename = os.path.join(image_folder, f"{title.replace(' ', '_').replace('/', '_')}.jpg")
#             img_data = requests.get(img_url, timeout=10)
#             img_data.raise_for_status()  # Ensure valid HTTP response

#             # Save the image
#             with open(image_filename, 'wb') as img_file:
#                 img_file.write(img_data.content)
#             print(f"Image saved as: {image_filename}")
#         except requests.exceptions.RequestException as e:
#             print(f"Failed to download image from {img_url}. Error: {e}")
#             image_filename = None

#     # Add data to formatted_data
#     formatted_data.append([
#         item['id'],  # id
#         item['title'],  # title
#         item['title'].replace(" ", "-").lower(),  # slug
#         "",  # lead
#         item['img'],  # content (URL)
#         image_filename or "",  # image path (local file path)
#         "news",  # type
#         "",  # custom_field
#         "",  # parent_id
#         date,  # created_at
#         date,  # updated_at
#         "en",  # language
#         item['title'],  # seo_title
#         "",  # seo_content
#         item['title'],  # seo_title_desc
#         "",  # seo_content_desc
#         "1"  # category_id
#     ])

# # Define headers
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Convert to DataFrame
# df = pd.DataFrame(formatted_data, columns=headers)

# # Save to a CSV file
# output_file = "lhw_news_data.csv"
# check_and_remove_file(output_file)
# df.to_csv(output_file, index=False)

# print(f"Data saved to {output_file}")

# # Optional: Insert data into the database
# # insert_into_db(output_file)





# Sorry, you have been blocked
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up Chrome options for headless mode (optional)
chrome_options = Options()
# chrome_options.add_argument("--headless")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open the target URL
driver.get("https://www.lhw.com/press-center")  # Replace with the actual URL

# JavaScript code to extract the href and open it
js_code = """
let linkElement = document.querySelector('.press-release .btn-link');  // Select the 'Read More' button
let href = linkElement ? linkElement.href : null;  // Extract href from the link

if (href) {
    window.location.href = href;  // Open the link in the browser
}
"""

# Execute the JavaScript code in the browser context
driver.execute_script(js_code)

# Optionally, wait for the page to load if needed (e.g., time.sleep())
import time
time.sleep(5)

# Close the browser
driver.quit()
