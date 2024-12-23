import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
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

# Navigate to the target website
# driver.get("https://www.discoverasr.com/en/the-ascott-limited/newsroom")

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]


# Navigate to the page containing the press item
driver.get("https://www.tuigroup.com/en-en/media/press-releases")  # Replace with the actual URL

# Wait for the press item to load
WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, '.press-item'))
)

# JavaScript to get the href of the <a> tag inside the .title div
js_code = """
const linkElement = document.querySelector('.press-item .title a');
if (linkElement) {
    return linkElement.href; // Get the href attribute of the <a> tag
} else {
    return null; // Return null if no <a> tag is found
}
"""

# Execute the JavaScript code
href = driver.execute_script(js_code)

if href:
    print(f"Opening the link: {href}")
    driver.get(href)  # Open the extracted URL in the browser

    # Extract data
    js_code = """
    const dateElement = document.querySelector('.media-news-header .date');
    if (dateElement) {
        return dateElement.innerText.trim();
    } else {
        return null;
    }
    """
    date_text = date_format(driver.execute_script(js_code))

    js_code = """
    const titleElement = document.querySelector('header.content-header h1');
    if (titleElement) {
        return titleElement.innerText.trim();
    } else {
        return null;
    }
    """
    title_text = generate_title(driver.execute_script(js_code))

    js_code = """
    let pTags = document.querySelectorAll('.content.row p');
    let pContent = [];
    pTags.forEach(p => {
        pContent.push(p.innerText.trim());
    });
    return pContent.join('\\n');
    """
    p_tags_content = generate_news(driver.execute_script(js_code))

    js_code = """
    let imgElement = document.querySelector('img');
    if (imgElement) {
        return imgElement.getAttribute('data-src') || imgElement.src;
    } else {
        return null;
    }
    """

    img_name  = generate_random_filename()
    image_url = driver.execute_script(js_code,img_name)
    download_image(image_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Prepare row data
    row_data = {
        "id": None,  # Set a unique ID if needed
        "title": title_text,
        "subtitle":generate_subtitle(title_text),
        "slug": title_text.lower().replace(" ","-"),
        "lead": None,
        "content": p_tags_content,
        "image": "information/"+img_name,
        "type": None,
        "custom_field": None,
        "parent_id": None,
        "created_at": date_text,
        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "added_timestamp":date_text,
        "language": "en",
        "seo_title": None,
        "seo_content": None,
        "seo_title_desc": None,
        "seo_content_desc": None,
        "category_id": 100
    }

    # Save data to CSV
    output_file = "tuigroup_output.csv"
    try:
        # Check if file exists
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            # Write header only if the file is empty
            if file.tell() == 0:
                writer.writeheader()

            # Write the row
            writer.writerow(row_data)

        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")
else:
    print("No link found.")

# Close the driver when done
driver.quit()


if date_text ==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data(output_file, "informations")
    append_unique_records(output_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")