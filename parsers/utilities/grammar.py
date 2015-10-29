#!/usr/bin/python

import re
from collections import defaultdict


class Grammar:
    """A grammar containing rules of the form "A -> B | C D"

    Attributes:
        grammar (dict<string, [string]>): Dictionary of rules of the form "A": ["B", "C D"] (A -> B | C D)
        word_pos (dict<string, [string]>): Dictionary of POS for a given word
        pos (set<string>): POS found in the grammar
    """

    def __init__(self, rules):
        """
        Initialize a grammar with a set of rules and extracts POS from the rules.

        :param rules: array of strings of the form "A -> B | C".
        """

        self.grammar = defaultdict(list)
        self.word_pos = dict()
        self.pos = set()

        for rule in rules:
            rule = rule.rstrip()
            if len(rule) > 0:
                rule = rule.split('->')  # split start/end
                left = rule[0].strip()
                right = [(re.sub(r'[^a-zA-Z\d\s-]', '', r)).strip().split(' ') for r in rule[1].split('|')]
                self.grammar[left] += right

        # extract POS tags
        # pos iff on lhs of rhs without lhs
        # det -> that
        # that -> #
        for left, right in self.grammar.iteritems():
            for r in right:
                for r2 in r:
                    if not self.grammar.has_key(r2):
                        self.pos.add(left)

    def get(self, lhs):
        """
        Returns the right-hand side of rules associated with `lhs`

        :param lhs: string
        :return: Array of strings if `lhs` was in the rules, empty array otherwise.
        """
        return self.grammar.get(lhs) if self.grammar.has_key(lhs) else []

    def is_pos(self, term):
        """
        Returns True if `term` if a POS for the grammar

        :param term: string
        """
        return term in self.pos

    def pos_for(self, word):
        """
        Returns POS tags for word `word` or [] if `word` is not a terminal symbol.

        :param word: string
        :return:  [string] or []
        """
        if not self.word_pos:
            for l in self.grammar.keys():
                r = self.grammar[l]
                for rr in r:
                    for w in rr:
                        if not w in self.grammar:
                            if not w in self.word_pos:
                                self.word_pos[w.lower()] = []
                            self.word_pos[w.lower()].append(l)
        return self.word_pos[word.lower()] if self.word_pos.has_key(word.lower()) else []

    @property
    def terminals(self):
        if not hasattr(self, '_terminals'):
            self._terminals = set()
            for _,right in self.grammar.iteritems():    #right: [[string]]
                for r in right:     #r: [string]
                    for rr in r:    #rr: string
                        if len(self.get(rr)) is 0:
                            self._terminals.add(rr)

        return self._terminals

    def __repr__(self):
        print "Grammar ["
        for k, v in self.grammar.iteritems():
            print "{0}:{1}".format(k, v)
        print "]"
        print "POS {0}".format(self.pos)
