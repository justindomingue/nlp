#!/usr/bin/python

from utilities.grammar import Grammar

class CKY:
    """CKY Parser"""

    def __init__(self, grammar):
        '''Initializes a CKY Parser
        :param grammar: utilities.grammar.Grammar object - must be in CNF
        '''
        self.grammar = grammar

    def parse(self, words):
        """Parses `words`

        Follows algorithm given in J&M, 2008

        :param words([string]): list of words representing the string to parse
        :return: CKY Table
        """

        # Create a 2D array for the parse table
        x = len(words)
        table = [ [set()]*x for _ in xrange(x) ]


        # Fill the parse table
        for j in range(0, x):
            A = self.grammar.left_for_right([words[j]])
            table[j][j] = table[j][j] | set([Component(a) for a in A])
            for i in reversed(xrange(j)):
                for k in xrange(i, j):
                    B = table[i][k]
                    C = table[k+1][j]
                    if B and C:
                        for b in B:
                            for c in C:
                                A = [b.tag,c.tag]
                                x = self.grammar.left_for_right(A)
                                if x:
                                    table[i][j] = table[i][j] | set([Component(y, (b, c)) for y in x])
        return table

    def all(self, table):
        '''Returns a list of parses'''
        parses = []

        last = table[0][-1]
        for component in last:
            if component.is_S():
                parses.append(self.retrieve_all(component))

        return parses


    def retrieve_all(self, component):
        if component.is_terminal():
            return '({0})'.format(component.tag)

        return '({0} {1} {2})'.format(component.tag, self.retrieve_all(component.origin[0]), self.retrieve_all(component.origin[1]))


class Component:
    '''Represents a component constituent'''

    def __init__(self, tag, origin=None):
        '''Initializes a component

        :param tag: Tag of the component
        :param origin: A duple of components or None
        '''
        self.tag = tag
        self.origin = origin

    def is_terminal(self):
        return self.origin is None

    def is_S(self):
        return self.tag is 'S'

    def __repr__(self):
        return "{0}".format(self.tag)

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
        table = self.cky.parse('book the flight through Houston'.split(' '))
        #
        # print table
        # for i, p in enumerate(table):
        #     print '\t'*4*i, p[i:]

        print self.cky.all(table)



