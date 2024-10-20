from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time

class ProductScraper:
    """
    Scrapes products for a given keyword on iHerb.
    """
    def __init__(self,url):
        """
        url: The url from the search page with format "https://www.iherb.com/search?kw=(keyword)"
        """
        self.url = url

    def page_scraper(self,sub_url):
        """
        Scrapes products on one page
        sub_url: the sub url from search page with format "https://www.iherb.com/search?kw=(keyword)&p=(page_number)"
        """

        products = []

        # Open the URL
        req = Request(url=sub_url, headers={'User-Agent': 'Mozilla/5.0'})
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
                    
            # add to list
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
        """
        Scrapes all pages given a key word
        """

        products = []

        # Open the URL
        req = Request(url=self.url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = webpage.decode('ISO-8859-1')
        soup = BeautifulSoup(data, 'html.parser')

        # Get the total page number
        pagination_links = soup.find_all('a',class_='pagination-link')
        last_page_number = pagination_links[-1].find('span').text

        # Go through each page number
        for p in range(1,int(last_page_number)+1):
            print(f"Scraping products from page : {p}.")
            sub_url = f"{self.url}&p={p}"
            products_one_page = self.page_scraper(sub_url)
            time.sleep(1) # add rate control to avoid error

            for item in products_one_page:
                products.append(item) # add each product (in the format of dictionary) to a list
        
        print("Scraping Completed!")

        return products
