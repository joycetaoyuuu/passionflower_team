from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import os


folder_path = './reviews'
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

sid = SentimentIntensityAnalyzer()

for file in csv_files:
    product_id = file.split('_')[0]
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['review_text'])

    df['scores'] = df['review_text'].apply(lambda text: sid.polarity_scores(str(text)))
    
    df['compound'] = df['scores'].apply( lambda score_dict: score_dict['compound']) 
    df['sentiment'] = df['compound'].apply(lambda c: 'pos' if c >= 0.05 else ('neg' if c <= -0.05 else 'neu'))

    df.to_csv(f'./reviews_with_sentiment/{product_id}_reviews_with_sentiment.csv')