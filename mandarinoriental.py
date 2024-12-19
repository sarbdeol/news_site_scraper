import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image


# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Set up Selenium WebDriver
options = Options()
options.headless = False  # Set to False to open the browser window
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)
driver = webdriver.Chrome(options=options)

# Navigate to the page
driver.get("https://press.mandarinoriental.com/")  # Replace with the actual URL

# JavaScript code to get the most recent href
js_code = """
const mostRecentLink = document.querySelector('.swiper-slide-active a');
if (mostRecentLink) {
    return mostRecentLink.href;  // Get the href of the most recent link
} else {
    return null;  // No link found
}
"""

# Execute JavaScript to get the most recent href
most_recent_href = driver.execute_script(js_code)

# Check if a href is found and open it in the browser
if most_recent_href:
    driver.get(most_recent_href)

    # JavaScript code to get the date
    js_code = """
    const dateElement = document.querySelector('#single-pr__head__infos .date');
    if (dateElement) {
        return dateElement.innerText;  // Get the text content of the date element
    } else {
        return null;  // No date found
    }
    """

    # Execute JavaScript to get the date
    date = driver.execute_script(js_code)

    # JavaScript code to get the title from <h1>
    js_code = """
    const titleElement = document.querySelector('h1');
    if (titleElement) {
        return titleElement.innerText.trim();  // Get the text content of the <h1> tag
    } else {
        return null;  // No title found
    }
    """

    # Execute JavaScript to get the title
    title = driver.execute_script(js_code)

    # JavaScript code to get the image URL
    js_code = """
    const imgElement = document.querySelector('#single-pr__banner_wrapper img');
    if (imgElement) {
        return imgElement.src;  // Get the URL from the src attribute
    } else {
        return null;  // No image found
    }
    """

    # Execute JavaScript to get the image URL
    img_url = driver.execute_script(js_code)

    img_name = generate_random_filename()
    download_image(img_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")


    # JavaScript code to get content of the first few <p> tags
    js_code = """
    let pTags = document.querySelectorAll('section#single-pr__content p');
    let textContent = '';
    for (let i = 0; i < 3; i++) {  // Change 3 to the number of <p> tags you want
        if (pTags[i]) {
            textContent += pTags[i].innerText + ' ';
        }
    }
    return textContent.trim();
    """

    # Execute JavaScript to get the <p> tags content
    p_tags_text = driver.execute_script(js_code)

    # Collecting data to save to CSV
    data = [
        "11123",  # Example ID
        title,  # Title
        "subtitle",  # Placeholder for subtitle
        "slug",  # Placeholder for slug
        date,  # Lead
        p_tags_text,  # Content (first few <p> tags)
        "information/"+img_name,  # Image URL
        "type",  # Placeholder for type
        "custom_field",  # Placeholder for custom field
        "parent_id",  # Placeholder for parent_id
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Created at (current timestamp)
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Updated at (current timestamp)
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Added timestamp (current timestamp)
        "en",  # Language (assumed English here)
        "seo_title",  # Placeholder for SEO title
        "seo_content",  # Placeholder for SEO content
        "seo_title_desc",  # Placeholder for SEO title description
        "seo_content_desc",  # Placeholder for SEO content description
        "category_id"  # Placeholder for category_id
    ]

    # Saving the data to CSV
    with open('scraped_data.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

    print(f"Data saved to CSV: {data}")

else:
    print("No links found.")

# Optional: Close the driver after some time or when you're done
driver.quit()


# if date_format(data.get("date", ""))==date_format(datetime.now().today()):
#     # Insert the CSV data into the database
#     insert_csv_data(csv_filename, "informations")
#     append_unique_records(csv_filename,"combined_news_data.csv")

# else:
#     print("--------WE DO NOT HAVE DATA FOR TODAY--------")