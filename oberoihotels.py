
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from insert_csv_into_sql_db import generate_news, generate_subtitle, generate_title
from insert_csv_into_sql_db import insert_csv_data, generate_random_filename
from insert_csv_into_sql_db import check_and_remove_file, date_format, download_image,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from datetime import datetime
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disabling sandbox for headless mode
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)  # Set user-agent to mimic a real browser

# Setup Selenium WebDriver
driver = webdriver.Chrome(options=chrome_options)
# Initialize WebDriver
# driver = webdriver.Chrome()
url = "https://www.oberoihotels.com/media-press-releases/"  # Replace with the actual URL
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)


# JavaScript code to get the banner image URL
js_code = """
    let imgElement = document.querySelector('img[alt="Emagzine banner"]');
    return imgElement ? imgElement.getAttribute('src') : "Image not found";
"""
# Execute JavaScript to get the banner image URL

image_url = driver.execute_script(js_code)
img_name = generate_random_filename()

# JavaScript code to extract the link, title, date, content, and image URL
js_code = """
let linkElement = document.querySelector('div.article-item h3 a');
let href = linkElement ? linkElement.getAttribute('href') : null;

let titleElement = document.querySelector('h1') || document.querySelector('h3');
let title = titleElement ? titleElement.textContent.trim() : "Title not found";

let contentElement = document.querySelector('p');
let content = contentElement ? contentElement.textContent.trim() : "Content not found";

let dateElement = document.querySelector('time');
let date = dateElement ? dateElement.textContent.trim() : "Date not found";

let imageElement = document.querySelector('img');
let imageUrl = imageElement ? imageElement.getAttribute('src') : "Image not found";

return {
    href: href,
    title: title,
    date: date,
    content: content,
    imageUrl: imageUrl
};
"""

# Execute the JavaScript to get the data
result = driver.execute_script(js_code)

# If a href link was found, navigate to it and extract the required data
if result['href']:
    # Open the URL in the browser
    href = "https://www.oberoihotels.com" + result['href']
    driver.get(href)

    # Wait for the page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    # JavaScript code to extract the title from the <h1> with class 'h2'
    js_code = """
        let titleElement = document.querySelector('h1.h2');
        return titleElement ? titleElement.textContent.trim() : "Title not found";
    """

    # Execute JavaScript to get the title
    title = driver.execute_script(js_code)

    # JavaScript code to extract the date from the <p> tag containing the <strong> tag
    js_code = """
        let dateElement = document.querySelector('p strong');
        let dateText = dateElement ? dateElement.textContent.trim() : "Date not found";
        return dateText;
    """

    # Execute JavaScript to get the date
    date = driver.execute_script(js_code)

    # JavaScript code to get all <p> tag contents as a single string
    js_code = """
        let paragraphs = Array.from(document.querySelectorAll('.press-room-colms p'));
        return paragraphs.map(p => p.textContent.trim()).join(' ');
    """

    # Execute JavaScript to get the paragraphs content
    content = driver.execute_script(js_code)

    # # JavaScript code to get the banner image URL
    # js_code = """
    #     let imgElement = document.querySelector('img[alt="Emagzine banner"]');
    #     return imgElement ? imgElement.getAttribute('src') : "Image not found";
    # """
    # # Execute JavaScript to get the banner image URL

    # image_url = driver.execute_script(js_code)
    img_name = generate_random_filename()

    download_image("https://www.oberoihotels.com/"+image_url, img_name)

    upload_photo_to_ftp(img_name, "/public_html/storage/information/")

    title = generate_title(title)
    date  = date_format(date)

    # Prepare data to save in CSV
    data = {
        "id": "1",  # For simplicity, id is hardcoded as "1". You can modify this for unique ids.
        "title": title,
        "subtitle": generate_subtitle(title),  # You can add a subtitle extraction if needed.
        "slug": title.replace(" ", "-").lower(),  # Slug can be extracted or generated if needed.
        "lead": "",  # Lead information can be extracted from another source.
        "content": generate_news(content),
        "image": "information/" + img_name,
        "type": "",  # Add type if relevant.
        "custom_field": "",  # Add any custom fields if relevant.
        "parent_id": "",  # Parent ID can be added if relevant.
        "created_at":date ,
        "updated_at": datetime.now().today(),  # Set if applicable.
        "added_timestamp": date,  # You can add the current timestamp if needed.
        "language": "en",  # Assuming English language for simplicity.
        "seo_title": "",  # SEO title if relevant.
        "seo_content": "",  # SEO content if relevant.
        "seo_title_desc": "",  # SEO title description if relevant.
        "seo_content_desc": "",  # SEO content description if relevant.
        "category_id": 101  # Add category if relevant.
    }

    check_and_remove_file("news_data.csv")
    # Define CSV headers
    headers = [
        "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
        "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
        "language", "seo_title", "seo_content", "seo_title_desc", 
        "seo_content_desc", "category_id"
    ]

    # Write headers to CSV file if it does not exist
    file_exists = False
    try:
        with open("news_data.csv", mode="r", newline='', encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        pass
    
    with open("news_data.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists:
            writer.writeheader()  # Write the header if the file doesn't exist
        writer.writerow(data)

    print("Data saved to CSV successfully.")
else:
    print("No recent news found.")

# Quit the driver
driver.quit()


if date == date_format(datetime.now().today()):
    insert_csv_data("news_data.csv","informations")
    append_unique_records("news_data.csv","combined_news_data.csv")
else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")