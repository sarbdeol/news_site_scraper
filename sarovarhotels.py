import pytesseract
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import io
from pdf2image import convert_from_path
import PyPDF2  # For PDF text extraction
import re
import os


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



# Update this line with the path to your Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Akshay\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"  # For Windows
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # For Windows


# Open the page URL containing the PDF link
driver.get("https://www.sarovarhotels.com/newsroom/newsroom.html")  # Replace with actual page URL

# JavaScript code to click the link and open the PDF in a new tab
js_code = """
var pdfLink = document.querySelector('a.page_link');
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

# Wait for the new tab to open (adjust as needed)
time.sleep(5)

# Download the PDF (fetch the PDF content)
response = requests.get(pdf_url)
pdf_filename = "downloaded_pdf.pdf"
with open(pdf_filename, 'wb') as file:
    file.write(response.content)

# Try to extract text from the PDF directly (if it contains text)
def extract_pdf_text(pdf_filename):
    with open(pdf_filename, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()  # Extract text from each page
        return text

# Function to extract title, content, and date from the PDF text
def extract_title_content_date(pdf_text):
    # Split the text into lines
    lines = pdf_text.split('\n')

    # Try to identify the first heading (usually the first non-empty line)
    title = ""
    content = ""
    date = ""

    for line in lines:
        line = line.strip()
        if title == "" and line:
            title = line  # First non-empty line is considered as title
        else:
            content += line + " "

        # Check for date format (This regex will match many common date formats)
        if re.match(r"\b(?:\d{1,2}[\/\-\.\s]?[A-Za-z]+[\s]?\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})\b", line):
            date = line

    return title, content.strip(), date.strip()

# Extract text directly from the PDF (if available)
pdf_text = extract_pdf_text(pdf_filename)

# If text is found, extract title, content, and date
if pdf_text.strip():
    title, content, date = extract_title_content_date(pdf_text)
    print("Title Extracted from PDF:")
    print(title)
    print("\nNews Content Extracted from PDF:")
    print(content)
    print("\nDate Extracted from PDF:")
    print(date)
else:
    # Convert the first page of the PDF to an image using pdf2image
    images = convert_from_path(pdf_filename)

    # Perform OCR on the first page (index 0) image if no text found
    if images:
        first_page_image = images[0]  # Get the first page as an image

        # Save the image if needed
        output_image_path = "first_page_image.png"
        first_page_image.save(output_image_path)
        print(f"Image saved as {output_image_path}")

        # Perform OCR on the image
        ocr_text = pytesseract.image_to_string(first_page_image)

        # Extract title, content, and date from OCR text
        title, content, date = extract_title_content_date(ocr_text)

        # Print the OCR-extracted title, content, and date
        print("OCR Extracted Title:")
        print(title)
        print("\nOCR Extracted News Content:")
        print(content)
        print("\nOCR Extracted Date:")
        print(date)
    else:
        print("No images found in the PDF.")

# Close the browser when done
driver.quit()
