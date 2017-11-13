import tweepy
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import pprint
import json

consumer_key = 'AuqelaIt0YLkWC4vToUV8bUMg'
consumer_secret = 'SECNwzCczYbJlIAnxUyfd0ytDDCq2o4Fsr1ZGTMLdCskCxYwPm'
access_token = '147892105-88JainiSiKVksISvRRBvwucpASZsfHKycnwEKWXU'
access_secret = 'nGcAuRx6YAg405JSb6sV1SjkydONgg8H97IGAygvFvt1f'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

queries = ['@awkarin', '@realDonaldTrump', '@pewdiepie','@BarackObama', '@MichelleObama', '@IvankaTrump', '@justinbieber']

total_data = 0
for query in queries:
    max_tweets = 250
    searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]
    with open('data.json', 'r') as fin:
        data = json.loads(fin.read())

    for tweet in searched_tweets:
        if (tweet.lang == 'en' and 'RT' not in tweet.text):
            data.append({
                'text': tweet.text,
                'time': str(tweet.created_at),
                'username': tweet.user.screen_name,
                'full_name': tweet.user.name,
                'lang': tweet.lang,
                'is_hate': False,
            })

    pprint.pprint(data)
    total_data = len(data)
    with open('data.json', 'wb') as f:
        f.write(json.dumps(data).encode('utf-8'))

print(total_data)
