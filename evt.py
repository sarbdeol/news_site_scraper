# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # import csv
# # import os
# # import requests
# # from datetime import datetime

# # # Configure Selenium WebDriver
# # driver = webdriver.Chrome()  # Make sure the WebDriver is installed and configured
# # url = "https://www.evt.com/news"  # Replace with the actual URL
# # driver.get(url)

# # # Define the CSV headers
# # headers = [
# #     "id", "title", "slug", "lead", "content", "image", "type",
# #     "custom_field", "parent_id", "created_at", "updated_at",
# #     "language", "seo_title", "seo_content", "seo_title_desc",
# #     "seo_content_desc", "category_id"
# # ]

# # # Create a folder for images
# # os.makedirs("images", exist_ok=True)

# # # Create and write to the CSV file
# # csv_file = "evt_news.csv"
# # with open(csv_file, "w", newline="", encoding="utf-8") as file:
# #     writer = csv.writer(file)
# #     writer.writerow(headers)  # Write the header row

# #     # Locate all news items
# #     news_items = driver.find_elements(By.CSS_SELECTOR, ".news-item")

# #     for idx, item in enumerate(news_items, start=1):
# #         try:
# #             # Extract the title
# #             title = item.find_element(By.CSS_SELECTOR, ".news-item-title a").text
# #             slug = title.lower().replace(" ", "-")  # Generate a slug from the title

# #             # Extract the category
# #             category = item.find_element(By.CSS_SELECTOR, ".news-item-category").text

# #             # Extract the publication date
# #             date = item.find_element(By.CSS_SELECTOR, ".news-item-date").text
# #             created_at = updated_at = datetime.strptime(date, "%d %B %Y").strftime("%Y-%m-%d %H:%M:%S")

# #             # Extract the link
# #             link = item.find_element(By.CSS_SELECTOR, ".news-item-title a").get_attribute("href")

# #             # Extract the image URL
# #             image_url = item.find_element(By.CSS_SELECTOR, ".news-item-image").get_attribute("src")
# #             image_name = f"images/{slug}.jpg"

# #             # Download the image
# #             try:
# #                 response = requests.get(image_url)
# #                 if response.status_code == 200:
# #                     with open(image_name, "wb") as img_file:
# #                         img_file.write(response.content)
# #             except Exception as e:
# #                 print(f"Error downloading image for {title}: {e}")
# #                 image_name = None

# #             # Write the data to the CSV file
# #             writer.writerow([
# #                 idx,             # id
# #                 title,           # title
# #                 slug,            # slug
# #                 category,        # lead (using category as lead)
# #                 "",              # content (not available)
# #                 image_name,      # image (local path)
# #                 "news",          # type (hardcoded as "news")
# #                 "",              # custom_field
# #                 None,            # parent_id
# #                 created_at,      # created_at
# #                 updated_at,      # updated_at
# #                 "en",            # language (assumed English)
# #                 title,           # seo_title
# #                 category,        # seo_content
# #                 title,           # seo_title_desc
# #                 category,        # seo_content_desc
# #                 None             # category_id (not available)
# #             ])

# #         except Exception as e:
# #             print(f"Error processing item {idx}: {e}")

# # # Close the browser
# # driver.quit()

# # print(f"Data saved to {csv_file}. Images saved to the 'images' folder.")




# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import time

# # Configure Selenium WebDriver
# chrome_options = Options()
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Initialize the WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# base_url = "https://preferredhotels.com/press-center/press-releases"  # Replace with the actual URL of the news page

# try:
#     # Navigate to the base URL
#     driver.get(base_url)
#     time.sleep(5)  # Allow the page to load fully

#     # Execute JavaScript to extract the href and other details
#     news_details = driver.execute_script("""
#         const newsItem = document.querySelector('.news-item');
#         if (!newsItem) return null;

#         const linkElement = newsItem.querySelector('a.news-item-image-wrapper');
#         const titleElement = newsItem.querySelector('h5.news-item-title a');
#         const imageElement = linkElement ? linkElement.querySelector('img') : null;
#         const dateElement = newsItem.querySelector('.news-item-date');
#         const categoryElement = newsItem.querySelector('.news-item-category');

#         return {
#             href: linkElement ? linkElement.href : null,
#             title: titleElement ? titleElement.textContent.trim() : null,
#             image: imageElement ? imageElement.src : null,
#             date: dateElement ? dateElement.textContent.trim() : null,
#             category: categoryElement ? categoryElement.textContent.trim() : null
#         };
#     """)

#     # Check if news details were found
#     if news_details and news_details['href']:
#         print("News Details:")
#         print(f"Title: {news_details['title']}")
#         print(f"Date: {news_details['date']}")
#         print(f"Category: {news_details['category']}")
#         print(f"Image URL: {news_details['image']}")
#         print(f"Link: {news_details['href']}")

#         # Open the href in a new tab in the browser
#         driver.get(news_details['href'])
#         time.sleep(5)  # Allow the new page to load fully

#         # Optionally, extract further details from the new page
#         title = driver.title  # Get the title of the new page
#         print(f"Opened page title: {title}")
#     else:
#         print("No news item found.")

# finally:
#     driver.quit()





import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests

# Setup Chrome in headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)  # Make sure chromedriver is installed and in PATH

# Define the target URL
url = "https://www.evt.com/news"  # Replace with the actual URL
driver.get(url)

# Get the first news item's href using JavaScript
first_link = driver.execute_script("""
    var firstLink = document.querySelector('.news-item a').getAttribute('href');
    return firstLink;
""")

print(f"Opening first link: {first_link}")

# Open the link in the browser
driver.get(first_link)

# Wait for the page to load (optional, depending on content)
time.sleep(3)

# Extract title, date, and image
try:
    # Extract title
    title = driver.find_element(By.CSS_SELECTOR, '.news-item-title a').text.strip()
    print(f"Title: {title}")

    # Extract date
    date = driver.find_element(By.CSS_SELECTOR, '.news-item-date').text.strip()
    print(f"Date: {date}")

    # Extract image URL
    image_url = driver.find_element(By.CSS_SELECTOR, '.news-item-image').get_attribute('src')
    print(f"Image URL: {image_url}")

    # Optionally, download the image
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        with open(f"{title}.jpg", "wb") as file:
            file.write(image_response.content)
        print(f"Image saved as {title}.jpg")
    else:
        print("Failed to download the image.")

except Exception as e:
    print(f"Error extracting data: {e}")

# Quit the browser
driver.quit()
