
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import insert_csv_data
from insert_csv_into_sql_db import generate_random_filename
from insert_csv_into_sql_db import check_and_remove_file,date_format,download_image,append_unique_records
from datetime import datetime
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
    "seo_content_desc", "category_id"
]


check_and_remove_file("marriott_news_data.csv")

# Create the CSV file and write the headers
with open("marriott_news_data.csv", mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    try:
        # Load the main page
        driver.get("https://news.marriott.com/news?newstype=press-releases")  # Replace with the actual URL

        # Execute JavaScript to get all hrefs
        links = driver.execute_script("""
            let anchors = Array.from(document.querySelectorAll("a.block.cursor-pointer"));
            return anchors.map(anchor => anchor.href);
        """)

        # Visit each link and extract data
        for link in links[:1]:  # Limit to the first link for testing
            driver.get(link)  # Navigate to the link
            time.sleep(2)  # Wait for the page to load

            # Extract data
            title_text = driver.execute_script("""
                return document.querySelector("div.w-full.flex.items-center.justify-center h3").textContent;
            """)
            date = driver.execute_script("""
                return document.querySelector("div.flex.items-center.justify-center span").textContent;
            """)
            print(date)
            combined_paragraph = driver.execute_script("""
                return Array.from(document.querySelectorAll("div.rte p"))
                    .map(p => p.textContent.trim())
                    .join(" ");
            """)
            image_url = driver.execute_script("""
                return document.querySelector("img.download-asset").src;
            """)

            title_text = generate_title(title_text)

            img_name =generate_random_filename()

            download_image(image_url,img_name)

            upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    
            date = date_format(date)

            # Generate data for the current article (mock data for the fields not present)
            news_item = [
                "1",  # id (this would be dynamically generated in a real use case)
                title_text,
                generate_subtitle(title_text),  # subtitle
                title_text.lower().replace(" ","-"),  # slug
                "",  # lead
                generate_news(combined_paragraph),
                "information/"+img_name,
                "",  # type
                "",  # custom_field
                "",  # parent_id
                date,  # created_at
                datetime.now().today(),  # updated_at
                date , # added_timestamp
                "",  # language
                "",  # seo_title
                "",  # seo_content
                "",  # seo_title_desc
                "",  # seo_content_desc
                100   # category_id
            ]

            # Write the data to CSV file
            writer.writerow(news_item)
            print(f"Saved: {title_text}")

    finally:
        driver.quit()

print("Data extraction completed.")


if date==date_format(datetime.now().today()):
    insert_csv_data("marriott_news_data.csv","informations")
    append_unique_records("marriott_news_data.csv","combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")