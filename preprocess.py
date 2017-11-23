#!/usr/bin/python3
import json
import string
import re
from pprint import pprint
import nltk

def getTweetsOnly(json_data):
    """
    Return list of tweets from json file
    """
    tweets = []
    for tweet in json_data:
        tweets.append(tweet['text'])
    return tweets

def load_data(filename):
    """
    Return list of tweets from json file
    """
    with open(filename, 'r') as f:
        data = json.loads(f.read())
    return data

def separateTweets(json_data):
    hate = []
    nothate = []
    for tweets in json_data:
        tweet_data = {}
        tweet_data["is_hate"] = tweets["is_hate"]
        tweet_data["subject"] = []
        tweet_data["text"] = tweets["text"]
        if tweets["is_hate"] == True:
            hate.append(tweet_data)
        else:
            nothate.append(tweet_data)
    return hate, nothate

def getSubject(json_data):
    """
    Return list of subjects corresponding to tweet (by mention)
    Example:
    Tweet1: "@user1 @user2 how are you?"
    Tweet2: "@user3 I'm peachy"
    Subject: [[user1, user2], [user3]]
    """
    for tweets in json_data:
        mentioned = []
        words = tweets["text"].split(' ')
        for word in words:
            if (word != ''):
                if (word[0] == "@"):
                    mentioned.append(word[1:])
        tweets["subject"] = mentioned
    return json_data

def stripUnused(json_data):
    """
    Strip emoji, hashtags, mentions, numbers, and URL from tweets
    """

    new_tweet = ""
    printable = set(string.printable)
    for tweets in json_data:
        new_tweet = tweets["text"]
        new_tweet = ''.join(filter(lambda x: x in printable, new_tweet))
        new_tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', new_tweet)
        new_tweet = re.sub(r'\\ud...', '', new_tweet)
        new_tweet = re.sub(r'\n', '', new_tweet)
        new_tweet = re.sub(r'\"', '', new_tweet)
        new_tweet = re.sub(r'\#(\S)*', '', new_tweet)
        new_tweet = re.sub(r'@(\S)*', '', new_tweet)
        new_tweet = re.sub(r'(\d)*', '', new_tweet)
        tweets["text"] = new_tweet
    return json_data

def removeWhitespace(json_data):
    for tweets in json_data:
        tweets["text"] = tweets["text"].strip()
    return json_data

def onlyLetters(text):
    return ''.join(filter(str.isalpha, text))

def filterSpam(json_data):
    """
    Filter spam tweet (e.g. Only emoji tweet) from list of tweets
    """
    for idx, tweets in enumerate(json_data):
        if onlyLetters(tweets["text"]).len() == 0:
            del json_data[idx]
    return json_data

def remove_stopwords(tweet_tokens):
    english_stopwords = nltk.corpus.stopwords.words('english')
    result = [token for token in tweet_tokens if token not in english_stopwords]
    return result

def remove_punctuation(tweet_tokens):
    regex = re.compile('[%s]' % re.escape(string.punctuation))

    result = []
    for token in tweet_tokens:
        token = regex.sub('', token)
        if (token):
            result.append(token)
    return result

def prepre(json_data):
    for tweets in json_data:
        tweet_tokens = nltk.word_tokenize(tweets["text"])
        tweet_tokens = remove_stopwords(tweet_tokens)
        tweet_tokens = remove_punctuation(tweet_tokens)
        tweets["text"] = " ".join(tokens for tokens in tweet_tokens)
    return json_data

def doPreprocess(filename):
    json_data = load_data(filename)
    hate_data, nonhate_data = separateTweets(json_data)
    hate_data = getSubject(hate_data)
    nonhate_data = getSubject(nonhate_data)
    hate_data = stripUnused(hate_data)
    nonhate_data = stripUnused(nonhate_data)
    hate_data = removeWhitespace(hate_data)
    nonhate_data = removeWhitespace(nonhate_data)
    hate_data = prepre(hate_data)
    nonhate_data = prepre(nonhate_data)
    return hate_data, nonhate_data

def separateBySubject(json_data, username, filename):
    data = []
    for tweets in json_data:
        if (username in tweets["subject"]):
            data.append(tweets)

    with open(filename, 'wb') as f:
        f.write(json.dumps(data, indent=2).encode('utf-8'))

def transformContracted(tweets):
    """
    Transform contracted form to its original word, e.g. isn't to is not, he's to he is
    """
    # for tweet in tweets:
    #     words = tweet.split(' ')
    #     if ("'").in(word):


"""
TO DO:
Slang words transformation
"""
if __name__ == '__main__':
    filename = "readable_data.json"
    hate_data, nonhate_data = doPreprocess(filename)
    # print json.dumps(hate_data, indent=2).encode('utf-8')
    # print json.dumps(nonhate_data, indent=2).encode('utf-8')
    targets = ['realDonaldTrump', 'pewdiepie','BarackObama', 'MichelleObama', 'IvankaTrump', 'justinbieber']
    for target in targets:
        nonhate_file = target + "-nonhate.json"
        hate_file = target + "-hate.json"
        separateBySubject(hate_data, target, hate_file)
        separateBySubject(nonhate_data, target, nonhate_file)
    # json for all username
    with open("all-hate.json", 'wb') as f:
        f.write(json.dumps(hate_data, indent=2).encode('utf-8'))
    with open("all-nonhate.json", 'wb') as f:
        f.write(json.dumps(nonhate_data, indent=2).encode('utf-8'))
