import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
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


# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Initialize a list to store the data
data = []


# Navigate to the page containing the news items
driver.get("https://virginhotels.com/the-virgin-voice/")  # Replace with the actual URL

# Wait for the news items to load
WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, '.news__item'))
)

# JavaScript to get the href of the first link inside .news__item
js_code = """
const linkElement = document.querySelector('.news__item .news__content a');
if (linkElement) {
    return linkElement.href; // Get the href attribute of the first link
} else {
    return null; // Return null if no link is found
}
"""

# Execute the JavaScript code
href = driver.execute_script(js_code)

if href:
    print(f"Opening the link: {href}")
    driver.maximize_window()
    driver.get(href)  # Open the extracted URL in the browser

    # Wait for the page to load completely (adjust the condition as needed)
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'body'))  # Adjust CSS selector as necessary
    )

    # JavaScript to extract the title from the <h1> tag
    js_code = """
    const titleElement = document.querySelector('.intro__title h1');
    if (titleElement) {
        return titleElement.innerText; // Get the text content of the <h1> tag
    } else {
        return null; // Return null if no <h1> is found
    }
    """
    title = driver.execute_script(js_code)

    title = generate_title(title)

    # JavaScript to extract all <p> tag contents
    js_code = """
    let pTags = document.querySelectorAll('p'); // Select all <p> tags
    let pContent = []; // Initialize an array to store content

    // Loop through each <p> tag and extract the text content
    pTags.forEach(p => {
        pContent.push(p.innerText.trim());
    });

    // Join all contents into a single string
    return pContent.join('\\n');
    """
    p_tags_content = driver.execute_script(js_code)

    p_tags_content = generate_news(p_tags_content)

    # JavaScript to extract the src of the first <img> tag
    js_code = """
    let imgElement = document.querySelector('img'); // Select the first <img> tag
    if (imgElement) {
        return imgElement.src; // Return the src attribute
    } else {
        return null; // Return null if no <img> tag is found
    }
    """

    # JavaScript to extract the date from the <strong> tag within the <p> element
    js_code = """
    const dateElement = document.querySelector('p');
    if (dateElement) {
        const strongText = dateElement.querySelector('strong') ? dateElement.querySelector('strong').innerText : null;
        return strongText; // Get the text content of the <strong> tag inside the <p>
    } else {
        return null; // Return null if the <p> tag or <strong> tag is not found
    }
    """

    # Execute the JavaScript code
    date_text = driver.execute_script(js_code)

    date =  date_format(date_text)

    img_name = generate_random_filename()
    image_url = driver.execute_script(js_code)

    download_image(image_url,img_name)

    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Add data to the list in the specified format
    data.append({
        "id": 1,  # Increment ID as needed
        "title": title,
        "subtitle": generate_subtitle(title),  # Not scraped in the logic provided
        "slug": title.lower().replace(" ","-"),  # Not scraped in the logic provided
        "lead": "",  # Not scraped in the logic provided
        "content": p_tags_content,
        "image": "information/"+img_name,
        "type": "news",  # Example type
        "custom_field": "",  # Not scraped
        "parent_id": "",  # Not scraped
        "created_at": date,  # Not scraped
        "updated_at": time.time(),  # Not scraped
        "added_timestamp": date,  # Current timestamp
        "language": "en",  # Example language
        "seo_title": "",  # Not scraped
        "seo_content": "",  # Not scraped
        "seo_title_desc": "",  # Not scraped
        "seo_content_desc": "",  # Not scraped
        "category_id": 100,  # Not scraped
    })
else:
    print("No link found.")

# Close the driver when done
driver.quit()

# Write the data to a CSV file
csv_file = "scraped_data.csv"

with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()  # Write the headers
    writer.writerows(data)  # Write the rows of data

print(f"Data saved to {csv_file}")




if date==date_format(datetime.now().today()):
    # Insert the CSV data into the database
    insert_csv_data(csv_file, "informations")
    append_unique_records(csv_file,"combined_news_data.csv")

else:
    print("--------WE DO NOT HAVE DATA FOR TODAY--------")
