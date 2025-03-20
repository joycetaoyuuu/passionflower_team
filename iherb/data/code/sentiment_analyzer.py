from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import os


folder_path = './reviews'
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

sid = SentimentIntensityAnalyzer()

for file in csv_files:
    product_id = file.split('_')[0]

    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path,index_col=0)
    df['text'] = df['review_title'].fillna('')+ ' ' + df['review_text'].fillna('')
    df['text'] = df['text'].astype(str)

    df['scores'] = df['text'].apply(lambda text: sid.polarity_scores(text))
    
    df['compound'] = df['scores'].apply( lambda score_dict: score_dict['compound']) 
    df['vader_sentiment'] = df['compound'].apply(lambda c: 'pos' if c >= 0 else 'neg')

    df.to_csv(f'./reviews_with_sentiment/{product_id}_reviews_with_sentiment.csv',index = True)