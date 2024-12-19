# import csv
# import os
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# import datetime

# # Setup Chrome in headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# driver = webdriver.Chrome(options=chrome_options)  # Make sure chromedriver is installed and in PATH

# # Define the target file/URL
# url = "https://www.historichotels.org/press/press-releases.php"  # Replace with the actual URL
# driver.get(url)

# # Create a folder to save images
# image_folder = "historichotels"
# os.makedirs(image_folder, exist_ok=True)

# # Extract all articles/cards
# articles = driver.find_elements(By.CSS_SELECTOR, ".item.card")

# data = []

# # Loop through articles to extract content
# for index, article in enumerate(articles, start=1):
#     try:
#         # Get the title
#         title = article.find_element(By.TAG_NAME, "h2").text.strip()

#         # Generate a slug from the title
#         slug = title.lower().replace(" ", "-").replace("®", "").replace(",", "").replace(".", "")

#         # Get the publication date
#         date = article.find_element(By.TAG_NAME, "p").text.strip()

#         # Get the image URL
#         image_url = article.find_element(By.TAG_NAME, "img").get_attribute("src")

#         # Download the image and save it locally
#         image_filename = f"{slug}.jpg"
#         image_path = os.path.join(image_folder, image_filename)
#         try:
#             response = requests.get(image_url, stream=True)
#             if response.status_code == 200:
#                 with open(image_path, "wb") as img_file:
#                     for chunk in response.iter_content(1024):
#                         img_file.write(chunk)
#             else:
#                 print(f"Failed to download image: {image_url}")
#         except Exception as e:
#             print(f"Error downloading image: {e}")
#             image_path = None  # Set to None if the image fails to download

#         # Get the link
#         link = article.find_element(By.TAG_NAME, "a").get_attribute("href")

#         # Open the link in the browser to extract additional content
#         driver.get(link)
#         content = driver.find_element(By.CSS_SELECTOR, ".press-release-content").text.strip()

#         # Additional placeholders for CSV headers
#         lead = f"Press release published on {date}"
#         type_field = "press_release"
#         custom_field = ""
#         parent_id = None
#         created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         updated_at = created_at
#         language = "en"
#         seo_title = title
#         seo_content = f"Discover more about {title}."
#         seo_title_desc = f"{title} - SEO Title"
#         seo_content_desc = f"{title} - SEO Description"
#         category_id = None

#         # Add to data list
#         data.append({
#             "id": index,
#             "title": title,
#             "slug": slug,
#             "lead": lead,
#             "content": content,
#             "image": image_url,
#             "type": type_field,
#             "custom_field": custom_field,
#             "parent_id": parent_id,
#             "created_at": created_at,
#             "updated_at": updated_at,
#             "language": language,
#             "seo_title": seo_title,
#             "seo_content": seo_content,
#             "seo_title_desc": seo_title_desc,
#             "seo_content_desc": seo_content_desc,
#             "category_id": category_id
#         })
#     except Exception as e:
#         print(f"Error extracting data from an article: {e}")

# # Write to CSV
# output_file = "historichotels.csv"
# headers = [
#     "id", "title", "slug", "lead", "content", "image", "type", 
#     "custom_field", "parent_id", "created_at", "updated_at", 
#     "language", "seo_title", "seo_content", "seo_title_desc", 
#     "seo_content_desc", "category_id"
# ]

# with open(output_file, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.DictWriter(file, fieldnames=headers)
#     writer.writeheader()
#     writer.writerows(data)

# print(f"Data successfully written to {output_file}")
# print(f"Images saved in the '{image_folder}' folder")

# # Quit the browser
# driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up Selenium WebDriver (using Chrome in this example)
options = Options()
options.headless = False  # Set to True for headless mode (no UI)
driver = webdriver.Chrome(options=options)

# Open the page URL
driver.get("https://www.historichotels.org/press/press-releases.php")  # Replace with the actual URL

# JavaScript code to get the most recent href and navigate to it
js_code = """
var mostRecentItem = document.querySelector('li.item.card .card-cta a');
if (mostRecentItem) {
    var href = mostRecentItem.href;
    window.location.href = href;  // Navigate to the link in the same tab
    return href;  // Return the href for verification or logging
} else {
    return "No link found";  // If no link is found
}
"""

# Execute the JavaScript code in Selenium and navigate to the most recent href
href = driver.execute_script(js_code)

# Print the href (optional)
print(f"Navigating to: {href}")

# Close the browser when done
driver.quit()
