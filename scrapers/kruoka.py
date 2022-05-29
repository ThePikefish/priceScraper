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

# Get product from user
product_link = input("Anna tuotteen linkki: ")

# Get stores from user
stores = input("Anna haettavien kauppojen nimet: ")
print()
stores = stores.split(",")

#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Use undetected chrome driver
driver = uc.Chrome(use_subprocess=True)

# Open product link for driver
driver.get(product_link)

# Find product name
try:
    product_name = driver.find_element(By.CLASS_NAME, 'product-details-info')
    product_name = product_name.find_element(By.TAG_NAME, 'span').text
    print("Tuote:")
    print(product_name)
    print()
except:
    print("Tuotetta ei löytynyt")

# Loop product in all selected stores
for store in stores:

    switch_store_button = driver.find_element(By.CLASS_NAME, 'switch-icon')
    switch_store_button.click()

    all_stores_button = driver.find_element(By.XPATH, "//*[text()='Kaikki']")
    all_stores_button.click()

    store_selector = driver.find_element(By.CLASS_NAME, 'store-selector__search')
    store_search_input = store_selector.find_element(By.XPATH, ".//input[@type='text']")
    store_search_input.send_keys(store)
    store_search_input.submit()

    # Store search function
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

    print(store_name + ':')
    time.sleep(1.5)

    # Parse product info from selenium to beautifulsoup
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")

    price_info = soup.find('div', class_='product-details-price')
    try:
        # If discount, show original price
        price = price_info.find('div', class_='original-price')
        results.append(price.text) # Try should end here if no discount
        sale_price = price_info.find('span', class_='price')

        try:
            # If discount has batch size
            batch_size = price_info.find('span', class_='batch-size').text
            results.append(batch_size) # Try should end here if no batch size

            print("Discount: " + sale_price.text + " /" + batch_size, end='')
        except:
            # If no batch size
            print("Discount: " + sale_price.text, end='')
        
        try:
            # If discount requires plussa-card
            plussa = price_info.find('span', class_='plussa-discount-text').text
            results.append(plussa) # Try should end here if no plussa-card is required

            print(" " + plussa)
        except:
            print()

        print(price.text)
    except:
        try:
            # If no discount, show price
            price = price_info.find('span', class_='price')
            results.append(price.text)

            print(price.text)
        except:
            # If no price, no product
            print("Tuotetta ei löytynyt")
    try:
        weight_price = price_info.find('div', class_='reference').text
        print(weight_price)
    except:
        pass

    print()
