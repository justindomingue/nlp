#!/usr/bin/python

from utilities.grammar import Grammar

class CKY:
    """CKY Parser"""

    def __init__(self, grammar):
        self.grammar = grammar

    def parse(self, words):
        """Parses `words`

        Follows algorithm given in J&M, 2008

        :param words(string):
        :return:
        """

        # Create a 2D array for the parse table
        x = len(words)
        table = [ [set()]*x for _ in xrange(x) ]


        # Fill the parse table
        for j in range(0, x):
            A = self.grammar.left_for_right([words[j]])
            table[j][j] = table[j][j] | set(A)
            for i in reversed(xrange(j)):
                for k in xrange(i, j):
                    B = table[i][k]
                    C = table[k+1][j]
                    if B and C:
                        for b in B:
                            for c in C:
                                A = [b,c]
                                x = self.grammar.left_for_right(A)
                                if x:
                                    table[i][j] = table[i][j] | set(x)
        return table


import unittest

class CKYTest(unittest.TestCase):
    def setUp(self):
        rules = [
            'S -> NP VP',
            'S -> X1 VP',
            'X1 -> Aux NP',
            'S -> book | include | prefer',
            'S -> Verb NP',
            'S -> X2 PP',
            'S -> Verb PP',
            'S -> VP PP',
            'NP -> I | she | me',
            'NP -> TWA | Houston',
            'NP -> Det Nominal',
            'Nominal -> book | flight | meal | money',
            'Nominal -> Nominal Noun',
            'Nominal -> Nominal PP',
            'VP -> book | include | prefer',
            'VP -> Verb NP',
            'VP -> X2 PP',
            'X2 -> Verb NP',
            'VP -> Verb PP',
            'VP -> VP PP',
            'PP -> Preposition NP',
            'Preposition -> from | through',
            'Det -> a | the',
            'Verb -> book',
            'Noun -> book'
        ]

        grammar = Grammar(rules)
        self.cky = CKY(grammar)

    def test_parse(self):
        parse = self.cky.parse('book the flight through Houston'.split(' '))
        for p in parse:
            print p


