import requests
import time
import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from datetime import datetime
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# Setup Selenium WebDriver
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

# Update this line with the path to your Tesseract executable (if you need OCR)
# pytesseract.pytesseract.tesseract_cmd = r"C:\path\to\tesseract.exe"  # For Windows
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# Open the page URL containing the PDF link
driver.get("https://www.redroof.com/media")  # Replace with the actual page URL

# JavaScript code to extract title, image URL, and date
js_code = """
var result = {};

// Extract the title from the <a> tag
var titleElement = document.querySelector('.body-title.mb-2.text-decoration-none');
if (titleElement) {
    result.title = titleElement.textContent.trim();
} else {
    result.title = 'Title not found';
}

// Extract the image URL (if image is present) — the code assumes the image URL is located in the surrounding div
var imageElement = document.querySelector('.w-100.d-flex.image-vertical-tiles.rounded');
if (imageElement && imageElement.src) {
    result.image_url = imageElement.src.trim();
} else {
    result.image_url = 'Image not found';
}

// Extract the date from the text inside the body-small div (class "text-black-50")
var dateElement = document.querySelector('.body-small.text-black-50.mt-2');
if (dateElement) {
    result.date = dateElement.textContent.trim();
} else {
    result.date = 'Date not found';
}

return result;
"""

# Execute JavaScript code to get the result
result = driver.execute_script(js_code)

date = date_format(result.get('date'))
print(date)
title = generate_title(result.get('title'))

img_name = generate_random_filename()

if result.get('image_url') != 'Image not found':

    download_image(result.get('image_url'),img_name)

    upload_photo_to_ftp(result.get('image_url'),"/public_html/storage/information/")

# Check if data is available, otherwise close and exit
if result.get('title') == 'Title not found' and result.get('date') == 'Date not found':
    print("No title or date found, closing browser.")
    driver.quit()
    exit()


# JavaScript code to click the link and open the PDF in a new tab
js_code = """
var pdfLink = document.querySelector('a[href="https://images.redroof.com/m/260a3c604c0f8b5e/original/Adrian-Award-press-release.pdf"]');
if (pdfLink) {
    var href = pdfLink.href;
    window.open(href, '_blank');  // Open the PDF in a new tab
    return href;  // Return the href for verification or logging
} else {
    return "No link found";  // If the link isn't found
}
"""

# Execute JavaScript code to open the PDF
pdf_url = driver.execute_script(js_code)

# Wait for the new tab to open and the PDF to load (adjust as needed)
time.sleep(5)

# Download the PDF (fetch the PDF content)
response = requests.get(pdf_url)
pdf_filename = "downloaded_pdf.pdf"
with open(pdf_filename, 'wb') as file:
    file.write(response.content)

# Extract text from the PDF (if text is present)
def extract_pdf_text(pdf_filename):
    with open(pdf_filename, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()  # Extract text from each page
        return text

# Function to extract the first header, content, and date from the PDF text
def extract_title_content_date(pdf_text):
    lines = pdf_text.split('\n')
    
    title = ""
    content = ""
    date = ""
    
    # More refined regular expression to capture multiple date formats
    date_pattern = r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{1,2} [A-Za-z]+ \d{4}|\w+ \d{1,2}, \d{4})\b"
    
    # Log the text to inspect the structure
    print("Extracted PDF Text:")
    print(pdf_text)
    
    for line in lines:
        line = line.strip()
        
        # First non-empty line is considered as title
        if title == "" and line:
            title = line
        
        # All other text is considered content
        else:
            content += line + " "
        
        # Check for date-like string
        if not date:
            # Match date pattern: either MM/DD/YYYY, DD Month YYYY, or Month DD, YYYY
            date_match = re.search(date_pattern, line)
            if date_match:
                date = date_match.group(0)

    return title, content.strip(), date.strip()

# Extract text directly from the PDF (if available)
pdf_text = extract_pdf_text(pdf_filename)

# If text is found, extract title, content, and date
if pdf_text.strip():
    title, content, date = extract_title_content_date(pdf_text)
else:
    print("No text found in the PDF, performing OCR...")

    # If no text was extracted, convert the first page to an image and run OCR
    images = convert_from_path(pdf_filename)
    if images:
        first_page_image = images[0]
        
        # Save the image if needed (Optional)
        first_page_image.save("first_page_image.png", "PNG")
        try:
            # Perform OCR on the first page (index 0)
            ocr_text = pytesseract.image_to_string(first_page_image)
        except Exception as e:
            print(f"Error performing OCR: {e}")
            ocr_text = ""

        print("OCR Extracted Text:")
        print(ocr_text)
        
        # Extract title, content, and date from OCR text
        title, content, date = extract_title_content_date(ocr_text)

# If no content was extracted, close the browser and exit
if not title and not content and not date:
    print("No valid data extracted, closing browser.")
    driver.quit()
    exit()

# Save data to a CSV file
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Prepare data to be written into CSV
data = [
    {
        "id": 1,  # Replace with an appropriate ID or unique identifier
        "title": title,
        "subtitle": generate_subtitle(title),  # You can extract or add a subtitle if needed
        "slug": title.lower().replace(" ","-"),  # Generate or add a slug
        "lead": "",  # Add the lead if available
        "content":generate_news(content),
        "image": "information/"+img_name,
        "type": "",  # Add type if applicable
        "custom_field": "",  # Add custom fields if needed
        "parent_id": "",  # Add parent ID if applicable
        "created_at": date,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "added_timestamp": date,
        "language": "en",  # Replace with actual language if necessary
        "seo_title": "",  # Add SEO title if available
        "seo_content": "",  # Add SEO content if available
        "seo_title_desc": "",  # Add SEO title description
        "seo_content_desc": "",  # Add SEO content description
        "category_id": "100"  # Add the category ID if applicable
    }
]

# Writing to the CSV file
csv_filename = "extracted_data.csv"
check_and_remove_file(csv_filename)
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    for row in data:
        writer.writerow(row)

print(f"Data saved to {csv_filename}")

# Close the browser when done
driver.quit()



if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data(csv_filename, "informations")
    append_unique_records(csv_filename,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")
