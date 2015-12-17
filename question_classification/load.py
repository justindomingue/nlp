#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import SGDClassifier, LogisticRegression, ElasticNet
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.feature_extraction import DictVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import accuracy_score, classification_report

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.pipeline import Pipeline, FeatureUnion

import numpy as np

from question import Question, Label


class HeadWordExtractorPlus(BaseEstimator, TransformerMixin):
    """Extracts wh-word and head word (optionally, WordNet semantic features for head word) and prepares the data for DictVectorizer"""
    def __init__(self, semantic_features=False, depth=1):
        self.semantic_features = semantic_features
        self.depth = depth

    def fit(self, x, y=None):
        return self

    def transform(self, questions):
        print 'HeadWordExtractorPlus> transforming'

        lst = []
        for q in questions:
            dict = {'wh-word': q.type}
            head = q.head_word
            if head is not None:
                dict['head-word'] = q.head_word
                if self.semantic_features:
                    hypernym = q.hypernym(self.depth)
                    if hypernym is not None:
                        dict['hypernym'] = hypernym

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

    def __init__(self, lower=False, lemmatize=False, punct=False, stops=False):
        self.lower=lower
        self.lemmatize = lemmatize
        self.punct = punct
        self.stops = stops

    def fit(self, x, y=None):
        return self

    def transform(self, questions):
        return [q.normalize(q.words, lower=self.lower, lemmatize=self.lemmatize, punct=self.punct, stops=self.stops) for q in questions]


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
        for line in file.readlines():
            split_point = line.find(' ')    # find first space
            label = line[0:split_point]
            text = line[split_point+1:].rstrip('\n')
            head = None

            if head_present:
                split_point = text.rfind(' ')
                head = text[split_point+1:]     # head was extracted before, keep it
                text = text[0:split_point]

            labels.append(Label(label))
            questions.append(Question(text, head, head_present=True))

    return labels, questions


def extract_heads_persistent(labels, questions, filename):
    data = zip([l.fine for l in labels], [q.text for q in questions], [q.head_word for q in questions])

    name, extension = filename.split('.')
    f = "{0}+heads.{1}".format(name, extension)
    with codecs.open(f, 'w', encoding='ascii') as file:
        for item in data:
            print>>file, "{0} {1} {2}".format(item[0], item[1], item[2])

def extract_trees_persistent(questions, filename):
    print 'Extracting trees from {0}'.format(filename)
    trees = [q.tree for q in questions]

    name, extension = filename.split('.')
    f = "{0}+trees.{1}".format(name, extension)
    with codecs.open(f, 'w') as file:
        for t in trees:
            print>>file, t

if __name__ == "__main__":
    dev_filename = 'data/train_5500.label'
    test_filename = 'data/TREC_10.label'

    load_heads = True
    extract_head = False # load the question list, and extract heads with persistence
    extract_trees = False # load the question list, and extract trees with persistence

    granularity = 'coarse'  # defines the granularity of the target classes (6 vs. 50)
    # granularity = 'fine'

    # Load the data set (label, question)
    dev_labels, dev_questions = load_instances(dev_filename, head_present=load_heads)
    test_labels, test_questions = load_instances(test_filename, head_present=load_heads)

    test = {"data": test_questions, "target": [l.get(granularity) for l in test_labels]}
    dev  = {"data": dev_questions,  "target": [l.get(granularity) for l in dev_labels]}

    ##########
    # Routine to extra the heads of the questions so they don't need to be extracted every time
    ##########
    if extract_head:
        extract_heads_persistent(dev_labels, dev_questions, dev_filename)
        extract_heads_persistent(test_labels, test_questions, test_filename)
        exit()
    if extract_trees:
        extract_trees_persistent(dev_questions, dev_filename)
        extract_trees_persistent(test_questions, test_filename)
        exit()

    parameters = {
        # 'features__wh_head_word__selector__depth': [1,3,6],
        # 'features__ngrams__vectorizer__ngram_range': [(1,1), (1,2), (1,3)],
        # 'features__ngrams__vectorizer__stop_words': ('english', None),
        # 'features__ngrams__extractor__lower': (True, False),
        # 'features__ngrams__extractor__lemmatize': (True, False),
        # 'features__ngrams__extractor__punct': (True, False),
        # 'features__ngrams__extractor__stops': (True, False),
        # 'features__word_shape__vectorizer__ngram_range': [(1,8), (1,7), (2,8)],
        # 'features__word_shape__vectorizer__stop_words': ('english', None),
        'clf__alpha': (1e-4, 1e-3, 4e-4),
        'clf__loss': (
            'hinge',
            'modified_huber',
            # 'log',
            'squared_hinge',
            # 'perceptron'
        ),
        # 'svc__C': (5.0, 2.0,10.0),
    }

    pipeline = Pipeline([
        # Use FeatureUnion to combine the features
        ('features', FeatureUnion(
            transformer_list=[
                #
                # WH-WORD AND HEAD WORDS
                ('wh_head_word', Pipeline([
                    ('selector', HeadWordExtractorPlus(semantic_features=False, depth=3)),
                    ('vect', DictVectorizer(sparse=True)),
                ])),

                # WORD SHAPE
                ('word_shape', Pipeline([
                    ('selector', WordShapeExtractor()),
                    ('vectorizer', TfidfVectorizer(use_idf=True, norm="l2", ngram_range=(1,7), stop_words=None)),
                ])),

                # N-GRAMS
                ('ngrams', Pipeline([
                    ('extractor', TextExtractor(lemmatize=True, lower=False, punct=True, stops=False)),       # returns a list of strings
                    ('vectorizer', TfidfVectorizer(analyzer='word', strip_accents='ascii', use_idf=True, norm="l2", ngram_range=(1,2), stop_words=None)),
                ])),
            ],

            transformer_weights= {
                'wh+head-word'  : 1.0,
                'word_shape'    : 1.0,
                'ngrams'        : 1.0,
            },
        )),

        # TODO when writing the report, see http://scikit-learn.org/stable/tutorial/machine_learning_map/index.html
        # ('clf', SGDClassifier(n_jobs=-1, verbose=1, alpha=3e-4, loss='modified_huber')),
        ('svc', LinearSVC(C=10.0))
    ])

    clf = pipeline.fit(dev['data'], dev['target'])

    # clf = GridSearchCV(pipeline, parameters, n_jobs=2)
    # _ = clf.fit(dev['data'], dev['target'])

    predicted = clf.predict(test['data'])

    print accuracy_score(test["target"], predicted)
    print clf.named_steps['svc'].coef_.shape
    for i in range(6):
        print np.count_nonzero(clf.named_steps['svc'].coef_[i])

    # print classification_report(test["target"], predicted)

    # best_parameters, score, _ = max(clf.grid_scores_, key=lambda x: x[1])
    # for param_name in sorted(parameters.keys()):
    #     print "{0}: {1}".format(param_name, best_parameters[param_name])
