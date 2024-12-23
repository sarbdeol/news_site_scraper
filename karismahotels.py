# import os
# import csv
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

# # Set up Selenium WebDriver in headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Path to ChromeDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Target URL
# url = "https://www.karismahotels.com/press"  # Replace with the actual URL
# driver.get(url)

# # Wait for the page to load
# try:
#     WebDriverWait(driver, 15).until(
#         EC.presence_of_all_elements_located((By.CLASS_NAME, "flex"))
#     )
# except Exception as e:
#     print(f"Error: {e}")
#     driver.quit()
#     exit()

# # Execute JavaScript to extract data
# js_code = """
# let extractedData = [];
# const blocks = document.querySelectorAll('.flex.h-full.flex-col.justify-between.px-10.py-12');

# blocks.forEach((block) => {
#     const titleElement = block.querySelector('h6');
#     const descriptionElement = block.querySelector('p');
#     const linkElement = block.querySelector('a');
#     const imageElement = block.querySelector('img');

#     const title = titleElement ? titleElement.textContent.trim() : 'No title';
#     const description = descriptionElement ? descriptionElement.textContent.trim() : 'No description';
#     const link = linkElement ? linkElement.href : 'No link';
#     const image = imageElement ? imageElement.src : 'No image';

#     extractedData.push({ title, description, link, image });
# });

# return extractedData;
# """
# data = driver.execute_script(js_code)

# # Debug: Print extracted data
# print("Extracted Data:", data)

# # Close the WebDriver
# driver.quit()

# # Check if data is empty
# if not data:
#     print("No data extracted. Check the webpage structure or selectors.")
#     exit()

# # Prepare output folder for images
# output_folder = "scraped_images"
# os.makedirs(output_folder, exist_ok=True)

# # Prepare the CSV file
# csv_file = "scraped_data.csv"
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at",
#     "language", "seo_title", "seo_content", "seo_title_desc",
#     "seo_content_desc", "category_id"
# ]

# with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()

#     # Process the extracted data
#     for idx, item in enumerate(data):
#         # Extract fields
#         title = item.get("title", "No title")
#         slug = title.lower().replace(" ", "-").replace(",", "").replace("'", "")
#         lead = item.get("description", "No description")
#         content = item.get("link", "No link")
#         image_url = item.get("image", "No image")
#         created_at = updated_at = "2024-01-01"  # Replace with actual date logic if available

#         # Download image
#         image_path = "No image"
#         if image_url and image_url != "No image":
#             try:
#                 response = requests.get(image_url, stream=True)
#                 if response.status_code == 200:
#                     # Extract the image filename
#                     image_name = os.path.basename(image_url.split("?")[0])
#                     image_path = os.path.join(output_folder, image_name)

#                     # Save the image locally
#                     with open(image_path, "wb") as img_file:
#                         for chunk in response.iter_content(1024):
#                             img_file.write(chunk)

#                     print(f"Image downloaded: {image_path}")
#             except Exception as e:
#                 print(f"Error downloading image {image_url}: {e}")

#         # Create a row for the CSV
#         row = {
#             "id": idx + 1,
#             "title": title,
#             "slug": slug,
#             "lead": lead,
#             "content": content,
#             "image": image_path,
#             "type": "article",  # Default type
#             "custom_field": "",
#             "parent_id": "",
#             "created_at": created_at,
#             "updated_at": updated_at,
#             "language": "en",
#             "seo_title": title,
#             "seo_content": lead,
#             "seo_title_desc": title,
#             "seo_content_desc": lead,
#             "category_id": ""
#         }

#         # Write the row to the CSV
#         writer.writerow(row)

# print(f"Data saved to {csv_file} and images saved in '{output_folder}' folder.")











from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Navigate to the page containing the anchor link
driver.get("https://www.karismahotels.com/news-press")  # Replace with the URL where this HTML is located

try:

    driver.maximize_window()
    # Wait until the anchor tag is visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href*="le-chique-earns-coveted-michelin-star"]'))
    )
    
    # Execute JavaScript to open the href in a new tab
    driver.execute_script("""
        let link = document.querySelector('a[href*="le-chique-earns-coveted-michelin-star"]');
        window.open(link.href, '_blank');
    """)
    
        # Wait until the <p> tag with the date is visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'p.text-[14px].font-bold'))
    )

    time.sleep(10)

    #     # Wait for the <p> tag with the date to be present
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, 'p.text-\[14px\].font-bold.uppercase'))
    # )
    
    # # Execute JavaScript to extract the date
    # date = driver.execute_script("""
    #     let dateText = document.querySelector('p.text-\[14px\].font-bold.uppercase').textContent.trim();
    #     return dateText;
    # """)
    
    # # Print the extracted date
    # print(f"Extracted Date: {date}")


        # Wait until the <h1> tag with the title is visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//h1'))
    )
    
    # Execute JavaScript to get the title text
    title_text = driver.execute_script("""
        return document.querySelector('h1').textContent;
    """)
    
    # Print the extracted title
    print(f"Extracted Title: {title_text}")

      # Wait until the page content is loaded (in case there's a delay)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'p'))
    )
    
    # Execute JavaScript to get all the <p> tags' text content
    paragraphs = driver.execute_script("""
        let pTags = document.querySelectorAll('p');
        let pText = [];
        pTags.forEach(tag => {
            pText.push(tag.textContent.trim());
        });
        return pText;
    """)
            # Wait for the <p> tag with the date to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'p.text-\[14px\].font-bold.uppercase'))
    )
    
    # Execute JavaScript to extract the date
    date = driver.execute_script("""
        let dateText = document.querySelector('p.text-\[14px\].font-bold.uppercase').textContent.trim();
        return dateText;
    """)
    
    # Print the extracted date
    print(f"Extracted Date: {date}")

finally:
    # Optionally, you can add a delay or let the user interact with the new tab
    # Wait for some time to observe the new tab before closing
    WebDriverWait(driver, 5)  # Adjust the wait time as necessary
    driver.quit()
