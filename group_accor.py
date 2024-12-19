
# sorry you are blocked error while automation

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up Selenium WebDriver
options = Options()
options.headless = False  # Set to True for headless mode
driver = webdriver.Chrome(options=options)

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
