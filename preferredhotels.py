# import os
# import csv
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from insert_csv_into_sql_db import insert_into_db,check_and_remove_file,generate_news
# import shutil

# # Setup Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Enable headless mode for scraping without opening the browser
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")

# # Initialize the Selenium WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Open the target URL
# url = "https://preferredhotels.com/press-center/press-releases"  # Replace with your actual URL
# driver.get(url)

# # Wait for the press-release table to load
# try:
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, '.press-release-table'))
#     )
#     print("Page loaded successfully.")
# except Exception as e:
#     print(f"Error: {e}")
#     driver.quit()
#     exit()

# # Initialize CSV output directory and file
# output_csv = "preferredhotels_scraped_news.csv"

# check_and_remove_file(output_csv)

# if os.path.exists('preferredhotels_images'):
#     print(f"Folder '{'preferredhotels_images'}' exists. Deleting and creating a new one...")
#     shutil.rmtree('preferredhotels_images') 
# os.makedirs("preferredhotels_images", exist_ok=True)

# # Define headers for CSV
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Open the CSV file for writing
# with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(headers)

#     # Loop through each press release entry
#     press_cards = driver.find_elements(By.CSS_SELECTOR, '.press-release-table tbody tr')
    
#     for idx, card in enumerate(press_cards, start=1):
#         try:
#             # Extracting the release date
#             date = card.find_element(By.CSS_SELECTOR, '.date-field div').text.strip()

#             # Extracting the title and URL
#             title_element = card.find_element(By.CSS_SELECTOR, '.title-field a')
#             title = title_element.text.strip()
#             slug = title.replace(" ", "-").lower()
#             link = title_element.get_attribute("href")

#             # Placeholder values for non-available fields
#             lead = "N/A"
#             content = "N/A"
#             image_url = "N/A"
#             type_ = "Press Release"
#             custom_field = "N/A"
#             parent_id = "N/A"
#             created_at = date
#             updated_at = date
#             language = "en"
#             seo_title = title
#             seo_content = "N/A"
#             seo_title_desc = "N/A"
#             seo_content_desc = "N/A"
#             category_id = "N/A"

#             # Scrape image (if available)
#             try:
#                 image_element = card.find_element(By.CSS_SELECTOR, '.press-card__image img')
#                 image_url = image_element.get_attribute("src")
#                 image_name = image_url.split("/")[-1]
#                 image_path = os.path.join("images", image_name)

#                 # Download the image
#                 response = requests.get(image_url, stream=True)
#                 if response.status_code == 200:
#                     with open(image_path, "wb") as img_file:
#                         for chunk in response.iter_content(1024):
#                             img_file.write(chunk)
#                 else:
#                     image_path = 'Failed to download'
#             except Exception as e:
#                 image_path = 'No image found'

#             title = generate_news(title)
#             # Write the scraped data to the CSV
#             writer.writerow([idx, title, slug, lead, content, image_path, type_, custom_field, parent_id, created_at, updated_at, language, seo_title, seo_content, seo_title_desc, seo_content_desc, category_id])

#             print(f"Scraped: {title}, {date}, Image Path: {image_path}")

#         except Exception as e:
#             print(f"Error processing entry: {e}")

# # Clean up and close the browser
# driver.quit()

# print(f"Scraping completed. Data saved to {output_csv} and images saved in 'images' folder.")

# insert_into_db(output_csv)





import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,check_and_remove_file,download_image,append_unique_records
from insert_csv_into_sql_db import insert_csv_data,date_format
from upload_and_reference import upload_photo_to_ftp

# CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Configure ChromeDriver in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run browser in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
driver = webdriver.Chrome(options=chrome_options)  # Set up WebDriver with options

base_url = "https://preferredhotels.com/press-center/press-releases"  # Replace with the actual URL

if True:

    try:
        # Navigate to the page
        driver.get(base_url)
        time.sleep(5)  # Allow the page to load

        # Execute the JavaScript to get the most recent news
        recent_news = driver.execute_script("""
            const rows = document.querySelectorAll('table.press-release-table tbody tr');
            function parseDate(dateString) {
                const months = {
                    January: '01', February: '02', March: '03', April: '04', May: '05', June: '06',
                    July: '07', August: '08', September: '09', October: '10', November: '11', December: '12'
                };
                const parts = dateString.split(' ');
                const month = months[parts[0]];
                const day = parts[1].replace(',', '').padStart(2, '0');
                const year = parts[2];
                return `${year}-${month}-${day}`;
            }

            const newsItems = Array.from(rows).map((row, index) => {
                const dateText = row.querySelector('td.date-field div').textContent.trim();
                const titleLink = row.querySelector('td.title-field a');
                const imageElem = row.querySelector('img');  // Assuming there's an <img> tag
                return {
                    id: index + 1,  // Generate an ID for each item
                    date: parseDate(dateText),
                    title: titleLink.textContent.trim(),
                    href: titleLink.href,
                    image: imageElem ? imageElem.src : null  // Get the image URL if it exists
                };
            });

            newsItems.sort((a, b) => new Date(b.date) - new Date(a.date));
            const mostRecentNews = newsItems[0];

            const linkElement = document.querySelector(`a[href="${mostRecentNews.href}"]`);
            if (linkElement) {
                linkElement.click();
                return mostRecentNews;  // Return the most recent news item details
            } else {
                return null;
            }
        """)

        img_name = generate_random_filename()
        
        download_image(recent_news['image'],img_name)

        upload_photo_to_ftp(img_name,recent_news['image'])
        title=  generate_title(recent_news['title'])
        date = date_format(recent_news['date'])
        # Save the extracted data in CSV format
        if recent_news:
            csv_data = [
                {
                    "id": recent_news['id'],
                    "title": title,
                    "subtitle": generate_subtitle(title),  # No subtitle available
                    "slug": title.lower().replace(" ","-"),  # No slug available
                    "lead": None,  # No lead available
                    "content": generate_news(title),  # No content available (PDF needs separate processing)
                    "image":"information/"+img_name,  # Include the image URL
                    "type": "Press Release",
                    "custom_field": None,
                    "parent_id": None,
                    "created_at": date,
                    "updated_at": time.time(),
                    "added_timestamp": date,
                    "language": "en",
                    "seo_title": '',
                    "seo_content": None,
                    "seo_title_desc": None,
                    "seo_content_desc": None,
                    "category_id": 100,
                }
            ]
            check_and_remove_file('recent_news_with_image.csv')
            # Write to CSV file
            with open("recent_news_with_image.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(csv_data)

            print(f"Most Recent News saved to 'recent_news_with_image.csv':\nTitle: {recent_news['title']}\nDate: {recent_news['date']}\nLink: {recent_news['href']}\nImage: {recent_news['image']}")
        else:
            print("No recent news found.")

    finally:
        driver.quit()

    if date == date_format(time.time()):
        insert_csv_data("recent_news_with_image.csv","informations")
        append_unique_records("recent_news_with_image.csv","combined_news_data.csv")
    else:
        print("WE DO NOT HAVE DATA FOR TODAY")

else:
    print("WE DO NOT HAVE DATA FOR TODAY")