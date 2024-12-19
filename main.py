from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape_with_selenium():
    # Data storage
    all_news = []

    # Define the websites and selectors#
    websites = [
        {"url": "https://www.absolutehotelservices.net/news-1", "selector": "Zc7IjY"},
        # {"url": "https://group.accor.com/en/news-media", "selector": "nm-news-article-list__slider"},#not done
         {"url": "https://www.amarahotels.com/about-us/press-releases", "selector": "views-row"},
        #  {"url": "https://www.amarahotels.com/about-us/press-releases", "selector": "news-content-center"}#not done
         {"url": "https://news.groupbanyan.com/archive/press_releases/", "selector": "article__text-holder"},
         {"url": "https://www.bestwestern.com/en_US/about/press-media.html", "selector": "richTextEditorExtended parbase"},
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
                title = item.text
                link = item.get_attribute('href')
                all_news.append({"Title": title, "Link": link})
        except Exception as e:
            print(f"Error with {site['url']}: {e}")
    
    driver.quit()

    # Save to CSV
    df = pd.DataFrame(all_news)
    df.to_csv("selenium_news_data.csv", index=False)
    print("Data saved to selenium_news_data.csv")

# Run the function
scrape_with_selenium()
