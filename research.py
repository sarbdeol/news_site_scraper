from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://www.panpacific.com/en/newsroom.html#/latest_news")
print(driver.title)
driver.quit()
