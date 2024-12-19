




import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from insert_csv_into_sql_db import generate_news,generate_subtitle,generate_title
from insert_csv_into_sql_db import generate_random_filename,insert_csv_data,date_format,check_and_remove_file
from insert_csv_into_sql_db import download_image,append_unique_records
from upload_and_reference import upload_photo_to_ftp
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Disabling sandbox for headless mode
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
)  # Set user-agent to mimic a real browser

# Setup Selenium WebDriver
driver = webdriver.Chrome(options=chrome_options)

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


