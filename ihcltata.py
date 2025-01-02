import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
from selenium.webdriver.chrome.options import Options
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




# Define headers for the CSV
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Navigate to the page
driver.get("https://www.ihcltata.com/press-room/")  # Replace with the actual URL

# Wait for the press card elements to load
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.pressCard-description-container'))
)

# Scrape the data (retaining your scraping logic)

# Get the date
js_code_date = """
const dateElement = document.querySelector('.pressCard-date span');
if (dateElement) {
    return dateElement.innerText.trim();
} else {
    return null;
}
"""
date = date_format(driver.execute_script(js_code_date))

print(date)

# Get the most recent href
js_code_href = """
const mostRecentLink = document.querySelector('.pressCard-description-container a');
if (mostRecentLink) {
    return mostRecentLink.href;
} else {
    return null;
}
"""
most_recent_href = driver.execute_script(js_code_href)

if most_recent_href:
    driver.get(most_recent_href)  # Open the extracted URL in the browser

    # Get the title text
    js_code_title = """
    const titleElement = document.querySelector('h1.cm-header-label.title-center');
    if (titleElement) {
        return titleElement.innerText.trim();
    } else {
        return null;
    }
    """
    title = generate_title(driver.execute_script(js_code_title))

    # Get the image URL
    js_code_image = """
    const imgElement = document.querySelector('img.about-carousel-images');
    if (imgElement) {
        return imgElement.src;
    } else {
        return null;
    }
    """
    image_url = driver.execute_script(js_code_image)

    img_name = generate_random_filename()

    download_image(image_url,img_name)

    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")


    # Get the content of all <p> tags inside .news-description
    js_code_p_tags = """
    let pTags = document.querySelectorAll('.news-description p');
    let pContent = [];
    pTags.forEach(p => {
        pContent.push(p.innerText.trim());
    });
    return pContent.join('\\n');
    """
    p_tags_content =generate_news(driver.execute_script(js_code_p_tags))

    # Store the data in a dictionary
    data = {
        "id": 1,  # You can set this to None or extract from the page if available
        "title": title,
        "subtitle": generate_subtitle(title),  # Set if available
        "slug": title.lower().replace(" ","-"),  # You can extract the slug from the href
        "lead": None,  # Set if available
        "content": p_tags_content,
        "image": "information/"+img_name,
        "type": None,  # Set if available
        "custom_field": None,  # Set if available
        "parent_id": None,  # Set if available
        "created_at": date,
        "updated_at": datetime.now().today(),  # Set if available
        "added_timestamp": date,  # Set if available
        "language": None,  # Set if available
        "seo_title": None,  # Set if available
        "seo_content": None,  # Set if available
        "seo_title_desc": None,  # Set if available
        "seo_content_desc": None,  # Set if available
        "category_id": None  # Set if available
    }
    csv_file ="ihcltata_scraped_data.csv"
    # Write the data to CSV
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Write the header only once
        if file.tell() == 0:  # Check if file is empty (i.e., write header)
            writer.writeheader()

        # Write the row of data
        writer.writerow(data)

    print("Data saved to CSV")

else:
    print("No recent link found.")

# Close the driver when done
driver.quit()


if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    insert_csv_data(csv_file, "informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")