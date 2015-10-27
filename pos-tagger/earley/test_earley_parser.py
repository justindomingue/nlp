# !/usr/bin/python

"""test_earley_parser

Test grammar and string taken from
    Andreas Stolcke. 1995. An Efficient Probabilistic Context-Free Parsing Algorithm that Computes Prefix Probabilities. Computational Linguistics 21(2), 165-201.
"""

from unittest import TestCase
from nltk import Tree

from earley_parser import EarleyParser
from grammar import Grammar
from state import State


class TestEarleyParser(TestCase):
    def setUp(self):
        rules = [
            'S -> NP VP',
            'NP -> Det N',
            'VP -> VT NP',
            'VP -> VI PP',
            'PP -> P NP',
            'Det -> a',
            'N -> circle | square | triangle',
            'VT -> touches',
            'VI -> is',
            'P -> above | below'
        ]
        grammar = Grammar(rules)

        self.earley = EarleyParser(grammar)
        self.earley.words = 'a circle touches a triangle'.split(' ')
        self.earley.chart = [[] for _ in range(5)]

    def test_parse(self):
        """A complete parse"""

        self.earley.parse('a circle touches a triangle')

        chart = []
        chart.append([State(self.earley.DUMMY_CHAR,['S'],0,0,0),State('S',['NP','VP'],0,0,0),State('NP',['Det','N'],0,0,0)])
        chart.append([State('Det',['a'],1,0,1),State('NP', ['Det','N'],1,0,1)])
        chart.append([State('N', ['circle'],1,1,2),State('NP',['Det','N'],2,0,2),State('S',['NP','VP'],1,0,2),State('VP',['VT','NP'],0,2,2),State('VP',['VI','PP'],0,2,2)])
        chart.append([State('VT', ['touches'],1,2,3),State('VP',['VT','NP'],1,2,3),State('NP', ['Det','N'],0,3,3)])
        chart.append([State('Det',['a'],1,3,4),State('NP',['Det','N'],1,3,4)])
        chart.append([State('N',['triangle'],1,4,5),State('NP',['Det','N'],2,3,5),State('VP',['VT','NP'],2,2,5),State('S',['NP','VP'],2,0,5),State(self.earley.DUMMY_CHAR,['S'],1,0,5)])

        self.assertItemsEqual(chart,self.earley.chart)

    def test_predictor(self):
        self.assertEqual(len(self.earley.chart[0]), 0)

        # Call predictor
        state = State('S', ['VP'], 0, 0, 0)
        self.earley.predictor(state)

        self.assertEqual(len(self.earley.chart[0]), 2)
        self.assertIn(State('VP', ['VT', 'NP'], 0, 0, 0), self.earley.chart[0])
        self.assertIn(State('VP', ['VI', 'PP'], 0, 0, 0), self.earley.chart[0])

    def test_scanner(self):
        state1 = State('NP', ['Det', 'N'], 1, 0, 1)
        state2 = State('VP', ['VT', 'NP'], 1, 0, 1)

        # Scan these states
        self.earley.scanner(state1)
        self.earley.scanner(state2)

        # Expect only `state1` to have added a new state
        self.assertIn(State('N', ['circle'], 1, 1, 2), self.earley.chart[2])
        self.assertEqual(1, len(self.earley.chart[2]))

    def test_completer(self):
        state1 = State('NP', ['Det', 'N'], 0, 0, 0)
        self.earley.chart[0].append(state1)

        state2 = State('Det', ['a'], 1, 0, 1)
        self.earley.completer(state2)

        self.assertIn(State('NP', ['Det', 'N'], 1, 0, 1), self.earley.chart[1])

    def test_enqueue(self):
        state = State('S', ['VP'], 0, 0, 0)
        self.earley.enqueue(state, 0)
        self.earley.enqueue(state, 1)

        self.assertEqual(len(self.earley.chart[0]), 1)
        self.assertEqual(len(self.earley.chart[1]), 1, "Doesn't add duplicates")
        self.assertEqual(len(self.earley.chart[2]), 0)

        self.earley.enqueue(State('VP', ['V'], 0, 0, 0), 1)
        self.assertEqual(len(self.earley.chart[1]), 2)

    def test_tree(self):
        # No parse for sentence
        self.earley.parse('Not valid')
        self.assertEqual('Not valid', self.earley.tree())

        # Sentence has parse
        self.earley.parse('a circle touches a triangle')
        actual = self.earley.tree()
        expected = Tree('S', [Tree('NP', [Tree('Det', ['a']), Tree('N', ['circle'])]), Tree('VP', [Tree('VT', ['touches']), Tree('NP', [Tree('Det', ['a']), Tree('N', ['triangle'])])])])
        self.assertEqual([expected], actual)

    def test_parse_with_ambiguity(self):
        # Define new rules
        rules = ['S->NP | VP', 'NP->book', 'VP->book']
        earley = EarleyParser(Grammar(rules))
        earley.parse('book')

        self.assertIn(State(earley.DUMMY_CHAR,['S'],1,0,1), earley.chart[1])
        self.assertIn(State('S',['NP'],1,0,1), earley.chart[1])
        self.assertIn(State('S',['VP'],1,0,1), earley.chart[1])

        self.assertItemsEqual([Tree('S', [Tree('NP', ['book'])]), Tree('S', [Tree('VP', ['book'])])], earley.tree())

        print earley.tree()

