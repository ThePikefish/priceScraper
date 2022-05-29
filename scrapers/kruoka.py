import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
#import pandas as pd

import time

wait_time = 5
results = []

print()
print("############### K-Ruoka ###############")
print("########### Hintavertailija ###########")
print()

# Get stores from user
stores = input("Anna haettavien kauppojen nimet: ")
stores = stores.split(",")

# Get product from user
product_link = input("Hae tuotetta tai anna sen linkki: ")
print()


# Search and select product
def search_product(driver):
    global product_link
    if "https" not in product_link:
        # Search product by name if no link given
        driver.get("https://www.k-ruoka.fi/kauppa/tuotehaku")
        product_search_input = driver.find_element(By.XPATH, ".//input[@type='search']")
        product_search_input.send_keys(product_link)
        WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.CLASS_NAME, 'bundle-list-item'))).click()
        product_link = driver.current_url

# Select K-Ruoka store
def set_store(driver, store):
    # Go to store selection
    switch_store_button = driver.find_element(By.CLASS_NAME, 'switch-icon')
    switch_store_button.click()

    all_stores_button = driver.find_element(By.XPATH, "//*[text()='Kaikki']")
    all_stores_button.click()

    store_selector = driver.find_element(By.CLASS_NAME, 'store-selector__search')
    store_search_input = store_selector.find_element(By.XPATH, ".//input[@type='text']")
    store_search_input.send_keys(store)
    store_search_input.submit()

    # Search and select store
    try:
        time.sleep(0.5)
        store_list = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, 'store-list')))
        store_element = store_list.find_element(By.TAG_NAME, 'div')
        store_name = store_element.find_element(By.TAG_NAME, 'span').text
        store_element.click()
        print(store_name + ':')
    except:
        print("Kauppaa ei löytynyt")
        print()
        driver.get(product_link)
        return False



# Main program
def main():

    # Use undetected chrome driver
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = uc.Chrome(use_subprocess=True)

    search_product(driver)

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

        if set_store(driver, store) == False:
            continue

        time.sleep(0.5)
        try:
            WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-details-price')))
        except:
            pass

        # Parse product info from selenium to beautifulsoup
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        price_info = soup.find('div', class_='product-details-price')
        # Try to find discount
        try:
            # Show original price
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
        # If no discount
        except:
            try:
                # Show price
                price = price_info.find('span', class_='price')
                results.append(price.text)

                print(price.text)
            except:
                # If no price, no product
                print("Tuotetta ei löytynyt")
                driver.get(product_link)
                # TODO: Ask user if similar product should be searched
        try:
            # Show price to weight ratio
            weight_price = price_info.find('div', class_='reference').text
            print(weight_price)
        except:
            pass

        print()

main()