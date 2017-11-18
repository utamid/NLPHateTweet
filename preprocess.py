#!/usr/bin/python3
import json
import string
import re
from pprint import pprint

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
    with open(json_file, 'r') as f:
        data = json.loads(f.read())
    return data

def getSubject(tweets):
    """
    Return list of subjects corresponding to tweet (by mention)
    Example:
    Tweet1: "@user1 @user2 how are you?"
    Tweet2: "@user3 I'm peachy"
    Subject: [[user1, user2], [user3]]
    """
    subjects = []
    for tweet in tweets:
        mentioned = []
        words = tweet.split(' ')
        for word in words:
            if (word != ''):
                if (word[0] == "@"):
                    mentioned.append(word[1:])
        subjects.append(mentioned)
    return subjects

def stripMentioned(tweets):
    """
    Strip mentioned users
    """
    new_tweets = []
    for tweet in tweets:
        new_tweet = tweet
        words = tweet.split(' ')
        for idx, word in enumerate(words):
            if (word != ''):
                if (word[0] == "@"):
                    strreplace = ''
                    if (idx == len(words)):
                        strreplace = ' ' + word
                    else:
                        strreplace = word + ' '
                    new_tweet = new_tweet.replace(strreplace, '')
        new_tweets.append(new_tweet)
    return new_tweets

def stripUnused(tweets):
    """
    Strip emoji, hashtags, mentions, numbers, and URL from tweets
    """
    new_tweets = []
    printable = set(string.printable)
    for tweet in tweets:
        tweet = ''.join(filter(lambda x: x in printable, tweet))
        tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', tweet)
        tweet = re.sub(r'\\ud...', '', tweet)
        tweet = re.sub(r'\#(\S)*', '', tweet)
        tweet = re.sub(r'@(\S)*', '', tweet)
        tweet = re.sub(r'(\d)*', '', tweet)
        new_tweets.append(tweet)
    return new_tweets

def onlyLetters(text):
    return ''.join(filter(str.isalpha, text))

def filterSpam(tweets):
    """
    Filter spam tweet (e.g. Only emoji tweet) from list of tweets
    """
    non_spam_tweets = []
    for tweet in tweets:
        if onlyLetters(tweet).len() > 0:
            non_spam_tweets.append(tweet)
    return non_spam_tweets

def transformContracted(tweets):
    """
    Transform contracted form to its original word, e.g. isn't to is not, he's to he is
    """
    # for tweet in tweets:
    #     words = tweet.split(' ')
    #     if ("'").in(word):

def load_data(filename):
    with open(filename, 'r') as fin:
        data = json.loads(fin.read())

    return data

"""
TO DO:
Slang words transformation
"""
if __name__ == '__main__':
    s = ["@Hehe @Hello hello guys http://heello.com #test 667\ud83d\udc9c", "@You aiiiihui @haha"]
    data = load_data('data.json')
    s = getTweetsOnly(data)
    subjects = getSubject(s)
    # print t
    t = stripUnused(s)
    pprint(t)
