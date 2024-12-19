import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title,check_and_remove_file
from insert_csv_into_sql_db import generate_random_filename,date_format,download_image,insert_csv_data,append_unique_records
from upload_and_reference import upload_photo_to_ftp

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Set up Chrome options for headless mode (optional)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Uncomment this line if you want headless mode

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open the target URL
driver.get("https://www.absolutehotelservices.net/news-1")  # Replace with the actual URL where the HTML content is located

# JavaScript code to extract the href from the "Read More" link
js_code = """
let linkElement = document.querySelector('.comp-l74oae14 a');  // Select the <a> tag inside the comp-l74oae14 div
let href = linkElement ? linkElement.href : null;  // Get the href attribute

return href;  // Return the extracted href
"""
href = driver.execute_script(js_code)  # Execute the JavaScript code and get the result (href)
print(f"Extracted Href: {href}")

# Navigate to the extracted link if available
if href:
    driver.get(href)

    # Extract the title
    js_code = """
    let titleElement = document.querySelector('.wixui-rich-text__text');  // Select the <span> tag with the class wixui-rich-text__text
    let title = titleElement ? titleElement.innerText : null;  // Get the text content (title)
    return title;
    """
    title = generate_title(driver.execute_script(js_code))
    print(f"Extracted Title: {title}")

    # Extract the image URL
    js_code = """
    let imageElement = document.querySelector('img');  // Select the first <img> element
    let imageUrl = imageElement ? imageElement.src : null;  // Get the src of the image
    return imageUrl;
    """
    image_url = driver.execute_script(js_code)
    print(f"Extracted Image URL: {image_url}")

    img_name = generate_random_filename()

    download_image(image_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Extract the date
    js_code = """
    let dateElement = document.querySelector('#comp-l74oadod span');  // Select the <span> inside the #comp-l74oadod div
    let date = dateElement ? dateElement.innerText : null;  // Get the text content (date)
    return date;
    """
    date = date_format(driver.execute_script(js_code))
    print(f"Extracted Date: {date}")

    # Extract all <p> tags as text
    js_code = """
    let paragraphs = document.querySelectorAll('p');  // Select all <p> elements
    let allText = Array.from(paragraphs).map(p => p.innerText.trim()).join(" ");  // Extract text, trim it, and join with a space
    return allText;
    """
    all_paragraphs_text = generate_news(driver.execute_script(js_code))
    print(f"Extracted Text from all <p> tags: {all_paragraphs_text}")

    # Prepare the data to be saved in CSV
    data = [
        {
            "id": 1,  # You can dynamically generate or assign this value
            "title": title,
            "subtitle": generate_subtitle(title),  # No subtitle provided in this example
            "slug": title.lower().replace(" ", "-") if title else "",  # Convert title to a slug
            "lead": "",  # First 100 characters as lead
            "content": all_paragraphs_text,
            "image": "information/"+img_name,
            "type": "press_release",  # Assuming type is "press_release"
            "custom_field": "",
            "parent_id": "",
            "created_at": date,  # Use the extracted date as created_at
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "added_timestamp": date,
            "language": "en",
            "seo_title": "",
            "seo_content": "",
            "seo_title_desc": "",
            "seo_content_desc": "",
            "category_id": "100"  # Assuming category_id is "1"
        }
    ]

    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)

    # Save data to CSV
    output_file = "press_release_data.csv"
    df.to_csv(output_file, index=False)

    print(f"Data saved to {output_file}")

# Close the browser
driver.quit()

if date == date_format(time.strftime("%Y-%m-%d %H:%M:%S")):
    append_unique_records(output_file,"")
    insert_csv_data(output_file,"informations")
else:
    print("WE DO NOT HAVE DATA FOR TODAY")