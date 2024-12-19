import csv
import json
from selenium import webdriver

# Set up the WebDriver
driver = webdriver.Chrome()  # Or another WebDriver (e.g., Firefox)
driver.get('https://capellahotels.com/press-releases/')  # Replace with actual URL

# JavaScript to extract the data
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
            content: title,
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

# Execute the JavaScript and get the data
data = driver.execute_script(script)

# Parse the JSON data
extracted_data = json.loads(data)

# Define CSV structure and initialize the file
csv_file = "scraped_capella_hotels_news_data.csv"
headers = [
    "id", "title", "slug", "lead", "content", "image", "type", 
    "custom_field", "parent_id", "created_at", "updated_at", 
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Open the CSV file and write the headers and the data
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    # Loop through the extracted data and write it to the CSV file
    for item in extracted_data:
        writer.writerow({
            "id": item["id"],
            "title": item["title"],
            "slug": item["slug"],
            "lead": item["lead"],
            "content": item["content"],
            "image": item["image"],
            "type": item["type"],
            "custom_field": item["custom_field"],
            "parent_id": item["parent_id"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "language": item["language"],
            "seo_title": item["seo_title"],
            "seo_content": item["seo_content"],
            "seo_title_desc": item["seo_title_desc"],
            "seo_content_desc": item["seo_content_desc"],
            "category_id": item["category_id"]
        })

# Close the WebDriver
driver.quit()

print(f"Scraped data has been saved to {csv_file}")
