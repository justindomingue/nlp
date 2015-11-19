#!/usr/bin/python

import re
from string import punctuation
# from bllipparser import RerankingParser, Tree, tokenize

# rrp = RerankingParser.fetch_and_load('WSJ+Gigaword-v2')

class Question:
    """Question

    Encapsulates a question

    Attributes:
        text (string): text of the question
        words ([sting]): individual words of the questions
        type (string): wh_word of the question

    """

    # Regex patterns to help question head word identification
    patterns = {
        'set1': {
            'DESC:def_1': '^what (is|are) ((a|an|the) )?(\w+ ?){1,2}',
            'DESC:def_2': '^what (do|does) (\w+ ?)+ mean \?$',
            'ENTY:substance': '^what (is|are) (\w+ ?)+ ((composed|made|made out) of) \?$',
            'DESC:desc': '^what (does) (\w+ ?)+ (do) \?$',
            'ENTY:term': '^what do you call',
            'DESC:reason_1': '^what causes?',
            'DESC:reason_2': '^what (is|are) (\w+ ?)+ (used for) \?$',
            'ABBR:exp': '^what (do|does) (\w+ ?)+ (stand for) \?$'
        },
        'set2': {
            'HUM:desc': '^who (is|was) [A-Z]'
        }
    }

    def __init__(self, question):
        """
        Creates a Question
        :param question: question text. Must be ended with a ' ?'
        """

        self.text = question

        # self.words = tokenize(self.text)
        self.words = self.text.split(' ')

        wh_word = self.words[0].lower()
        self.type = wh_word if wh_word in ['what', "which", "when", "where", "who", "how", "why"] else "rest"

    ### FEATURE EXTRACTOR

    def features(self):
        """
        Returns a dictionary of features
        """
        return {
            self.type: 1,
            "word-shape": self.word_shape,
            "head-word": self.head_word,
            "unigrams": self.words,
            "bigrams": self.ngrams(2),
            "trigrams": self.ngrams(3)
        }

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
    def head_word(self):
        """head_word Gets the head word of the question
        From Huang et al. 2008)
        """

        if self.type in ['when', 'where', 'why']:
            return None

        if self.type == 'how':
            return self.words[1]

        if self.type == 'what':
            for placehold, pattern in Question.patterns['set1'].iteritems():
                if re.match(pattern, self.text):
                    return placehold

        if self.type == 'who' and re.match(Question.patterns['set2']['HUM:desc'], self.text):
            return 'HUM:desc'

        return None

    def apply_collins_rules_on(self, tree):
        return

    def extract_head_word(self):
        sentence = self.words + ['?']               #add '?' so parser knows it's a question (parse differs otherwise)
        tree = Tree(rrp.simple_parse(sentence))     #get the best parse

        return self.apply_collins_rules_on(tree)

    ### N-GRAMS

    def ngrams(self, n):
        return zip(*[self.words[i:] for i in range(n)])


    ### OTHER
    def __repr__(self):
        return "Question({0}--{1})".format(self.type, self.text)

    def __len__(self):
        return len(self.words)

