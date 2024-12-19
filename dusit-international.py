from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import os
import requests
from datetime import datetime

# Configure Selenium WebDriver
driver = webdriver.Chrome()  # Ensure the appropriate WebDriver is installed
url = "https://www.dusit-international.com/en/updates/press-releases"  # Replace with the actual URL
driver.get(url)

# Define CSV headers as per your requested format
headers = [
    "id", "title", "slug", "lead", "content", "image", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Create a CSV file for saving the data
csv_file = "dusit_press_releases.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the header row

    # Find all cards containing press release information
    cards = driver.find_elements(By.CSS_SELECTOR, ".card--news-horizontal")

    for idx, card in enumerate(cards, start=1):
        try:
            # Extract the title
            title = card.find_element(By.CSS_SELECTOR, ".card__title").text
            slug = title.lower().replace(" ", "-")  # Generate a slug from the title

            # Extract the description (lead)
            lead = card.find_element(By.CSS_SELECTOR, ".card__body").text

            # Extract the link
            link = card.get_attribute("href")

            # Extract the publication date
            date = card.find_element(By.CSS_SELECTOR, ".card__date").text
            created_at = updated_at = datetime.strptime(date, "%d %B %Y").strftime("%Y-%m-%d %H:%M:%S")

            # Extract the image URL
            try:
                image_url = card.find_element(By.CSS_SELECTOR, ".card__img").get_attribute("style")
                image_url = image_url.split("url('")[1].split("')")[0]  # Parse the URL
                image_name = f"images/{slug}.jpg"

                # Download the image
                os.makedirs("images", exist_ok=True)
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    with open(image_name, "wb") as img_file:
                        img_file.write(img_response.content)
            except:
                image_url = None
                image_name = None

            # Write the data to the CSV file
            writer.writerow([
                idx,             # id
                title,           # title
                slug,            # slug
                lead,            # lead
                "",              # content (not available)
                image_name,      # image (local path)
                "news",          # type
                "",              # custom_field
                None,            # parent_id
                created_at,      # created_at
                updated_at,      # updated_at
                "en",            # language (assumed English)
                title,           # seo_title
                lead,            # seo_content
                title,           # seo_title_desc
                lead,            # seo_content_desc
                None             # category_id (not available)
            ])

        except Exception as e:
            print(f"Error processing card {idx}: {e}")

# Close the browser
driver.quit()

print(f"Data saved to {csv_file}. Images saved to the 'images' folder.")
