from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def scrape_news():
    # List to store all scraped news data
    all_news = []

    # Websites with CSS selectors
    websites = [
        {
            "url": "https://www.discoverasr.com/en/the-ascott-limited/newsroom#",
            "selector": "c-card__time",
            "date_selector": "c-card__item",
            "content_selector": "article__title"
        },
        {
            "url": "https://news.groupbanyan.com/",
            "selector": "card-title",
            "date_selector": "date",
            "content_selector": "card-description"
        },
        {
            "url": "https://www.bestwestern.com/en_US/about/press-media.html",
            "selector": "press-release-card",
            "date_selector": "date",
            "content_selector": "description"
        },
        # Add more websites as necessary...
    ]

    # Set up Selenium WebDriver with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without UI
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Loop through each website
    for site in websites:
        print(f"Scraping: {site['url']}")
        try:
            # Load the website
            driver.get(site["url"])
            wait = WebDriverWait(driver, 20)

            # Wait until elements matching the selector are loaded
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, site["selector"])))

            # Find all news items
            news_items = driver.find_elements(By.CLASS_NAME, site["selector"])

            # Extract data from each news item
            for item in news_items:
                try:
                    # Extract title
                    title = item.text.strip()

                    # Extract link (if available)
                    link = item.find_element(By.TAG_NAME, "a").get_attribute("href") if item.find_elements(By.TAG_NAME, "a") else None

                    # Extract date
                    date_element = item.find_element(By.CLASS_NAME, site["date_selector"]) if site.get("date_selector") else None
                    date = date_element.text.strip() if date_element else None

                    # Extract content
                    content_element = item.find_element(By.CLASS_NAME, site["content_selector"]) if site.get("content_selector") else None
                    content = content_element.text.strip() if content_element else None

                    # Append the news data as a dictionary
                    all_news.append({
                        "Title": title,
                        "Link": link,
                        "Date": date,
                        "Content": content
                    })
                except Exception as e:
                    print(f"Error extracting data from an item: {e}")

        except Exception as e:
            print(f"Error loading website {site['url']}: {e}")

    # Close the browser
    driver.quit()

    # Save the scraped data to a CSV file
    df = pd.DataFrame(all_news)
    df.to_csv("news_data.csv", index=False)
    print("Scraping complete. Data saved to 'news_data.csv'.")

# Run the scraper function
scrape_news()
