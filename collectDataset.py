import tweepy
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener


consumer_key = 'AuqelaIt0YLkWC4vToUV8bUMg'
consumer_secret = 'SECNwzCczYbJlIAnxUyfd0ytDDCq2o4Fsr1ZGTMLdCskCxYwPm'
access_token = '147892105-88JainiSiKVksISvRRBvwucpASZsfHKycnwEKWXU'
access_secret = 'nGcAuRx6YAg405JSb6sV1SjkydONgg8H97IGAygvFvt1f'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)
query = '@awkarin'
max_tweets = 500
searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]
for tweet in searched_tweets:
    print (tweet)

with open('result.json', 'wb') as f:
    for tweet in searched_tweets:
        f.write(tweet.text.encode('utf-8'))
