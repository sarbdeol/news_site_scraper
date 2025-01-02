# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import csv
# import os

# # Setup Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")

# # Initialize WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # URL to scrape
# url = "https://www.panpacific.com/en/newsroom.html#/latest_news"  # Replace with the actual URL
# driver.get(url)

# # Wait for the page to load
# try:
#     WebDriverWait(driver, 30).until(
#         EC.presence_of_all_elements_located((By.CLASS_NAME, 'panel'))
#     )
#     print("Page loaded successfully.")
# except Exception as e:
#     print(f"Error: {e}")
#     driver.quit()
#     exit()

# # Execute JavaScript to scrape data
# news_data = driver.execute_script("""
#     let data = [];
#     document.querySelectorAll('.panel').forEach(article => {
#         let titleElement = article.querySelector('.panel__heading a');
#         let title = titleElement ? titleElement.getAttribute('title').trim() : 'N/A';

#         let dateElement = article.querySelector('.panel__date');
#         let date = dateElement ? dateElement.textContent.trim() : 'N/A';

#         let imageElement = article.querySelector('.panel__media img');
#         let imageUrl = imageElement ? imageElement.src : 'N/A';

#         data.push({
#             title: title,
#             date: date,
#             image: imageUrl
#         });
#     });
#     return data;
# """)

# # Debugging: Print the extracted data
# if not news_data:
#     print("No data was scraped. Check your JavaScript or page content.")
# else:
#     print("Scraped Data:", news_data)

# # Output directory for CSV
# output_csv = "scraped_news.csv"

# # Save data to CSV
# with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(["Title", "Date", "Image URL"])  # CSV headers

#     for item in news_data:
#         writer.writerow([item['title'], item['date'], item['image']])

# print(f"Scraping completed. Data saved to {output_csv}.")

# # Clean up and close the browser
# driver.quit()











import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,insert_into_db
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,append_unique_records
from upload_and_reference import upload_photo_to_ftp

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage (optional, improves performance)
chrome_options.add_argument("--no-sandbox")  # Recommended for headless mode in some environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues
chrome_options.add_argument("--window-size=1920,1080")  # Set the window size for screenshots

# Specify the path to your ChromeDriver executable
chromedriver_path = "/usr/local/bin/chromedriver"  # Replace with the actual path to ChromeDriver

# Set up the WebDriver with Chrome options
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id", "date"
]

# CSV file to save the data
csv_file = "panpacific_data.csv"

base_url = "https://www.panpacific.com/en/newsroom.html#/latest_news"  # Replace with the actual URL

try:
    # Navigate to the page
    driver.get(base_url)
    time.sleep(5)  # Allow the page to load fully

    # Execute JavaScript to get the most recent news item details and click on it
    recent_news = driver.execute_script("""
        const storyPanel = document.querySelector('.panel__content.story');
        if (!storyPanel) return null;

        const titleElement = storyPanel.querySelector('.panel__heading a');
        const contentElement = storyPanel.querySelector('p');
        const imageElement = storyPanel.querySelector('.panel__media img');
        const dateElement = storyPanel.querySelector('time');

        const data = {
            title: titleElement ? titleElement.getAttribute('title') : null,
            href: titleElement ? titleElement.getAttribute('href') : null,
            content: contentElement ? contentElement.textContent.trim() : null,
            image: imageElement ? imageElement.getAttribute('src') : null,
            date: dateElement ? dateElement.getAttribute('datetime') : null
        };

        if (data.href) {
            titleElement.click();  // Simulate clicking on the link
        }

        return data;  // Return the extracted details
    """)
    if not recent_news:
        print("NO RECENT NEWS WAS FOUND,EXITING SCRIPT")
        driver.quit()
        exit(0)
    if recent_news:
        print("Most Recent News:")
        print("Title:", recent_news["title"])
        print("Content:", recent_news["content"])
        print("Image URL:", recent_news["image"])
        print("Link:", recent_news["href"])
        print("Date:", recent_news["date"])
        
        img_name=generate_random_filename()

        download_image(recent_news["image"],img_name)

        # upload_photo_to_ftp(img_name,recent_news["image"])

        # Save to CSV file
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            # Write header row
            writer.writeheader()

            title =  generate_title(recent_news["title"])
            date  = date_format(recent_news["date"])
            print(date)
            # Map extracted data to the headers
            row = {
                "id": 1,  # Example ID, you can use dynamic values if needed
                "title": recent_news["title"],
                "subtitle": generate_subtitle(title),  # Add this value if available
                "slug": title.lower().replace(" ","-"),  # Add this value if available
                "lead": "",  # Add this value if available
                "content": generate_news(recent_news["content"]),
                "image": recent_news["image"],
                "type": "news",  # Static type, change if needed
                "custom_field": "",  # Add this value if available
                "parent_id": "",  # Add this value if available
                "created_at": date,  # Current timestamp
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),  # Current timestamp
                "added_timestamp": date,  # Current timestamp
                "language": "en",  # Static language, change if needed
                "seo_title":"",  # Use title for SEO
                "seo_content": "",  # Use content for SEO
                "seo_title_desc": "",  # Add this value if available
                "seo_content_desc": "",  # Add this value if available
                "category_id": 100,  # Add this value if availableL
            }

            writer.writerow(row)

        print(f"Data saved to {csv_file}")
    else:
        print("No recent news found.")

finally:
    driver.quit()


if date_format(recent_news["date"]) ==  date_format(time.strftime("%Y-%m-%d %H:%M:%S")):
    upload_photo_to_ftp(img_name,recent_news["image"])
    insert_into_db(csv_file,'informations')
    append_unique_records(csv_file,"combined_news_data.csv")
else:
    print("WE DO NOT HAVE DATA FOR TODAY")