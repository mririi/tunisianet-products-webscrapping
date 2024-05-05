import time
import requests
from bs4 import BeautifulSoup
import mysql.connector

def save_to_database(products):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="webscrapping"
        )
        cursor = db.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS informations (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), url VARCHAR(255), price VARCHAR(255))")

        for product in products:
            cursor.execute("INSERT INTO informations (name, url, price) VALUES (%s, %s, %s)", (product['name'], product['link'], product['price']))

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
            
            products.append({'name': product_name, 'link': product_link, 'price': price_value})
    else:
        print("Failed to fetch the page.")
    
    return products

products = scrape_aliexpress()
save_to_database(products)
