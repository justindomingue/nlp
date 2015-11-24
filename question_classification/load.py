#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import accuracy_score, classification_report

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline

import numpy as np

from question import Question, Label


def load_instances(f, head_present=False):
    '''
    Loads data set in file `f`. Returns a list of tuple (label, Question, head) where `head` is optional

    :param f file with data set to load

    Note. The data set has one question per line with format "type text"
    Example. DESC:manner How did serfdom develop in and then leave Russia ?

    '''
    labels = []
    questions = []

    with codecs.open(f, 'r', encoding='ascii') as file:
        for line in file:
            split_point = line.find(' ')    # find first space
            label = line[0:split_point]
            text = line[split_point+1:].rstrip('\n')
            head = None

            if head_present:
                head = text[-1]     # head was extracted before, keep it
                text = text[:-1]

            labels.append(Label(label))
            questions.append(Question(text, head))

    return labels, questions, head


def extract_heads_persistent(labels, questions, filename):
    data = zip([l.coarse for l in labels], [q.text for q in questions], [q.head_word for q in questions])

    name, extension = filename.split('.')
    f = "{0}+heads.{1}".format(name, extension)
    with codecs.open(f, 'w', encoding='ascii') as file:
        for item in data:
            print>>file, item


if __name__ == "__main__":
    dev_filename = 'data/train_5500.label'
    test_filename = 'data/TREC_10.label'

    extract_head = True     # load the question list, and extract heads with persistence
    granularity = 'coarse'
    # granularity = 'fine'

    feature = 'whword+headword'
    # feature = 'wordshape'
    # feature = 'ngram'

    # Load the data set (label, question)
    dev_labels, dev_questions, dev_heads = load_instances(dev_filename)
    test_labels, test_questions, test_heads = load_instances(test_filename)

    dev_target = [l.get(granularity) for l in dev_labels]
    test_target = [l.get(granularity) for l in test_labels]

    # Estimators used in the model pipeline
    estimators = []

    ##########
    # Routine to extra the heads of the questions so they don't need to be extracted every time
    ##########
    if extract_head:
        extract_heads_persistent(dev_labels, dev_questions, dev_filename)
        extract_heads_persistent(dev_labels, test_questions, test_filename)
        exit()

    ############
    # wh-word + head word
    ############
    if feature == 'whword+headword':
        print 'Evaluating individual contribution of WH-WORD + HEAD WORD'
        estimators = [('dictvect', DictVectorizer())]
        dev  =  {'data': [{'wh-word': q.type, 'head-word': q.head_word} for q in dev_questions], 'target': dev_target}
        test =  {'data': [{'wh-word': q.type, 'head-word': q.head_word} for q in test_questions], 'target': test_target}

    exit()
    #############
    # word shape: convert word shape to string and use count vectorizer
    #############
    if feature == 'wordshape':
        print 'Evaluating individual contribution of WORD SHAPE'
        estimators = [('countvect', CountVectorizer()),('tfidf', TfidfTransformer())]
        # dev  =  {'data': [' '.join(q.word_shape) for q in dev_questions], 'target': dev_target}
        # test =  {'data': [' '.join(q.word_shape) for q in test_questions], 'target': test_target}

    #############
    # n-grams
    #############
    if feature == 'ngram':
        print 'Evaluating individual contribution of N-GRAMS'
        estimators = [('countvect', CountVectorizer()),('tfidf', TfidfTransformer())]
        # dev = {'data': [q.normalized_text for q in dev_questions], 'target': dev_target}
        # test = {'data': [q.normalized_text for q in test_questions], 'target': test_target}

    #############
    # Count vectorizer
    #############

    parameters = {'countvect__ngram_range': [(1,1), (1,2), (1,3), (1,4), (1,5)],
                  'countvect__stop_words': ('english', None),
                  'tfidf__use_idf': (True, False),
                  'tfidf__norm': ('l1', 'l2'),
                  'clf__alpha': (1e-1, 1e-2),#, 1e-3, 1e-4),
                  'clf__loss': ('hinge', 'modified_huber')#, 'log', 'squared_hinge', 'perceptron'),
    }

    # TODO when writing the report, see http://scikit-learn.org/stable/tutorial/machine_learning_map/index.html
    # for explanation on model used
    text_clf = Pipeline(estimators + [('clf', SGDClassifier(shuffle=True, n_jobs=-1, verbose=1))] )
    gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
    _ = gs_clf.fit(dev['data'], dev['target'])
    predicted = gs_clf.predict(test['data'])

    print accuracy_score(test["target"], predicted)
    print classification_report(test["target"], predicted)

    best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])
    for param_name in sorted(parameters.keys()):
        print "{0}: {1}".format(param_name, best_parameters[param_name])
