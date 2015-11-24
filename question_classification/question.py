#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from collections import defaultdict as dd
from bllipparser import RerankingParser, Tree, tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from string import punctuation

wordnet_lemmatizer = WordNetLemmatizer()
stop = stopwords.words('english') + list(punctuation)

print 'Loading BLLIP reranking parser...'

# rrp = RerankingParser.fetch_and_load('WSJ+Gigaword-v2')

class Question:
    """Question

    Encapsulates a question
            print label
            print  text.strip()

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
        self.words = word_tokenize(self.text)
        self.normalized_words = self.normalize(self.words)  # used when generating bigrams

        self.normalized_text = self.normalize(self.words)

        wh_word = self.words[0].lower()
        self.type = wh_word if wh_word in Question.types[:-1] else Question.types[-1]

    def normalize(self, words):
        normalized = []
        for word in words:
            word = wordnet_lemmatizer.lemmatize(word)
            # word = word.lower()
            normalized.append(word)
        # words = [word for word in words if word not in stop]

        return ' '.join(normalized)

    ### FEATURE EXTRACTOR

    def features(self):
        """
        Returns a dictionary of features
        """

        # dictionary of features that will be returned
        features = dd(int)

        # Wh-word type feature
        # for type in Question.types:
        #     features[type] = 1 if self.type == type else 0

        # features["head-word"] = self.head_word

        # Word shape feature - activated if text contains shape
        # ws = self.word_shape
        # for shape in Question.word_shapes:
        #     features[shape] = 1 if shape in ws else 0

        # N-gram features
        for ngram in self.normalized_words: #n=1
            features[ngram] += 1
        # for ngram in self.ngrams(2):        #n=2
        #     features[ngram] += 1

        return features

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

        return HeadFinder(self.words).semantic_head()

    ### N-GRAMS

    def ngrams(self, n):
        return zip(*[self.normalized_words[i:] for i in range(n)])

    ### OTHER
    def __repr__(self):
        return "Question('{0}')".format(self.text)

    def __len__(self):
        return len(self.words)

class HeadFinder:

    # Rules used to find heads of constituents in the treebank
    collins_rules = {
        'ADJP'  : ('left',  ['NNS','QP','NN','$','ADVP','JJ','VBN','ADJP','JJR','NP','JJS','DT','FW','RBR','RBS','SBAR','RB']),
        'ADVP'  : ('right', ['RB','RBR','RBS','FW','ADVP','TO','CD','JJR','JJ','IN','NP','JJS','NN']),
        'CONJP' : ('right', ['CC','RB','IN']),
        'FRAG'  : ('right', ['SBAR']),
        'INTJ'  : ('left',  []),
        'LST'   : ('right', ['LS',':']),
        'NAC'   : ('left',  ['NN','NNS','NNP','NNPS','NP','NAC','EX','$','CD','QP','PRP','VBG','JJ','JJS','JJR','ADJP','FW']),
        'PP'    : ('right', ['IN','TO','VBG','VBN','RP','FW']),
        'PRN'   : ('left',  []),
        'PRT'   : ('right', ['RP']),
        'QP'    : ('left',  ['$','IN','NNS','NN','JJ','RB','DT','CD','NCD','QP','JJR','JJS']),
        'RRC'   : ('right', ['VP','NP','ADVP','ADJP','PP']),
        'S'     : ('left',  ['TO','IN','VP','S','SBAR','ADJP','UCP','NP']),
        'SBAR'  : ('left',  ['WHNP','VVHPP','WHADVP','WHADJP','IN','DT','S','SQ','SINV','SBAR','FRAG']),
        'SBARQ' : ('left',  ['WHNP', 'SQ','S','SINV','SBARQ','FRAG']),
        'SINV'  : ('left',  ['NP','VBZ','VBD','VBP','VB','MD','VP','S','SINV','ADJP']),
        'SQ'    : ('left',  ['NN','NNS','NNP','NNPS','NP','SQ']),
        'UCP'   : ('right', []),
        'VP'    : ('left',  ['TO','NN','NNS','NP','VBD','VBN','MD','VBZ','VB','VBC','VBP','VP','ADJP']),
        'WHADJP': ('left',  ['CC','WRB','JJ','ADJP']),
        'WHADVP': ('right', ['CC','WRB']),
        'WHNP'  : ('left',  ['WDT','WP','WP','$','WHADJP','WHPP','WHNP']),
        'WHPP'  : ('right', ['IN','TO','FW'])
    }

    def __init__(self, sentence):
        '''Initializes a HeadFinder with a sentence

        :param sentence (String or [String]) Sentence for which to find the semantic head word
        '''
        self.tree = Tree(rrp.simple_parse(sentence))

    def semantic_head(self):
        '''Extracts semantic head word from tree using Collins Rules'''

        # Candidate head and tag
        candidate, tag = self.head_recursive(self.tree)

        if candidate is not None and tag.startswith("NN"):
            return candidate
        else:
            return self.firstNN(self.tree)

    def head_recursive(self, tree):
        if tree is None:
            return None, None

        if tree.is_preterminal():
            return tree.token, tree.label
        if tree.label == "S1":
            return self.head_recursive(tree.subtrees()[0])

        if tree.label == 'NP':
            last_word = tree.subtrees()[-1]
            if last_word.label == 'POS':  # last word is tag POS
                return self.head_recursive(last_word)

            candidate = self.search(tree, 'right', ['NN', 'NNP', 'NNPS', 'NNS', 'NX', 'POS', 'JJR'])
            if candidate: return self.head_recursive(candidate)

            candidate = self.search(tree, 'left', ['NP'])
            if candidate: return self.head_recursive(candidate)

            candidate = self.search(tree, 'right', ['$', 'ADJP', 'PRN'])
            if candidate: return self.head_recursive(candidate)

            candidate = self.search(tree, 'right', ['CD'])
            if candidate: return self.head_recursive(candidate)

            candidate = self.search(tree, 'right', ['JJ', 'JJS', 'RB', 'QP'])
            if candidate: return self.head_recursive(candidate)

            return self.head_recursive(last_word)

        elif tree.label == 'CC':
            raise NotImplementedError

        rule = HeadFinder.collins_rules[tree.label]
        candidate = self.search(tree, rule[0], rule[1], one_at_a_time=True)
        return self.head_recursive(candidate)

        return None, None


    def search(self, tree, direction, tags, one_at_a_time=False):
        """Searches `tree` in `direction` for node with label in `tags`

        :param tree: Tree in which to perform the search
        :param direction: Direction of the search. Either 'right-to-left- or 'left-to-right'
        :param tags: List of tags to search for
        :param one_at_a_time: True if the tags should be searched one at a time (order matters) or not
        :return: The token of the matched node or None
        """
        enumerator = tree.subtrees() if direction == 'left' else reversed(tree.subtrees())
        if one_at_a_time:
            tags = [[tag] for tag in tags]
        else:
            tags = [tags]

        for tag_list in tags:
            for t in enumerator:
                if t.label in tag_list:
                    return t

        return None


    def last_word(self, tree):
        '''Returns the right-most tree in `tree`'''
        while tree.subtrees() != []:
            tree = tree.subtrees()[-1]
        return tree

    def firstNN(self, tree, tag="NN"):
        '''Returns the first word whose tag starts with 'NN'''''
        try:
            return tree.tokens()[next(i for i,tag in enumerate(tree.tags()) if tag.startswith("NN"))]
        except StopIteration:
            if tag != "JJ":
                return self.firstNN(self, tree, "JJ")
            else:
                return None

class Label:
    '''Represents a question label

    Form: `DESC:manner`
        where DESC is the coarse class and manner is the fine class
    '''

    def __init__(self, label):
        coarse, fine = label.split(':')
        self.coarse = coarse
        self.fine = label
