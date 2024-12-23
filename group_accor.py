
# sorry you are blocked error while automation

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from insert_csv_into_sql_db import date_format,download_image

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
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
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to the page
driver.get("https://group.accor.com/en/news-media")  # Replace with the actual URL

# JavaScript to extract the href and navigate to it
js_code = """
// Locate the main link within the specified element and extract its href
const mainLink = document.querySelector(".nm-news-article-list__slider__item a.nm-news-article-list__slider__item__main-link");
if (mainLink) {
    const href = mainLink.href;  // Get the href attribute
    window.location.href = href; // Navigate to the link in the same tab
    return href; // Return the href for debugging
} else {
    return "No link found";
}
"""

# Execute the JavaScript code in Selenium
href = driver.execute_script(js_code)

# Print the href for debugging
print(f"Navigated to: {href}")

# Allow time for the new page to load
driver.implicitly_wait(10)

# Close the browser when done
driver.quit()
