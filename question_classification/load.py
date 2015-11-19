#!/usr/bin/python

from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
import numpy as np

# from question import Question

def load_instances(f):
    '''
    Loads data set in file `f`. Returns a list of tuple (label, Question)

    :param f file with data set to load

    Note. The data set has one question per line with format "type text"
    Example. DESC:manner How did serfdom develop in and then leave Russia ?

    '''
    X = []
    y = []

    with open(f, 'r') as file:
        for line in file:
            split_point = line.find(' ')    # find first space
            label = line[0:split_point]
            text = line[split_point+1:].rstrip('\n')

            # X.append(Question(text).features)
            X.append(text)
            y.append(label)

    return np.array(X), np.array(y)

if __name__ == "__main__":
    names = ['1000', '2000', '3000', '4000', '5500']

    dev_X, dev_y = [], []
    test_X, test_y= load_instances('data/TREC_10.label')

    for name in names:
        X, y = load_instances('data/train_{0}.label'.format(name))
        dev_X += X
        dev_y += y

    models = [SVC(), MultinomialNB()]

    # fit each model
    for model in models:
        model.fit(dev_X, dev_y)

        predicted = model.predict(test_X)
        print np.mean(predicted == test_y)
