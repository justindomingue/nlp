#!/usr/bin/python

import re


class Question:
    """Question

    Encapsulates a question

    Attributes:
        text (string): text of the question
        words ([sting]): individual words of the questions
        type (string): wh_word of the question

    """
    def __init__(self, question):
        self.text = question
        self.words = self.text.split(' ')

        wh_word = self.words[0].lower()
        self.type = wh_word if wh_word in ['what', "which", "when", "where", "who", "how", "why"] else "rest"

    def shape(self, text):
        """Returns the (case) shape of the question as a string"""

        if not any(c.isdigit() for c in text):
            if text.islower():
                return 'all_lower'
            elif text.isupper():
                return 'all_upper'
            else:
                return 'mixed'
        else:
            if text.isdigit():
                return 'all_digit'
            else:
                return 'other'

    def word_shape(self):
        """Returns the word shape for each word in the question"""
        return [self.shape(word) for word in self.words]

    def __repr__(self):
        return "Question({0})".format(self.text)

    def __len__(self):
        return len(self.words)


