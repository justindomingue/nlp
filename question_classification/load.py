#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
from sklearn.svm import SVC, LinearSVC
from sklearn.feature_selection import SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

import numpy as np

from question import Question

dictVectorizer = DictVectorizer(sparse=False)
le = LabelEncoder()

def load_instances(f):
    '''
    Loads data set in file `f`. Returns a list of tuple (label, Question)

    :param f file with data set to load

    Note. The data set has one question per line with format "type text"
    Example. DESC:manner How did serfdom develop in and then leave Russia ?

    '''
    labels = []
    questions = []

    with codecs.open(f, 'r', encoding='utf-8') as file:
        for line in file:
            split_point = line.find(' ')    # find first space
            label = line[0:split_point]
            text = line[split_point+1:].rstrip('\n')

            labels.append(label)
            questions.append(Question(text))

    return labels, questions


def feature_vector(data, fit=False):
    '''Creates a feature vector from a dictionary of Question'''
    if fit:
        return dictVectorizer.fit_transform([d.features() for d in data])
    else:
        return dictVectorizer.transform([d.features() for d in data])

if __name__ == "__main__":
    names = ['1000']#, '2000', '3000', '4000', '5500']

    # Load the data set [(label, question)]

    test_labels, test_questions = load_instances('data/TREC_10.label')

    dev_labels, dev_questions = [], []
    for name in names:
        labels, questions = load_instances('data/train_{0}.label'.format(name))
        dev_labels += labels
        dev_questions += questions

    # Make the feature vectors

    le.fit(dev_labels+test_labels)

    dev_y = le.transform(dev_labels)
    test_y = le.transform(test_labels)

    dev_X = feature_vector(dev_questions, fit=True)
    test_X = feature_vector(test_questions, fit=False)

    models = [SVC(), MultinomialNB()]

    print 'EXPERIMENT'
    print 'Development set size: {0}'.format(dev_X.size)
    print 'Test set size: {0}'.format(test_X.size)

    # fit each model
    for model in models:
        model.fit(dev_X, dev_y)

        predicted = model.predict(test_X)
        print(accuracy_score(test_y, predicted))
