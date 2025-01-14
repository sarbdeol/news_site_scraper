from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import csv

def initialize_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chromedriver_path = "/usr/local/bin/chromedriver"
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)  # 20-second timeout
    return driver, wait

def scrape_pages(letter, total_pages, existing_immat, writer):
    for page_num in range(1, total_pages + 1):
        print(f"Processing letter {letter}, page {page_num} of {total_pages}")
        if letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            try:
                url = f"https://edv.travel/annuaire-des-adherents/?ordre={letter}&pagination={page_num}"
                driver.get(url)
                time.sleep(2)  # Allow the page to load

                # Extract detail page links
                detail_links = driver.execute_script("""
                    return Array.from(document.querySelectorAll('.result-liste ul li a')).map(a => a.href);
                """)

                for href in detail_links:
                    print(f"Processing detail page: {href}")
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    driver.switch_to.window(driver.window_handles[-1])

                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#fichead")))
                        data = driver.execute_script("""
                            let data = {};
                            document.querySelectorAll('#fichead dl').forEach(dl => {
                                let key = dl.querySelector('dt')?.innerText.trim();
                                let value = dl.querySelector('dd')?.innerText.trim();
                                if (key && value) {
                                    data[key] = value;
                                }
                            });
                            data["Hyperlink"] = arguments[0];
                            return data;
                        """, href)
                        data["Alphabet"] = letter

                        # if "Immatriculation" in data and data["Immatriculation"].strip() in existing_immat:
                        #     print(f"Skipping duplicate Immatriculation: {data['Immatriculation']}")
                        # else:
                        writer.writerow(data)
                        existing_immat.add(data["Immatriculation"].strip())
                    except Exception as e:
                        print(f"Error processing detail page: {e}")
                    finally:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(f"Error processing page {page_num} for letter {letter}: {e}")

if __name__ == "__main__":
    existing_immat = set()
    try:
        with open("scraped_data.csv", "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if "Immatriculation" in row:
                    existing_immat.add(row["Immatriculation"].strip())
    except FileNotFoundError:
        pass

    driver, wait = initialize_browser()
    main_url = "https://edv.travel/annuaire-des-adherents/"
    driver.get(main_url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fitre-abc ul")))

    with open("edv_travel_scraped_data11012025.csv", "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Alphabet", "Immatriculation", "Raison sociale", "Enseigne", "Adresse", "Code postal",
            "Ville", "Téléphone", "Fax", "E-mail", "Site web", "Hyperlink"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()

        # Loop through alphabet letters dynamically
        alphabet_links = driver.find_elements(By.CSS_SELECTOR, ".fitre-abc ul li a")
        alphabet_letters = [link.text for link in alphabet_links] 

        for letter in alphabet_letters:
            print(f"Processing letter: {letter}")
            # if letter not in  ["A","B","C","D","E","F","G","H","I","J"]:
            driver.get(main_url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fitre-abc ul")))

            # Click the current letter
            alphabet_links = driver.find_elements(By.CSS_SELECTOR, ".fitre-abc ul li a")
            for link in alphabet_links:
                if link.text == letter:
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)
                    break

            # Get total pages for the current letter
            try:
                page_info = driver.execute_script("""
                    const pageInfo = document.querySelector('.col-sm-6.text-left');
                    if (pageInfo) {
                        return parseInt(pageInfo.querySelector('strong:last-child').innerText || "1");
                    }
                    return 1;
                """)
                total_pages = page_info if page_info else 1
            except Exception as e:
                print(f"Error fetching total pages for {letter}: {e}")
                continue

            scrape_pages(letter, total_pages, existing_immat, writer)

            time.sleep(10)
 
    driver.quit()
