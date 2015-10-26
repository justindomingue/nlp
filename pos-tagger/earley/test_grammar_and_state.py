#!/usr/bin/env python

import unittest
from state import State
from grammar import Grammar


class StateTests(unittest.TestCase):
    def setUp(self):
        self.state = State('S', ['VP', 'NP'], 0, 0, 0)

    def test_is_complete(self):
        self.assertFalse(self.state.is_complete())

        self.state.dot = 1
        self.assertFalse(self.state.is_complete())

        self.state.dot = 2
        self.assertTrue(self.state.is_complete())

        self.state.dot = 3
        self.assertFalse(self.state.is_complete())

    def test_next_cat(self):
        self.assertEqual(self.state.next_cat(), 'VP')

        self.state.dot = 1
        self.assertEqual(self.state.next_cat(), 'NP')

        self.state.dot = 2
        self.assertEqual(self.state.next_cat(), None)

    def test_after_dot(self):
        self.assertEqual(self.state.after_dot(), 'VP')

        self.state.dot = 1
        self.assertEqual(self.state.after_dot(), 'NP')

        self.state.dot = 2
        self.assertEqual(self.state.after_dot(), None)


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