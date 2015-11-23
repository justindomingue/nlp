#!/usr/bin/python

import re
from bllipparser import RerankingParser, Tree, tokenize

print 'Loading parser...'
rrp = RerankingParser.fetch_and_load('WSJ+Gigaword-v2')

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

        self.words = tokenize(self.text)

        wh_word = self.words[0].lower()
        self.type = wh_word if wh_word in Question.types[:-1] else Question.types[-1]

    ### FEATURE EXTRACTOR

    def features(self):
        """
        Returns a dictionary of features
        """

        # dictionary of features that will be returned
        features = {}

        # Wh-word type feature
        for type in Question.types:
            features[type] = 1 if self.type == type else 0

        # features["head-word"] = self.head_word

        # Word shape feature - activated if text contains shape
        ws = self.word_shape
        for shape in Question.word_shapes:
            features[shape] = 1 if shape in ws else 0

        ngrams = self.ngrams(2)
        for ngram in ngrams:
            features[ngram] = 1
        # n-gram feature
        # features.update({
        #     "unigrams": self.words,
        #     "bigrams": self.ngrams(2),
        #     "trigrams": self.ngrams(3)
        # })

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

        return HeadFinder.semantic_head(self.words)

    ### N-GRAMS

    def ngrams(self, n):
        return zip(*[self.words[i:] for i in range(n)])

    ### OTHER
    def __repr__(self):
        return "Question('{0}')".format(self.text)

    def __len__(self):
        return len(self.words)

class HeadFinder:

    def __init__(self, sentence):
        '''Initializes a HeadFinder with a sentence

        :param sentence (String or [String]) Sentence for which to find the semantic head word
        '''
        self.tree = Tree(rrp.simple_parse(sentence))

    def semantic_head(self):
        '''Extracts semantic head word from tree using Collins Rules'''

        # Candidate head and tag
        candidate, tag = self.head_recursive(self.tree.subtrees()[0])

        print "Cand: {0}, tag: {1}".format(candidate, tag)
        return candidate if tag.startswith("NN") else self.firstNN(self.tree)

    def head_recursive(self, tree):
        if tree.is_preterminal():
            return tree.token

        if tree.label == 'NP':
            last_word = tree.subtrees()[-1]
            if last_word.label == 'POS':  # last word is tag POS
                return last_word.token, last_word.label

            candidate = self.search(tree, 'right', ['NN', 'NNP', 'NNPS', 'NNS', 'NX', 'POS', 'JJR'])
            if candidate is not None: return candidate.token, candidate.label

            candidate = self.search(tree, 'left', ['NP'])
            if candidate is not None: return candidate.token, candidate.label

            candidate = self.search(tree, 'right', ['$', 'ADJP', 'PRN'])
            if candidate is not None: return candidate.token, candidate.label

            candidate = self.search(tree, 'right', ['CD'])
            if candidate is not None: return candidate.token, candidate.label

            candidate = self.search(tree, 'right', ['JJ', 'JJS', 'RB', 'QP'])
            if candidate is not None: return candidate.token, candidate.label

            return last_word.token, last_word.label

        elif tree.label == 'CC':
            raise NotImplementedError

        collins_rules = {
            'ADJP': ('left', ['NNS', 'QP', 'NN', '$', 'ADVP', 'JJ', 'VBN', 'ADJP', 'JJR', 'NP', 'JJS', 'DT', 'FW', 'RBR', 'RBS', 'SBAR', 'RB']),
            'ADVP': ('right', ['RB','RBR','RBS','FW','ADVP','TO','CD','JJR','JJ','IN','NP','JJS','NN']),
            'CONJP': ('right', ['CC','RB','IN']),
            'FRAG': ('right', []),
            'INTJ': ('left', []),
            'LST': ('right', ['LS',':']),
            'NAC': ('left', ['NN','NNS','NNP','NNPS','NP','NAC','EX','$','CD','QP','PRP','VBG','JJ','JJS','JJR','ADJP','FW']),
            'PP': ('right', ['IN','TO','VBG','VBN','RP','FW']),
            'PRN': ('left', [])
        }


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

    def firstNN(self, tree):
        '''Returns the first word whose tag starts with 'NN'''''
        return tree.tokens()[next(i for i,tag in enumerate(tree.tags()) if tag.startswith("NN"))]

if __name__ == "__main__":
    print 'Finding head'
    head = HeadFinder('the titanic').semantic_head()

    print head