# import os
# import csv
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Setup Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# # driver_path = "path/to/chromedriver"  # Replace with your actual chromedriver path

# # Initialize the Selenium WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Open the target URL
# url = "https://www.radissonhotels.com/en-us/corporate/media/press-releases"  # Replace with the actual URL
# driver.get(url)

# # Wait for press cards to load (adjust if needed)
# try:
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, '.press-card'))
#     )
#     print("Page loaded successfully.")
# except Exception as e:
#     print(f"Error: {e}")
#     driver.quit()
#     exit()

# # Execute JavaScript code to extract the news data
# news_data = driver.execute_script("""
#     let pressCards = document.querySelectorAll('.press-card');
#     let data = [];
#     pressCards.forEach((card) => {
#         let titleElement = card.querySelector('.title');
#         let title = titleElement ? titleElement.textContent.trim() : 'N/A';
        
#         let dateElement = card.querySelector('.date');
#         let date = dateElement ? dateElement.textContent.trim() : 'N/A';
        
#         let imageElement = card.querySelector('.press-card__image img');
#         let imageUrl = imageElement ? imageElement.src : 'N/A';

#         data.push({
#             title: title,
#             date: date,
#             imageUrl: imageUrl
#         });
#     });
#     return data;
# """)

# # Debugging: Print the data returned from JavaScript
# print("Scraped Data:", news_data)

# # Output directories
# output_csv = "raddisonblue_scraped_news_data.csv"
# image_dir = "raddisonblue_image"
# os.makedirs(image_dir, exist_ok=True)

# # Define CSV headers as required
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Write the data to a CSV file
# if news_data:
#     with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         writer.writerow(headers)

#         for idx, news in enumerate(news_data, 1):
#             title = news['title']
#             date = news['date']
#             image_url = news['imageUrl']
#             image_path = 'N/A'
#             slug = title.replace(" ", "-").lower()  # Simple slug generation
#             lead = "N/A"  # Placeholder for lead
#             content = "N/A"  # Placeholder for content
#             type_ = "Press Release"  # Placeholder for type
#             custom_field = "N/A"  # Placeholder for custom_field
#             parent_id = "N/A"  # Placeholder for parent_id
#             created_at = date  # Placeholder for created_at (using date)
#             updated_at = date  # Placeholder for updated_at (using date)
#             language = "en"  # Placeholder for language
#             seo_title = title  # Placeholder for SEO title
#             seo_content = "N/A"  # Placeholder for SEO content
#             seo_title_desc = "N/A"  # Placeholder for SEO title description
#             seo_content_desc = "N/A"  # Placeholder for SEO content description
#             category_id = "N/A"  # Placeholder for category_id

#             # If there's an image URL, download the image
#             if image_url != 'N/A':
#                 image_name = image_url.split("/")[-1]
#                 image_path = os.path.join(image_dir, image_name)

#                 # Download the image
#                 try:
#                     response = requests.get(image_url, stream=True)
#                     if response.status_code == 200:
#                         with open(image_path, "wb") as img_file:
#                             for chunk in response.iter_content(1024):
#                                 img_file.write(chunk)
#                     else:
#                         image_path = 'Failed to download'
#                 except Exception as e:
#                     image_path = f"Error: {e}"

#             # Write the row data to CSV with required format
#             writer.writerow([idx, title, slug, lead, content, image_path, type_, custom_field, parent_id, created_at, updated_at, language, seo_title, seo_content, seo_title_desc, seo_content_desc, category_id])

#             print(f"Scraped: {title}, {date}, Image Path: {image_path}")
# else:
#     print("No data found.")

# # Clean up and close the browser
# driver.quit()

# print(f"Scraping completed. Data saved to {output_csv} and images saved in {image_dir}.")














from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from insert_csv_into_sql_db import download_image,generate_random_filename
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import check_and_remove_file
from upload_and_reference import upload_photo_to_ftp

# Initialize WebDriver
driver = webdriver.Chrome()  # Use your preferred WebDriver
url = "https://www.radissonhotels.com/en-us/corporate/media/press-releases"  # Starting URL
driver.get(url)

# Wait for elements to load
wait = WebDriverWait(driver, 10)

# JavaScript to extract all hrefs that contain news links
news_links = driver.execute_script("""
    let links = document.querySelectorAll('a');
    return Array.from(links)
        .map(link => link.href)
        .filter(href => href.includes('/press-releases/'));  // Adjust based on URL structure
""")

print(f"Found {len(news_links)} news links.")

# List to store scraped data
news_data = []

# Visit each link and extract details
for link in news_links[:1]:
    driver.execute_script(f"window.open('{link}', '_blank');")  # Open link in a new tab
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
    try:
        # Wait for the title to load
        title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text

        # Extract content
        content = driver.execute_script("""
            let contentElement = document.querySelector("p.color-gunmetal.container-card-press-release__description");
            return contentElement ? contentElement.innerText : "Content not found";
        """)

        # Extract the image URL
        image_element = driver.find_element(By.CSS_SELECTOR, "img")
        image_url = image_element.get_attribute("src")

        image_name = generate_random_filename()

        download_image(image_url,image_name)

        upload_photo_to_ftp(image_name,"")

        # Store the scraped data
        news_data.append({
            "title": title,
            "content": content,
            "image_url": image_url,
            "news_url": link
        })
        print(f"Scraped: {title}")
    except Exception as e:
        print(f"Error scraping {link}: {e}")
    finally:
        # Close the current tab and switch back to the main tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

# Quit the WebDriver
driver.quit()

# Display the scraped data
for news in news_data:
    print("Title:", news["title"])
    print("Content:", news["content"])
    print("Image URL:", news["image_url"])
    print("News URL:", news["news_url"])
    print("-" * 80)
