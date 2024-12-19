#BOT VERIFICATION

import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import json
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU
chrome_options.add_argument("--no-sandbox")  # Disable sandbox
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues


# Initialize WebDriver
driver = webdriver.Chrome()  # Or another WebDriver (e.g., Firefox)
driver.get('https://capellahotels.com/press-releases/')  # Replace with actual URL

# Wait for page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.press-subnode')))

# JavaScript to extract the data for the list of press releases
script = """
    const pressNodes = document.querySelectorAll('.press-subnode');
    const extractedData = [];

    pressNodes.forEach((node, index) => {
        const date = node.querySelector('.press-subnode-date') ? node.querySelector('.press-subnode-date').innerText : '';
        const title = node.querySelector('.press-subnode-title h4') ? node.querySelector('.press-subnode-title h4').innerText : '';
        const synopsis = node.querySelector('.press-subnode-synopsis p') ? node.querySelector('.press-subnode-synopsis p').innerText : '';
        const readMoreLink = node.querySelector('.press-subnode-actioncontainer a') ? node.querySelector('.press-subnode-actioncontainer a').href : '';
        
        let imageUrl = '';
        const imageElement = node.querySelector('img');
        if (imageElement) {
            imageUrl = imageElement.src;
        } else {
            const backgroundElement = node.querySelector('.press-subnode');
            if (backgroundElement) {
                const backgroundStyle = window.getComputedStyle(backgroundElement).backgroundImage;
                if (backgroundStyle && backgroundStyle !== 'none') {
                    imageUrl = backgroundStyle.slice(5, -2); // Extract URL from `url(...)`
                }
            }
        }

        extractedData.push({
            id: index + 1,
            title: title,
            slug: readMoreLink.split('/').pop().split('.')[0],  // Use last part of the URL as the slug
            lead: '',
            content: synopsis,
            read_more_link: readMoreLink,
            image: imageUrl,
            type: 'press-release',
            custom_field: '',
            parent_id: '',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            language: 'en',
            seo_title: title,
            seo_content: synopsis,
            seo_title_desc: title.slice(0, 60),
            seo_content_desc: synopsis.slice(0, 160),
            category_id: 'news'
        });
    });

    return JSON.stringify(extractedData);
"""

# Execute JavaScript and get the list of press releases
data = driver.execute_script(script)
extracted_data = json.loads(data)

# Define CSV structure and initialize the file
csv_file = "capella_hotels_news_data.csv"
headers = [
    "id", "title", "slug", "lead", "content", "read_more_link", "image", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open the CSV file and write the headers
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    # Loop through the extracted data, click "Read More" and extract full content
    for item in extracted_data:
        # Extract the link for "Read More"
        read_more_link = item['read_more_link']
        
        # Click on "Read More" link to open the full article in the same window
        driver.get(read_more_link)
        
        # Wait for the content to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.press-release-content')))
        
        # Extract detailed content (title, content, images)
        try:
            content_title = driver.find_element(By.CSS_SELECTOR, '.press-release-title').text
            content_body = driver.find_element(By.CSS_SELECTOR, '.press-release-content').text
        except Exception as e:
            print(f"Error extracting content from {read_more_link}: {e}")
            content_title = ""
            content_body = ""

        # Extract images from the full article page
        images = driver.find_elements(By.TAG_NAME, 'img')
        image_urls = [img.get_attribute('src') for img in images]

        # Save the images locally
        image_folder = "capella_hotels_images"
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        # Download and save images
        image_paths = []
        for idx, img_url in enumerate(image_urls):
            try:
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                img_path = os.path.join(image_folder, f"image_{item['id']}_{idx + 1}.jpg")
                img.save(img_path)
                image_paths.append(img_path)
            except Exception as e:
                print(f"Failed to save image: {str(e)}")

        # Write the data into CSV
        writer.writerow({
            "id": item["id"],
            "title": content_title,  # Use the full title from the read more page
            "slug": item["slug"],
            "lead": item["lead"],
            "content": content_body,  # Use the full content from the read more page
            "read_more_link": read_more_link,
            "image": ', '.join(image_paths),  # Save all image paths
            "type": item["type"],
            "custom_field": '',
            "parent_id": '',
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "language": '',
            "seo_title": '',
            "seo_content": '',
            "seo_title_desc": '',
            "seo_content_desc": '',
            "category_id": 101
        })

# Close the WebDriver
driver.quit()

print(f"Scraped data has been saved to {csv_file}")
