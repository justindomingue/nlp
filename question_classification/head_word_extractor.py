#!/usr/bin/python


class HeadWordExtractor():
    """Extracts head word from a sentence"""
    def __init__(self):
        self.a="1"

    def get_head_word(self, sentence):
        """Returns the semantic head word in `sentence`"""

        parse = list() #TODO parse sentence

        return self.find_head_word_in_tree(parse)

    def find_head_word_in_tree(self, tree):
        """Finds the head word in `tree` by applying refined Collins rules (Huang et al. 2008)"""
        return ""
