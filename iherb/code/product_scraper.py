from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time

class ProductScraper:
    """
    Scrapes products for a given keyword on iHerb.
    """
    def __init__(self):
        """
        url: The url from the search page with format "https://www.iherb.com/search?kw=(keyword)"
        """
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'}

    def product_info_scraper(self,product_url):
        """
        Scrapes product info including product code, upc number, and sales info
        product_url: The homepage url for a product.
        """

        req = Request(url = product_url,headers = self.headers)
        webpage = urlopen(req).read()
        data = webpage.decode('ISO-8859-1')
        soup = BeautifulSoup(data, 'html.parser')
        product_decsription_container = soup.find('section', class_ = 'column product-description-specifications')
        li_elements = product_decsription_container.find_all('li')

        # get product code and upc
        for li in li_elements:
            if "Product code" in li.text:
                product_code = li.find('span').text
            if 'UPC' in li.text:
                upc = li.text.split(': ')[1]

        # get sales info
        sold_info_container = soup.find('div',class_ = 'recent-activity-message')
        sold_info = (sold_info_container.text.split('+')[0].strip()+'+' if sold_info_container else np.nan)

        return (product_code,upc,sold_info)


    def page_scraper(self,sub_url):
        """
        Scrapes products on one page
        sub_url: the sub url from search page with format "https://www.iherb.com/search?kw=(keyword)&p=(page_number)"
        """

        products = []

        # Open the URL
        req = Request(url=sub_url, headers=self.headers)
        webpage = urlopen(req).read()
        data = webpage.decode('ISO-8859-1')
        soup = BeautifulSoup(data, 'html.parser')
        product_containers = soup.find_all('div', class_='product-cell-container')

        # Go through each product

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

            # Get product rating
            rating_meta = product.find('meta', itemprop="ratingValue")
            product_rating = rating_meta['content'] if rating_meta else np.nan
            
            # Get number of reviews
            count_meta = product.find('meta', itemprop = 'reviewCount')
            review_count = count_meta['content'] if count_meta else 0

            product_code,upc,sold_info = self.product_info_scraper(product_link)
                    
            # add to list
            products.append({
                'product_id': product_id,
                'brand_id': brand_id,
                'brand_name': brand_name,
                'product_title': product_title,
                'product_code':product_code,
                'upc':upc,
                'sold_in_30_days': sold_info,
                'price': price,
                'rating':product_rating,
                'review_count':review_count,
                'url': product_link
            })

        return products
    
    
    def product_scraper(self,url):
        """
        Scrapes all pages given a key word
        """

        products = []

        # Open the URL
        req = Request(url=url, headers=self.headers)
        webpage = urlopen(req).read()
        data = webpage.decode('ISO-8859-1')
        soup = BeautifulSoup(data, 'html.parser')

        # Get the total page number
        pagination_links = soup.find_all('a',class_='pagination-link')
        last_page_number = pagination_links[-1].find('span').text

        # Go through each page number
        for p in range(1,int(last_page_number)+1):
            print(f"Scraping products from page : {p}...")
            sub_url = f"{url}&p={p}"
            products_one_page = self.page_scraper(sub_url)
            time.sleep(1) # add rate control to avoid error

            for item in products_one_page:
                products.append(item) # add each product (in the format of dictionary) to a list
        
        print("Scraping Completed!")

        return products
