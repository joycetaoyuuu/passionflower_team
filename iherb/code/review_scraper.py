from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import numpy as np
import time
import math
import json



class ReviewScraper:
    """
    Scrapes the reviews of a product from iHerb.
    """

    def __init__(self,url,product_id):
        """
        url: The homepage of the product containing "/pr/" in URL.
        product_id: The id of the product, which is usually the number at the end of the URL.
        """

        # modify the url from the product homepage to the review page
        self.url = url.replace("/pr/","/r/")+"?sort=6&isshowtranslated=true"
        self.product_id = product_id
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36','Accept-Language': 'en-US,en;q=0.9','Referer': 'https://www.google.com/'}
        

    def page_scraper(self,sub_url):
        """
        Scrapes the reviews on one page.
        sub_url: the link that contains the page number (ending with &p=?)
        """
        saved_reviews = [] # save reviews

        max_retries = 5 # set a maximum number of retries

        for attempt in range(max_retries):
            try:

                # Open the URL

                req = Request(url=sub_url, headers=self.headers)
                webpage = urlopen(req).read()
                soup = BeautifulSoup(webpage, 'html.parser')

                review_script = soup.find('script', {'id': 'reviews-schema'})
                reviews_data = json.loads(review_script.string).get('review',[])

                for r in reviews_data:
                    date_posted = r.get("datePublished").strip() or np.nan 
                    review_title = r.get("name","") or np.nan
                    review_text = r.get("reviewBody").strip() or np.nan
                    rating = r.get("reviewRating", {}).get("ratingValue", "") or np.nan
                     
                    saved_reviews.append({
                        'product_id' : self.product_id,
                        'date_posted' : datetime.strptime(date_posted,"%b %d, %Y").date(),
                        'review_title' : review_title,
                        'review_text' : review_text,
                        'rating' : rating
                        })
                    
                
                return saved_reviews
            
            except (HTTPError,URLError) as e: # take a break if error occurs then retry
                print(f"Attempt {attempt+1} failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

        print("Max retries reached. Could not scrape the page.")
        return saved_reviews

    
    def review_scraper(self,begin_page = 1,end_page = None):
        """
        Scrapes all the pages of the product
        """

        if end_page is None:
            end_page = self.get_last_page(self.url)

        reviews = []

        # go through each page
        for p in range(begin_page,end_page+1):

            sub_url = f"{self.url}&p={p}" # generate the sub_url

            print(f"Scraping reviews from product_id = {self.product_id}. Page = {p} / {end_page}.")

            reviews_one_page = self.page_scraper(sub_url)

            time.sleep(1) # rate limiting control

            # go through list of dictionaries
            for review in reviews_one_page:
                reviews.append(review) # generate a list of dictionary with all reviews of the product

        return reviews
    
    def get_last_page(self,url):
        req = Request(url=url, headers=self.headers)
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')
        reviews_script = soup.find('script', {'id': 'reviews-schema'})
        review_count = json.loads(reviews_script.string).get('aggregateRating').get('reviewCount')

        last_page_number = math.ceil(int(review_count)/10)

        return last_page_number




