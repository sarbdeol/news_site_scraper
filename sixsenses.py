import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

# Navigate to the page
driver.get("https://www.sixsenses.com/en/corporate/media-center/press-releases/")  # Replace with your actual URL

# JavaScript to extract the date
js_code = """
const dateElement = document.querySelector("div p.category");
if (dateElement) {
    return dateElement.textContent.trim();
} else {
    return "Date not found";
}
"""
date = driver.execute_script(js_code)
print(date)

# JavaScript to find the most recent href and open it
js_code = """
const mostRecentDiv = document.querySelector("div[onclick]");
if (mostRecentDiv) {
    const onclickAttr = mostRecentDiv.getAttribute("onclick");
    const hrefMatch = onclickAttr.match(/window\\.open\\('(.*?)'/);
    if (hrefMatch && hrefMatch[1]) {
        const fullUrl = new URL(hrefMatch[1], window.location.origin).href;
        window.location.href = fullUrl; // Open the link in the same tab
    } else {
        return "No valid href found in onclick attribute";
    }
} else {
    return "No div with onclick attribute found";
}
"""
driver.execute_script(js_code)
driver.implicitly_wait(10)  # Add a delay if necessary to allow the page to load

# JavaScript to extract the title
js_code = """
const titleElement = document.querySelector("h1");
if (titleElement) {
    return titleElement.textContent.trim();
} else {
    return "Title not found";
}
"""
title = driver.execute_script(js_code)
print("Extracted Title:", title)

# JavaScript to extract the image URL
js_code = """
const imgElement = document.querySelector("img.lcp");
if (imgElement) {
    return imgElement.src;
} else {
    return "Image not found";
}
"""
image_url = driver.execute_script(js_code)
print(image_url)

# JavaScript to extract all <p> tag content
js_code = """
const paragraphs = Array.from(document.querySelectorAll("p")).map(p => p.textContent.trim());
return paragraphs;
"""
paragraphs = driver.execute_script(js_code)
print(paragraphs)

# Save data to a CSV file
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

title = generate_title(title)
date = date_format(title)
img_name = generate_random_filename()
download_image(image_url,img_name)
upload_photo_to_ftp(img_name,"/public_html/storage/information/")

data = {
    "id": 1,  # Unique ID (can be generated if needed)
    "title": title,
    "subtitle": generate_subtitle(title),  # No subtitle extraction logic, set to None or default
    "slug": title.lower().replace(" ","-"),  # Slug not extracted, can be generated from title if needed
    "lead": "",  # First paragraph as lead
    "content": generate_news(" ".join(paragraphs)),  # All paragraphs joined as content
    "image": "information/"+img_name,
    "type": None,  # Type not extracted, set to None or default
    "custom_field": None,  # No custom field logic, set to None
    "parent_id": None,  # Parent ID not extracted, set to None
    "created_at": date,  # Using the extracted date
    "updated_at": None,  # No updated_at logic, set to None
    "added_timestamp": None,  # Timestamp not extracted, set to None
    "language": "en",  # Defaulting to English
    "seo_title": "",  # Assuming title as SEO title
    "seo_content": " ",  # First two paragraphs for SEO content
    "seo_title_desc": None,  # Not extracted, set to None
    "seo_content_desc": None,  # Not extracted, set to None
    "category_id": 100  # No category logic, set to None
}

csv_file = "extracted_data.csv" 
check_and_remove_file(csv_file)
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()  # Write CSV header
    writer.writerow(data)  # Write the data row

print(f"Data saved to {csv_file}")

# Close the driver when done
driver.quit()


if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data(csv_file, "informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")
