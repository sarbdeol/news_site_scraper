import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
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

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Navigate to the page
driver.get("https://www.shangri-la.com/group/media/")  # Replace with the actual URL of the page

# Wait for the page to load completely before extracting content
WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, '.single-media-posts-box'))
)

# JavaScript code to get the most recent href from the Learn More button
js_code = """
const mostRecentLink = document.querySelector('.single-media-posts-box .row .single-posts-learn-more a'); 
if (mostRecentLink) {
    return mostRecentLink.href;  // Get the href attribute of the most recent link
} else {
    return null;  // No link found
}
"""

# Execute JavaScript to get the most recent href
most_recent_href = driver.execute_script(js_code)

if most_recent_href:
    print(f"Most recent href: {most_recent_href}")
    driver.get(most_recent_href)  # Open the most recent link in the browser

    # Wait for the title and date to be visible before extracting them
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h2.single-press-releases-title'))
    )

    # JavaScript code to extract the title and date
    js_code = """
    const titleElement = document.querySelector('h2.single-press-releases-title');
    const dateElement = document.querySelector('p.press-releases-meta span[ng-if="article.date"]');

    let title = titleElement ? titleElement.innerText : null;
    let date = dateElement ? dateElement.innerText : null;

    return { title, date };
    """

    # Execute JavaScript to get the title and date
    result = driver.execute_script(js_code)

    if result:
        title = result.get('title')
        date = result.get('date')
        print(f"Title: {title}")
        print(f"Date: {date}")

    # Wait for the image URL to be available before extracting
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.btn-banner-video'))
    )

    # JavaScript code to extract the image URL
    js_code = """
    const imageUrlElement = document.querySelector('a.btn-banner-video');
    if (imageUrlElement) {
        return imageUrlElement.getAttribute('data-video-poster');
    } else {
        return null;
    }
    """

    # Execute JavaScript to get the image URL
    image_url = driver.execute_script(js_code)
    img_nmae = generate_random_filename()
    if image_url:
        print(f"Image URL: {image_url}")

        download_image(image_url,img_nmae)
        upload_photo_to_ftp(img_nmae,"/public_html/storage/information/")
    else:
        print("Image URL not found.")

    # JavaScript code to extract content of first 5 <p> tags
    js_code = """
    let pTags = document.querySelectorAll('p');  // Select all <p> tags
    let pContent = [];  // Initialize an empty array to store the content

    // Loop through the first 5 <p> tags and add their text content to the array
    for (let i = 0; i < 5 && i < pTags.length; i++) {
        pContent.push(pTags[i].innerText.trim());  // Add the text of each <p> tag to the array
    }

    return pContent;  // Return the array of <p> tag contents
    """

    # Execute JavaScript to get the <p> tags content
    p_tags_content = driver.execute_script(js_code)

    print(p_tags_content)
    title =  generate_title(result.get('title'))

    date  = date_format(result.get('date'))

    print(date)

    # Prepare data to store in CSV
    data = {
        "id": 1,  # You can dynamically generate this ID if needed
        "title": title,
        "subtitle": generate_subtitle(title),  # Placeholder for the missing subtitle
        "slug": title.lower().replace(" ","-"),  # Placeholder for the missing slug
        "lead": None,  # Placeholder for the missing lead
        "content": generate_news(" ".join(p_tags_content)),
        "image": "information/"+img_nmae,
        "type": None,  # Placeholder for the missing type
        "custom_field": None,  # Placeholder for the missing custom field
        "parent_id": None,  # Placeholder for the missing parent_id
        "created_at": date,  # Using the extracted date
        "updated_at": time.time(),  # Placeholder for the missing updated_at
        "added_timestamp": date,  # Placeholder for the missing added_timestamp
        "language": None,  # Placeholder for the missing language
        "seo_title": None,  # Placeholder for the missing seo_title
        "seo_content": None,  # Placeholder for the missing seo_content
        "seo_title_desc": None,  # Placeholder for the missing seo_title_desc
        "seo_content_desc": None,  # Placeholder for the missing seo_content_desc
        "category_id": 100  # Placeholder for the missing category_id
    }

    # Write data to CSV file
    with open('shangri_extracted_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()  # Write headers to the CSV
        writer.writerow(data)  # Write the extracted data

else:
    print("No link found.")

# Optional: Close the driver after some time or when you're done
driver.quit()

if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data("shangri_extracted_data.csv", "informations")
    append_unique_records("shangri_extracted_data.csv","combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")
