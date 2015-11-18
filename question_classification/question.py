#!/usr/bin/python

import re
from string import punctuation
from bllipparser import RerankingParser, Tree, tokenize

rrp = RerankingParser.fetch_and_load('WSJ+Gigaword-v2')

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
        'DESC:def': ['^what (is|are) ((a|an|the) )?(\w+ ?){1,2}', '^what (do|does) (\w+ ?)+ mean ?$'],
        'ENTY:substance': ['^what (is|are) (\w+ ?)+ ((composed|made|made out) of) ?$'],
        'DESC:desc': ['^what (does) (\w+ ?)+ (do) ?$'],
        'ENTY:term': ['^what do you call'],
        'DESC:reason': ['^what causes?', '^what (is|are) (\w+ ?)+ (used for) ?$'],
        'ABBR:exp': ['^what (do|does) (\w+ ?)+ (stand for) ?$'],
        'HUM:desc': '^who (is|was) [A-Z]'
    }

    def __init__(self, question):
        """
        Creates a Question
        :param question: question text. Must be ended with a ' ?'
        """

        self.text = self.preprocess(question)
        self.words = tokenize(self.text)

        wh_word = self.words[0].lower()
        self.type = wh_word if wh_word in ['what', "which", "when", "where", "who", "how", "why"] else "rest"

    def preprocess(self, text):
        """Removes punctuation and makes text lowecase"""
        # return text.translate(None, punctuation)
        return text #TODO get rid of it?

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
        return [self.shape(word) for word in self.text.split(' ')]

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
            for placehold, patterns in Question.patterns.iteritems():
                if placehold == 'HUM:desc': continue

                for pattern in patterns:
                    if re.match(pattern, self.text):
                        return placehold

        if self.type == 'who' and re.match(Question.patterns['HUM:desc'], self.text):
            return 'HUM:desc'

        return None

    def apply_collins_rules_on(self, tree):
        return

    def extract_head_word(self):
        sentence = self.words + ['?']               #add '?' so parser knows it's a question (parse differs otherwise)
        tree = Tree(rrp.simple_parse(sentence))     #get the best parse

        return self.apply_collins_rules_on(tree)


    ### OTHER
    def __repr__(self):
        return "Question({0})".format(self.text)

    def __len__(self):
        return len(self.words)




def load_instances(f):
    '''
    Load two lists of cases to perform WSD on. The structure that is returned is a dict, where
    the keys are the ids, and the values are instances of WSDInstance.
    '''
    tree = ET.parse(f)
    root = tree.getroot()

    dev_instances = {}
    test_instances = {}

    for text in root:
        if text.attrib['id'].startswith('d001'):
            instances = dev_instances
        else:
            instances = test_instances
        for sentence in text:
            # construct sentence context
            context = [to_ascii(el.attrib['lemma']) for el in sentence]
            for i, el in enumerate(sentence):
                if el.tag == 'instance':
                    my_id = el.attrib['id']
                    lemma = to_ascii(el.attrib['lemma'])
                    instances[my_id] = WSDInstance(my_id, lemma, context, i)
    return dev_instances, test_instances

if __name__ == "__main__":