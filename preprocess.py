import json
import string
import re

def getTweetsOnly(json_file):
    """
    Return list of tweets from json file
    """
    tweets = []
    with open(json_file, 'r') as f:
        data = json.loads(f.read())
        for tweet in data:
            tweets.append(tweet["text"].encode('utf-8'))
    return tweets

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
    Strip emoji, and URL from tweets
    """
    new_tweets = []
    printable = set(string.printable)
    for tweet in tweets:
        tweet = ''.join(filter(lambda x: x in printable, tweet))
        tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', tweet)
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

"""
TO DO:
Slang words transformation
"""
s = ["@Hehe @Hello hello guys http://heello.com \ud83d\udc9c", "@You aiiiihui"]
subjects = getSubject(s)
print subjects
t = stripMentioned(s)
print t
v = filterSpam(t)
print v
