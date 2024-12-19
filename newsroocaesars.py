import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from urllib.parse import urljoin  # To handle relative URLs
from selenium.webdriver.chrome.options import Options



# Setup Chrome in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set up the WebDriver

driver = webdriver.Chrome(options=chrome_options)   # Or another WebDriver (e.g., Firefox)
driver.get('https://newsroom.caesars.com/press-releases/default.aspx')  # URL of the page

# Wait for the page to load (add explicit waits as needed)
time.sleep(2)

# Select a year from the dropdown
year_dropdown = driver.find_element(By.ID, "newsYear")
select = Select(year_dropdown)
select.select_by_visible_text('2024')  # Replace '2024' with desired year

# Wait for the content to update
time.sleep(2)

# Extract news headlines and associated images
news_items = driver.find_elements(By.CSS_SELECTOR, '.module_item')

# Define CSV structure and initialize the file
csv_file = "scraped_newsroom.caesars_images.csv"
headers = [
    "id", "title", "slug", "lead", "content", "image", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Write to CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    for idx, item in enumerate(news_items, start=1):
        headline_element = item.find_element(By.CSS_SELECTOR, '.module_headline-link')
        image_element = item.find_element(By.CSS_SELECTOR, 'img') if item.find_elements(By.CSS_SELECTOR, 'img') else None
        
        # Ensure the image URL is absolute
        image_url = ""
        if image_element:
            image_url = image_element.get_attribute('src')
            # Convert relative URLs to absolute URLs
            image_url_1 = urljoin(driver.current_url, image_url)
        
        writer.writerow({
            "id": idx,
            "title": headline_element.text,
            "slug": headline_element.get_attribute('href').split('/')[-1],
            "lead": "",  # Placeholder for "lead"
            "content": headline_element.text,
            "image": image_url,  # Use absolute image URL
            "type": "press-release",  # Default type
            "custom_field": "",  # Placeholder
            "parent_id": "",  # Placeholder
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "language": "en",
            "seo_title": headline_element.text,
            "seo_content": headline_element.text,
            "seo_title_desc": headline_element.text[:60],
            "seo_content_desc": headline_element.text[:160],
            "category_id": "news"
        })

# Close the WebDriver
driver.quit()

print(f"Scraped data with images has been saved to {csv_file}")
