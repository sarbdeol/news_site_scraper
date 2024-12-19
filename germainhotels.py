from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import urllib.request
import csv
from datetime import datetime

# Setup the Selenium WebDriver (use appropriate WebDriver for your browser)
driver = webdriver.Chrome()  # Make sure chromedriver is installed and in PATH

# Navigate to the webpage containing the HTML content
driver.get("https://www.germainhotels.com/en/about/mediaroom/")  # Change this to the URL you need

# Wait for the table to be visible
wait = WebDriverWait(driver, 10)
press_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.css-8atqhb')))

# Locate all press release rows in the table
press_rows = driver.find_elements(By.CSS_SELECTOR, 'table.css-8atqhb tbody tr')

# Create a directory to save the images
os.makedirs("germainhotels_images", exist_ok=True)

# Define CSV headers
headers = [
    "id", "title", "slug", "lead", "content", "image", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open CSV file to write the data
csv_file = "germainhotels_news.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write header row

    # Iterate through the rows and extract details
    for idx, row in enumerate(press_rows, start=1):
        try:
            # Extract title
            title_element = row.find_element(By.CSS_SELECTOR, '.css-stz03g')
            title = title_element.text if title_element else "No Title"

            # Extract date
            date_element = row.find_element(By.CSS_SELECTOR, '.css-tlj14j')
            date = date_element.text if date_element else "No Date"

            # Extract city
            city_element = row.find_element(By.CSS_SELECTOR, '.css-ruc5cq')
            city = city_element.text if city_element else "No City"

            # Image URL (If available, otherwise set a default)
            img_url = "default_image_url_here"  # Set a default image URL if none is found
            img_filename = f"germainhotels_images/{title.replace(' ', '_')}.jpg"
            
            # Download the image if the URL is valid
            if img_url != "default_image_url_here":
                urllib.request.urlretrieve(img_url, img_filename)
                print(f"Saved: {img_filename}")
            else:
                print("No image found, skipping download.")

            # Populate other fields based on provided HTML
            slug = title.lower().replace(" ", "-")
            lead = date  # Using date as lead for simplicity
            content = lead  # Using lead as content for simplicity
            type_ = "press_release"  # Assuming press release type
            custom_field = None  # No custom field provided, set as None
            parent_id = None  # No parent_id provided, set as None
            created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Using current timestamp
            language = "en"  # Assuming English language
            seo_title = title
            seo_content = lead
            seo_title_desc = title
            seo_content_desc = lead
            category_id = None  # No category_id provided, set as None

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

        except Exception as e:
            print(f"Error processing row {idx}: {e}")

# Close the browser
driver.quit()

print(f"Data saved to {csv_file}. Images saved in the 'germainhotels_images' folder.")
