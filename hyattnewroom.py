import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

# Setup Chrome in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)  # Ensure chromedriver is installed and in PATH

# Define the target URL
url = "https://newsroom.hyatt.com/"  # Replace with the correct URL
driver.get(url)

# Wait for elements to load
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.wd_layout-simple.wd_item_list"))
    )
except Exception as e:
    print("Error: Elements not found or page took too long to load.")
    print(driver.page_source)  # Debug: Check if content is loaded
    driver.quit()
    exit()

# Create a folder to save images
image_folder = "hyatt_images"
os.makedirs(image_folder, exist_ok=True)

# Locate all the news items
news_items = driver.find_elements(By.CSS_SELECTOR, "ul.wd_layout-simple.wd_item_list > li.wd_item")

# Prepare data for CSV
data = []

for index, item in enumerate(news_items, start=1):
    try:
        # Extract the title
        title_element = item.find_element(By.CSS_SELECTOR, ".wd_title a")
        title = title_element.text.strip()

        # Generate a slug from the title
        slug = title.lower().replace(" ", "-").replace("®", "").replace(",", "").replace(".", "")

        # Extract the date
        date = item.find_element(By.CSS_SELECTOR, ".wd_date").text.strip()

        # Extract the subtitle/lead
        lead = item.find_element(By.CSS_SELECTOR, ".wd_subtitle").text.strip()

        # Extract the summary/content
        content = item.find_element(By.CSS_SELECTOR, ".wd_summary p").text.strip()

        # Extract the image URL
        image_element = item.find_element(By.CSS_SELECTOR, ".wd_thumbnail img")
        image_url = image_element.get_attribute("src")
        if image_url.startswith("/"):  # Handle relative URLs
            image_url = f"https://newsroom.hyatt.com{image_url}"

        # Download and save the image locally
        image_filename = f"{slug}.jpg"
        image_path = os.path.join(image_folder, image_filename)
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
            else:
                print(f"Failed to download image: {image_url}")
                image_path = None
        except Exception as e:
            print(f"Error downloading image: {e}")
            image_path = None

        # Extract the link
        link = title_element.get_attribute("href")

        # Placeholder values for remaining fields
        type_field = "press_release"
        custom_field = ""
        parent_id = None
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_at = created_at
        language = "en"
        seo_title = title
        seo_content = f"Discover more about {title}."
        seo_title_desc = f"{title} - SEO Title"
        seo_content_desc = f"{title} - SEO Description"
        category_id = None

        # Append data to the list
        data.append({
            "id": index,
            "title": title,
            "slug": slug,
            "lead": lead,
            "content": content,
            "image": image_path,
            "type": type_field,
            "custom_field": custom_field,
            "parent_id": parent_id,
            "created_at": created_at,
            "updated_at": updated_at,
            "language": language,
            "seo_title": seo_title,
            "seo_content": seo_content,
            "seo_title_desc": seo_title_desc,
            "seo_content_desc": seo_content_desc,
            "category_id": category_id
        })

    except Exception as e:
        print(f"Error processing news item: {e}")

# Write to CSV
output_file = "hyatt_newsroom_output.csv"
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)

print(f"Data successfully written to {output_file}")
print(f"Images saved in the '{image_folder}' folder")

# Quit the browser
driver.quit()
