import csv
from datetime import datetime
from selenium import webdriver
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# Setup Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)
driver = webdriver.Chrome(options=chrome_options)
# Set up Selenium WebDriver
options = Options()
options.headless = False  # Set to True for headless mode
driver = webdriver.Chrome(options=options)

# Navigate to the page
driver.get("https://www.shhotelsandresorts.com/newsroom/")  # Replace with your actual URL

# JavaScript to extract the most recent href and navigate to it
js_code = """
// Locate the most recent press release and extract its href
const mostRecentLink = document.querySelector(".views-row section a.link--arrow");
if (mostRecentLink) {
    const href = mostRecentLink.href;
    window.location.href = href; // Open the link in the same tab
    return href; // Return the URL for verification
} else {
    return "No link found";
}
"""

# Execute the JavaScript code in Selenium
most_recent_href = driver.execute_script(js_code)

# Print the most recent href for debugging
print(f"Navigated to: {most_recent_href}")

# Add an implicit wait to allow the new page to load
driver.implicitly_wait(10)

# JavaScript to extract title, image URL, and date
js_code = """
// Extract the title
const titleElement = document.querySelector(".pattern-slide h1");
const title = titleElement ? titleElement.textContent.trim() : "Title not found";

// Extract the image URL
const imageElement = document.querySelector(".pattern-slide img");
const imageUrl = imageElement ? imageElement.src : "Image not found";

// Extract the date
const dateElement = document.querySelector(".pattern-slide .hero-bottom");
const dateMatch = dateElement ? dateElement.textContent.match(/\\| (.+)$/) : null;
const date = dateMatch ? dateMatch[1].trim() : "Date not found";

// Return the extracted data
return {
    title: title,
    image: imageUrl,
    date: date
};
"""

# Execute the JavaScript and get the extracted data
data = driver.execute_script(js_code)

# Print the extracted data
print("Title:", data['title'])
print("Image URL:", data['image'])
print("Date:", data['date'])

# JavaScript to extract the content
js_code = """
// Locate the content within the specified div
const contentElement = document.querySelector(".clearfix.text-formatted.field--name-field-body");
const content = contentElement ? contentElement.textContent.trim() : "Content not found";

// Return the extracted content
return content;
"""

# Execute the JavaScript code
content = driver.execute_script(js_code)

# Print the extracted content
print("Extracted Content:", content)
title = generate_title(data['title'])
date =  date_format(data['date'])
# Generate a slug from the title
slug = data['title'].lower().replace(" ", "-")
img_name =  generate_random_filename()
download_image(data['image'],img_name)
upload_photo_to_ftp(img_name,"/public_html/storage/information/")

# Prepare the row for the CSV file
row = {
    "id": 1,
    "title": title,
    "subtitle": generate_subtitle(title),
    "slug": slug,
    "lead": "",
    "content": generate_news(content),
    "image": "information/"+img_name,
    "type": "press_release",
    "custom_field": "",
    "parent_id": "",
    "created_at": date,
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "added_timestamp": date,
    "language": "en",
    "seo_title": '',
    "seo_content": '',  # First 150 characters of content
    "seo_title_desc": '',
    "seo_content_desc": '',  # First 150 characters of content
    "category_id": 100
}

# Save the data to a CSV file
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

csv_file = "press_releases.csv"
with open(csv_file, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    writer.writerow(row)

print("Data saved to press_releases.csv")

# Close the driver when done
driver.quit()

if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data(csv_file, "informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")