from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import csv
import requests
from datetime import datetime

# Configure Selenium WebDriver
driver = webdriver.Chrome()  # Ensure the correct WebDriver is installed
url = "https://www.corinthia.com/en-gb/latest-news/"  # Replace with the actual URL of the website
driver.get(url)

# Execute JavaScript to load all dynamic content
js_code = """
let loadMoreButton = document.querySelector('.listing__more button');
while (loadMoreButton) {
    loadMoreButton.click();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for content to load
    loadMoreButton = document.querySelector('.listing__more button');
}
return document.body.innerHTML;
"""
driver.execute_script(js_code)

# CSV setup
csv_file = "formatted_corinthia_news.csv"
headers = [
    "id", "title", "slug", "lead", "content", "image", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write header row

    # Find all news items
    items = driver.find_elements(By.CSS_SELECTOR, ".listing-result")

    for idx, item in enumerate(items, start=1):
        try:
            # Extract title
            title = item.find_element(By.CSS_SELECTOR, ".listing-result-card__head h3").text
            slug = title.lower().replace(" ", "-")  # Generate slug

            # Extract lead (description)
            lead = item.find_element(By.CSS_SELECTOR, ".listing-result-card__body p").text

            # Extract link
            link = item.find_element(By.CSS_SELECTOR, ".listing-result-card__content a").get_attribute("href")

            # Extract image
            try:
                image_url = item.find_element(By.CSS_SELECTOR, "picture source").get_attribute("srcset")
                image_name = f"images/{slug}.jpg"
                os.makedirs("images", exist_ok=True)

                # Download image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    with open(image_name, "wb") as img_file:
                        img_file.write(img_response.content)
            except:
                image_url = None
                image_name = None

            # Generate current timestamps for created_at and updated_at
            created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Write to CSV in the specified format
            writer.writerow([
                idx,            # id
                title,          # title
                slug,           # slug
                lead,           # lead
                "",             # content (not available in current context)
                image_name,     # image (local path)
                "news",         # type (hardcoded as "news")
                "",             # custom_field (not provided)
                None,           # parent_id (not applicable)
                created_at,     # created_at
                updated_at,     # updated_at
                "en",           # language (assumed English)
                title,          # seo_title (same as title)
                lead,           # seo_content (same as lead)
                title,          # seo_title_desc (same as title)
                lead,           # seo_content_desc (same as lead)
                None            # category_id (not provided)
            ])

        except Exception as e:
            print(f"Error processing item {idx}: {e}")

# Close the driver
driver.quit()

print(f"Data saved to {csv_file}. Images saved to the 'images' folder.")
