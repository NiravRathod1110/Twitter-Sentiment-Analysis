from flask import Flask, render_template, request,send_file
import spacy
import pandas as pd
import tweepy
import matplotlib.pyplot as plt
from textblob import TextBlob
import string

conKey=""
conSecret=""
accKey=""
accSecret=""

authentication = tweepy.OAuthHandler(conKey, conSecret)
authentication.set_access_token(accKey, accSecret)
getAPI = tweepy.API(authentication)

def removePunctuation(tweet):
    return ''.join(character for character in tweet if character not in set(string.punctuation))

def removeStopWords(tweet):
    spac=spacy.load('en_core_web_sm')
    stopWords=spac.Defaults.stop_words
    tweet=tweet.lower()
    tweet = ' '.join([w for w in tweet.split(' ') if w not in stopWords])
    return tweet

def tweetSentimentAnalysis(tweet):
    tb = TextBlob(tweet)
    score = tb.sentiment.polarity
    if score > 0.4:
        return 'Very Positive'
    elif score > 0:
        return 'Less Positive'
    elif score <-0.4:
        return 'Very Negative'
    elif score <0:
        return 'Less Negative'
    else:
        return 'Neutral'
    
db = pd.DataFrame(columns=['username','text',])

def scrapeTweets(ht, ds, numtweet):
    tweets = getAPI.search_tweets(ht, lang="en",
                        since_id=ds,
                        tweet_mode='extended',count=numtweet)

    list_tweets = [tweet for tweet in tweets]
    for tweet in list_tweets:
        username = tweet.user.screen_name
        hashtags = tweet.entities['hashtags']
        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:
            text = tweet.full_text
        hashtext = list()
        for j in range(0, len(hashtags)):
            hashtext.append(hashtags[j]['text'])
        ith_tweet = [username, text]
        db.loc[len(db)] = ith_tweet
        
    db['clean']=db['text'].apply(removePunctuation)
    db['stop_word']=db['clean'].apply(removeStopWords)
    db['sentiment'] = db['stop_word'].apply(tweetSentimentAnalysis)
    db.drop(['clean','stop_word'],axis=1, inplace=True)

app = Flask(__name__)
@app.route('/')
def home():
	return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    if request.method == 'POST':
        hashtag = request.form['hashtag']
        date=request.form['date']
        tweets=request.form['tweets']
        scrapeTweets(hashtag, date, tweets)
        db.to_csv('result.csv',index=False)
        return send_file('result.csv',as_attachment=True)
    return render_template('index.html')
if __name__ == '__main__':
	app.run(debug=True)