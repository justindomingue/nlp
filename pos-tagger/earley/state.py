#!/usr/bin/python

from copy import deepcopy


class State:
    """A state as defined in Earley's algorithm

    Attributes:
        l (string): left-hand side of the production
        r (string): right-hand side of the production
        dot (int): current position in the production
        i (int): position i in the input at which the matching of this production began
        j (int): position j in the input at which the matching of this production ended
        origin ([State]): list of completed states that generated the constituents of the states
    """

    DOT = '@'

    def __init__(self, l, r, dot, i, j, origin=[]):
        self.l = l
        self.r = r
        self.dot = dot
        self.i = i
        self.j = j
        self.origin = origin

    def is_complete(self):
        """Returns True if the state is completed (dot is at the end). """
        return self.dot == len(self.r)

    def next_cat(self):
        """ Returns the next constituent after the dot.

         Note: Not necessary per se but follows the Earley parser algorithm from J&M.
         """
        return self.after_dot()

    def after_dot(self):
        """ Returns the constituent after the dot or None. """
        return self.r[self.dot] if self.dot < len(self.r) else None

    def __repr__(self):
        r = deepcopy(self.r)

        try:
            r.insert(self.dot, self.DOT)
        except Exception:
            print 'The right-side should be an array'

        return "({0} -> {1}, ({2},{3}) {4})".format(self.l, ' '.join(r), self.i, self.j, [o.l for o in self.origin])

    def __eq__(self, other):
        """ Two states are equal if their all their attributes but origin are the same. """
        if isinstance(other, State):
            return self.l == other.l and self.r == other.r and self.i == other.i and self.j == other.j and self.dot == other.dot
        return False