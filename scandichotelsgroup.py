
import csv
from selenium import webdriver
import time
from datetime import datetime
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import date_format,download_image,generate_random_filename
from insert_csv_into_sql_db import insert_csv_data,check_and_remove_file,append_unique_records
from upload_and_reference import upload_photo_to_ftp

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disabling sandbox for headless mode
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)  # Set user-agent to mimic a real browser


# Add headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.rotana.com",  # Set a referer from the same domain if needed
}
# Setup Selenium WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Set up the Selenium WebDriver
base_url = "https://www.scandichotelsgroup.com/media/press-releases/"  # Replace with the actual URL

# CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

try:
    # Navigate to the page
    driver.get(base_url)
    time.sleep(5)  # Allow the page to load

    # Execute the JavaScript to extract the most recent news
    recent_news = driver.execute_script("""
        const firstItem = document.querySelector('div.item');
        const titleElem = firstItem.querySelector('h3.__name a');
        const imageElem = firstItem.querySelector('div._releaseImage img');
        const introElem = firstItem.querySelector('div.__intro');
        const dateElem = firstItem.querySelector('div._data');
        
        // Extracting the date part from the full string
        const dateText = dateElem ? dateElem.textContent.trim().split('|')[2].trim() : null;
        
        return {
            title: titleElem ? titleElem.textContent.trim() : null,
            href: titleElem ? titleElem.href : null,
            image: imageElem ? imageElem.src : null,
            content: introElem ? introElem.textContent.trim() : null,
            date: dateText ? dateText : null  // Get the correct date text
        };
    """)
    img_name =  generate_random_filename()

    download_image(recent_news['image'],img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    title = generate_title(recent_news['title'])
    date = date_format(recent_news['date'])
    print(date)
    # Prepare the data to write to CSV
    news_data = {
        "id": 1,  # Assign an ID for the entry
        "title": title,
        "subtitle": generate_subtitle(title),  # Placeholder
        "slug": title.lower().replace(" ","-"),       # Placeholder
        "lead": None,       # Placeholder
        "content": generate_news(recent_news['content']),
        "image": "information/"+img_name,
        "type": None,       # Placeholder
        "custom_field": None,  # Placeholder
        "parent_id": None,     # Placeholder
        "created_at": date,    # Placeholder
        "updated_at": datetime.now().today(),    # Placeholder
        "added_timestamp": date,  # Placeholder
        "language": None,         # Placeholder
        "seo_title": None,        # Placeholder
        "seo_content": None,      # Placeholder
        "seo_title_desc": None,   # Placeholder
        "seo_content_desc": None, # Placeholder
        "category_id": 100       # Placeholder
    }

    csv_file_path = "scandichotelsgroup_news.csv"
    check_and_remove_file(csv_file_path)
    # Write the data to CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerow(news_data)

    # print("News data successfully saved to 'recent_news.csv'")

finally:
    driver.quit()


if date == date_format(datetime.now().today()):
    insert_csv_data(csv_file_path,'informations')
    append_unique_records(csv_file_path,"combined_news_data.csv")

else:
    print("WE DO NOT HAVE DATA FOR TODAY")