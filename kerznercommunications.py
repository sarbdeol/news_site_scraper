import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import insert_into_db,check_and_remove_file,generate_news
import shutil
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disabling sandbox for headless mode
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)  # Set user-agent to mimic a real browser

# Path to chromedriver (ensure chromedriver is installed and accessible)
driver = webdriver.Chrome(options=chrome_options)

# Define CSV headers
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Month mapping for conversion
MONTHS = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12"
}

# Open the target webpage
driver.get("https://www.kerznercommunications.com/")  # Replace with the actual URL

# JavaScript to extract data
js_code = """
let extractedData = [];
const blocks = document.querySelectorAll('.pp_unit');
blocks.forEach((block, index) => {
    const titleElement = block.querySelector('.pp-block-item-heading');
    const title = titleElement ? titleElement.textContent.trim() : 'No title';
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    const lead = block.querySelector('.pp-block-item-intro')?.innerText.trim() || 'No lead';
    const linkElement = block.querySelector('.pp-block-item-container');
    const link = linkElement ? linkElement.href : 'No link';
    const imageElement = block.querySelector('.pp_blockheadlines_thumb');
    const image = imageElement ? imageElement.style.backgroundImage.match(/url\\(["']?([^"']+)["']?\\)/)[1] : 'No image';
    const dateDay = block.querySelector('.pp-block-item-date-day')?.textContent.trim() || 'No day';
    const dateMonth = block.querySelector('.pp-block-item-date-month')?.textContent.trim() || 'No month';
    const dateYear = block.querySelector('.pp-block-item-date-year')?.textContent.trim() || 'No year';
    const createdAt = `${dateYear}-${dateMonth}-${dateDay}`;
    extractedData.push({
        id: index + 1,
        title,
        slug,
        lead,
        content: link, // Assuming 'content' is the link
        image,
        type: 'article', // Default type
        custom_field: '',
        parent_id: '',
        created_at: createdAt,
        updated_at: createdAt,
        language: 'en',
        seo_title: title,
        seo_content: lead,
        seo_title_desc: title,
        seo_content_desc: lead,
        category_id: ''
    });
});
return extractedData;
"""

# Execute JavaScript and extract data
data = driver.execute_script(js_code)

for title in data:
    if title!='No title':
        title['title']=generate_news(title['title'])
    elif title.startswith('Sure!'):
        print(title)
        exit(0)

# Create a folder to store images
image_folder = "kerznercommunications_images"
os.makedirs(image_folder, exist_ok=True)

# Prepare CSV file
csv_file = "kerznercommunications_output.csv"
check_and_remove_file(csv_file)

with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    # Loop through extracted data
    for item in data:
        # Process and save the image
        image_url = item["image"]
        if image_url != "No image":
            try:
                # Ensure URL is absolute
                if not image_url.startswith("http"):
                    base_url = driver.current_url.split("//")[1].split("/")[0]
                    image_url = f"https://{base_url}{image_url}"

                # Get the image name and save it
                image_name = os.path.basename(image_url.split("?")[0])  # Remove query params
                image_path = os.path.join(image_folder, image_name)

                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(image_path, "wb") as img_file:
                        for chunk in response.iter_content(1024):
                            img_file.write(chunk)
                    print(f"Image saved: {image_path}")
                    item["image"] = image_path  # Update image path in CSV
                else:
                    print(f"Failed to download image: {image_url}")
                    item["image"] = "Download failed"
            except Exception as e:
                print(f"Error downloading image {image_url}: {e}")
                item["image"] = "Error downloading"

        # Convert month name to number for 'created_at'
        if item["created_at"] != "No year-No month-No day":
            parts = item["created_at"].split("-")
            month_name = parts[1]
            parts[1] = MONTHS.get(month_name, month_name)  # Replace month with numeric equivalent
            item["created_at"] = "-".join(parts)
            item["updated_at"] = item["created_at"]

        # Write row to CSV
        writer.writerow(item)

# Close the driver
driver.quit()

print(f"Data saved to {csv_file} and images saved in '{image_folder}' folder.")
