import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
import time
from datetime import datetime

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

# Navigate to the page
driver.get("https://www.yotel.com/en/news")  # Replace with the actual URL of the page

# JavaScript code to get the most recent href
js_code = """
const mostRecentLink = document.querySelector('article.yotel-blog-listing__item a');
if (mostRecentLink) {
    return mostRecentLink.href;  // Get the href of the most recent link
} else {
    return null;  // No link found
}
"""

# Execute JavaScript to get the most recent href
most_recent_href = driver.execute_script(js_code)

if most_recent_href:
    driver.get(most_recent_href)

    # JavaScript code to get the date and title
    js_code = """
    const dateElement = document.querySelector('div.container time');
    const titleElement = document.querySelector('div.container h2 span');

    const date = dateElement ? dateElement.innerText : null;
    const title = titleElement ? titleElement.innerText.trim() : null;

    return { date, title };
    """

    # Execute JavaScript to get the date and title
    data = driver.execute_script(js_code)

    # JavaScript code to get the image URL
    js_code = """
    const imgElement = document.querySelector('img[loading="lazy"]');
    if (imgElement) {
        return imgElement.src;
    } else {
        return null;
    }
    """
    
    img_url = driver.execute_script(js_code)

    # JavaScript code to get text from the first few <p> tags
    js_code = """
    let pTags = document.querySelectorAll('.container p'); 
    let textContent = '';
    for (let i = 0; i < 3; i++) {  // Adjust the number to get the required number of <p> tags
        if (pTags[i]) {
            textContent += pTags[i].innerText + ' ';
        }
    }
    return textContent.trim();  // Return the concatenated text as a string
    """
    
    p_tags_text = driver.execute_script(js_code)

    img_name =  generate_random_filename()

    download_image(img_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    
    date = date_format(data['date'])

    print(date)

    title = generate_title(data['title'])

    # Prepare the data for CSV
    row_data = {
        "id": 1,  # Set an ID for the entry (this could be dynamic if needed)
        "title": title,
        "subtitle": generate_subtitle(title),  # Assuming no subtitle is found
        "slug": title.lower().replace(" ","-"),  # Extract the slug from the URL
        "lead": "",  # You can adjust this if you have a specific lead to add
        "content": generate_news(p_tags_text),  # Add the content from the <p> tags
        "image": "information/"+img_name,
        "type": "",  # Set a type if applicable
        "custom_field": "",  # Custom fields, if any
        "parent_id": "",  # If you have a parent ID, you can set it here
        "created_at": date,
        "updated_at": time.time(),  # Set if you have an update date
        "added_timestamp": date,  # Current timestamp
        "language": "en",  # Assuming the language is English
        "seo_title": "",  # SEO Title, if any
        "seo_content": "",  # SEO content, if any
        "seo_title_desc": "",  # SEO title description
        "seo_content_desc": "",  # SEO content description
        "category_id": 100  # Set a category ID if available
    }

    # Define CSV headers
    headers = [
        "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
        "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
        "language", "seo_title", "seo_content", "seo_title_desc",
        "seo_content_desc", "category_id"
    ]

    # Write data to CSV
    check_and_remove_file("yotel_data.csv")
    with open('yotel_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()  # Write the header
        writer.writerow(row_data)  # Write the extracted data

    print("Data has been saved to yotel_data.csv")

else:
    print("No link found.")

# Optional: Close the driver after some time or when you're done
driver.quit()


if date_format(data.get("date", ""))==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data("yotel_data.csv", "informations")
    append_unique_records("yotel_data.csv","combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")