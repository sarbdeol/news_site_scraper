from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def dynamic_scrape_with_selenium():
    # Data storage
    all_news = []

    # List of websites to scrape
    websites = [
        {"url": "https://www.absolutehotelservices.net/news-1"},
        {"url": "https://www.amarahotels.com/about-us/press-releases"},
        {"url": "https://news.groupbanyan.com/archive/press_releases/"},
        {"url": "https://www.bestwestern.com/en_US/about/press-media.html"},
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
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Fetch the page source
            news_items = driver.find_elements(By.CSS_SELECTOR, "*")  # Select all elements

            for item in news_items:
                try:
                    # Attempt to extract title (using common heuristics)
                    title_element = item.find_element(By.XPATH, ".//*[contains(@class, 'title') or contains(@class, 'header') or contains(@class, 'headline') or self::h1 or self::h2]")
                    title = title_element.text.strip() if title_element else None

                    # Attempt to extract link
                    link_element = item.find_element(By.XPATH, ".//a[contains(@href, 'http')]")
                    link = link_element.get_attribute("href") if link_element else None

                    # Attempt to extract image
                    image_element = item.find_element(By.XPATH, ".//img[contains(@src, 'http')]")
                    image = image_element.get_attribute("src") if image_element else None

                    # Attempt to extract date
                    date_element = item.find_element(By.XPATH, ".//*[contains(@class, 'date') or contains(text(), '202')]")  # Adjust for modern years
                    date = date_element.text.strip() if date_element else None

                    # Attempt to extract content
                    content_element = item.find_element(By.XPATH, ".//*[contains(@class, 'content') or contains(@class, 'text') or contains(@class, 'description')]")
                    content = content_element.text.strip() if content_element else None

                    # Add the news data if title or link exists
                    if title or link:
                        all_news.append({
                            "Title": title,
                            "Link": link,
                            "Image": image,
                            "Date": date,
                            "Content": content
                        })

                except Exception as e:
                    # Ignore errors in extracting specific elements
                    pass

        except Exception as e:
            print(f"Error with {site['url']}: {e}")

    driver.quit()

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(all_news)
    df.to_csv("dynamic_selenium_news_data.csv", index=False)
    print("Data saved to dynamic_selenium_news_data.csv")

# Run the function
dynamic_scrape_with_selenium()
