import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

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

driver.maximize_window()

# Navigate to the page
driver.get("https://swissinternationalhotels.com/news-updates/")  # Replace with the actual URL

# JavaScript code to click the "Recent" button
js_code = """
const recentButton = document.querySelector('li.uael-post__header-filter[data-filter=".arecent"]');
if (recentButton) {
    recentButton.click();
} else {
    return 'Recent button not found';
}
"""

# Execute the JavaScript code to click the button
driver.execute_script(js_code)

# JavaScript code to get the href of the "Read More" button
js_code = """
const readMoreLink = document.querySelector('.uael-post__content-wrap .uael-post__read-more');
if (readMoreLink) {
    return readMoreLink.href;
} else {
    return null;
}
"""

# Execute JavaScript to get the URL of the most recent news
news_url = driver.execute_script(js_code)

if news_url:
    print(f"Opening the news article: {news_url}")
    driver.get(news_url)

    # JavaScript code to extract the title
    js_code = """
    const titleElement = document.querySelector('h1.elementor-heading-title');
    if (titleElement) {
        return titleElement.innerText.trim();
    } else {
        return null;
    }
    """

    # Execute JavaScript to get the title
    title = generate_title(driver.execute_script(js_code))

    print(title)

    # JavaScript code to extract image URLs and <p> tag content
    js_code = """
    // Extract the image URLs
    const imgElements = document.querySelectorAll('div.elementor-widget-container p img');
    let imgUrls = [];
    imgElements.forEach(img => {
        imgUrls.push(img.src);
    });

    // Extract the content of <p> tags
    const pElements = document.querySelectorAll('div.elementor-widget-container p');
    let pContent = [];
    pElements.forEach(p => {
        pContent.push(p.innerText.trim());
    });

    // Combine image URLs and <p> tag content into a single string
    return { images: imgUrls, paragraphs: pContent.join("\\n") };
    """

    # Execute JavaScript to get the image URLs and <p> tag content
    result = driver.execute_script(js_code)

    img_url = result['images'][0]
    img_name = generate_random_filename()
    download_image(img_url,img_name)
    # upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # JavaScript code to extract the date
    js_code = """
    const dateElement = document.querySelector('span.elementor-icon-list-text.elementor-post-info__item--type-date');
    if (dateElement) {
        return dateElement.innerText.trim();
    } else {
        return null;
    }
    """

    # Execute JavaScript to get the date
    date = date_format(driver.execute_script(js_code))
    print(f"Date: {date}")

    # Define headers for the CSV
    headers = [
        "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
        "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
        "language", "seo_title", "seo_content", "seo_title_desc", 
        "seo_content_desc", "category_id"
    ]

    # Prepare data in the required format
    data = [
        "1",  # Example ID, you can generate or extract this dynamically
        title,  # Title of the article
    generate_subtitle(title),  # Subtitle (you can leave it empty or extract if needed)
        title.lower().replace(" ","-"),  # Slug (you can extract or create a slug from the title or URL)
        "",  # Lead (this can be extracted from the content or left empty)
        generate_news(result['paragraphs']),  # Content of the article
        result['images'][0] if result['images'] else "",  # Image URL (first image)
        "article",  # Type (assuming this is an article type)
        "",  # Custom field (you can add if necessary)
        "",  # Parent ID (if applicable)
        date,  # Created date (use the extracted date)
        time.time(),  # Updated date (assuming same as created date for now)
        date,  # Added timestamp (you can add a timestamp if needed)
        "en",  # Language (example as 'en')
        "",  # SEO title (leave empty if not available)
        "",  # SEO content (leave empty if not available)
        "",  # SEO title description (if applicable)
        "",  # SEO content description (if applicable)
        "1"  # Category ID (this can be changed as required)
    ]

    # Write the data to CSV
    with open("scraped_data.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write headers only if the file is empty (for the first time)
        if file.tell() == 0:
            writer.writerow(headers)
        writer.writerow(data)

else:
    print("No 'Read More' link found.")

# Close the driver when done
driver.quit() 


if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    insert_csv_data("scraped_data.csv", "informations")
    append_unique_records("scraped_data.csv","combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")