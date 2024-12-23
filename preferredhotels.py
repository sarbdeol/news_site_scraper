


import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,check_and_remove_file,download_image,append_unique_records
from insert_csv_into_sql_db import insert_csv_data,date_format
from upload_and_reference import upload_photo_to_ftp

# CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

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

base_url = "https://preferredhotels.com/press-center/press-releases"  # Replace with the actual URL

if True:

    try:
        # Navigate to the page
        driver.get(base_url)
        time.sleep(5)  # Allow the page to load

        # Execute the JavaScript to get the most recent news
        recent_news = driver.execute_script("""
            const rows = document.querySelectorAll('table.press-release-table tbody tr');
            function parseDate(dateString) {
                const months = {
                    January: '01', February: '02', March: '03', April: '04', May: '05', June: '06',
                    July: '07', August: '08', September: '09', October: '10', November: '11', December: '12'
                };
                const parts = dateString.split(' ');
                const month = months[parts[0]];
                const day = parts[1].replace(',', '').padStart(2, '0');
                const year = parts[2];
                return `${year}-${month}-${day}`;
            }

            const newsItems = Array.from(rows).map((row, index) => {
                const dateText = row.querySelector('td.date-field div').textContent.trim();
                const titleLink = row.querySelector('td.title-field a');
                const imageElem = row.querySelector('img');  // Assuming there's an <img> tag
                return {
                    id: index + 1,  // Generate an ID for each item
                    date: parseDate(dateText),
                    title: titleLink.textContent.trim(),
                    href: titleLink.href,
                    image: imageElem ? imageElem.src : null  // Get the image URL if it exists
                };
            });

            newsItems.sort((a, b) => new Date(b.date) - new Date(a.date));
            const mostRecentNews = newsItems[0];

            const linkElement = document.querySelector(`a[href="${mostRecentNews.href}"]`);
            if (linkElement) {
                linkElement.click();
                return mostRecentNews;  // Return the most recent news item details
            } else {
                return null;
            }
        """)

        img_name = generate_random_filename()
         
        if recent_news['image'] != None:
            download_image(recent_news['image'],img_name)
            print("downloaded")
            upload_photo_to_ftp(img_name,recent_news['image'])
        else:
            print("NO IMAGE")

        
        title=  generate_title(recent_news['title'])
        date = date_format(recent_news['date'])
        print(date)
        # Save the extracted data in CSV format
        if recent_news:
            csv_data = [
                {
                    "id": recent_news['id'],
                    "title": title,
                    "subtitle": generate_subtitle(title),  # No subtitle available
                    "slug": title.lower().replace(" ","-"),  # No slug available
                    "lead": None,  # No lead available
                    "content": generate_news(title),  # No content available (PDF needs separate processing)
                    "image":"information/"+img_name,  # Include the image URL
                    "type": "Press Release",
                    "custom_field": None,
                    "parent_id": None,
                    "created_at": date,
                    "updated_at": time.time(),
                    "added_timestamp": date,
                    "language": "en",
                    "seo_title": '',
                    "seo_content": None,
                    "seo_title_desc": None,
                    "seo_content_desc": None,
                    "category_id": 100,
                }
            ]
            check_and_remove_file('recent_news_with_image.csv')
            # Write to CSV file
            with open("recent_news_with_image.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(csv_data)

            print(f"Most Recent News saved to 'recent_news_with_image.csv':\nTitle: {recent_news['title']}\nDate: {recent_news['date']}\nLink: {recent_news['href']}\nImage: {recent_news['image']}")
        else:
            print("No recent news found.")

    finally:
        driver.quit()

    if date == date_format(time.time()):
        insert_csv_data("recent_news_with_image.csv","informations")
        append_unique_records("recent_news_with_image.csv","combined_news_data.csv")
    else:
        print("WE DO NOT HAVE DATA FOR TODAY")

