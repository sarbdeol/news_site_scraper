import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

# Set up Chrome options for headless mode
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

# Open the URL
url = "https://press.iberostar.com/en/news/"  # Adjust this to your target URL
driver.get(url)

# Wait for the content to load dynamically
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.news-page__paged-news"))
    )
except Exception as e:
    print("Error: Could not load the page or elements:", e)
    driver.quit()
    exit()

# Create directory to save images
image_folder = "iberostar_images"
os.makedirs(image_folder, exist_ok=True)

# Prepare CSV headers
headers = [
    "id", "title", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at",
    "language", "seo_title", "seo_content", "seo_title_desc",
    "seo_content_desc", "category_id"
]

# Initialize data list for CSV
data = []

# Extract articles
articles = driver.find_elements(By.CSS_SELECTOR, "article.article-card")
print(f"Found {len(articles)} articles")  # Debug: Check number of articles

# Loop through the articles and extract information
for index, article in enumerate(articles, start=1):
    try:
        # Extract article title
        try:
            title_element = article.find_element(By.CSS_SELECTOR, ".article-card__title")
            title = title_element.text.strip()
        except Exception as e:
            print(f"Title extraction failed for article {index}: {e}")
            title = "No Title"  # Fallback title

        # Generate slug from the title
        slug = title.lower().replace(" ", "-").replace("®", "").replace(",", "").replace(".", "")

        # Extract publication date
        try:
            date_element = article.find_element(By.CSS_SELECTOR, ".article-card__meta .article-card__date")
            date = date_element.text.strip()
        except Exception as e:
            print(f"Date extraction failed for article {index}: {e}")
            date = "Unknown Date"  # Fallback date

        # Extract article link
        link = article.find_element(By.CSS_SELECTOR, ".article-card__title").get_attribute("href")

        # Extract the image URL
        try:
            image_element = article.find_element(By.CSS_SELECTOR, ".article-card__image img")
            image_url = image_element.get_attribute("src")
            if image_url.startswith("/"):
                image_url = f"https://newsroom.iberostar.com{image_url}"

            # Download and save the image locally
            image_filename = f"{slug}.jpg"
            image_path = os.path.join(image_folder, image_filename)
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
            else:
                print(f"Failed to download image from {image_url}")
                image_path = None
        except Exception as e:
            print(f"Error downloading image: {e}")
            image_path = None

        # Placeholder values for remaining fields
        lead = ""  # You can extract lead if available on the page
        content = ""  # You can extract content if available on the page
        type_field = "press_release"
        custom_field = ""
        parent_id = None
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_at = created_at
        language = "en"
        seo_title = title
        seo_content = f"Discover more about {title}."
        seo_title_desc = f"{title} - SEO Title"
        seo_content_desc = f"{title} - SEO Description"
        category_id = ""  # You can extract category if available on the page

        # Append data to the list
        data.append({
            "id": index,
            "title": title,
            "slug": slug,
            "lead": lead,
            "content": content,
            "image": image_url,
            "type": type_field,
            "custom_field": custom_field,
            "parent_id": parent_id,
            "created_at": created_at,
            "updated_at": updated_at,
            "language": language,
            "seo_title": seo_title,
            "seo_content": seo_content,
            "seo_title_desc": seo_title_desc,
            "seo_content_desc": seo_content_desc,
            "category_id": category_id
        })

        print(f"Appended article {index}: {title}")  # Debug: Check which article is added

    except Exception as e:
        print(f"Error processing article {index}: {e}")

# Write the extracted data to CSV
output_file = "iberostar_newsroom_output.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)

print(f"Data successfully saved to {output_file}")
print(f"Images saved in the '{image_folder}' folder")

# Check the first row of data saved
