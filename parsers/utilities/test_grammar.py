#!/usr/bin/env python

import unittest
from grammar import Grammar


class GrammarTest(unittest.TestCase):
    def setUp(self):
        rules = [
            'S -> VP | NP VP',
            'VP -> V',
            'NP -> Det N | N',
            'V -> walk | fly | book',
            'N -> I | you | cows | book',
            'Det -> the',
            'Det -> a'
        ]
        self.grammar = Grammar(rules)

    def test_init(self):
        self.assertItemsEqual([['VP'], ['NP', 'VP']], self.grammar.get('S'))
        self.assertItemsEqual([['the'], ['a']], self.grammar.get('Det'))

    def test_get(self):
        self.assertItemsEqual([['VP'], ['NP', 'VP']], self.grammar.get('S'))
        self.assertItemsEqual([['V']], self.grammar.get('VP'))
        self.assertItemsEqual([], self.grammar.get('NotThere'))

    def test_is_pos(self):
        self.assertFalse(self.grammar.is_pos('S'))
        self.assertFalse(self.grammar.is_pos('VP'))
        self.assertFalse(self.grammar.is_pos('NotThere'))
        self.assertTrue(self.grammar.is_pos('Det'))

    def test_pos_for(self):
        self.assertEqual(self.grammar.pos_for('the'), ['Det'])
        self.assertEqual(self.grammar.pos_for('book'), ['N', 'V'])  # 'book' has two POS
        self.assertEqual(self.grammar.pos_for('NotThere'), [])  # 'book' has two POS

    def test_terminals(self):
        self.assertItemsEqual(set(['walk', 'fly', 'book', 'I', 'you', 'cows', 'book', 'the', 'a']), self.grammar.terminals)