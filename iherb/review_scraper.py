from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import numpy as np
import time


class ReviewScraper:
    """
    Scrapes the reviews of a product from iHerb.
    """

    def __init__(self,url,product_id):
        """
        url: The homepage of the product containing "/pr/" in URL.
        product_id: The id of the product, which is usually the number at the end of the URL.
        """

        # from the product homepage to the review page
        self.url = url.replace("/pr/","/r/")+"?sort=6&isshowtranslated=true"
        self.product_id = product_id

    def page_scraper(self,sub_url):
        """
        Scrapes the reviews on one page.
        sub_url: the link that contains the page number (&p=?)
        """
        reviews = []

        # scrape the page
        req = Request(url=sub_url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')

        if not soup:
            print(f'Failed to parse the page: {sub_url}')
            return reviews
        
        # get key elements
        date_posted = soup.find_all('span', class_='MuiTypography-root MuiTypography-body2 css-1fktd33', attrs={'data-testid':'review-posted-date'})
        review_title = soup.find_all('span', class_='MuiTypography-root MuiTypography-body1 css-1dbe95',attrs={'data-testid': 'review-title'})
        review_text = soup.find_all('p', class_='MuiTypography-root MuiTypography-body1 css-1id4t2s')

        date_format = date_format = "%b %d, %Y"

        # save to list of dictionaries including reviews on one page
        for i in range(len(review_text)):

            reviews.append({
                'product_id': self.product_id,
                'date_posted':datetime.strptime(date_posted[i].text.replace('Posted on ',''),date_format),
                'review_title':review_title[i].text,
                'review_text':review_text[i].text
            })

        return reviews
    
    def review_scraper(self,last_page_number):
        """
        Scrapes all the pages of the product
        """
        reviews = []

        # go through each page
        for p in range(1,last_page_number+1):

            sub_url = f"{self.url}&p={p}" # generate the sub_url

            print("Scraping reviews from product_id = ",self.product_id,". Page = ", p, ".")
            reviews_one_page = self.page_scraper(sub_url) # scrape on one page
            time.sleep(1) # rate limiting control

            # go through list of dictionaries
            for review in reviews_one_page:
                reviews.append(review) # generate a list of dictionary with all reviews of the product

        return reviews


#if __name__ == '__main__':

#    products = pd.read_csv('./passionflower_products_iherb.csv')

    # get the product ID from the user
#    product_id = int(input('Product ID : '))

    # check if the ID is in products table
#    if not product_id in products['product_id'].values:
#        print(f'Product ID : {product_id} does not exist!')
#    else:
        # get product url and title from table
#        product_url = products[products['product_id']==product_id]['link'].values[0]
#        product_title = products[products['product_id']==product_id]['product_title'].values[0]

        # display the info for double check (for the users)
#        print(f'Product ID : {product_id}. Title : {product_title}.')

        # get the last page number from the user
#        p = int(input("Enter last page number : "))

        # start web scraping
#        reviews = ReviewScraper(product_url,product_id).review_scraper(p)

#        df = pd.DataFrame(reviews)

#        df.to_csv(f'./reviews/{product_id}_reviews.csv',index = True)

#        print('Scraping Finished!')


