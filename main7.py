from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import requests
from io import BytesIO

def scrape_with_selenium():
    # Define CSV structure and initialize the file
    csv_file = "scraped_news_data.csv"
    headers = [
        "id", "title", "slug", "lead", "content", "image", "type", 
        "custom_field", "parent_id", "created_at", "updated_at", 
        "language", "seo_title", "seo_content", "seo_title_desc", 
        "seo_content_desc", "category_id"
    ]

    # Create an empty CSV with the headers
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

    # Define the websites and selectors
    websites = [
        {"url": "https://www.absolutehotelservices.net/news-1", "selector": "Zc7IjY", "date_selector": "font_8", "content_selector": "wixui-rich-text__text"},
        # {"url": "https://www.amarahotels.com/about-us/press-releases", "selector": "views-row", "date_selector": "node__content", "content_selector": "field--name-body"},
        # {"url": "https://www.discoverasr.com/en/the-ascott-limited/newsroom#", "selector": "news-title-info", "date_selector": "news-date", "content_selector": "news-title-info"},
        # {"url":"https://news.groupbanyan.com/", "selector": "c-card__list", "date_selector": "c-card__item", "content_selector": "h5 c-card__title"}
        # {"url":"https://www.bestwestern.com/en_US/about/press-media.html", "selector": "press-release-card", "date_selector": "date", "content_selector": "description"} #you need handle seperatly
    ]

    # Setup WebDriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 50)

    id_counter = 1  # ID auto-increment counter


    for site in websites:
        try:
            driver.get(site["url"])
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, site["selector"])))
            news_items = driver.find_elements(By.CLASS_NAME, site["selector"])

            for item in news_items:
                try:
                    # Extract title
                    title = item.text.strip()

                    # Generate slug from title
                    slug = title.replace(" ", "-").lower()

                    # Extract link
                    link = item.find_element(By.TAG_NAME, "a").get_attribute("href") if item.find_elements(By.TAG_NAME, "a") else None

                    # # Extract date
                    # date_element = item.find_element(By.CLASS_NAME, site["date_selector"]) if site.get("date_selector") else None
                    # created_at = date_element.text.strip() if date_element else None

                     # Wait until the date element is visible (up to 10 seconds)
                    date_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, site["date_selector"])))
                    created_at = date_element.text.strip() if date_element else None

                    # # Extract content
                    # content_element = item.find_element(By.CLASS_NAME, site["content_selector"]) if site.get("content_selector") else None
                    # content = content_element.text.strip() if content_element else None

                    # Wait until the content element is visible (up to 10 seconds)
                    try:
                        content_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, site["content_selector"])))
                        content = content_element.text.strip() if content_element else None

                    except:
                        content =None

                    # Extract and print the href attribute
                    # try :
                            
                    #     for element in content_element:
                    #         href = element.get_attribute("href")
                    #         if href:
                    #            content=href

                    # except:
                    #     content = content_element.text.strip() if content_element else None

                    

                    # Image handling (dummy placeholder)

                    # # Attempt to extract image
                    # image_element = item.find_element(By.XPATH, ".//img[contains(@src, 'http')]")
                    # image = image_element.get_attribute("src") if image_element else None
                    image=None


                    # Write the data to the CSV file
                    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow([
                            id_counter,  # id
                            title,       # title
                            slug,        # slug
                            None,        # lead (empty for now)
                            content,     # content
                            image,       # image
                            "news",      # type (dummy value)
                            None,        # custom_field (empty)
                            None,        # parent_id (empty)
                            created_at,  # created_at
                            None,        # updated_at
                            "English",   # language (dummy value)
                            1,           # seo_title (enabled)
                            1,           # seo_content (enabled)
                            None,        # seo_title_desc (empty)
                            None,        # seo_content_desc (empty)
                            1            # category_id (dummy value)
                        ])
                    id_counter += 1

                except Exception as e:
                    print(f"Error extracting data from an item: {e}")

        except Exception as e:
            print(f"Error with {site['url']}: {e}")

    driver.quit()
    print(f"Data saved to {csv_file}")

# Run the function
scrape_with_selenium()
