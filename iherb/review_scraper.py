from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
import math



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
        

    def page_scraper(self,sub_url):
        """
        Scrapes the reviews on one page.
        sub_url: the link that contains the page number (ending with &p=?)
        """
        reviews = [] # save reviews

        max_retries = 5 # set a maximum number of retries

        for attempt in range(max_retries):
            try:

                # Open the URL
                req = Request(url=sub_url, headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                soup = BeautifulSoup(webpage, 'html.parser')
                
                # get elements needed from the URL (review date, review title, and review text)
                date_posted = soup.find_all('span', class_='MuiTypography-root MuiTypography-body2 css-1fktd33', attrs={'data-testid':'review-posted-date'})
                review_title = soup.find_all('span', class_='MuiTypography-root MuiTypography-body1 css-1dbe95',attrs={'data-testid': 'review-title'})
                all_comments = soup.find_all('p', class_='MuiTypography-root MuiTypography-body1 css-1id4t2s')

                # get the customer service comments
                customer_service_tags = soup.find_all('a',class_='MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineNone css-7ouxk9')
                customer_service_comments = [cs_tag.find_next('p') for cs_tag in customer_service_tags]

                # filter the customer service comments out, and keep customer reviews only
                review_text = [c for c in all_comments if c not in customer_service_comments]

                date_format = "%b %d, %Y"

                # save to list of dictionaries including reviews on one page
                for i in range(len(review_text)):

                    reviews.append({
                        'product_id': self.product_id, # save product_id
                        'date_posted':datetime.strptime(date_posted[i].text.replace('Posted on ',''),date_format), # save review date (in date format)
                        'review_title':review_title[i].text, # save title
                        'review_text':review_text[i].text # save text
                    })

                return reviews
            
            except (HTTPError,URLError) as e: # take a break if error occurs then retry
                print(f"Attempt {attempt+1} failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

        print("Max retries reached. Could not scrape the page.")
        return reviews

    
    def review_scraper(self,begin_page = 1,end_page = None):
        """
        Scrapes all the pages of the product
        """

        if end_page is None:
            end_page = self.get_last_page()

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
    
    def get_last_page(self):
        df = pd.read_csv('./passionflower_products_iherb.csv',index_col = 0)
        review_count = df[df['product_id']==self.product_id]['review_count'].values[0]
        last_page_number = math.ceil(review_count/10)

        return last_page_number




