#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
# from bllipparser import RerankingParser, Tree, tokenize
# from bllipparser import Tree
from nltk.corpus import stopwords, wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from nltk.wsd import lesk
from string import punctuation
from semantics.head_finder import SemanticHeadFinder

wordnet_lemmatizer = WordNetLemmatizer()
stop = stopwords.words('english')

# print 'Loading BLLIP reranking parser...'
# rrp = RerankingParser.fetch_and_load('WSJ+Gigaword-v2')

class Question:
    """Question

    Encapsulates a question

    Attributes:
        text (string): text of the question
        words ([sting]): individual words of the questions
        type (string): wh_word of the question

    """

    # Types of the different feature categories
    # Useful for binarizing the features
    types = ['what', "which", "when", "where", "who", "how", "why", "rest"]
    word_shapes = ['all_lower', 'all_upper', 'mixed', 'all_digit', 'other']

    # Regex patterns to help question head word identification
    patterns = {
        'set1': {
            'DESC:def_1': '^what (is|are) (a |an |the )?([^\s]* ?){1,2} \?$',
            'DESC:def_2': '^what (do|does) .* mean \?$',
            'ENTY:substance': '^what (is|are) .* ((composed|made|made out) of) \?$',
            'DESC:desc': '^what (does) .* (do) \?$',
            'ENTY:term': '^what do you call',
            'DESC:reason_1': '^what causes?',
            'DESC:reason_2': '^what (is|are) .* (used for) \?$',
            'ABBR:exp': '^what (do|does) .* (stand for) \?$'
        },
        'set2': {
            'HUM:desc': '^[w|W]ho (is|was) [A-Z]'
        }
    }

    head_finder = SemanticHeadFinder()

    def __init__(self, question, head=None, tree=None, head_present=False):
        """
        Creates a Question
        :param question: question text. Must be ended with a ' ?'
        """

        self.text = question
        self.words = word_tokenize(self.text)   # use NLTK's tokenizer because Bllip's raises an encoding error
        self.normalized_text = self.normalize(self.words)

        wh_word = self.words[0].lower()
        self.type = wh_word if wh_word in Question.types[:-1] else Question.types[-1]

        self._head = head
        self._head_present = head_present
        self._tree = tree

    def normalize(self, words, lower=True, lemmatize=True, punct=True, stops=False):
        normalized = []
        for word in words:
            if lower:
                word = word.lower()
            if lemmatize:
                word = wordnet_lemmatizer.lemmatize(word)
            normalized.append(word)

        if punct:
            normalized = [word for word in normalized if word not in punctuation]
        if stops:
            normalized = [word for word in normalized if word not in stop]

        return ' '.join(normalized)

    ### SHAPE

    def shape(self, text):
        """Returns the (case) shape of the question as a string"""

        if not any(c.isdigit() for c in text):
            if text.islower():
                return 'all_lower'
            elif text.isupper():
                return 'all_upper'
            else:
                return 'mixed'
        else:
            if text.isdigit():
                return 'all_digit'
            else:
                return 'other'

    @property
    def word_shape(self):
        """Returns the word shape for each word in the question"""
        return [self.shape(word) for word in self.words[:-1]]

    ### HEAD WORD

    @property
    def tree(self):
        if self._tree is None:
            self._tree = rrp.simple_parse(self.words)
        return Tree(self._tree)

    @property
    def head_word(self):
        """head_word Gets the head word of the question
        From Huang et al. 2008)
        """

        # Find the head word

        if self.type in ['when', 'where', 'why']:
            return None

        if self.type == 'how':
            return self.normalized_text.split(' ', 2)[1]    # return first word after type

        if self.type == 'what':
            for placehold, pattern in Question.patterns['set1'].iteritems():
                if re.match(pattern, self.text, re.IGNORECASE):
                    return placehold

        if self.type == 'who' and re.match(Question.patterns['set2']['HUM:desc'], self.text):
            return 'HUM:desc'

        if not self._head_present:
            self._head = SemanticHeadFinder().determine_head(self.tree)

        return self._head

    ### HYPERNYM

    def hypernym(self, level=1):
        '''Returns the hypernym of `self._head_word` or None'''

        if self._head is None:
            return None

        # 1. Get POS - actually we know it's a noun because that's what we've extracted
        pos = 'n'

        # 2. Which sense of the word is needed to be augmented
        try:
            sense = wn.synsets(self._head, pos)[0]  # get the best sense. Performance of ~55%, better than most Lesk algorithms

            for _ in range(level):
                hypernyms = sense.hypernyms()
                if len(hypernyms)==0: break
                sense = hypernyms[0]

            return sense.name()
        except IndexError:
            return None
        except AttributeError:
            return None

    ### OTHER
    def __repr__(self):
        return "Question('{0}')".format(self.text)

    def __len__(self):
        return len(self.words)

class Label:
    '''Represents a question label

    Form: `DESC:manner`
        where DESC is the coarse class and manner is the fine class
    '''

    def __init__(self, label):
        coarse, fine = label.split(':')
        self.coarse = coarse
        self.fine = label

    def get(self, name):
        return self.fine if name == 'fine' else self.coarse
