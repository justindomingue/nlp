#!/usr/bin/python

import unittest
from question import Question
from question import HeadFinder


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.q1 = Question('WHERE IS CANADA ?')
        self.q2 = Question('when can you find this ?')
        self.q3 = Question('Did 123 a1 ?')

    def test_init(self):
        self.assertEqual(self.q1.type, 'where')
        self.assertEqual(self.q2.type, 'when')
        self.assertEqual(self.q3.type, 'rest')

    def test_shape(self):
        self.assertEqual(self.q1.word_shape, ['all_upper', 'all_upper', 'all_upper'])
        self.assertEqual(self.q2.word_shape, ['all_lower' for _ in range(len(self.q2))][:-1])
        self.assertEqual(self.q3.word_shape, ['mixed', 'all_digit', 'other'])

    def test_head_word(self):
        # == FROM REGULAR EXPRESSION ==
        #should be  None
        self.assertEqual(Question('when is ?').head_word, None)
        self.assertEqual(Question('where is ?').head_word, None)
        self.assertEqual(Question('why is ?').head_word, None)

        #should be word following how
        self.assertEqual(Question('how is ?').head_word, 'is')
        self.assertEqual(Question('how long is a race ?').head_word, 'long')

        #test patterns
        #DESC:def pattern 1
        self.assertEqual(Question('what is an orange ?').head_word, 'DESC:def_1')    #what+is+an+1word
        self.assertEqual(Question('what are cold brewed ?').head_word, 'DESC:def_1')  #what+are+(2 words)

        #DESC:def pattern 2
        self.assertEqual(Question('what does this thing mean ?').head_word, 'DESC:def_2')    #what+do/does+...+mean

        #ENTY:substance
        self.assertEqual(Question('what is a senate composed of ?').head_word, 'ENTY:substance')    #what+is/are+...+composed of/made of/made out of
        self.assertEqual(Question('what is a state senate made of ?').head_word, 'ENTY:substance')
        self.assertEqual(Question('what are senates made out of ?').head_word, 'ENTY:substance')

        #DESC:desc
        self.assertEqual(Question('what does this thing do ?').head_word, 'DESC:desc')  #what+does+...+do

        #ENTY:term
        self.assertEqual(Question('what do you call a group of turkeys ?').head_word, 'ENTY:term')   #what+do+you+call

        #DESC:reason pattern 1
        self.assertEqual(Question('what causes a ?').head_word, 'DESC:reason_1')  #what causes/cause
        self.assertEqual(Question('what cause a ?').head_word, 'DESC:reason_1')  #what causes/cause

        #DESC:reason pattern 2
        self.assertEqual(Question('what is this used for ?').head_word, 'DESC:reason_2')     #what+is/are+...+used+for
        self.assertEqual(Question('what are this used for ?').head_word, 'DESC:reason_2')

        #ABBR:exp
        self.assertEqual(Question('what does this stand for ?').head_word, 'ABBR:exp')  #what+does/do+...+stand+for

        #should be HUM:desc
        self.assertEqual(Question('who is John ?').head_word, 'HUM:desc')    #what+is/was+(Capital letter)
        self.assertEqual(Question('who was Carla ?').head_word, 'HUM:desc')

        #should be candidate head word using head finder rules
        self.assertEqual(Question('who is john ?').head_word, None)

        # == FROM SYNTACTIC PARSE + COLLINS RULES ==

        pass
        #should be 'turkeys'
        self.assertEqual(Question('what is a group of turkeys called ?'), 'turkeys')
        self.assertEqual(Question('what year did the titanic sink ?'), 'year')
        self.assertEqual(Question('what is the sales tax in Minnesota ?'), 'tax')


class HeadFinderTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_head(self):

        #What year did the Titanic sink?
        self.assertEqual(HeadFinder('the Titanic').semantic_head(), 'Titanic')
        self.assertEqual(HeadFinder('the Titanic sink').semantic_head(), 'Titanic')
        self.assertEqual(HeadFinder('did the titanic sink').semantic_head(), 'Titanic')
        self.assertEqual(HeadFinder('what year').semantic_head(), 'year')
        self.assertEqual(HeadFinder('what year did the titanic sink ?').semantic_head(), 'year')

        #what is the sales tax in Minnesota?
        self.assertEqual(HeadFinder.semantic_head('in Minnesota').semantic_head(), 'in')
        self.assertEqual(HeadFinder.semantic_head('the sales tax').semantic_head(), 'tax')
        self.assertEqual(HeadFinder.semantic_head('the sales tax in Minnesota').semantic_head(), 'tax')
        self.assertEqual(HeadFinder.semantic_head('is the sales tax in Minnesota').semantic_head(), 'tax')
        self.assertEqual(HeadFinder.semantic_head('What is the sales tax in Minnesota ?').semantic_head(), 'tax')
