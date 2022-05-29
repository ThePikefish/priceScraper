import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import pandas as pd

import time

#stores = ['Ylioppilaskylä', 'Puhakka', 'Kupittaa']
#stores = ['Puhakka']
results = []

print("########## K-Ruoka ##########")
print("###### Hintavertailija ######")
print()

product_link = input("Anna tuotteen linkki: ")

stores = input("Anna haettavien kauppojen nimet: ")
print()
stores = stores.split(",")

#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Use undetected chrome driver
driver = uc.Chrome(use_subprocess=True)

driver.get(product_link)

for store in stores:

    switch_store_button = driver.find_element(By.CLASS_NAME, 'switch-icon')
    switch_store_button.click()

    all_stores_button = driver.find_element(By.XPATH, "//*[text()='Kaikki']")
    all_stores_button.click()

    store_selector = driver.find_element(By.CLASS_NAME, 'store-selector__search')
    store_search_input = store_selector.find_element(By.XPATH, ".//input[@type='text']")
    store_search_input.send_keys(store)
    store_search_input.submit()

    search = True
    while search:
        time.sleep(1)
        store_list = driver.find_element(By.CLASS_NAME, 'store-list')
        # Select the first store in store-list (first div)
        store_element = store_list.find_element(By.TAG_NAME, 'div')
        store_name = store_element.find_element(By.TAG_NAME, 'span').text
        if (store_name):
            search = False
        else:
            print("Haetaan uudelleen")
    store_element.click()

    driver.get("https://www.k-ruoka.fi/haku?q=pringles&tuote=pringles-sourcreamonion-200g-5053990138753")
    time.sleep(1)

    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")

    print(store_name + ':')

    price_info = soup.find('div', class_='product-details-price')
    try:
        # Jos alennuksia, näytä alkuperäinen hinta
        price = price_info.find('div', class_='original-price')
        results.append(price.text) # Try loppuu tähän jos ei alennuksia
        sale_price = price_info.find('span', class_='price')

        try:
            # Jos alennuksessa kappalemäärä
            batch_size = price_info.find('span', class_='batch-size').text
            results.append(batch_size) # Try loppuu tähän jos ei kappalemäärää

            print("Discount: " + sale_price.text + " /" + batch_size)
        except:
            # Jos ei kappalemäärää
            print("Discount: " + sale_price.text)
    except:
        #Jos ei alennuksia, näytä hinta
        price = price_info.find('span', class_='price')
        results.append(price.text)

    print(price.text)
    print()
