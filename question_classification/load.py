#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import accuracy_score

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline

import numpy as np

from question import Question, Label

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

            labels.append(Label(label).coarse)
            questions.append(Question(text).normalized_text)

    return labels, questions


def feature_vector(data, fit=False):
    '''Creates a feature vector from a dictionary of Question'''
    if fit:
        return dictVectorizer.fit_transform([d.features() for d in data])
    else:
        return dictVectorizer.transform([d.features() for d in data])

if __name__ == "__main__":
    dev_filename = 'data/train_5500.label'
    test_filename = 'data/TREC_10.label'

    # Load the data set [(label, question)]

    dev_labels, dev_questions = load_instances(dev_filename)
    test_labels, test_questions = load_instances(test_filename)

    dev = {'data': dev_questions, 'target': dev_labels}
    test = {'data': test_questions, 'target': test_labels}

    parameters = {'vect__ngram_range': [(1,1), (1,2)],
                  'vect__stop_words': ('english', None),
                  'tfidf__use_idf': (True, False),
                  'tfidf__norm': ('l1', 'l2'),
                  'clf__alpha': (1e-3, 1e-4, 2e-4, 3e-4),
                  'clf__loss': ('hinge', 'modified_huber', 'log', 'squared_hinge', 'perceptron'),
    }

    # TODO when writing the report, see http://scikit-learn.org/stable/tutorial/machine_learning_map/index.html
    # for explanation on model used

    text_clf = Pipeline([('vect', CountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         ('clf', SGDClassifier(n_iter=15, shuffle=True, n_jobs=-1)),
                         ])
    gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
    _ = gs_clf.fit(dev['data'], dev['target'])
    predicted = gs_clf.predict(test['data'])

    best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])
    for param_name in sorted(parameters.keys()):
        print "{0}: {1}".format(param_name, best_parameters[param_name])

    print score
