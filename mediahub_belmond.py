import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import check_and_remove_file,download_image, append_unique_records,generate_news, generate_subtitle, generate_title, insert_csv_data, generate_random_filename
from upload_and_reference import upload_photo_to_ftp
from insert_csv_into_sql_db import date_format

# Setup Selenium WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
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

csv_file ="extracted_data.csv"
# Create or open a CSV file in write mode
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()  # Write headers to CSV file
    

    try:
        driver.maximize_window()
        # Load the page or HTML content (example: local file or URL)
        driver.get("https://mediahub.belmond.com/en/?lang=en")  # Replace with the path to your HTML file or URL

        # Locate the desired element using XPath
        link_element = driver.find_element(By.XPATH, "//div[@class='item-row homepage__latest--item']//a")

        # Extract the href attribute
        href = link_element.get_attribute("href")
        print(f"Extracted href: {href}")

        if href:
            driver.get(href)

            # Extract the title text
            subtitle_element = driver.find_element(By.XPATH, "//h2[@class='cp__subtitle']/p/strong")
            title_text = subtitle_element.text
            print(f"Extracted title: {title_text}")

            # Extract the date text
            date_element = driver.find_element(By.XPATH, "//div[@class='cp__date']")
            date_text = date_element.text
            print(f"Extracted date: {date_text}")

            # Extract all <p> tag texts
            p_elements = driver.find_elements(By.TAG_NAME, "p")
            p_texts = [p.text for p in p_elements]
            all_p_texts = " ".join(p_texts)
            print(f"All <p> tag texts: {all_p_texts}")

            # Extract the image URL from the banner element
            banner_element = driver.find_element(By.XPATH, "//div[@class='cp__banner']")
            style_attribute = banner_element.get_attribute("style")
            match = re.search(r'url\((.*?)\)', style_attribute)
            image_url = match.group(1).strip('"') if match else None
            print(f"Extracted image URL: {image_url}")

            img_name = generate_random_filename()

            download_image(image_url,img_name)

            upload_photo_to_ftp(img_name,"/public_html/storage/information/")

            # Prepare the data to save into the CSV file
            data = {
                "id": "",  # You can add logic to generate or extract an ID if needed
                "title": title_text,
                "subtitle": "",  # You can add logic to extract subtitle if needed
                "slug": "",  # You can extract the slug if it's available
                "lead": "",  # Extract lead text if needed
                "content": all_p_texts,
                "image": image_url,
                "type": "",  # Set the type if known
                "custom_field": "",  # Set any custom field if needed
                "parent_id": "",  # Extract parent ID if applicable
                "created_at": date_text,  # Use the date or created_at if available
                "updated_at": "",  # Extract the update date if needed
                "added_timestamp": "",  # Set the timestamp if applicable
                "language": "en",  # Assuming English language
                "seo_title": "",  # Extract SEO title if available
                "seo_content": "",  # Extract SEO content if available
                "seo_title_desc": "",  # Extract SEO title description if available
                "seo_content_desc": "",  # Extract SEO content description if available
                "category_id": "",  # Set the category ID if available
            }

            # Write data to CSV file
            writer.writerow(data)

    finally:
        # Close the WebDriver
        driver.quit()


# if date == date_format(datetime.now().today()):
#     insert_csv_data(csv_file,"informations")

# else:
#     print("WE DO NOT HAVE DATA FOR TODAY")
