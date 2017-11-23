import sys
import random
import re
import tarfile
import operator
import os
import json
import string
try:
    from svmutil import *
except ImportError:
    print "Could not find LIBSVM.  Please download here: http://bit.ly/2rwxl"

HATE_FILES = ['all-hate.json']
NONHATE_FILES = ['all-nonhate.json']

class TweetSentiment:

    def __init__(self, options=None):
        self.hate = {}
        self.nothate = {}
        self.common = {}
        self.svm_features = []
        self.tweets = []
        self.prob_hate = 0.38
        # SVM Feature options
        self.svm_prob_threshold = 0.3         # Before considering feature significant
        self.svm_count_threshold = 30         # Number of times string appears

        # Auto-learning options
        self.auto_learn = True
        self.taoplus = 0.98           # Threshold for exemplar spam for auto-learning
        self.taominus = 0.05          # Threshold for exemplar ham for auto-learning

        # Stats
        self.exemplar_spam = 0
        self.exemplar_ham = 0
        self.false_positives = 0
        self.true_positives = 0
        self.false_negatives = 0
        self.true_negatives = 0

        self.cutoff = 0.75      # Cutoff for classifying as spam (higher, fewer false positive)
        self.count_threshold = 20   # Number of times token appears to be relevant
        self.size_threshold = 6     # The token '1c' is less significant then 'einstein'
        self.unique_threshold = 3   # Unique characters in string ('qqqq' => 1)
        self.prob_threshold = 0.1   # Before considering token significant
        self.lower = False          # Whether or not to normalize to all lowercase

    def _error(self, data, classifier):
        """ Returns the error rate of a classifier on training or development data """
        errors = 0
        for X,y in data:
            c = classifier(X)
            if c != y:
                errors += 1
            if c and not y:
                self.false_positives += 1
            elif c and y:
                self.true_positives += 1
            elif not c and y:
                self.false_negatives += 1
            elif not c and not y:
                self.true_negatives += 1

        return errors/float(len(data))

    def load_corpus(self, files, hate=True):
        """
        Loads corpus into the hate or not hate dictionary, as well as a common dictionary
        """
        for fname in files:
            if os.path.exists(fname):
                path_to_file = fname
            else:
                print "file doesn't exist"
                return

            with open(path_to_file) as f:
                contents = json.loads(f.read())
                for content in contents:
                    if hate:
                        self.tweets.append((content["text"], 1))
                    else:
                        self.tweets.append((content["text"], 0))

        print "done, read %d tweets." % len(self.tweets)

    def _parse_tweet(self, table, content):
        """ Parse tweet, adding tokens to appropriate dictionary """
        tokens = content.split(' ')
        for t in tokens:
            if t not in table:
                table[t] = 0
            table[t] += 1
            if t not in self.common:
                self.common[t] = 0
            self.common[t] += 1

    def train_data(self, training_percent=33.0):
        N = len(self.tweets)
        training_indices = set(random.sample(range(N), \
                                             int(N*training_percent/100.0)))
        self.training = []
        self.development = []
        for i in range(N):
            if i in training_indices:
                self.training.append(self.tweets[i])
            else:
                self.development.append(self.tweets[i])
        for tweet in self.training:
            if tweet[1]:
                # Add words to spam dictionary
                self._parse_tweet(self.hate, tweet[0])
            else:
                # Add words to ham dictionary
                self._parse_tweet(self.nothate, tweet[0])

    def calculate_probability_hate(self, token):
        """
        Calculate Bayesian probability of hate tweet given token, P(S|w), meeting minimum criteria
        P(S|w) = P(w|S)*P(S) / [ P(w|S)*P(S) + P(w|H)*P(H) ]
        """
        if len(token) >= self.size_threshold and len(set(token)) > self.unique_threshold:
            # Use Laplace (additive) smoothing with k=1, if feature not found
            b = self.hate[token] if token in self.hate else 1
            g = self.nothate[token] if token in self.nothate else 1
            if b+g > self.count_threshold:
                numerator = b * 1.0 / len(self.hate) * self.prob_hate
                denominator = b * 1.0 / len(self.hate) * self.prob_hate + \
                              g * 1.0 / len(self.nothate) * (1. - self.prob_hate)

                phate_word = numerator / denominator
                if abs(0.5 - phate_word) > self.prob_threshold:
                    return (token, phate_word, b + g)
        return None

    def _set_svm_features(self):
        """ Get SVM features """
        for token in self.common:
            probability_hate = self.calculate_probability_hate(token)
            if  probability_hate \
                and probability_hate[2] >= self.svm_count_threshold \
                and abs(0.5 - probability_hate[1]) >= self.svm_prob_threshold:
                # Limit the number of SVM features, for a quicker build
                self.svm_features.append(token)

    def _get_svm_classifier(self, data, options='-c 1 -t 0'):
        """ Returns SVM classifer based on svmlib model """

        labels = [y for (X,y) in data]
        samples = [X for (X,y) in data]

        # Return classification value for testing
        svm_model.predict = lambda self, x: svm_predict([0], [x], self, '-q')[0][0]
        problem = svm_problem(labels, samples)
        param = svm_parameter(options)
        model = svm_train(problem, param)
        return model.predict

    def _build_svm_features(self, tweets):
        """
        Builds a binary feature vector where each feature is 1 if the corresponding
        dictionary words is in the review, 0 if not.
        """
        features = []
        tweets_tokens = tweets.split(' ')
        for token in self.svm_features:
            if token in tweets_tokens:
                features.append(1)
            else:
                features.append(0)
        return features

    def print_strong_words(self):
        """ Prints the most significant words, indicating hate or not hate """
        strong_words = []
        for token, value in self.common.items():
            probability_hate = self.calculate_probability_hate(token)
            if probability_hate:
                strong_words.append(probability_hate)
        strong_words.sort(key=operator.itemgetter(1))
        print "\nTop words most likely to be hate:"
        for s in strong_words[:-10:-1]:
            print "%s = %f, %d occurrences" % (s[0], s[1], s[2])
        print "\nTop words least likely to be hate:"
        for s in strong_words[:10]:
            print "%s = %f, %d occurences" % (s[0], s[1], s[2])

    def print_stats(self):
        if not self.tweets or not self.hate or not self.nothate:
            print "Error.  Insufficient tweet data found."
            return
        self.num_hate = [i[1] for i in self.tweets].count(1)
        print "Read %d tweets," % len(self.tweets),
        print "{:.2%} hate ".format(self.num_hate * 1.0 / len(self.tweets))
        self.print_strong_words()
        print "\nVariables:"
        print "tao- = %f" % self.taominus
        print "tao+ = %f" % self.taoplus
        print "Prob(Hate) = %f" % self.prob_hate
        print "Hate cutoff = %f" % self.cutoff
        print "Count minimum = %d" % self.count_threshold
        print "\n########################################################"
        self._set_svm_features()
        print "SVM (%d features):" % len(self.svm_features)
        print "Building training samples..."
        training_samples = [(self._build_svm_features(self.tweets[0]), self.tweets[1]) \
                            for tweets in self.training]
        print training_samples
        classify_svm = self._get_svm_classifier(training_samples, options='-c 1 -t 0')
        print "Training error:", self._error(training_samples, classify_svm)
        print "Building development samples..."
        development_samples = [(self._build_svm_features(tweets[0]), tweets[1]) \
                            for tweets in self.development]
        print development_samples
        print "development SAMPLES: %d" % len(self.development)
        print "Development error:", self._error(development_samples, classify_svm)
        print "False positives = %.3f%%" % \
                (self.false_positives * 1.0 / (self.false_positives + self.true_positives))
        print "False negatives = %.3f%%" % \
                (self.false_negatives * 1.00 / (self.false_negatives + self.true_negatives))
        print "\n" * 5

def main():
    ts = TweetSentiment()
    ts.load_corpus(NONHATE_FILES, hate=False)
    ts.load_corpus(HATE_FILES, hate=True)
    ts.train_data(training_percent=80)
    ts.print_stats()

if __name__=="__main__":
    main()
    sys.exit()
