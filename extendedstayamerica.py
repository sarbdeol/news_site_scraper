# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import csv
# import os
# import requests
# from datetime import datetime
# import time

# # Set up the WebDriver (ensure you have the appropriate WebDriver, e.g., ChromeDriver)
# driver = webdriver.Chrome()  # Use the correct driver
# url = "https://www.extendedstayamerica.com/media-center/"  # Replace with the actual URL

# # Open the webpage
# driver.get(url)

# # Optional: Wait for the page to fully load
# time.sleep(3)

# # Execute JavaScript if needed to load more content or manipulate the DOM
# js_code = """
# // Scroll to the bottom of the page to load any dynamically loaded content if required
# window.scrollTo(0, document.body.scrollHeight);
# return document.body.innerHTML;
# """
# driver.execute_script(js_code)

# # Create a folder for images
# os.makedirs("images", exist_ok=True)

# # Define the CSV headers and output file
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type", 
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# csv_file = "extendedstayamerica.csv"

# # Open the CSV file to write data
# with open(csv_file, "w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(headers)  # Write header row

#     # Find all cards in the card-deck
#     cards = driver.find_elements(By.CSS_SELECTOR, ".card.mb-9")

#     for idx, card in enumerate(cards, start=1):
#         try:
#             # Extract title and generate slug
#             title = card.find_element(By.CSS_SELECTOR, ".card-title").text
#             slug = title.lower().replace(" ", "-")  # Convert title to slug (lowercase with hyphens)

#             # Extract the lead text (description)
#             lead = card.find_element(By.CSS_SELECTOR, ".card-text").text

#             # Extract link
#             link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

#             # Extract image URL
#             image_url = card.find_element(By.CSS_SELECTOR, ".card-img-top").get_attribute("src")
#             image_name = f"images/{slug}.jpg"

#             # Download image
#             try:
#                 img_response = requests.get(image_url)
#                 if img_response.status_code == 200:
#                     with open(image_name, "wb") as img_file:
#                         img_file.write(img_response.content)
#             except Exception as e:
#                 print(f"Error downloading image for {title}: {e}")
#                 image_name = None

#             # Extract the current date for created_at and updated_at
#             created_at = updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#             # Populate the data with the structure defined by headers
#             custom_field = None  # Custom field is not provided, so left as None
#             parent_id = None     # Parent ID is not provided, so left as None
#             language = "en"      # Assuming English language
#             seo_title = title    # Using the title for SEO title
#             seo_content = lead   # Using the lead for SEO content
#             seo_title_desc = title  # Using the title for SEO title description
#             seo_content_desc = lead  # Using the lead for SEO content description
#             category_id = None   # Category ID is not provided, so left as None

#             # Write the data into the CSV file
#             writer.writerow([
#                 idx,             # id
#                 title,           # title
#                 slug,            # slug
#                 lead,            # lead
#                 "",              # content (not provided in this example)
#                 image_url,      # image (local path)
#                 "press_release", # type (hardcoded as press_release)
#                 custom_field,    # custom_field
#                 parent_id,       # parent_id
#                 created_at,      # created_at
#                 updated_at,      # updated_at
#                 language,        # language
#                 seo_title,       # seo_title
#                 seo_content,     # seo_content
#                 seo_title_desc,  # seo_title_desc
#                 seo_content_desc, # seo_content_desc
#                 category_id,     # category_id
#             ])

#         except Exception as e:
#             print(f"Error processing card {idx}: {e}")

# # Close the WebDriver
# driver.quit()

# print(f"Data saved to {csv_file}. Images saved in the 'images' folder.")


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Setup Chrome in headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)  # Make sure chromedriver is installed and in PATH

# Define the target URL
url = "https://www.extendedstayamerica.com/media-center/"  # Replace with the actual URL of the page where the card is
driver.get(url)

# Execute JavaScript to get the most recent href and navigate to it
driver.execute_script("""
    var link = document.querySelector('.card.mb-9 a').getAttribute('href');
    window.location.href = link;
""")

# Wait for the page to load (You might need to adjust the time or use explicit waits)
time.sleep(3)

# Extract the title, date, and image from the newly opened page
try:
    # Extract title
    title = driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()  # Adjust the selector as needed
    
    # Extract date (assuming it is in a <p> tag or a similar element, adjust selector)
    date = driver.find_element(By.CSS_SELECTOR, 'p.date').text.strip()  # Adjust the selector as needed

    # Extract image URL
    image_url = driver.find_element(By.CSS_SELECTOR, 'img.card-img-top').get_attribute('src')
    
    # Print the extracted data
    print(f"Title: {title}")
    print(f"Date: {date}")
    print(f"Image URL: {image_url}")

except Exception as e:
    print(f"Error extracting data: {e}")

# Quit the browser
driver.quit()
