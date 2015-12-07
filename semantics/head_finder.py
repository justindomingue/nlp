#!/usr/bin/python
# -*- coding: utf-8 -*-

from bllipparser import Tree

class AbstractCollinsHeadFinder:
    ''' A base class for a HeadFinder similar to the one described in Michael Collins' 1999 thesis '''

    WILDCARD = '**'

    def determine_head(self, tree):
        '''Determines which daugther of `tree` is the head'''
        raise NotImplementedError

    def _apply_collins(self, tree, candidates):
        '''Applies Collins' rules to find the most likely head of tree'''
        raise NotImplementedError

    def _search(self, candidates, direction, tags, one_at_a_time=False):
        """Searches `tree` in `direction` for node with label in `tags`

        :param tree: Tree in which to perform the search
        :param direction: Direction of the search. Either 'right-to-left- or 'left-to-right'
        :param tags: List of tags to search for
        :param one_at_a_time: True if the tags should be searched one at a time (order matters) or not
        :return: The token of the matched node or None
        """
        iterator = candidates if direction == 'left' else list(reversed(candidates))

        # wildcard value - anything can be its head
        if tags[0] == AbstractCollinsHeadFinder.WILDCARD:
            return iterator[0]

        if one_at_a_time:
            tags = [[tag] for tag in tags]
        else:
            tags = [tags]

        for tag_list in tags:
            for t in iterator:
                if t[2] in tag_list:
                    return t

        return None

    def _last_word(self, tree):
        '''Returns the right-most tree in `tree`'''
        while tree.subtrees() != []:
            tree = tree.subtrees()[-1]
        return tree

    def _find(self, tree):
        # tree has no children, it is its own head
        if tree.is_preterminal():
            return tree.token, tree.label, tree.label

        # recursively find the candidate heads of the children
        candidate_heads = []
        for subtree in tree.subtrees():
            candidate_heads.append(self._find(subtree))

        # now choose a head using Collins' rules
        candidate, tag = self._apply_collins(tree, candidate_heads)

        candidate = (candidate[0], candidate[1], tag)
        return candidate

    def _firstNN(self, tree, tag="NN"):
        '''Returns the first word whose tag starts with 'NN'''''
        try:
            return tree.tokens()[next(i for i,tag in enumerate(tree.tags()) if tag.startswith("NN"))]
        except StopIteration:
            if tag != "JJ":
                return self._firstNN(tree, "JJ")
            else:
                return None

class CollinsHeadFinder(AbstractCollinsHeadFinder):
    '''Implements the HeadFinder described in Michael Collins' 1999 thesis.'''

    # Rules used to find heads of constituents in the treebank
    collins_rules = {
        'ADJP'  : ('left',  ['NNS','QP','NN','$','ADVP','JJ','VBN','ADJP','JJR','NP','JJS','DT','FW','RBR','RBS','SBAR','RB']),
        'ADVP'  : ('right', ['RB','RBR','RBS','FW','ADVP','TO','CD','JJR','JJ','IN','NP','JJS','NN']),
        'CONJP' : ('right', ['CC','RB','IN']),
        'FRAG'  : ('right', [AbstractCollinsHeadFinder.WILDCARD]),
        'INTJ'  : ('left',  [AbstractCollinsHeadFinder.WILDCARD]),
        'LST'   : ('right', ['LS',':']),
        'NAC'   : ('left',  ['NN','NNS','NNP','NNPS','NP','NAC','EX','$','CD','QP','PRP','VBG','JJ','JJS','JJR','ADJP','FW']),
        'PP'    : ('right', ['IN','TO','VBG','VBN','RP','FW']),
        'PRN'   : ('left',  [AbstractCollinsHeadFinder.WILDCARD]),
        'PRT'   : ('right', ['RP']),
        'QP'    : ('left',  ['$','IN','NNS','NN','JJ','RB','DT','CD','NCD','QP','JJR','JJS']),
        'RRC'   : ('right', ['VP','NP','ADVP','ADJP','PP']),
        'S1'    : ('left',  [AbstractCollinsHeadFinder.WILDCARD]),   #custom: `S1` is root of bllipparser
        'S'     : ('left',  ['TO','IN','VP','S','SBAR','ADJP','UCP','NP']),
        'SBAR'  : ('left',  ['WHNP','WHPP','WHADVP','WHADJP','IN','DT','S','SQ','SINV','SBAR','FRAG']),
        'SBARQ' : ('left',  ['SQ','S','SINV','SBARQ','FRAG']),
        'SINV'  : ('left',  ['VBZ','VBD','VBP','VB','MD','VP','S','SINV','ADJP','NP']),
        'SQ'    : ('left',  ['VBZ','VBD','VB','MD','VP','SQ']),
        'UCP'   : ('right', [AbstractCollinsHeadFinder.WILDCARD]),
        'VP'    : ('left',  ['TO','VBD','VBN','MD','VBZ','VB','VBG','VBP','VP','ADJP','NN','NNS','NP']),
        'WHADJP': ('left',  ['CC','WRB','JJ','ADJP']),
        'WHADVP': ('right', ['CC','WRB']),
        'WHNP'  : ('left',  ['WDT','WP','WP$','WHADJP','WHPP','WHNP']),
        'WHPP'  : ('right', ['IN','TO','FW'])
    }

    def determine_head(self, tree):
        '''
        Determines which daugther of `tree` is the head

        The method works by assigning a head to every node in a bottom-up fashon
        '''

        # Find a candidate head  for the tree
        candidate, tag, _ = self._find(tree)
        return candidate

    def _apply_collins(self, tree, candidates):
        '''Applies Collins' rules to find the most likely head of tree'''
        if tree.label == 'NP':
            last_word = candidates[-1]
            if last_word[0] == 'POS':  # last word is tag POS
                return (last_word, last_word.label)

            candidate = self._search(candidates, 'right', ['NN', 'NNP', 'NNPS', 'NNS', 'NX', 'POS', 'JJR'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'left', ['NP'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'right', ['$', 'ADJP', 'PRN'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'right', ['CD'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'right', ['JJ', 'JJS', 'RB', 'QP'])
            if candidate is not None: return (candidate, tree.label)

            return last_word, tree.label

        elif tree.label == 'CC':
            raise NotImplementedError

        rule = CollinsHeadFinder.collins_rules[tree.label]
        candidate = self._search(candidates, rule[0], rule[1], one_at_a_time=True)
        return (candidate, tree.label)

class SemanticHeadFinder(AbstractCollinsHeadFinder):
    '''Variant of a HeadFinder described in Collins' 1999 thesis that returns the semantic head noun of a phrase'''

    # Modification of Collins' rules giving preference to noun or noun phrases
    collins_rules = {
        'ADJP'  : ('left',  ['NNS','QP','NN','$','ADVP','JJ','VBN','ADJP','JJR','NP','JJS','DT','FW','RBR','RBS','SBAR','RB']),
        'ADVP'  : ('right', ['RB','RBR','RBS','FW','ADVP','TO','CD','JJR','JJ','IN','NP','JJS','NN']),
        'CONJP' : ('right', ['CC','RB','IN']),
        'FRAG'  : ('right', [AbstractCollinsHeadFinder.WILDCARD]),
        'INTJ'  : ('left',  [AbstractCollinsHeadFinder.WILDCARD]),
        'LST'   : ('right', ['LS',':']),
        'NAC'   : ('left',  ['NN','NNS','NNP','NNPS','NP','NAC','EX','$','CD','QP','PRP','VBG','JJ','JJS','JJR','ADJP','FW']),
        'PP'    : ('right', ['IN','TO','VBG','VBN','RP','FW', 'PP']),
        'PRN'   : ('left',  [AbstractCollinsHeadFinder.WILDCARD]),
        'PRT'   : ('right', ['RP']),
        'QP'    : ('left',  ['$','IN','NNS','NN','JJ','RB','DT','CD','NCD','QP','JJR','JJS']),
        'RRC'   : ('right', ['VP','NP','ADVP','ADJP','PP']),
        'S1'    : ('left',  [AbstractCollinsHeadFinder.WILDCARD]),   #custom: `S1` is root of bllipparser
        'S'     : ('left',  ['NP','TO','IN','VP','S','SBAR','ADJP','UCP']),
        'SBAR'  : ('left',  ['WHNP','WHPP','WHADVP','WHADJP','IN','DT','S','SQ','SINV','SBAR','FRAG']),
        'SBARQ' : ('left',  ['SQ','S','SINV','SBARQ','FRAG']),
        'SINV'  : ('left',  ['NP','VBZ','VBD','VBP','VB','MD','VP','S','SINV','ADJP']),
        'SQ'    : ('left',  ['NP','VBZ','VBD','VB','MD','VP','SQ']),
        'UCP'   : ('right', [AbstractCollinsHeadFinder.WILDCARD]),
        'VP'    : ('left',  ['NN', 'NNS', 'NP', 'S', 'TO','VBD','VBN','MD','VBZ','VB','VBG','VBP','VP','ADJP']),
        'WHADJP': ('left',  ['CC','WRB','JJ','ADJP']),
        'WHADVP': ('right', ['CC','WRB']),
        'WHNP'  : ('left',  ['NP','NN','NNS','WDT','WP','WP$','WHADJP','WHPP','WHNP']),
        'WHPP'  : ('right', ['IN','TO','FW']),
        'X'     : ('left',  [AbstractCollinsHeadFinder.WILDCARD]),
        'NX'    : ('left',  [AbstractCollinsHeadFinder.WILDCARD])
    }

    def determine_head(self, tree):
        '''
        Determines which daugther of `tree` is the head

        The method works by assigning a head to every node in a bottom-up fashon
        '''

        # Find a candidate head  for the tree
        candidate, tag, _ = self._find(tree)

        if candidate is not None:
            return candidate
        else:
            return self._firstNN(tree)

    def _apply_collins(self, tree, candidates):
        '''Applies Collins' rules to find the most likely head of tree'''
        last_candidate = candidates[-1]

        if tree.label == 'NP':
            if last_candidate[1] == 'POS':  # last word is tag POS
                return last_candidate, tree.label

            candidate = self._search(candidates, 'right', ['NN', 'NNP', 'NNPS', 'NNS', 'NX', 'POS', 'JJR'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'left', ['NP'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'right', ['$', 'ADJP', 'PRN'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'right', ['CD'])
            if candidate is not None: return (candidate, tree.label)

            candidate = self._search(candidates, 'right', ['JJ', 'JJS', 'RB', 'QP'])
            if candidate is not None: return (candidate, tree.label)

            return last_candidate, tree.label

        elif tree.label == 'CC':
            raise NotImplementedError

        rule = SemanticHeadFinder.collins_rules[tree.label]
        candidate = self._search(candidates, rule[0], rule[1], one_at_a_time=True)
        if candidate is None:
            return last_candidate, tree.label
        else:
            return candidate, tree.label

    def _search(self, candidates, direction, tags, one_at_a_time=False):
        """Searches `tree` in `direction` for node with label in `tags`

        :param tree: Tree in which to perform the search
        :param direction: Direction of the search. Either 'right-to-left- or 'left-to-right'
        :param tags: List of tags to search for
        :param one_at_a_time: True if the tags should be searched one at a time (order matters) or not
        :return: The token of the matched node or None
        """
        iterator = candidates if direction == 'left' else list(reversed(candidates))

        # wildcard value - anything can be its head
        if tags[0] == AbstractCollinsHeadFinder.WILDCARD:
            return iterator[0]


        if one_at_a_time:
            tags = [[tag] for tag in tags]
        else:
            tags = [tags]

        for tag_list in tags:
            for t in iterator:
                if t[2] in tag_list or t[1] in ['NN','NS', 'NNS']:
                    return t

        return None

