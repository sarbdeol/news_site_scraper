from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib.request
import os
import base64
import csv
from datetime import datetime

# Setup the Selenium WebDriver (Make sure chromedriver is installed and in PATH)
driver = webdriver.Chrome()  # Make sure chromedriver is in the PATH

# Open the target page
driver.get("https://hotel.hardrock.com/news/")

# Wait for the content to load (adjust timeout if needed)
driver.implicitly_wait(10)

# Create a directory to save the images
os.makedirs("hardrock_images", exist_ok=True)

# Define CSV headers
headers = [
    "id", "title", "slug", "lead", "content", "image_data", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open CSV file to write the data
csv_file = "hardrock_news.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write header row

    # Locate all blog post items
    blog_items = driver.find_elements(By.CSS_SELECTOR, ".blogPost")

    # Iterate through each blog post item
    for idx, item in enumerate(blog_items, start=1):
        try:
            # Extract title and URL
            title = item.find_element(By.CSS_SELECTOR, '.blogPostTitleLink').text
            url = item.find_element(By.CSS_SELECTOR, '.blogPostTitleLink').get_attribute('href')

            # Extract publication date
            date = item.find_element(By.CSS_SELECTOR, '.blogPostDate').text

            # Extract image URL (background-image from the style)
            img_element = item.find_element(By.CSS_SELECTOR, '.blogPostImagePreview')
            img_url = img_element.get_attribute('style').split('url(')[1].split(')')[0]

            # Download and save the image
            img_filename = f"hardrock_images/{title.replace(' ', '_')}.jpg"
            urllib.request.urlretrieve(img_url, img_filename)

            # Convert the image to base64
            with open(img_filename, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')

            # Generate slug and content for SEO purposes
            slug = title.lower().replace(" ", "-")
            lead = f"Press release for {title} on {date}"
            content = lead  # Simple placeholder content
            type_ = "press_release"
            custom_field = None  # No custom field
            parent_id = None  # No parent ID
            created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            language = "en"  # Assuming English language
            seo_title = title
            seo_content = lead
            seo_title_desc = title
            seo_content_desc = lead
            category_id = None  # No category ID

            # Write the data to the CSV file
            writer.writerow([
                idx,             # id
                title,           # title
                slug,            # slug
                lead,            # lead
                content,         # content
                img_data,        # image data (base64 encoded)
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
            print(f"Error processing blog post {idx}: {e}")

# Close the browser
driver.quit()

print(f"Data saved to {csv_file}. Images saved in the 'hardrock_images' folder.")
