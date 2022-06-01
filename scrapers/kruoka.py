import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
#import pandas as pd

import traceback
import time
import platform
import glob
import os
import sys


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


def accept_cookie(driver):
    try:
        cookie_overlay = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'kconsent')))
        cookie_overlay.find_element(By.ID, 'kc-acceptAndHide').click()
        print("Cookie accepted")
    except:
        pass


# Search and select product
def search_product(driver):
    global product_link
    if "https" not in product_link:
        # Search product by name if no link given
        driver.get("https://www.k-ruoka.fi/kauppa/tuotehaku")
        print("Driver navigated to URL")

        accept_cookie(driver)

        product_search_input = driver.find_element(By.XPATH, ".//input[@type='search']")
        product_search_input.send_keys(product_link)
        WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.CLASS_NAME, 'bundle-list-item'))).click()
        product_link = driver.current_url
        print("Searched item")
        print()


# Select K-Ruoka store
def set_store(driver, store):
    # Go to store selection
    switch_store_button = driver.find_element(By.CLASS_NAME, 'switch-icon')
    switch_store_button.click()

    all_stores_button = driver.find_element(By.XPATH, "//*[text()='Kaikki']")
    all_stores_button.click()

    # Search store
    store_selector = driver.find_element(By.CLASS_NAME, 'store-selector__search')
    store_search_input = store_selector.find_element(By.XPATH, ".//input[@type='text']")
    store_search_input.send_keys(store)
    store_search_input.submit()

    # Select store if found
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


def scrape_product(driver):
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

# Cache undetected_chromedriver so it doesn't need to be installed at every run
# Solves slow launch times on windows after first load
def try_local_driver():
    if platform.system() == "Windows":
        driver_path = os.path.abspath(os.path.expanduser("~/appdata/roaming/undetected_chromedriver"))
        files = glob.glob(driver_path + '\*')
        if files:
            driver_exe = max(files, key=os.path.getctime) # Latest file
            os.rename(driver_exe, driver_path + "\manual_chromedriver.exe")
            return driver_path + "\manual_chromedriver.exe"
    return None



# Main program
def main():

    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Use undetected chrome driver
    options = uc.ChromeOptions()
    options.Proxy = None
    
    if "--headless" in sys.argv:
        options.headless=True
        options.add_argument('--headless')

    driver = uc.Chrome(use_subprocess=True, options=options, driver_executable_path=try_local_driver())
    try_local_driver()
    print("Driver initialized")

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

        # Calls function to set the store. Incase of failure, skip store
        if set_store(driver, store) == False:
            continue

        # Wait for prodcut
        time.sleep(0.5)
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-details-price')))
        except:
            pass

        # Find relevant information from product
        scrape_product(driver)

        # If * specified, loop product in all near stores aswell
        if '*' in store:
            store = store.replace('*','')
            try:
                # Find near stores
                driver.find_element(By.XPATH, "//*[text()='Tuote muissa kaupoissa']").click()
                near_stores_element = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-availability-container')))
                WebDriverWait(near_stores_element, wait_time).until(EC.element_to_be_clickable((By.TAG_NAME, 'a')))

                # Get links
                near_stores = near_stores_element.find_elements(By.TAG_NAME, 'a')
                near_store_links = []
                near_store_names = []
                for link in near_stores:
                    near_store_links.append(link.get_attribute('href'))
                    near_store_names.append(link.text)

                # Loop all near stores
                for link, store_name in zip(near_store_links, near_store_names):
                    print(store_name + ':')
                    driver.get(link)
                    # Find relevant information from product
                    scrape_product(driver)

            except Exception:
                traceback.print_exc()
                print("Tuotetta ei voitu hakea kaupan " + store + " läheltä.")

main()