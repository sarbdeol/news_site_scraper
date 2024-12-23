# import os
# import requests
# import csv
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Set up Selenium WebDriver in headless mode
# def setup_driver():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Run in headless mode
#     chrome_options.add_argument("--disable-gpu")  # Disable GPU
#     chrome_options.add_argument("--no-sandbox")  # Disable sandbox
#     chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent memory issues
#     return webdriver.Chrome(options=chrome_options)

# # Scrape data
# def scrape_data(driver, url):
#     driver.get(url)

#     # Wait for the page to load and elements to be present
#     try:
#         WebDriverWait(driver, 30).until(
#             EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".richTextEditorExtended a"))
#         )
#     except Exception as e:
#         print(f"Error waiting for elements: {e}")
#         return []

#     # JavaScript to extract data
#     js_code = """
#     let extractedData = [];
#     document.querySelectorAll('.richTextEditorExtended a').forEach(link => {
#         let title = link ? link.textContent.trim() : 'No title';
#         let date = link.previousSibling?.textContent.trim() || 'No date';
#         let newsLink = link.href || 'No link';
#         let image = 'No image'; // No specific image selector available, adjust if needed
#         extractedData.push({ date, title, image, link: newsLink });
#     });
#     return extractedData;
#     """
#     return driver.execute_script(js_code)

# # Save images locally
# def save_image(image_url, save_path):
#     try:
#         response = requests.get(image_url, stream=True, timeout=10)
#         if response.status_code == 200:
#             with open(save_path, "wb") as f:
#                 for chunk in response.iter_content(1024):
#                     f.write(chunk)
#             return save_path
#     except Exception as e:
#         print(f"Error downloading image: {e}")
#     return "No image"

# # Save data to CSV
# def save_to_csv(data, image_dir, csv_file):
#     headers = [
#         "id", "title", "slug", "lead", "content", "image", "type",
#         "custom_field", "parent_id", "created_at", "updated_at", 
#         "language", "seo_title", "seo_content", "seo_title_desc", 
#         "seo_content_desc", "category_id"
#     ]

#     rows = []
#     for index, item in enumerate(data, start=1):
#         # Generate image file name
#         image_filename = os.path.join(image_dir, f"image_{index}.jpg")

#         # Download image if URL exists
#         if item['image'] and item['image'] != 'No image':
#             image_filename = save_image(item['image'], image_filename)
        
#         # Create a row for the CSV
#         row = [
#             index,  # id
#             item['title'],  # title
#             item['link'],  # slug (using the link as a placeholder)
#             'No lead',  # lead
#             'No content',  # content
#             image_filename,  # image path
#             'No type',  # type
#             'No custom field',  # custom_field
#             'No parent id',  # parent_id
#             item['date'],  # created_at
#             item['date'],  # updated_at
#             'en',  # language
#             'No SEO title',  # seo_title
#             'No SEO content',  # seo_content
#             'No SEO title description',  # seo_title_desc
#             'No SEO content description',  # seo_content_desc
#             'No category id'  # category_id
#         ]
#         rows.append(row)

#     # Write to CSV
#     with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(headers)
#         writer.writerows(rows)

# # Main function
# def main():
#     url = "https://www.bestwestern.com/en_US/about/press-media.html"  # Target URL
#     csv_file = "scraped_data.csv"
#     image_dir = "downloaded_images"

#     # Create image directory if not exists
#     if not os.path.exists(image_dir):
#         os.makedirs(image_dir)

#     # Initialize driver and scrape data
#     driver = setup_driver()
#     try:
#         data = scrape_data(driver, url)
#         if not data:
#             print("No data extracted. Please check the selectors or webpage content.")
#             return

#         # Save data to CSV and download images
#         save_to_csv(data, image_dir, csv_file)
#         print(f"Data saved to {csv_file} and images saved in {image_dir}/")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     main()




#-----------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage (optional, improves performance)
chrome_options.add_argument("--no-sandbox")  # Recommended for headless mode in some environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues
chrome_options.add_argument("--window-size=1920,1080")  # Set the window size for screenshots
# Specify the path to your ChromeDriver executable
chromedriver_path = "/usr/local/bin/chromedriver"  # Replace with the actual path to ChromeDriver

# Set up the WebDriver with Chrome options
# Set up the WebDriver with Chrome options
service = Service(chromedriver_path)
driver = webdriver.Chrome(options=chrome_options)

 # Update path to your chromedriver

# Navigate to the page with the news list
driver.get('https://www.bestwestern.com/en_US/about/press-media.html')  # Replace with the URL of the page containing the news links

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

# Step 1: Execute JavaScript to get the most recent news link and open it in a new window
script = """
    // Get the first news link
    let firstLink = document.querySelector('a[href^="/en_US/about/press-media/2024-press-releases/"]');
    let href = firstLink ? firstLink.getAttribute('href') : null;
    
    // Open the link in a new tab
    if (href) {
        window.open(href, '_blank');
        return href;
    }
    return null;
"""

# Execute the script to get the href and open the link in a new tab
news_link = driver.execute_script(script)

if news_link:
    # Switch to the new window/tab
    driver.switch_to.window(driver.window_handles[1])  # Switch to the new tab

    # Wait for the new page to load (adjust the wait time based on the content)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "article")))

    # Step 2: Execute JavaScript to extract date, title, content, and image from the news page
    extract_script = """
        let date = document.querySelector('time').textContent.trim();
        let title = document.querySelector('h1').textContent.trim();
        let content = document.querySelector('.field--name-body').textContent.trim();
        let image = document.querySelector('img') ? document.querySelector('img').src : null;
        
        return {
            date: date,
            title: title,
            content: content,
            image: image
        };
    """

    # Execute the script to get the news details
    news_details = driver.execute_script(extract_script)

    # Print the extracted details
    print("Date:", news_details['date'])
    print("Title:", news_details['title'])
    print("Content:", news_details['content'])
    print("Image URL:", news_details['image'])

    # Close the new window
    driver.close()

    # Switch back to the original window
    driver.switch_to.window(driver.window_handles[0])
else:
    print("No recent news link found.")

# Close the browser
driver.quit()
