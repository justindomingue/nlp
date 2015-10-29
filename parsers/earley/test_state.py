#!/usr/bin/env python

import unittest
from state import State


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
