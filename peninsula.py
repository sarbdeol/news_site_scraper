

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename
from insert_csv_into_sql_db import check_and_remove_file,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import download_image,date_format
from selenium.webdriver.chrome.options import Options

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

url = "https://www.peninsula.com/en/newsroom/news"  # Replace with your target URL
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# JavaScript to get the most recent news URL
js_code = """
    let links = document.querySelectorAll('.cardContainerlessNews-text h3.cardContainerless-headline a');
    
    let newsData = Array.from(links).map(link => {
        return {
            url: link.href,
            date: link.closest('.cardContainerlessNews').querySelector('h4.cardContainerless-title').innerText,
            title: link.innerText
        };
    });

    newsData.sort((a, b) => {
        let dateA = new Date(a.date.split('/').reverse().join('-'));
        let dateB = new Date(b.date.split('/').reverse().join('-'));
        return dateB - dateA;
    });

    return newsData.length > 0 ? newsData[0].url : null;
"""

# Get the most recent news URL
recent_news_url = driver.execute_script(js_code)

# Save the data to CSV
csv_file = "pennnisula_news.csv"
check_and_remove_file(csv_file)

# Print the most recent news URL
print("Recent News URL:", recent_news_url)

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# List to store data to save into CSV
news_data = []

# If a URL is found, navigate to it and extract title, content, and images
if recent_news_url:
    driver.get(recent_news_url)  # Open the recent news link
    
    # Wait for the page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))  # Assuming title is in <h1>
    
    # Extract title
    title = driver.find_element(By.TAG_NAME, "h1").text
    
    # Extract content (assuming content is within <div class="content">, update as per actual structure)
    js_code = """
    let paragraphs = document.querySelectorAll('p');
    let paragraphTexts = Array.from(paragraphs).map(p => p.innerText);
    let paragraphString = paragraphTexts.join('\\n');
    return paragraphString;
"""
    # Execute the JavaScript code to get all paragraph content in a single string
    paragraph_content = driver.execute_script(js_code)
    
    # Extract image URL (assuming image is in <img> tag)
    js_code = """
    let imageUrl = document.querySelector('div.imageWrapper img').getAttribute('src');
    return imageUrl;
"""

# Execute the JavaScript code to get the image URL
    image_url = driver.execute_script(js_code)

    image_url = "https://www.peninsula.com/"+image_url

    img_name = generate_random_filename()

    download_image(image_url,img_name)

    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    
    # Extract date (assuming date is in <p> tag with class 'date')
    js_code = """
    let date = document.querySelector('div.headline-footnote').innerText;
    return date;
"""
    # Execute the JavaScript code to get the date
    date = driver.execute_script(js_code)  # Adjust the selector for the date

    print(date)
    
    title = generate_title(title)

    date = date_format(date)
    # Prepare the data for CSV
    news_item = {
        "id": "",  # You can populate this if needed
        "title": title,
        "subtitle": generate_subtitle(title),  # Add subtitle if available or leave empty
        "slug": title.lower().replace(" ", "-").replace(",", "").replace(".", ""),  # Slug generated from title
        "lead": "",  # Add lead if available or leave empty
        "content": generate_news(paragraph_content),
        "image": "information/"+img_name,
        "type": "news",  # You can customize this if needed
        "custom_field": "",  # Add custom fields if needed
        "parent_id": "",  # Add parent ID if needed
        "created_at": date,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "added_timestamp": date,
        "language": "en",  # Modify as needed
        "seo_title": "",
        "seo_content": "",
        "seo_title_desc": "",
        "seo_content_desc": "",
        "category_id": "100"  # Add category ID if available
    }

    # Append the data to the list
    news_data.append(news_item)

# Quit the driver
driver.quit()


with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    for row in news_data:
        writer.writerow(row)

print(f"Data saved to {csv_file}")

if date != date_format(datetime.now().today()):
    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    # insert_csv_data(csv_file,'informations')
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("WE DO NOT HAVE DATA FOR TODAY")