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

    def test_head_word(self):
        #should be  None
        self.assertEqual(Question('when is').head_word(), None)
        self.assertEqual(Question('where is').head_word(), None)
        self.assertEqual(Question('why is').head_word(), None)

        #should be word following how
        self.assertEqual(Question('how is').head_word(), 'is')

        #test patterns
        #DESC:def pattern 1
        self.assertEqual(Question('what is an orange').head_word(), 'DESC:def')    #what+is+an+1word
        self.assertEqual(Question('what are cold brewed').head_word(), 'DESC:def')  #what+are+(2 words)

        #DESC:def pattern 2
        self.assertEqual(Question('what does this thing mean?').head_word(), 'DESC:def')    #what+do/does+...+mean

        #ENTY:substance
        self.assertEqual(Question('what is a senate composed of').head_word(), 'ENTY:substance')    #what+is/are+...+composed of/made of/made out of
        self.assertEqual(Question('what is a state senate made of').head_word(), 'ENTY:substance')
        self.assertEqual(Question('what are senates made out of').head_word(), 'ENTY:substance')

        #DESC:desc
        self.assertEqual(Question('what does this thing do').head_word(), 'DESC:desc')  #what+does+...+do

        #ENTY:term
        self.assertEqual(Question('what do you call a ...').head_word(), 'ENTY:term')   #what+do+you+call

        #DESC:reason pattern 1
        self.assertEqual(Question('what causes a').head_word(), 'DESC:reason')  #what causes/cause
        self.assertEqual(Question('what cause a').head_word(), 'DESC:reason')  #what causes/cause

        #DESC:reason pattern 2
        self.assertEqual(Question('what is this used for').head_word(), 'DESC:reason')     #what+is/are+...+used+for
        self.assertEqual(Question('what are this used for').head_word(), 'DESC:reason')

        #ABBR:exp
        self.assertEqual(Question('what does this stand for').head_word(), 'ABBR:exp')  #what+does/do+...+stand+for

        #should be HUM:desc
        self.assertEqual(Question('who is John...').head_word(), 'HUM:desc')    #what+is/was+(Capital letter)
        self.assertEqual(Question('who was Carla...').head_word(), 'HUM:desc')

        #should be candidate head word using head finder rules
        self.assertEqual(Question('who is john').head_word(), None)
