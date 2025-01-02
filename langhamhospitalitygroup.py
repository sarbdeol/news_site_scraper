import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image,append_unique_records


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
# Ensure you have the appropriate WebDriver for your browser
driver.get("https://www.langhamhospitalitygroup.com/en/media/latest-news/")  # Replace with the URL of the page you are targeting

# Open a CSV file to write the extracted data
with open('news_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the headers

    try:
        # Wait for the link to be present in the DOM
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.tile a.js-link'))
        )
        
        # JavaScript to extract and open the href
        js_code = """
        const linkElement = document.querySelector('.tile a.js-link');
        if (linkElement) {
            const href = linkElement.href;
            window.open(href, '_blank'); // Open in new tab
            return href;  // Return href to Python
        } else {
            console.log("Link element not found.");
            return null;
        }
        """
        
        # Execute the JavaScript to get the href and open it
        extracted_href = driver.execute_script(js_code)

        # Navigate to the extracted href
        driver.get(extracted_href)

        # JavaScript code to extract title and subtitle
        js_code = """
        const titleElement = document.querySelector('div.l-container header h1');
        const subtitleElement = document.querySelector('div.l-container header h2');

        const title = titleElement ? titleElement.textContent.trim() : null;
        const subtitle = subtitleElement ? subtitleElement.textContent.trim() : null;

        return { title, subtitle };
        """

        # Execute JavaScript in the browser and get the title and subtitle
        result = driver.execute_script(js_code)
        title = result['title']
        subtitle = result['subtitle']

        print(f"Title: {title}, Subtitle: {subtitle}")

        # JavaScript code to extract the date
        js_code = """
        const pElement = document.querySelector('p[style="text-align: left;"]');
        if (pElement) {
            const dateText = pElement.textContent.match(/\\d{1,2} \\w+ \\d{4}/);
            return dateText ? dateText[0] : null;
        } else {
            console.log("Date element not found.");
            return null;
        }
        """
        # Execute JavaScript in the browser and get the date
        extracted_date = driver.execute_script(js_code)
        print("Date:", extracted_date)

        # JavaScript code to extract the image URL
        js_code = """
        const imageElement = document.querySelector('img');
        if (imageElement) {
            return imageElement.src;
        } else {
            console.log("Image not found.");
            return null;
        }
        """
        # Execute JavaScript in the browser and get the image URL
        image_url = driver.execute_script(js_code)
        print("Image URL:", image_url)

        img_name = generate_random_filename()

        download_image(image_url,img_name)
        # upload_photo_to_ftp(img_name,"/public_html/storage/information/")
        
        # JavaScript code to extract all <p> content
        js_code = """
        const pTags = document.querySelectorAll('.text-section--description.rich-content p');
        let textContent = '';
        pTags.forEach(p => {
            textContent += p.innerText + ' ';
        });
        return textContent.trim();
        """

        # Execute the JavaScript and retrieve the combined <p> tag text
        combined_text = driver.execute_script(js_code)
        print("Combined text content from <p> tags:", combined_text)

        # Prepare data to be written in CSV
        # Note: Some fields like "id", "slug", "lead", "type", etc., need to be filled with actual values if available
        data = [
            "unique_id",  # id (example placeholder, replace with actual logic)
            title,  # title
            subtitle,  # subtitle
            "slug_placeholder",  # slug (example placeholder)
            "lead_placeholder",  # lead (example placeholder)
            combined_text,  # content (from all <p> tags)
            image_url,  # image URL
            "type_placeholder",  # type (example placeholder)
            "custom_field_placeholder",  # custom_field (example placeholder)
            "parent_id_placeholder",  # parent_id (example placeholder)
            extracted_date,  # created_at (extracted date)
            "updated_at_placeholder",  # updated_at (example placeholder)
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # added_timestamp (current timestamp)
            "language_placeholder",  # language (example placeholder)
            "seo_title_placeholder",  # seo_title (example placeholder)
            "seo_content_placeholder",  # seo_content (example placeholder)
            "seo_title_desc_placeholder",  # seo_title_desc (example placeholder)
            "seo_content_desc_placeholder",  # seo_content_desc (example placeholder)
            "category_id_placeholder"  # category_id (example placeholder)
        ]

        # Write the row to the CSV file
        writer.writerow(data)

    finally:
        # Close the WebDriver
        driver.quit()

print("Data extraction and CSV writing completed.")



if extracted_date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")
    insert_csv_data("news_data.csv", "informations")
    append_unique_records("news_data.csv","combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")