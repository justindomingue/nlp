#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import copy

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import accuracy_score, classification_report

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline, FeatureUnion

import numpy as np

from question import Question, Label


class HeadWordExtractorPlus(BaseEstimator, TransformerMixin):
    """Extracts wh-word and head word (optionally, WordNet semantic features for head word) and prepares the data for DictVectorizer"""
    def __init__(self, semantic_features=False, wordnet_depth=1):
        self.semantic_features = semantic_features
        self.depth = wordnet_depth

    def fit(self, x, y=None):
        return self

    def transform(self, questions):
        print 'HeadWordExtractorPlus> transforming'

        lst = []
        for q in questions:
            dict = {}
            dict['wh-word'] = q.type
            dict['head-word'] = q.head_word
            if self.semantic_features:
                dict['hypernym'] = q.hypernym(self.depth)
            lst.append(dict)
        return lst

class WordShapeExtractor(BaseEstimator, TransformerMixin):
    """ Extracts the word shape for each question and represents the shapes as strings for language modelling """
    def fit(self, x, y=None):
        return self

    def transform(self, questions):
        print 'WordShapeExtractor> transforming'
        return [' '.join(q.word_shape) for q in questions]

class TextExtractor(BaseEstimator, TransformerMixin):
    """ Extract text from each question to be used for language modelling """
    def __init__(self, normalized=False):
        self.normalized = normalized

    def fit(self, x, y=None):
        return self

    def transform(self, questions):
        print 'TextExtractor> transforming '
        if self.normalized:
            return [q.normalized_text for q in questions]
        else:
            return [q.text for q in questions]



def load_instances(f, head_present=False):
    '''
    Loads data set in file `f`. Returns a list of tuple (label, Question) where `head` is optional

    :param f file with data set to load
    :param head_present Will extract the head. Insert '+heads' in `f` before the extension.

    Note. The data set has one question per line with format "type text"
    Example. DESC:manner How did serfdom develop in and then leave Russia ?

    '''
    labels = []
    questions = []

    if head_present:
        name, extension = f.split('.')
        f = "{0}+heads.{1}".format(name, extension)

    print "Loading data set {1} ({0} head)".format('with' if head_present else 'without', f)

    with codecs.open(f, 'r', encoding='ascii') as file:

        for line in file:
            split_point = line.find(' ')    # find first space
            label = line[0:split_point]
            text = line[split_point+1:].rstrip('\n')
            head = None

            if head_present:
                split_point = text.rfind(' ')
                head = text[split_point+1:]     # head was extracted before, keep it
                text = text[0:split_point]

            labels.append(Label(label))
            questions.append(Question(text, head))

    return labels, questions


def extract_heads_persistent(labels, questions, filename):
    data = zip([l.fine for l in labels], [q.text for q in questions], [q.head_word for q in questions])

    name, extension = filename.split('.')
    f = "{0}+heads.{1}".format(name, extension)
    with codecs.open(f, 'w', encoding='ascii') as file:
        for item in data:
            print>>file, "{0} {1} {2}".format(item[0], item[1], item[2])


if __name__ == "__main__":
    dev_filename = 'data/train_5500.label'
    test_filename = 'data/TREC_10.label'

    extract_head = False # load the question list, and extract heads with persistence

    # granularity = 'coarse'  # defines the granularity of the target classes (6 vs. 50)
    granularity = 'fine'

    # Load the data set (label, question)
    dev_labels, dev_questions = load_instances(dev_filename, head_present=not extract_head)
    test_labels, test_questions = load_instances(test_filename, head_present=not extract_head)

    dev  = {"data": dev_questions,  "target": [l.get(granularity) for l in dev_labels]}
    test = {"data": test_questions, "target": [l.get(granularity) for l in test_labels]}

    ##########
    # Routine to extra the heads of the questions so they don't need to be extracted every time
    ##########
    if extract_head:
        extract_heads_persistent(dev_labels, dev_questions, dev_filename)
        extract_heads_persistent(dev_labels, test_questions, test_filename)
        exit()

    parameters = {'union__ngrams__vect__ngram_range': [(1,1), (1,2)],
                  # 'union__ngrams__vect__stop_words': ('english', None),
                  # 'union__ngrams__tfidf__use_idf': (True, False),
                  # 'union__ngrams__tfidf__norm': ('l1', 'l2'),
                  # 'union__ngrams__extractor__normalized': (True, False),
                  # 'union__word_shape__vect__ngram_range': [(1,1), (1,2)],
                  # 'union__word_shape__vect__stop_words': ('english', None),
                  # 'union__word_shape__tfidf__use_idf': (True, False),
                  # 'union__word_shape__tfidf__norm': ('l1', 'l2'),
                  # 'clf__alpha': (1e-1, 1e-2, 1e-3, 1e-4),
                  'clf__loss': ('hinge', 'modified_huber'), #'log', 'squared_hinge', 'perceptron'),
                  }

    pipeline = Pipeline([
        # Use FeatureUnion to combine the features
        ('union', FeatureUnion(
            transformer_list=[
                #
                # # WH-WORD AND HEAD WORDS
                # ('wh+head-word', Pipeline([
                #     ('selector', HeadWordExtractorPlus(semantic_features=False, wordnet_depth=1)),
                #     ('vect', DictVectorizer())
                # ])),
                #
                # # WORD SHAPE
                # ('word_shape', Pipeline([
                #     ('selector', WordShapeExtractor()),
                #     ('vect', CountVectorizer(ngram_range=(1,5))),
                #     ('tfidf', TfidfTransformer(use_idf=True, norm='l2')),
                #     # ('best')  #TODO
                # ])),

                # N-GRAMS
                ('ngrams', Pipeline([
                    ('extractor', TextExtractor(normalized=True)),       # returns a list of strings
                    ('vect', CountVectorizer(analyzer='word', strip_accents='ascii')),
                    ('tfidf', TfidfTransformer(use_idf=True, norm='l2')), #TODO
                ])),
            ],

            # transformer_weights= {
            #     'wh+head-word'  : 1.0,
            #     'word_shape'    : 1.0,
            #     'ngrams'        : 1.0,
            # },
        )),

        ('clf', SGDClassifier(n_jobs=-1, verbose=0, alpha=1e-4)),  # TODO when writing the report, see http://scikit-learn.org/stable/tutorial/machine_learning_map/index.html
    ])

    # clf = pipeline.fit(dev['data'], dev['target'])
    # predicted = clf.predict(test['data'])

    gs_clf = GridSearchCV(pipeline, parameters, n_jobs=1)
    _ = gs_clf.fit(dev['data'], dev['target'])

    predicted = gs_clf.predict(test['data'])

    print accuracy_score(test["target"], predicted)
    print classification_report(test["target"], predicted)

    best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])
    for param_name in sorted(parameters.keys()):
        print "{0}: {1}".format(param_name, best_parameters[param_name])

