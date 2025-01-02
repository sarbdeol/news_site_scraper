
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,insert_csv_data
from insert_csv_into_sql_db import generate_random_filename,download_image,date_format,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime
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

# Set up WebDriver (replace with the path to your ChromeDriver)

wait = WebDriverWait(driver, 30)  # Increase the wait time

# Navigate to the webpage
driver.get("https://www.leonardo-hotels.com/press")  # Replace with the target URL

# Define headers for CSV
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Sample data to write, you can populate these dynamically with your scraped content
data = {
    "id": "1",  # For example, could be dynamically generated or scraped
    "title": None,
    "subtitle":None,
    "slug": None,
    "lead": None,
    "content": None,
    "image": None,
    "type": None,
    "custom_field": None,
    "parent_id": None,
    "created_at": None,
    "updated_at": None,
    "added_timestamp": None, 
    "language": None,
    "seo_title": None,
    "seo_content": None,
    "seo_title_desc": None,
    "seo_content_desc": None,
    "category_id": None
}

try:
    # Wait until the link is visible (use the appropriate CSS selector to find the <a> tag)
    press_release_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".press__release")))

    # Use JavaScript to click on the link (to open the href)
    driver.execute_script('arguments[0].click();', press_release_link)

    # Optionally, you can wait for the new page to load
    # wait.until(EC.url_changes(driver.current_url))

    # Wait until the image is visible
    img_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='leonardo-hotels-employees']")))

    # Extract the src URL using JavaScript
    image_url = driver.execute_script('return arguments[0].src;', img_element)
      # Save the image URL

    img_name = generate_random_filename()

    download_image(data['image'],img_name)

    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Wait for the article to load
    article_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.col-12.w-lg-75.mx-auto.my-5.images_fix")))

    # Extract Title using JavaScript
    title = driver.execute_script("""
        var titleElement = document.querySelector('article p strong');
        return titleElement ? titleElement.innerText.trim() : null;
    """)
     # Save the title

    # Extract Date using JavaScript (it's assumed to be in a <small> element inside the article)
    date = driver.execute_script("""
        var pTags = document.querySelectorAll('article p');
        var date = null;

        pTags.forEach(function(p) {
            var text = p.innerText;
            // Use regex to search for a date pattern
            var match = text.match(/\\d{1,2}\\. [A-Za-z]+ \\d{4}/);  // Matches "19. November 2024"
            if (match) {
                date = match[0];  // Save the matched date
            }
        });

        return date;
    """)
      # Save the date as the creation date

    # Extract all <p> tags inside the article and concatenate their content
    paragraphs = driver.execute_script("""
        var pTags = document.querySelectorAll('article p');
        var text = '';
        pTags.forEach(function(p) {
            text += p.innerText + '\\n';  // Add newline after each paragraph for readability
        });
        return text;
    """)  # Save the article content

    # Set other data fields as needed
    title=generate_title(title) 
    data['id']=1
    data['title']=title
    data['subtitle']=generate_subtitle(title)
    data['slug'] = title.lower().replace(" ","-")  # Assign dynamically if possible
    data['lead'] = ""  # Assign dynamically if possible
    data['content'] = generate_news(paragraphs)
    data['image'] = 'information/'+img_name
    data['type'] = ""  # Example, assign based on actual content
    data['custom_field'] = ""  # Optional, assign if applicable
    data['parent_id'] = ""  # Optional, assign if applicable
    data['created_at'] = date_format(date)
    data['updated_at'] = datetime.now().today() # If not available, use created_at
    date['added_timestamp'] = date_format(date)
    data['language'] = ""  # Optional, assign the language
    data['seo_title'] = ""  # Optional, assign dynamically if applicable
    data['seo_content'] = ""  # Optional, assign dynamically if applicable
    data['seo_title_desc'] = ""  # Optional, assign dynamically if applicable
    data['seo_content_desc'] = ""  # Optional, assign dynamically if applicable
    data['category_id'] = 100  # Example, assign dynamically if applicable


    csv_file = "leonardo_Scraped_data.csv"
    # Write the data to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(data)  # Write the scraped data

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()

if date_format(date) ==  datetime.now().today():
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    insert_csv_data(csv_file,"informations")
    append_unique_records(csv_file,"combined_news_data.csv")
else:
    print("WE DO NOT HAVE DATA FOR TODAY")