import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from insert_csv_into_sql_db import check_and_remove_file, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format,download_image
from selenium.webdriver.chrome.options import Options

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


# Navigate to the page
driver.get("https://sagehospitalitygroup.com/our-stories/")  # Replace with the actual URL

# Execute JavaScript to get the most recent href (the last item in the list)
js_code = """
const links = document.querySelectorAll('.filters__results__list .card__link');
if (links.length > 0) {
    const mostRecentLink = links[links.length - 1].href;  // Get the href of the last link
    return mostRecentLink;
} else {
    return null;  // No links found
}
"""

# Execute JavaScript to get the most recent href
most_recent_href = driver.execute_script(js_code)

# Check if a href is found and open it in the browser
if most_recent_href:

    driver.get(most_recent_href)

    # Execute JavaScript to get the image URL from the <source> tag inside <picture>
    js_code = """
    const pictureElement = document.querySelector('.picture--default source');
    if (pictureElement) {
        return pictureElement.srcset;  // Get the URL from the srcset attribute
    } else {
        return null;  // No source found
    }
    """

    # Execute JavaScript to get the image URL
    image_url = driver.execute_script(js_code)

    print(image_url)
    img_name=generate_random_filename()
    download_image(image_url,img_name)
    upload_photo_to_ftp(img_name,"/public_html/storage/information/")

    # Execute JavaScript to get the title from the <h1> tag
    js_code = """
    const headingElement = document.querySelector('.heading-text__heading span');
    if (headingElement) {
        return headingElement.innerText;  // Get the text content of the <span> inside <h1>
    } else {
        return null;  // No heading found
    }
    """

    # Execute JavaScript to get the heading text
    title = driver.execute_script(js_code)

    print("title", title)

    # JavaScript code to extract all <p> tags text content
    js_code = """
    let pTags = document.querySelectorAll('p');
    let textContent = '';
    pTags.forEach(tag => {
        textContent += tag.innerText + ' ';
    });
    return textContent.trim();
    """

    # Execute the JavaScript to get the text content from all <p> tags
    all_text = driver.execute_script(js_code)

    print(all_text)

    # Prepare the data to be written into the CSV file
    row_data = [
        "1",  # id
        title,  # title
        "",  # subtitle (if applicable, you can fill this later)
        "",  # slug (if applicable, you can fill this later)
        "",  # lead (if applicable, you can fill this later)
        all_text,  # content (all <p> text)
        image_url,  # image URL
        "",  # type (if applicable)
        "",  # custom_field (if applicable)
        "",  # parent_id (if applicable)
        "",  # created_at (if applicable)
        "",  # updated_at (if applicable)
        "",  # added_timestamp (if applicable)
        "",  # language (if applicable)
        "",  # seo_title (if applicable)
        "",  # seo_content (if applicable)
        "",  # seo_title_desc (if applicable)
        "",  # seo_content_desc (if applicable)
        100,  # category_id (if applicable)
    ]

    # Write to CSV file
    with open("scraped_data.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write headers only once
        if file.tell() == 0:
            writer.writerow(headers)
        writer.writerow(row_data)

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
