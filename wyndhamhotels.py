import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
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
options.headless = False  # Set to False to open the browser window
driver = webdriver.Chrome(options=options)

# Navigate to the page
driver.get("https://corporate.wyndhamhotels.com/news-releases")  # Replace with the actual URL of the page

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# JavaScript code to get the date from the first <span class="archive-entries__entry__date">
js_code = """
const dateElement = document.querySelector('span.archive-entries__entry__date');
if (dateElement) {
    return dateElement.innerText;  // Get the text content of the date element
} else {
    return null;  // No date element found
}
"""

# Execute JavaScript to get the date
date_text = driver.execute_script(js_code)

print(date_text)

date = date_format(date_text)

# JavaScript code to get the most recent href (first entry)
js_code = """
const mostRecentLink = document.querySelector('ul.archive-entries.press-releases li.archive-entries__entry a');
if (mostRecentLink) {
    return mostRecentLink.href;  // Get the href of the most recent link
} else {
    return null;  // No link found
}
"""

# Execute JavaScript to get the most recent href
most_recent_href = driver.execute_script(js_code)

if most_recent_href:
    print(f"Most recent href: {most_recent_href}")
    driver.get(most_recent_href)  # Open the most recent link in the browser

    # JavaScript code to get the title from <h1 class="page-title">
    js_code = """
    const titleElement = document.querySelector('h1.page-title');
    if (titleElement) {
        return titleElement.innerText;  // Get the text content of the title element
    } else {
        return null;  // No title element found
    }
    """

    # Execute JavaScript to get the title
    title_text = driver.execute_script(js_code)

    title = generate_title(title_text)

    if title_text:
        print(f"Title: {title_text}")
    else:
        print("Title not found.")

    # JavaScript code to get the image URL from the <img class="featured-image">
    js_code = """
    const imgElement = document.querySelector('figure.featured-media img.featured-image');
    if (imgElement) {
        return imgElement.src;  // Get the src attribute of the featured image
    } else {
        return null;  // No image found
    }
    """

    # Execute JavaScript to get the image URL
    image_url = driver.execute_script(js_code)

    print(image_url)

    img_name = generate_random_filename()

    download_image(image_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # JavaScript code to get all <p> tags and store their content as a string
    js_code = """
    let pTags = document.querySelectorAll('p');  // Select all <p> tags
    let textContent = '';  // Initialize an empty string to store the text content
    pTags.forEach(p => {
        textContent += p.innerText + ' ';  // Add the text of each <p> tag to the string
    });
    return textContent.trim();  // Return the concatenated string, trimmed of extra spaces
    """

    # Execute JavaScript to get the text from all <p> tags
    p_tags_text = driver.execute_script(js_code)

    print(p_tags_text)

    p_tags_text = generate_news(p_tags_text)

    # Prepare the data to be written into CSV
    data = {
        "id": "1",  # Example, should be unique for each entry
        "title": title,  # Title from <h1>
        "subtitle": generate_subtitle(title),  # Example subtitle, can be filled if available
        "slug": title.lower().replace(" ","-"),  # Example slug, should be scraped or generated if needed
        "lead": "Wyndham Hotels & Resorts launches a holiday campaign.",  # Example lead text
        "content": p_tags_text,  # Content from <p> tags
        "image": "information/"+img_name,  # Image URL
        "type": "Press Release",  # Example type
        "custom_field": "",  # Example custom field
        "parent_id": "0",  # Example parent ID
        "created_at": date,  # Example created_at timestamp
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Example updated_at timestamp
        "added_timestamp": date,  # Example added_timestamp
        "language": "en",  # Example language
        "seo_title": '',  # SEO title (can be the same as the main title)
        "seo_content": '',  # SEO content (can be the same as the main content)
        "seo_title_desc": "",  # Example SEO title description
        "seo_content_desc": "",  # Example SEO content description
        "category_id": "100"  # Example category ID
    }

    # Specify the CSV file name
    csv_file = "output_data.csv"

    # Write to CSV
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write header only if the file is empty
        if file.tell() == 0:
            writer.writeheader()

        # Write the data row
        writer.writerow(data)

    print(f"Data has been written to {csv_file}")

else:
    print("No link found.")

# Optional: Close the driver after some time or when you're done
driver.quit()


if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data(csv_file, "informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")
