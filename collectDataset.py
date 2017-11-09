import tweepy
from tweepy import OAuthHandler
 
consumer_key = 'IjuTVCVVxNIlLivYDVyvNPIqB'
consumer_secret = 'gg6hT2pV4pIMT4yvn99PaBA5YSCC2oGRsR3v9ssfuZA8WYoU1c'
access_token = '2751957908-u1ju4PWIQTVoqdl1CS0NHm638BsUWomhwwrLD0X'
access_secret = 'qzBiIyzo2aRReKlUbg0bVjm2pu0B4cNglz0XWhfY935na'
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

# Read my own timeline
for status in tweepy.Cursor(api.home_timeline).items(10):
    # Process a single status
    print(status.text)

from tweepy import Stream
from tweepy.streaming import StreamListener
 
class MyListener(StreamListener):
 
    def on_data(self, data):
        try:
            with open('python.json', 'a') as f:
                f.write(data)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
 
    def on_error(self, status):
        print(status)
        return True
 
twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(track=['awkarin'])