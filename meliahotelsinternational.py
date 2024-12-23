




import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,insert_csv_data,date_format,check_and_remove_file
from insert_csv_into_sql_db import download_image,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from selenium.webdriver.chrome.options import Options
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

# Define CSV headers
headers = [
    "id", "title", "subtitle", "slug", "lead", "content", "image", "type",
    "custom_field", "parent_id", "created_at", "updated_at", "added_timestamp",
    "language", "seo_title", "seo_content", "seo_title_desc", 
    "seo_content_desc", "category_id"
]

# Set up WebDriver
chrome_options = Options()

try:
    # Load the main page
    driver.get("https://www.meliahotelsinternational.com/en/newsroom/our-news/")  # Replace with the actual URL

    # Extract news URLs
    news_links = driver.execute_script("""
        let news = [];
        document.querySelectorAll(".news-pill a").forEach(anchor => {
            let title = anchor.querySelector("h2")?.textContent.trim() || "No Title";
            let href = anchor.href;
            news.push({title: title, href: href});
        });
        return news;
    """)

    # Prepare data for CSV
    csv_data = []
    id_counter = 1

    # Visit each news page and extract details
    for item in news_links[:1]:
        driver.get(item['href'])
        news_details = driver.execute_script("""
            let newsData = [];
            document.querySelectorAll('.o-destacados').forEach(article => {
                let date = article.querySelector('time')?.textContent.trim() || 'No Date';
                let title = article.querySelector('h2.a-titular-article')?.textContent.trim() || 'No Title';
                let content = article.querySelector('h4.a-subtitle-article')?.textContent.trim() || 'No Summary';
                let image = article.querySelector('img.img-article')?.src || 'No Image';
                newsData.push({date, title, content, image});
            });
            return newsData;
        """)

        img_name =  generate_random_filename()

        image_urls = [item['image'] for item in news_details if 'image' in item]
        title = [item['title'] for item in news_details if 'title' in item]
        content = [item['content'] for item in news_details if 'content' in item]
        date = [item['date'] for item in news_details if 'date' in item]

        print(date)

        download_image(image_urls[0],img_name)

        upload_photo_to_ftp(img_name,"/public_html/storage/information/")

        title =  generate_title(title)
        # Transform extracted data to match CSV format
        for news in news_details:
            row = {
                "id": id_counter,
                "title": title.strip('"'),
                "subtitle": generate_subtitle(title),  # Subtitle is not extracted
                "slug": title.lower().replace(" ", "-").strip('"'),  # Generate slug
                "lead": "",  # Lead not extracted
                "content": generate_news(news['content']),
                "image": "information/"+img_name,
                "type": "news",  # Static value
                "custom_field": "",  # Not applicable
                "parent_id": None,  # Not applicable
                "created_at": date_format(news['date']),  # Use extracted date
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Current timestamp
                "added_timestamp": date_format(news['date']),  # Current timestamp in Unix
                "language": "en",  # Assuming English
                "seo_title":'',  # Use title for SEO title
                "seo_content": '',  # Use content for SEO content
                "seo_title_desc": "",  # Not applicable
                "seo_content_desc": "",  # Not applicable
                "category_id": '100',  # Not extracted
            }
            csv_data.append(row)
            id_counter += 1

    # Write to CSV file
    output_file = "meliahotelsinternational_news_data.csv"
    check_and_remove_file(output_file)
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"Data saved to {output_file} successfully!")

    if date_format(news['date']) == date_format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")): 
        insert_csv_data(output_file,'informations')
        append_unique_records(output_file,"combined_news_data.csv")

    else:
        print("--------WE DO NOT HAVE DATA FOR TODAY--------")

finally:
    # Quit the WebDriver
    driver.quit()


