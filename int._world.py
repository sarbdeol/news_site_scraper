from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import urllib.request
import csv
from datetime import datetime

# Setup the Selenium WebDriver (Make sure chromedriver is installed and in PATH)
driver = webdriver.Chrome()  # Change this to use the appropriate WebDriver

# Open the target page
driver.get("https://int.hworld.com/press/press-releases")

# Wait for the content to load
wait = WebDriverWait(driver, 10)
press_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".filter-list__item.flex_item.news")))

# Create a directory to save the images
os.makedirs("hworld_images", exist_ok=True)

# Define CSV headers
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Open CSV file to write the data
csv_file = "hworld_news.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write header row

    # Iterate through each press release item
    for idx, item in enumerate(press_items, start=1):
        try:
            # Extract title
            title = item.find_element(By.CSS_SELECTOR, 'h4 a').text

            # Extract date
            date = item.find_element(By.CSS_SELECTOR, '.date').text

            # Extract tags (if any)
            tags = item.find_element(By.CSS_SELECTOR, '.tags').text

            # Extract image URL
            img_element = item.find_element(By.CSS_SELECTOR, '.image img')
            img_url = img_element.get_attribute('src')
            
            # Download the image
            img_filename = f"hworld_images/{title.replace(' ', '_')}.jpg"
            urllib.request.urlretrieve(img_url, img_filename)
            print(f"Saved: {img_filename}")

            # Generate slug, lead, and content from title and date (or use other logic as needed)
            slug = title.lower().replace(" ", "-")
            lead = date  # Using date as lead for simplicity
            content = f"Press release for {title} on {date}"  # Customize as needed
            type_ = "press_release"
            custom_field = None  # No custom field provided, set as None
            parent_id = None  # No parent_id provided, set as None
            created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Using current timestamp
            language = "en"  # Assuming English language
            seo_title = title
            seo_content = content
            seo_title_desc = title
            seo_content_desc = content
            category_id = None  # No category_id provided, set as None

            # Write the data to the CSV with the specific headers
            writer.writerow([
                idx,             # id
                title,           # title
                slug,            # slug
                lead,            # lead
                content,         # content
                img_url,    # image (local file path)
                type_,           # type
                custom_field,    # custom_field
                parent_id,       # parent_id
                created_at,      # created_at
                updated_at,      # updated_at
                language,        # language
                seo_title,       # seo_title
                seo_content,     # seo_content
                seo_title_desc,  # seo_title_desc
                seo_content_desc, # seo_content_desc
                category_id,     # category_id
            ])

        except Exception as e:
            print(f"Error processing row {idx}: {e}")

# Close the browser
driver.quit()

print(f"Data saved to {csv_file}. Images saved in the 'hworld_images' folder.")
