#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from bllipparser import Tree
from head_finder import CollinsHeadFinder


class TestCollinsHeadFinder(unittest.TestCase):
    def test_determine_head(self):

        trees = [
            "(S1 (S (WHNP (WP What) (NN year)) (VP (VBD did) (S (NP (DT the) (NNP Titanic)) (VP (VB sink))))))",
            "(S1 (SBARQ (WHADVP (WRB How)) (SQ (VBD did) (NP (NN serfdom)) (VP (VP (VB develop) (PRT (RP in))) (CC and) (RB then) (VP (VB leave) (NP (NNP Russia))))) (. ?)))",
            "(S1 (SBARQ (WHNP (WDT What) (NNS films)) (SQ (VP (VBD featured) (NP (DT the) (NN character)) (NP (NNP Popeye) (NNP Doyle)))) (. ?)))",
            "(S1 (SBARQ (WHADVP (WRB How)) (SQ (MD can) (NP (PRP I)) (VP (VB find) (NP (NP (DT a) (NN list)) (PP (IN of) (NP (NP (NNS celebrities) (POS ')) (JJ real) (NNS names)))))) (. ?)))",
            "(S1 (S (NP (WP What) (NN fowl)) (VP (NNS grabs) (NP (DT the) (NN spotlight)) (PP (IN after) (NP (NP (DT the) (NNP Chinese) (NNP Year)) (PP (IN of) (NP (DT the) (NNP Monkey)))))) (. ?)))",
            "(S1 (SBARQ (WHNP (WP What)) (SQ (VP (VBZ is) (NP (NP (DT the) (JJ full) (NN form)) (PP (IN of) (NP (NN .com)))))) (. ?)))",
            "(S1 (SBARQ (WHNP (WP What) (JJ contemptible) (NN scoundrel)) (SQ (VP (VBD stole) (NP (DT the) (NN cork)) (PP (IN from) (NP (PRP$ my) (NN lunch))))) (. ?)))",
        ]

        heads = [
            "did",
            "did",
            "featured",
            "find",
            "grabs",
            "is",
            "stole"
        ]

        assert len(heads) == len(trees)

        chf = CollinsHeadFinder()
        for i in range(len(trees)):
            self.assertEqual(heads[i], chf.determine_head(Tree(trees[i])))

