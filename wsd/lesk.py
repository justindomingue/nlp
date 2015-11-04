#!/usr/bin/python
# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn
from collections import Counter


def original_lesk(sentence):
    """Original Lesk algorithm as defined by M. Lesk in 1986

    To disambiguate a word, the gloss of each of its senses is compared to the
    glosses of every other word in a phrase.

    M. Lesk. Automatic sense disambiguation using machine readable dictionaries:
    How to tell a pine cone from a ice cream cone. In Proceedings of SIGDOC ’86,
    1986.
    """
    words = sentence.split(' ')
    best_sense = []    # where best_sense[i] is the best sense of word i in `sentence`

    # disambiguate each word
    for word in words:
        # Get the definitions of every other word
        definitions = [wn.synsets(w) for w in words if w is not word]
        signature = [val.definition() for sublist in definitions for val in sublist]

        print word
        print signature

        best = ""
        max_overlap = 0

        # Compute the overlap for each sense
        for sense in wn.synsets(word):
            overlap = compute_overlap(sense.definition().split(' '), signature)

            if overlap > max_overlap:
                max_overlap = overlap
                best = sense

        best_sense.append(best)

    return best_sense


def simple_lesk(word, sentence):
    """Simple Lesk

    Determine correct meaning of `word` in a given context (`sentence`)
    by locating the sense the overlaps the most between its dictionary
    definition and the given context.

    Florentina Vasilescu, Philippe Langlais, and Guy Lapalme. 2004.
    Evaluating Variants of the Lesk Approach for Disambiguating Words. LREC, Portugal.
    """

    synsets = wn.synsets(word)
    if not synsets:
        return []

    best_sense = synsets[0] # most frequent sense for word

    max_overlap = 0
    context = sentence.split(' ')

    for sense in synsets:
        examples = [e.split(' ') for e in sense.examples()]
        examples_flat = [val for sublist in examples for val in sublist]
        definitions = sense.definition().split(' ')

        signature = definitions + examples_flat
        overlap = compute_overlap(signature, context)

        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = sense

    return best_sense

def disambiguate(sentence, lesk=simple_lesk):
    """Disambiguates every word in `sentence` using function `lesk` """
    words = sentence.split(' ')

    best_sense = []

    for word in words:
        best_sense.append(lesk(word, sentence))

    return best_sense

def define_each(synsets):
    """Defines each synset in `synsets`"""
    return [s.definition() for s in synsets if s]


def compute_overlap(a,b):
    """Computes the overlap between lists `a` and `b`"""
    return list((Counter(a) & Counter(b)).elements())
