#!/usr/bin/python

"""Earley

Implementation of an Earley Parser based on J&M. Speech and Language Processing, 2nd ed.

Example

    # Define rules
    rules = [
        'S -> VP | NP VP',
        'VP -> V',
        'NP -> Det N | N',
        'V -> gave',
        'N -> I | you | book',
        'Det -> the'
    ]

    # Initialize Earley parser
    earley = EarleyParser(Grammar(rules))

    # Get nltk.tree's for the sentence
    trees = earley.parse('I gave the book')

    # Do something with the parses
    for tree in trees:
        tree.draw()
        # tree.print

"""

import sys

from nltk.tree import Tree

from state import State


class EarleyParser:
    DUMMY_CHAR = '$'

    chart = []
    grammar = {}

    def __init__(self, grammar):
        self.grammar = grammar

    def parse(self, sentence):
        """
        Parses sentence `sentence`.

        :param sentence: Sentence to parse
        :return: Parse trees for `sentence`
        """

        self.words = sentence.split(' ')
        self.chart = [[] for _ in range(len(self.words) + 1)]

        self.enqueue(State(self.DUMMY_CHAR, ["S"], 0, 0, 0), 0)

        for i in range(len(self.words) + 1):
            for state in self.chart[i]:
                if not state.is_complete():
                    if not self.grammar.is_pos(state.next_cat()):
                        self.predictor(state)
                    else:
                        self.scanner(state)
                else:
                    self.completer(state)

            # Abort if next state set is empty
            if i+1 < len(self.chart) and not len(self.chart[i+1]):
                return []

        return self.chart

    def predictor(self, state):
        """
        Creates new states representing top-down expaectations generated during the parsing process
        :param state: A -> C @ B D [i,j]
        """
        B = state.after_dot()
        j = state.j

        for y in self.grammar.get(B):
            self.enqueue(State(B, y, 0, j, j), j)

    def scanner(self, state):
        """
        Examine the input and incorporate a state corresponding to the predicted POS in the chart
        :param state: A -> C @ B D [i,j]
        """
        B = state.after_dot()
        j = state.j

        if j < len(self.words):
            word = self.words[j]
            if B in self.grammar.pos_for(word):
                self.enqueue(State(B, [word], 1, j, j + 1), j + 1)

    def completer(self, state):
        """
        Find and advance all previously created states that were looking for this grammatical category at this position in the input
        :param state: B -> y @ [j,k]
        """
        B = state.l
        j, k = state.i, state.j

        for old in self.chart[j]:
            if old.after_dot() == B and not old.is_complete():
                i = old.i
                origin = old.origin[:]
                origin.append(state)
                self.enqueue(State(old.l, old.r, old.dot + 1, i, k, origin), k)

    def enqueue(self, state, i):
        """ Enqueues State `state` at `i`-th level of self.chart """
        if state not in self.chart[i]:
            self.chart[i].append(state)

    def tree(self):
        """Returns an NLTK.tree of a successful parse"""
        #TODO handle returning multiple parses (ambiguous grammar)

        fin = State(self.DUMMY_CHAR, ["S"], 1, 0, len(self.words))
        last_chart = self.chart[len(self.chart) - 1]

        if fin in last_chart:
            index = last_chart.index(fin)
            root = last_chart[index]

            print root.origin
            tmp = []
            for node in root.origin[0].origin:
                tmp.append(self.treeRecursive(node))

            self.treelist = Tree('S', tmp)

            return self.treelist
        else:
            return ' '.join(self.words)

    def treeRecursive(self, node):
        # base case - node of the form Det->That, []
        if node.origin == []:
            return Tree(node.l, node.r)

        ret = []
        for n in node.origin:
            ret.append(self.treeRecursive(n))

        return Tree(node.l, ret)
