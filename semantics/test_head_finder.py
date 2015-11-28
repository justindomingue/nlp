#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from bllipparser import Tree
from head_finder import CollinsHeadFinder


class TestCollinsHeadFinder(unittest.TestCase):
    def test_determine_head(self):

        trees = [
            "(S1 (S (WHNP (WP What) (NN year)) (VP (VBD did) (S (NP (DT the) (NNP Titanic)) (VP (VB sink))))))",
            "(S1 (SBARQ (WHADVP (WRB How) (RB far)) (SQ (VBZ is) (NP (PRP it)) (PP (PP (IN from) (NP (NNP Denver))) (PP (TO to) (NP (NNP Aspen))))) (. ?)))",
            "(S1 (SBARQ (WHNP (WP What) (NN county)) (SQ (VBZ is) (NP (NP (NNP Modesto)) (, ,) (NP (NNP California))) (ADVP (RB in))) (. ?)))",
            "(S1 (SBARQ (WHNP (WP Who)) (SQ (VP (VBD was) (NP (NNP Galileo)))) (. ?)))",
            "(S1 (SBARQ (WHNP (WP What)) (SQ (VBZ is) (NP (DT an) (NN atom))) (. ?)))",
            "(S1 (SBARQ (WHADVP (WRB When)) (SQ (VBD did) (NP (NNP Hawaii)) (VP (VB become) (NP (DT a) (NN state)))) (. ?)))",
            "(S1 (SBARQ (WHNP (WRB How) (JJ tall)) (SQ (VP (VBZ is) (NP (DT the) (NNP Sears) (NNP Building)))) (. ?)))",
            "(S1 (S (NP (NNP George) (NNP Bush)) (VP (VBD purchased) (NP (NP (DT a) (JJ small) (NN interest)) (PP (IN in) (WHNP (WDT which) (NN baseball) (NN team))))) (. ?)))",
            "(S1 (SBARQ (WHNP (WP What)) (SQ (VBZ is) (NP (NP (NNP Australia) (POS 's)) (JJ national) (NN flower))) (. ?)))",
            "(S1 (SBARQ (WHADVP (WRB Why)) (SQ (VBZ does) (NP (DT the) (NN moon)) (VP (VB turn) (NP (NN orange)))) (. ?)))",
            "(S1 (SBARQ (WHNP (WP What)) (SQ (VBZ is) (NP (NN autism))) (. ?)))",
        ]

        heads = [ "did", "is", "is", "was", "is", "did", "is", "purchased", "is", "does", "is", ]

        assert len(heads) == len(trees)

        chf = CollinsHeadFinder()
        for i in range(len(trees)):
            self.assertEqual(heads[i], chf.determine_head(Tree(trees[i])))

