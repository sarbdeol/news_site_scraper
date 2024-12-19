from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import urllib.request
import csv
from datetime import datetime

# Setup the Selenium WebDriver (use appropriate WebDriver for your browser)
driver = webdriver.Chrome()  # Make sure chromedriver is installed and in PATH

# Navigate to the webpage containing the HTML content
driver.get("https://www.frasershospitality.com/en/about-us/newsroom/")  # Change this to the local file path or URL

# Locate all news blocks
news_blocks = driver.find_elements(By.CSS_SELECTOR, '.newsroom-grid-block')

# Create a directory to save the images
os.makedirs("frasershospitality_images", exist_ok=True)

# Define CSV headers
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open CSV file to write the data
csv_file = "frasershospitality_news.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write header row

    # Iterate through news blocks and extract details
    for idx, block in enumerate(news_blocks, start=1):
        try:
            # Get the title
            title = block.find_element(By.CSS_SELECTOR, '.newsroom-info h3').text
            
            # Generate a slug from the title (lowercase with hyphens)
            slug = title.lower().replace(" ", "-")
            
            # Get the date (or lead text, if available)
            lead = block.find_element(By.CSS_SELECTOR, '.news-date').text
            content = lead  # Using lead as content for simplicity

            # Get the image source URL and alternative text
            img_element = block.find_element(By.CSS_SELECTOR, '.img-holder img')
            img_url = img_element.get_attribute('src')
            img_alt = img_element.get_attribute('alt')
            
            # Download the image
            img_filename = f"frasershospitality_images/{slug}.jpg"
            urllib.request.urlretrieve(img_url, img_filename)
            
            # Populate the rest of the fields as per the format
            type_ = "press_release"  # Assuming press release type
            custom_field = None  # No custom field provided, so we set it as None
            parent_id = None  # No parent_id provided, so we set it as None
            created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Using current timestamp
            language = "en"  # Assuming English language
            seo_title = title
            seo_content = lead
            seo_title_desc = title
            seo_content_desc = lead
            category_id = None  # No category_id provided, so we set it as None

            # Write the data to the CSV
            writer.writerow([
                idx,             # id
                title,           # title
                slug,            # slug
                lead,            # lead
                content,         # content (using lead as content for simplicity)
                img_url,    # image (local file path)
                type_,           # type (hardcoded as press_release)
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
            
            print(f"Saved: {img_filename}, Title: {title}, Date: {lead}, Image Alt: {img_alt}")

        except Exception as e:
            print(f"Error processing block {idx}: {e}")

# Close the browser
driver.quit()

print(f"Data saved to {csv_file}. Images saved in the 'frasershospitality_images' folder.")
