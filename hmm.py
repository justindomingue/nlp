from __future__ import division
from collections import defaultdict

class HMM:
    def __init__(self):
        self.PI = {}
        self.A = {}
        self.B = {}

    def prob_sequence(self, Q, O):
        # initial state probability
        initial = self.PI[Q[0]]

        # compute state transition probabilities
        transition = 1
        for t in range(1,len(Q)-1):
            transition *= self.A[(Q[t], Q[t+1])]

        # compute state emission probabilities
        emission = 1
        for t in range(1,len(Q)):
            emission *= self.B[(Q[t],O[t])]

        print initial
        print transition
        print emission

        return initial * transition * emission

    def train(self, data):
        '''Trains the HMM using text

        @param data([[(String, String)]]): List of list of tuple `(word, pos-tag)`

        @example:
            Merger proposed. She accepted.
            => [
                [(u'Merger', u'NN-HL'), (u'proposed', u'VBN-HL')],
                [(u'She', u'NN-HL'), (u'accepted', u'VBN-HL')],
               ]
        '''

        # Model parameters' MLE
        self.PI = defaultdict(float)
        self.A = dict(defaultdict(float))
        self.B = dict(defaultdict(float))

        bigrams = defaultdict(int)      # used for computing a
        word_tag = defaultdict(int)     # used for computing b
        initial = defaultdict(int)      # used for computing pi
        vocabulary = defaultdict(int)   # #(i)

        for d in data:
            words = zip(*d)[0]

            # Initial word frequency
            initial_word = d[0][0]
            initial[initial_word] += 1

            # Word frequency
            for word in words:
                vocabulary[word] += 1

            # Word bigram frequency
            for bigram in  zip(*[words[i:] for i in range(2)]):
                bigrams[bigram] += 1

            for bigram in d:
                word_tag[bigram] += 1

        # PI - initial probabilities
        for word,count in initial.iteritems():
            self.PI[word] = count/len(data)

        # A - transitition probabilities Qt to Qt+1
        for bigram, count in bigrams.iteritems():
            self.A[bigram] = count / vocabulary[bigram[0]]

        # B - emission probabilities for Qt to Ot
        for w_t, count in word_tag.iteritems():
            self.B[w_t] = count / vocabulary[bigram[0]]

    def pretty_print(self):
        print "HMM:"
        # print "\tInitial probabilities: {0}".format(self.PI)
        # print "\tTransition probabilities: {0}".format(self.A)
        # print "\tEmission probabilities: {0}".format(self.B)

if __name__ == "__main__":
    import nltk
    from nltk.corpus import brown
    brown_train = list(brown.tagged_sents(categories='news'))

    hmm = HMM()
    hmm.train(brown_train)
    # hmm.pretty_print()

    test = [(u'The', u'AT'), (u'jury', u'NN'), (u'said', u'VBD'), (u'it', u'PPS'), (u'did', u'DOD'), (u'find', u'VB'), (u'that', u'CS'), (u'many', u'AP'), (u'of', u'IN'), (u"Georgia's", u'NP$'), (u'registration', u'NN'), (u'and', u'CC'), (u'election', u'NN'), (u'laws', u'NNS'), (u'``', u'``'), (u'are', u'BER'), (u'outmoded', u'JJ'), (u'or', u'CC'), (u'inadequate', u'JJ'), (u'and', u'CC'), (u'often', u'RB'), (u'ambiguous', u'JJ'), (u"''", u"''"), (u'.', u'.')]

    tmp = zip(*test)
    print hmm.prob_sequence(tmp[0],tmp[1])
