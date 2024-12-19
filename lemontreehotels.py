# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import pandas as pd
# import os
# import requests
# from insert_csv_into_sql_db import insert_into_db, check_and_remove_file, generate_news
# import shutil

# # Set up Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
# )

# # Initialize WebDriver
# driver = webdriver.Chrome(options=chrome_options)

# # Load the target URL
# url = "https://www.lemontreehotels.com/media"  # Replace with the actual URL containing the HTML structure
# driver.get(url)

# # JavaScript code to extract data
# js_code = """
# const articles = document.querySelectorAll('.card-body ul li a');
# const data = Array.from(articles).map((article, index) => {
#     const title = article.innerText.split('\\n')[0].trim(); // Get the title
#     const date = article.querySelector('.media-date')?.innerText || ''; // Get the date
#     const url = article.href; // Get the link URL
#     return { id: index + 1, title, date, url };
# });
# return data;
# """

# # Execute JavaScript and get the results
# news_data = driver.execute_script(js_code)

# # Close the browser
# driver.quit()

# # Create a folder to store images
# image_folder = "lemontree_news_data_images"
# if os.path.exists(image_folder):
#     print(f"Folder '{image_folder}' exists. Deleting and creating a new one...")
#     shutil.rmtree(image_folder)  # Remove the folder and its contents
# os.makedirs(image_folder, exist_ok=True)  # Create a new folder


# # Format the data for the CSV and download images (if necessary)
# formatted_data = []
# for item in news_data:
#     title = generate_news(item['title'])
#     date = item['date']
#     url = item['url']
    
#     # Initialize image_url as None (no images to download in this case)
#     image_url = None  # Modify this to extract actual image URLs if available

#     image_filename = None
#     # If an image URL is available, download and save the image
#     if image_url:
#         try:
#             # Create sanitized filename
#             image_filename = os.path.join(image_folder, f"{title.replace(' ', '_').replace('/', '_')}.jpg")
#             img_data = requests.get(image_url, timeout=10)
#             img_data.raise_for_status()  # Ensure valid HTTP response

#             # Save the image
#             with open(image_filename, 'wb') as img_file:
#                 img_file.write(img_data.content)
#             print(f"Image saved as: {image_filename}")
#         except requests.exceptions.RequestException as e:
#             print(f"Failed to download image from {image_url}. Error: {e}")
#             image_filename = None

#     # Add data to formatted_data
#     formatted_data.append([
#         item['id'],  # id
#         title,  # title
#         title.replace(" ", "-").lower(),  # slug
#         "",  # lead
#         url,  # content (using URL as content)
#         image_filename or "",  # image (empty if no image was saved)
#         "news",  # type
#         "",  # custom_field
#         "",  # parent_id
#         date,  # created_at
#         date,  # updated_at
#         "en",  # language
#         title,  # seo_title
#         "",  # seo_content
#         title,  # seo_title_desc
#         "",  # seo_content_desc
#         "1"  # category_id
#     ])

# # Define headers
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type",
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# # Convert to DataFrame
# df = pd.DataFrame(formatted_data, columns=headers)

# # Save to a CSV file
# output_file = "lemontree_news_data.csv"
# check_and_remove_file(output_file)
# df.to_csv(output_file, index=False)

# print(f"Data saved to {output_file}")

# # Optional: Insert data into the database
# # insert_into_db(output_file)






import os
import requests
import pdfplumber
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import shutil
import datetime
import re

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Set the path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Akshay\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Open the webpage containing the links
driver.get("https://www.lemontreehotels.com/media")  # Replace with actual URL

# Use JavaScript to find the most recent href
script = """
// Get all anchor tags
let links = Array.from(document.querySelectorAll('a[href]'));

// Extract links and their associated dates
let linkData = links.map(link => ({
    href: link.href,
    dateText: link.innerText.match(/\\d{1,2}\\s\\w+\\s\\d{4}/)?.[0] // Extract date using regex
}));

// Sort links by date (descending)
linkData.sort((a, b) => {
    let dateA = new Date(a.dateText);
    let dateB = new Date(b.dateText);
    return dateB - dateA;
});

// Return the most recent href
return linkData[0]?.href;
""";

# Execute the script to get the most recent href
most_recent_href = driver.execute_script(script)

if most_recent_href:
    print(f"Most recent PDF link: {most_recent_href}")
    
    # Download the PDF using its URL
    response = requests.get(most_recent_href, verify=False)
    if response.status_code == 200:
        # Save the PDF locally
        pdf_path = "downloaded_pdf.pdf"
        with open(pdf_path, "wb") as file:
            file.write(response.content)
        print(f"PDF downloaded successfully: {pdf_path}")
        
        # Initialize storage for CSV data
        data_rows = []
        image_folder = "pdf_images"
        os.makedirs(image_folder, exist_ok=True)

        # Extract data from the PDF
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # Extract text
                text = page.extract_text() or ""
                
                # Save OCR output if text is not selectable
                page_image_path = f"{image_folder}/page_{page_number}.png"
                page_image = page.to_image(resolution=300)
                page_image.save(page_image_path)

                ocr_text = pytesseract.image_to_string(Image.open(page_image_path))
                full_text = text if text.strip() else ocr_text

                # Use the first line of text as the title
                title = full_text.split("\n")[0].strip() if full_text else f"Page {page_number}"

                # Extract the published date from the text (if available)
                # Assuming the date is in a format like "31 Oct 2024"
                date_match = re.search(r"\d{1,2}\s\w+\s\d{4}", full_text)
                published_date = date_match.group(0) if date_match else datetime.datetime.now().strftime("%Y-%m-%d")

                # Save data for each page
                data_rows.append({
                    "id": page_number,
                    "title": title,
                    "subtitle": "",
                    "slug": title.lower().replace(" ", "-"),
                    "lead": full_text[:100],  # First 100 characters as lead
                    "content": full_text,
                    "image": page_image_path,
                    "type": "pdf_page",
                    "custom_field": "",
                    "parent_id": "",
                    "created_at": published_date,  # Use the extracted published date as created_at
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "added_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "language": "en",
                    "seo_title": title,
                    "seo_content": "",
                    "seo_title_desc": title,
                    "seo_content_desc": "",
                    "category_id": "1",
                })

        # Clean up the downloaded file
        os.remove(pdf_path)
    else:
        print("Failed to download the PDF.")
else:
    print("No valid PDF links found!")

# Close the browser
driver.quit()

# Define headers for the CSV
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Save data to CSV
output_file = "lemontree_pdf_data.csv"
df = pd.DataFrame(data_rows, columns=headers)
df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")

# Optional: Cleanup the image folder
# shutil.rmtree(image_folder)
