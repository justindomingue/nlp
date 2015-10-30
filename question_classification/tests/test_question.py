#!/usr/bin/python

import unittest
from question_classification.question import Question


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.q1 = Question('WHERE IS CANADA')
        self.q2 = Question('when can you find this')
        self.q3 = Question('Did 123 a1')

    def test_init(self):
        self.assertEqual(self.q1.type, 'where')
        self.assertEqual(self.q2.type, 'when')
        self.assertEqual(self.q3.type, 'rest')

    def test_shape(self):
        self.assertEqual(self.q1.word_shape(), ['all_upper', 'all_upper', 'all_upper'])
        self.assertEqual(self.q2.word_shape(), ['all_lower' for _ in range(len(self.q2))])
        self.assertEqual(self.q3.word_shape(), ['mixed', 'all_digit', 'other'])
