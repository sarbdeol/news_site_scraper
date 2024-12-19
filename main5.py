from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

def scrape_with_selenium():
    # Data storage
    all_news = []

    # Define the websites and selectors
    websites = [
        {"url": "https://www.discoverasr.com/en/the-ascott-limited/newsroom#", "selector": "news-title-info", "date_selector": "news-date-info", "content_selector": "news-date-info"},
        {"url": "https://news.groupbanyan.com/", "selector": "card-title", "date_selector": "date", "content_selector": "card-description"},
        {"url": "https://www.bestwestern.com/en_US/about/press-media.html", "selector": "press-release-card", "date_selector": "date", "content_selector": "description"},
        {"url": "https://newsroom.caesars.com/press-releases/default.aspx", "selector": "result-item", "date_selector": "pub-date", "content_selector": "result-item__title"},
        {"url": "https://capellahotels.com/en/press", "selector": "press-release", "date_selector": "date", "content_selector": "article__title"},
        {"url": "https://media.choicehotels.com/international-press-releases", "selector": "press-release-item", "date_selector": "release-date", "content_selector": "content-snippet"},
        {"url": "https://www.corinthia.com/en-gb/press/", "selector": "press-release-card", "date_selector": "published-date", "content_selector": "card-description"},
        {"url": "https://www.dusit-international.com/en/updates/press-releases", "selector": "media-release-item", "date_selector": "release-date", "content_selector": "release-title"},
        {"url": "https://www.evt.com/news-press/", "selector": "news-item", "date_selector": "publish-date", "content_selector": "content"},
        {"url": "https://www.extendedstayamerica.com/media-center/", "selector": "news-item", "date_selector": "news-date", "content_selector": "headline"},
        {"url": "https://press.fourseasons.com/?_gl=1*ifw3d6*_gcl_au*MzIxNTE5MTgzLjE3MjE5NDE3MjA.*_ga*MzgxNzc1MzMyLjE3MjE5NDE3MjE.*_ga_Q9N1LB2PM5*MTcyMTk0MTcyMC4xLjAuMTcyMTk0MTcyMC42MC4wLjA.&_ga=2.129691973.893900628.1721941721-381775332.1721941721", "selector": "press-release", "date_selector": "release-date", "content_selector": "headline"},
        {"url": "https://www.frasershospitality.com/en/about-us/newsroom/", "selector": "press-release", "date_selector": "date", "content_selector": "summary"},
        {"url": "https://www.germainhotels.com/en/about/mediaroom", "selector": "media-item", "date_selector": "date-published", "content_selector": "media-title"},
        {"url": "https://int.hworld.com/press", "selector": "press-item", "date_selector": "press-date", "content_selector": "title"},
        {"url": "https://hotel.hardrock.com/news/", "selector": "news-item", "date_selector": "publish-date", "content_selector": "news-title"},
        {"url": "https://stories.hilton.com/releases", "selector": "release-card", "date_selector": "release-date", "content_selector": "card-title"},
        {"url": "https://www.historichotels.org/press/press-releases.php", "selector": "press-release", "date_selector": "date-published", "content_selector": "headline"},
        {"url": "https://newsroom.hyatt.com/news-releases?year=2024", "selector": "news-item", "date_selector": "release-date", "content_selector": "title"},
        {"url": "https://press.iberostar.com/en/news/", "selector": "news-card", "date_selector": "news-date", "content_selector": "news-title"},
        {"url": "https://www.ihgplc.com/en/news-and-media/news-releases", "selector": "press-release", "date_selector": "date", "content_selector": "content-description"},
        {"url": "https://www.jumeirah.com/en/jumeirah-group/press-centre", "selector": "press-release-item", "date_selector": "release-date", "content_selector": "article-title"},
        {"url": "https://www.karismahotels.com/news-press", "selector": "news-item", "date_selector": "publish-date", "content_selector": "content-summary"},
        {"url": "https://www.kempinski.com/en/press-room", "selector": "media-release", "date_selector": "date", "content_selector": "title"},
        {"url": "https://www.kerznercommunications.com/", "selector": "press-release", "date_selector": "date-published", "content_selector": "headline"},
        {"url": "https://www.lhw.com/press-center", "selector": "press-release", "date_selector": "publish-date", "content_selector": "release-title"},
        {"url": "https://www.lemontreehotels.com/media", "selector": "news-item", "date_selector": "date", "content_selector": "title"},
        {"url": "https://www.leonardo-hotels.com/press", "selector": "media-release", "date_selector": "date", "content_selector": "title"},
        {"url": "https://www.louvrehotels.com/en-us/news/", "selector": "news-release", "date_selector": "release-date", "content_selector": "title"},
        {"url": "https://news.marriott.com/news?newstype=press-releases", "selector": "press-release", "date_selector": "date-published", "content_selector": "headline"},
        {"url": "https://www.meliahotelsinternational.com/en/newsroom/our-news", "selector": "news-item", "date_selector": "date-published", "content_selector": "content-snippet"},
        {"url": "https://media.minorhotels.com/", "selector": "press-release", "date_selector": "news-date", "content_selector": "title"},
        {"url": "https://www.okura-nikko.com/press-room/press-release/", "selector": "press-release-item", "date_selector": "release-date", "content_selector": "headline"},
        {"url": "https://www.oberoihotels.com/media-press-releases/", "selector": "press-release", "date_selector": "date-published", "content_selector": "headline"},
        {"url": "https://www.omnihotels.com/media-center", "selector": "news-item", "date_selector": "date", "content_selector": "title"},
        {"url": "https://www.panpacific.com/en/newsroom.html#/", "selector": "press-release-item", "date_selector": "date", "content_selector": "headline"},
        {"url": "https://www.peninsula.com/en/newsroom", "selector": "press-item", "date_selector": "publish-date", "content_selector": "title"},
        {"url": "https://preferredhotels.com/press-center/press-releases", "selector": "news-item", "date_selector": "publish-date", "content_selector": "content-title"},
        {"url": "https://www.radissonhotels.com/en-us/corporate/media/press-releases", "selector": "news-item", "date_selector": "date", "content_selector": "headline"},
        {"url": "https://www.redroof.com/media", "selector": "media-item", "date_selector": "date", "content_selector": "news-title"},
        {"url": "https://press.roccofortehotels.com/?_gl=1*s5v1wo*_ga*MjExODU4NzQxNi4xNzIyMDg2MDQx*_ga_MQJXMJ8EC7*MTcyMjA4NjA0MC4xLjAuMTcyMjA4NjA1OS4wLjAuMTc2MjI5NTM5Mw..*_fplc*bDJ4ZGRJYm8yQkhFR3IlMkJxMDh1VjAyMlQ1SW1jeXA5MVZtUDVCenNDVjk1d2Q2MlJKS2pPeDdkUndIU0V5eGQwQWRYWGNKeldKanR6Y2V2WTA0QVlIZ1QyOVVDM3prWXclMkJsZ1BvYlFLbGVvdWd3ak1ZSlFQTnJQT1R3Rk1oQSUzRCUzRA..*_gcl_au*MTUwMTcyNTUwMC4xNzIyMDg2MDU5*FPAU*MTUwMTcyNTUwMC4xNzIyMDg2MDU5", "selector": "news-item", "date_selector": "publish-date", "content_selector": "news-title"},
        {"url": "https://www.rotana.com/newsroom", "selector": "media-release", "date_selector": "release-date", "content_selector": "headline"},
        {"url": "https://www.scandichotelsgroup.com/media/press-releases/", "selector": "press-release", "date_selector": "date", "content_selector": "title"},
    ]

    # Setup WebDriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    

    for site in websites:
        try:
            driver.get(site["url"])
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, site["selector"])))
            news_items = driver.find_elements(By.CLASS_NAME, site["selector"])

            for item in news_items:
                try:
                    # Extract title
                    title = item.text.strip()

                    # Extract link
                    link = item.find_element(By.TAG_NAME, "a").get_attribute("href") if item.find_elements(By.TAG_NAME, "a") else None

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
    df.to_csv("selenium_news_data_with_content_and_images.csv", index=False)
    print("Data saved to selenium_news_data_with_content_and_images.csv")

# Run the function
scrape_with_selenium()
