import time
import requests
from bs4 import BeautifulSoup
import mysql.connector
import re

def extract_memory(name):
    # Regular expression pattern to find storage information
    pattern = r'(\d+)\s*Go'  # Assuming "Go" stands for gigabytes (GB)
    match = re.search(pattern, name)
    if match:
        return match.group(1)  # Extracting the first matched group (storage size in GB)
    else:
        return 0  # Return None if storage information is not found
    
def extract_product_name(name):
    # Regular expression pattern to extract the product name
    pattern = r'Pc Portable (.+?) /'  # Extracts the text between "Pc Portable " and "/"
    match = re.search(pattern, name)
    if match:
        return match.group(1)  # Extracting the matched group (product name)
    else:
        return "Product Name Not Available"
    
def save_to_database(products):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="webscrapping"
        )
        cursor = db.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS informations (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), url VARCHAR(255), price VARCHAR(255), memory VARCHAR(255))")

        for product in products:
            cursor.execute("INSERT INTO informations (name, url, price, memory) VALUES (%s, %s, %s, %s)", (product['name'], product['link'], product['price'], product['memory']))

        db.commit()
        print("Data saved successfully.")
    except mysql.connector.Error as error:
        print("Error saving to database:", error)
    finally:
        cursor.close()
        db.close()

def scrape_aliexpress():
    url = 'https://www.tunisianet.com.tn/301-pc-portable-tunisie'
    response = requests.get(url)
    products = []
    
    if response.status_code == 200:
        html_content = response.text
        
        time.sleep(5)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        product_items = soup.find_all('h2', class_='h3 product-title')
        product_prices = soup.find_all('span', class_='price')
        
        for i in range(len(product_items)):
            product_name_element = product_items[i].find('a')
            product_name = product_name_element.text.strip() if product_name_element else "Product Name Not Available"
            
            product_link_element = product_items[i].find('a')
            product_link = product_link_element.get('href') if product_link_element else "#"
            
            price_text = product_prices[i].text.strip()
            price_value = price_text.replace(' DT', '').replace(',', '')
            name = extract_product_name(product_name)
            memory = extract_memory(product_name)
            products.append({'name': name, 'link': product_link, 'price': price_value, 'memory': memory})
    else:
        print("Failed to fetch the page.")
    
    return products

products = scrape_aliexpress()
save_to_database(products)