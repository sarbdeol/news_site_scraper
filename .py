from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up Selenium WebDriver
options = Options()
options.headless = False  # Set to False to open the browser window
driver = webdriver.Chrome(options=options)

# Navigate to the page
driver.get("https://www.whitbread.co.uk/media/")  # Replace with the actual URL of the page

# JavaScript code to get the most recent href from the <h3> tag
js_code = """
const mostRecentLink = document.querySelector('div.post p.excerpt h3 a');  // Get the first <a> inside an <h3> tag
if (mostRecentLink) {
    return mostRecentLink.href;  // Get the href attribute of the most recent link
} else {
    return null;  // No link found
}
"""

# Execute JavaScript to get the most recent href
most_recent_href = driver.execute_script(js_code)

if most_recent_href:
    print(f"Most recent href: {most_recent_href}")
    driver.get(most_recent_href)  # Open the most recent link in the browser
else:
    print("No link found.")

# Optional: Close the driver after some time or when you're done
driver.quit()
