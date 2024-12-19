from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

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


driver.maximize_window()

# Navigate to the page
driver.get("https://newsroom.sonesta.com/news/")  # Replace with the actual URL

# JavaScript code to get the href of the most recent news item
js_code = """
const mostRecentLink = document.querySelector('.latest-news-list ul li:first-child p a');
if (mostRecentLink) {
    return mostRecentLink.href; // Return the href of the most recent news item
} else {
    return 'No recent news found'; // If no link is found
}
"""

# Execute the JavaScript to get the most recent href
recent_href = driver.execute_script(js_code)

if recent_href and recent_href != 'No recent news found':
    print(f"Opening the most recent news article: {recent_href}")
    driver.get(recent_href)  # Open the most recent news article in the browser

    # JavaScript code to extract date, image, title, and <p> tag content
    js_code = """
    const postInfo = {};

    const title = document.querySelector('.single-post-content h1');
    const date = document.querySelector('.single-post-info p');
    const image = document.querySelector('.single-post-thumbnail img');
    const firstParagraph = document.querySelector('.rtf p');

    postInfo.title = title ? title.textContent : 'No title found';
    postInfo.date = date ? date.textContent : 'No date found';
    postInfo.image = image ? image.src : 'No image found';
    postInfo.firstParagraph = firstParagraph ? firstParagraph.textContent : 'No content found';

    return postInfo;
    """

    # Execute the JavaScript to get the required information
    post_info = driver.execute_script(js_code)

    # Format the data according to the headers
    headers = [
        "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
        "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
        "language", "seo_title", "seo_content", "seo_title_desc", 
        "seo_content_desc", "category_id"
    ]

    title = generate_title(post_info["title"])

    img_name=generate_random_filename()

    download_image(post_info["image"],img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    date =  date_format(post_info["date"])
    # Data dictionary
    data = {
        "id": None,  # Assuming you do not have an id here, set as None or a generated ID
        "title": title,
        "subtitle": generate_subtitle(title),  # Assuming you don't have a subtitle
        "slug": title.lower().replace(" ","-"),  # Assuming you do not have a slug
        "lead": "",
        "content": generate_news(post_info["firstParagraph"]),  # You can extract the full content if needed
        "image": "information/"+img_name,
        "type": None,  # You can define the type if necessary
        "custom_field": None,  # If you have custom fields, extract them
        "parent_id": None,  # If there's a parent ID, extract it
        "created_at": date,  # Date can be used as the created_at
        "updated_at": time.time(),  # If you have an updated_at field, extract it
        "added_timestamp":date ,  # Use current timestamp
        "language": None,  # If you know the language, add it
        "seo_title": None,  # Extract SEO title if available
        "seo_content": None,  # Extract SEO content if available
        "seo_title_desc": None,  # SEO title description
        "seo_content_desc": None,  # SEO content description
        "category_id": 100  # Category ID can be added here if needed
    }

    # Save the data into a CSV file
    with open("scraped_data.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # If the file is empty, write the header first
        if file.tell() == 0:
            writer.writeheader()
        
        # Write the data
        writer.writerow(data)

    print("Data saved to 'scraped_data.csv'.")
else:
    print("No recent news found.")

# Close the driver when done
driver.quit()


if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data("scraped_data.csv", "informations")
    append_unique_records("scraped_data.csv","combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")
