from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time

class ProductScraper:
    def __init__(self,url):
        self.url = url

    def page_scraper(self,sub_url):

        products = []

        req = Request(url=sub_url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = webpage.decode('ISO-8859-1')
        soup = BeautifulSoup(data, 'html.parser')
        product_containers = soup.find_all('div', class_='product-cell-container')

        for product in product_containers:
            # Get product ID
            product_id = product.find('a', class_='absolute-link')['data-ga-product-id']
            
            # Get brand ID
            brand_id = product.find('a', class_='absolute-link')['data-ga-brand-id']
                    
            # Get product brand name
            brand_name = product.find('a', class_='absolute-link')['data-ga-brand-name']
                    
            # Get product price (from data attribute)
            price = product.find('a', class_='absolute-link')['data-ga-discount-price']
                    
            # Get product title
            product_title = product.find('a', class_='absolute-link')['title']
                    
            # Get hyperlink to product
            product_link = product.find('a', class_='absolute-link')['href']

            rating_meta = product.find('meta', itemprop="ratingValue")

            product_rating = rating_meta['content'] if rating_meta else np.nan
            
            count_meta = product.find('meta', itemprop = 'reviewCount')

            review_count = count_meta['content'] if count_meta else 0
                    
            # Append product info to list
            products.append({
                'product_id': product_id,
                'brand_id': brand_id,
                'brand_name': brand_name,
                'product_title': product_title,
                'price': price,
                'rating':product_rating,
                'review_count':review_count,
                'url': product_link
            })

        return products
    
    
    def product_scraper(self):

        products = []

        req = Request(url=self.url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = webpage.decode('ISO-8859-1')
        soup = BeautifulSoup(data, 'html.parser')
        pagination_links = soup.find_all('a',class_='pagination-link')
        last_page_number = pagination_links[-1].find('span').text



        for p in range(1,int(last_page_number)+1):
            print(f"Scraping products from page : {p}.")
            sub_url = f"{self.url}&p={p}"
            products_one_page = self.page_scraper(sub_url)
            time.sleep(1)
            for item in products_one_page:
                products.append(item)
        
        print("Scraping Completed!")

        return products
