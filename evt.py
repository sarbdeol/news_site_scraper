from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import os
import requests
from datetime import datetime

# Configure Selenium WebDriver
driver = webdriver.Chrome()  # Make sure the WebDriver is installed and configured
url = "https://www.evt.com/news"  # Replace with the actual URL
driver.get(url)

# Define the CSV headers
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Create a folder for images
os.makedirs("images", exist_ok=True)

# Create and write to the CSV file
csv_file = "evt_news.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the header row

    # Locate all news items
    news_items = driver.find_elements(By.CSS_SELECTOR, ".news-item")

    for idx, item in enumerate(news_items, start=1):
        try:
            # Extract the title
            title = item.find_element(By.CSS_SELECTOR, ".news-item-title a").text
            slug = title.lower().replace(" ", "-")  # Generate a slug from the title

            # Extract the category
            category = item.find_element(By.CSS_SELECTOR, ".news-item-category").text

            # Extract the publication date
            date = item.find_element(By.CSS_SELECTOR, ".news-item-date").text
            created_at = updated_at = datetime.strptime(date, "%d %B %Y").strftime("%Y-%m-%d %H:%M:%S")

            # Extract the link
            link = item.find_element(By.CSS_SELECTOR, ".news-item-title a").get_attribute("href")

            # Extract the image URL
            image_url = item.find_element(By.CSS_SELECTOR, ".news-item-image").get_attribute("src")
            image_name = f"images/{slug}.jpg"

            # Download the image
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(image_name, "wb") as img_file:
                        img_file.write(response.content)
            except Exception as e:
                print(f"Error downloading image for {title}: {e}")
                image_name = None

            # Write the data to the CSV file
            writer.writerow([
                idx,             # id
                title,           # title
                slug,            # slug
                category,        # lead (using category as lead)
                "",              # content (not available)
                image_name,      # image (local path)
                "news",          # type (hardcoded as "news")
                "",              # custom_field
                None,            # parent_id
                created_at,      # created_at
                updated_at,      # updated_at
                "en",            # language (assumed English)
                title,           # seo_title
                category,        # seo_content
                title,           # seo_title_desc
                category,        # seo_content_desc
                None             # category_id (not available)
            ])

        except Exception as e:
            print(f"Error processing item {idx}: {e}")

# Close the browser
driver.quit()

print(f"Data saved to {csv_file}. Images saved to the 'images' folder.")
