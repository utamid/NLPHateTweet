#!/usr/bin/python3
from preprocess import stripUnused, getSubject, getTweetsOnly, load_data
from pprint import pprint
import json, re, string
import nltk
from nltk.corpus import sentiwordnet

def preprocess(tweet_texts):
    subjects = getSubject(tweet_texts)
    tweet_texts = stripUnused(tweet_texts)
    tweets_tokens = [nltk.word_tokenize(tweet) for tweet in tweet_texts]
    tweets_tokens = [remove_stopwords(tweet) for tweet in tweets_tokens]
    tweets_tokens = [remove_punctuation(tweet) for tweet in tweets_tokens]
    # pprint(tweets_tokens)
    return tweets_tokens, subjects

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

def find_all_score(tweets_tokens):
    tagged_tweets = [nltk.pos_tag(stoken) for stoken in tweets_tokens]
    score = [find_sentence_score(tokens) for tokens in tagged_tweets]

    return score

def find_sentence_score(tokens):
    wnl = nltk.WordNetLemmatizer()

    sentence_score = []
    for token, tag in tokens:
        newtag = ''
        if tag.startswith('NN'):
            newtag = 'n'
        elif tag.startswith('JJ'):
            newtag = 'a'
        elif tag.startswith('V'):
            newtag = 'v'
        elif tag.startswith('R'):
            newtag = 'r'

        if (newtag != ''):
            lemmatized = wnl.lemmatize(token)
            synsets = list(sentiwordnet.senti_synsets(lemmatized, newtag))
            score = 0
            if(len(synsets)>0):
                for syn in synsets:
                    score += syn.pos_score()-syn.neg_score()
                sentence_score.append((token, score/len(synsets)))

    return sentence_score


def get_features(data, tweets_tokens):
    data_class = []
    all_scores = find_all_score(tweets_tokens)
    # pprint(all_scores)

    data_features = []
    for data, sentence_score in zip(data, all_scores):
        if (len(sentence_score) > 0):
            # pprint(sentence_score)
            n_neg = sum(y < 0 for x, y in sentence_score)
            most_neg = min(sentence_score, key = lambda x: x[1])
            sum_score = sum(y for x, y in sentence_score)

            data_features.append({
                "most_neg_word": most_neg[0] if most_neg[1] < 0 else '',
                "n_neg": n_neg,
                "n_non_neg": len(sentence_score) - n_neg,
                "sum_score": sum_score,
                "avg_score": sum_score/len(sentence_score),
            })
            data_class.append(data['is_hate'])

    return data_features, data_class

if __name__ == '__main__':
    json_data = load_data('data.json')
    # pprint(json_data)
    tweet_text = getTweetsOnly(json_data)
    tweets_tokens, subjects = preprocess(tweet_text)
    # print(tweet_text)
    # print(subjects)
    data_features, data_class = get_features(json_data, tweets_tokens)
    pprint([(f, c) for f, c in zip(data_features, data_class)])
