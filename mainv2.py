from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape_with_selenium():
    # Data storage
    all_news = []

    # Define the websites and selectors
    websites = [
        # {"url": "https://www.absolutehotelservices.net/news-1", "selector": "Zc7IjY", "date_selector": "font_8", "content_selector": "wixui-rich-text__text"},
        # {"url": "https://www.amarahotels.com/about-us/press-releases", "selector": "views-row", "date_selector": "node__content", "content_selector": "field--name-body"},  # Replace with actual class
        # {"url": "https://news.groupbanyan.com/archive/press_releases/", "selector": "article__title", "date_selector": "article-date-class", "content_selector": "article-content-class"},  # Replace with actual class
        {"url": "https://www.discoverasr.com/en/the-ascott-limited/newsroom#", "selector": "news-content-center", "date_selector": "news-date-info", "content_selector": "news-content-center"},  # Replace with actual class
    ]

    # Setup WebDriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 10)

    for site in websites:
        try:
            driver.get(site["url"])
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, site["selector"])))
            news_items = driver.find_elements(By.CLASS_NAME, site["selector"])

            for item in news_items:
                try:
                    # Extract title
                    title = item.text.strip()

                    # Extract link
                    link = item.find_element(By.TAG_NAME, "a").get_attribute("href") if item.find_elements(By.TAG_NAME, "a") else None

                    # Extract image
                    image = item.find_element(By.TAG_NAME, "img").get_attribute("src") if item.find_elements(By.TAG_NAME, "img") else None

                    # Extract date
                    date_element = item.find_element(By.CLASS_NAME, site["date_selector"]) if site.get("date_selector") else None
                    date = date_element.text.strip() if date_element else None

                    # Extract content
                    content_element = item.find_element(By.CLASS_NAME, site["content_selector"]) if site.get("content_selector") else None
                    content = content_element.text.strip() if content_element else None

                    # Append data as a dictionary
                    all_news.append({
                        "Title": title,
                        "Link": link,
                        "Image": image,
                        "Date": date,
                        "Content": content
                    })
                except Exception as e:
                    print(f"Error extracting data from an item: {e}")

        except Exception as e:
            print(f"Error with {site['url']}: {e}")

    driver.quit()

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(all_news)
    df.to_csv("selenium_news_data_with_content.csv", index=False)
    print("Data saved to selenium_news_data_with_content.csv")

# Run the function
scrape_with_selenium()
