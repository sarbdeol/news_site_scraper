from selenium import webdriver
import time

# Set up WebDriver
driver = webdriver.Chrome()

# Open the target webpage
driver.get("https://www.kempinski.com/en/press-room")  # Replace with the actual URL


time.sleep(20)
# JavaScript to extract date and title
js_code = """
let extractedData = [];
const blocks = document.querySelectorAll('.relative.flex.flex-col.items-center.justify-center.h-full.w-full.p-6.md\\:p-7.lg\\:p-9');

blocks.forEach((block) => {
    const dateElement = block.querySelector('span');
    const titleElement = block.querySelector('h5');

    const date = dateElement ? dateElement.textContent.trim() : 'No date';
    const title = titleElement ? titleElement.textContent.trim() : 'No title';

    extractedData.push({ date, title });
});

return extractedData;
"""

# Execute JavaScript and get the extracted data
data = driver.execute_script(js_code)

# Print the extracted data
for item in data:
    print(f"Date: {item['date']}, Title: {item['title']}")

# Close the driver
driver.quit()
