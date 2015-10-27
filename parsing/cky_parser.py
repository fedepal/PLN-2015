from nltk.grammar import nonterminals
from nltk.tree import Tree
from nltk.grammar import PCFG
from collections import defaultdict


class CKYParser:

    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """
        assert(grammar.is_chomsky_normal_form())
        assert(grammar.is_binarised())

        # grammar.start()
        # grammar.productions()
        # grammar.leftcorners(grammar.start())
        self.grammar = grammar


    def parse(self, sent):
        """Parse a sequence of terminals.

        sent -- the sequence of terminals.
        """
        grammar = self.grammar
        start = grammar.start() # Start symbol
        n = len(sent) # number of words in the sentence
        N = set()# non-terminals in the grammar
        for prod in grammar.productions():
            N.add(prod.lhs())

        # split the productions, X -> Y Z and X -> sent[i]
        term = []
        nonterm = []

        for prod in grammar.productions():
            if prod.is_lexical():
                term.append(prod)
            else:
                nonterm.append(prod)

        pi = {}
        # Init
        for i in range(1, n+1):
            pi[(i, i)] = {}
            for t in term:
                word = t.rhs()[0]
                if sent[i-1] == word:
                    pi[(i,i)][t.lhs()] = t.logprob()




        # i, j entre 1..n y i<=j
