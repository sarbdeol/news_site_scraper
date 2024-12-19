import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
from datetime import datetime

# Initialize Selenium WebDriver
driver = webdriver.Chrome()  # Ensure the correct WebDriver is in PATH
driver.get("https://stories.hilton.com/releases")  # Update this with the target URL

# Prepare directory for saving images
os.makedirs("stories_hilton_news_images", exist_ok=True)

# Prepare CSV file
csv_file = "stories_hilton_news_data.csv"
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Open CSV file for writing
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    # Wait for elements to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.card-grid-item'))
        )
    except Exception as e:
        print(f"Error loading cards: {e}")
        driver.quit()
        exit()

    # Locate news cards
    cards = driver.find_elements(By.CSS_SELECTOR, '.card-grid-item')
    for idx, card in enumerate(cards, start=1):
        try:
            # Extract data using JavaScript execution and standard methods
            title = card.find_element(By.CSS_SELECTOR, '.card-grid-item__title').text
            slug = title.lower().replace(" ", "-").replace("&", "and").replace("/", "-")
            date_element = card.find_element(By.CSS_SELECTOR, '.card-grid-item__date')
            created_at = date_element.get_attribute("datetime") or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            category = card.find_element(By.CSS_SELECTOR, '.card-grid-item__meta-cat-text').text if card.find_elements(By.CSS_SELECTOR, '.card-grid-item__meta-cat-text') else "Uncategorized"
            image_url = card.find_element(By.CSS_SELECTOR, 'img').get_attribute('src') if card.find_elements(By.CSS_SELECTOR, 'img') else ""

            # Download the image if URL exists
            img_filename = ""
            if image_url:
                img_filename = f"stories_hilton_news_images/{slug}.jpg"
                urllib.request.urlretrieve(image_url, img_filename)

            # Populate row for CSV
            row = [
                idx,              # id
                title,            # title
                slug,             # slug
                "",               # lead
                "",               # content
                img_filename,     # image
                "news",           # type (example)
                "",               # custom_field
                "",               # parent_id
                created_at,       # created_at
                updated_at,       # updated_at
                "en",             # language
                title,            # seo_title
                "",               # seo_content
                f"{title} desc",  # seo_title_desc
                "",               # seo_content_desc
                "1"               # category_id (example)
            ]

            # Write row to CSV
            writer.writerow(row)
            print(f"Processed: {title}")

        except Exception as e:
            print(f"Error processing card: {e}")

# Close the browser
driver.quit()
print(f"Data saved to {csv_file}")
