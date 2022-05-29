import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
#import pandas as pd

import time

results = []

print()
print("############### K-Ruoka ###############")
print("########### Hintavertailija ###########")
print()

product_link = input("Anna tuotteen linkki: ")

stores = input("Anna haettavien kauppojen nimet: ")
print()
stores = stores.split(",")

#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Use undetected chrome driver
driver = uc.Chrome(use_subprocess=True)

driver.get(product_link)

product_name = driver.find_element(By.CLASS_NAME, 'product-details-info')
product_name = product_name.find_element(By.TAG_NAME, 'span').text
print("Tuote:")
print(product_name)
print()

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
    search_counter = 0
    while search:
        time.sleep(1)
        search_counter = search_counter + 1
        if search_counter > 3:
            break
        try:
            store_list = driver.find_element(By.CLASS_NAME, 'store-list')
            search = False

            # Select the first store in store-list (first div)
            store_element = store_list.find_element(By.TAG_NAME, 'div')
            store_name = store_element.find_element(By.TAG_NAME, 'span').text
            store_element.click()

        except:
            print("Haetaan uudelleen..")
    if search_counter > 3:
        print("Kauppaa ei löytynyt")
        print()
        driver.get(product_link)
        continue


    time.sleep(1.5)

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

            print("Discount: " + sale_price.text + " /" + batch_size, end='')
        except:
            # Jos ei kappalemäärää
            print("Discount: " + sale_price.text, end='')
        
        try:
            # Jos alennus vaatii plussa-kortin
            plussa = price_info.find('span', class_='plussa-discount-text').text
            results.append(plussa) # Try loppuu tähän jos ei kappalemäärää

            print(" " + plussa)
        except:
            print()

        print(price.text)
    except:
        try:
            #Jos ei alennuksia, näytä hinta
            price = price_info.find('span', class_='price')
            results.append(price.text)

            print(price.text)
        except:
            # Jos ei hintaa, tuotetta ei ole
            print("Tuotetta ei löytynyt")
    try:
        weight_price = price_info.find('div', class_='reference').text
        print(weight_price)
    except:
        pass

    print()
