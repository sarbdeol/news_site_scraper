from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import os
import requests
from datetime import datetime

# Configure Selenium WebDriver
driver = webdriver.Chrome()  # Ensure the correct WebDriver is installed
url = "https://media.choicehotels.com/international-press-releases"
driver.get(url)

# Define the CSV headers as provided
headers = [
    "id", "title", "slug", "lead", "content", "image", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open CSV file for writing
csv_file = "formatted_press_releases.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the header row

    # Locate press release items
    items = driver.find_elements(By.CSS_SELECTOR, ".wd_item")

    for idx, item in enumerate(items, start=1):
        try:
            # Extract the date
            date = item.find_element(By.CSS_SELECTOR, ".wd_date").text
            created_at = updated_at = datetime.strptime(date, "%b %d, %Y").strftime("%Y-%m-%d %H:%M:%S")

            # Extract the title and link
            title_elem = item.find_element(By.CSS_SELECTOR, ".wd_title a")
            title = title_elem.text
            slug = title.lower().replace(" ", "-")  # Create a slug from the title
            link = title_elem.get_attribute("href")

            # Extract the summary (lead content)
            lead = item.find_element(By.CSS_SELECTOR, ".wd_summary").text

            # Extract the image link (if available)
            try:
                image_elem = item.find_element(By.CSS_SELECTOR, ".wd_asset_type_link a")
                image_link = image_elem.get_attribute("href")
                image_name = f"images/{slug}.jpg"
                # Download the image
                os.makedirs("images", exist_ok=True)
                img_response = requests.get(image_link)
                if img_response.status_code == 200:
                    with open(image_name, "wb") as img_file:
                        img_file.write(img_response.content)
            except:
                image_name = None  # No image found

            # Write data row to CSV
            writer.writerow([
                idx,             # id
                title,           # title
                slug,            # slug
                lead,            # lead
                "",              # content (not available in current context)
                image_link,      # image
                "press_release", # type
                "",              # custom_field
                None,            # parent_id
                created_at,      # created_at
                updated_at,      # updated_at
                "en",            # language
                title,           # seo_title
                lead,            # seo_content
                title,           # seo_title_desc
                lead,            # seo_content_desc
                None             # category_id (not available in current context)
            ])
        except Exception as e:
            print(f"Error processing item {idx}: {e}")

# Close the browser
driver.quit()

print(f"Data saved to {csv_file}. Images saved to the 'images' folder.")
