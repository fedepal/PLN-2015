from nltk.grammar import nonterminals
from nltk.tree import Tree
from nltk.grammar import PCFG
from collections import defaultdict


class CKYParser:

    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """
        # assert(grammar.is_chomsky_normal_form())
        assert(grammar.is_binarised())

        # grammar.start()
        # grammar.productions()
        # grammar.leftcorners(grammar.start())
        self.grammar = grammar
        self._pi = {}
        self._bp = {}

    def parse(self, sent):
        """Parse a sequence of terminals.

        sent -- the sequence of terminals.
        """
        grammar = self.grammar
        start = grammar.start() # Start symbol
        n = len(sent) # number of words in the sentence
        term = [] # Producciones con terminales
        nonterm = [] # Producciones con no terminales

        for prod in grammar.productions():
            if prod.is_lexical():
                term.append(prod)
            else:
                nonterm.append(prod)

        pi = self._pi
        bp = self._bp
        # Init
        for i in range(1, n+1):
            pi[(i, i)] = {}
            bp[(i, i)] = {}
            for t in term:
                word = t.rhs()[0]
                if sent[i-1] == word:
                    pi[(i, i)][str(t.lhs())] = t.logprob()
                    bp[(i, i)][str(t.lhs())] = Tree(str(t.lhs()), list(t.rhs()))

        for l in range(1,n):
            for i in range(1, (n-l)+1):
                j = i + l
                pi[(i,j)] = {}
                bp[(i,j)] = {}
                for X in nonterm:
                    for s in range(i, j):
                        prob = X.logprob()
                        pi_i_s = pi.get((i, s), None)
                        bp_i_s = bp.get((i, s), None)
                        pi_s_j = pi.get((s+1, j), None)
                        bp_s_j = bp.get((s+1, j), None)

                        if pi_i_s is not None and pi_s_j is not None:
                            pi_i_s = pi_i_s.get(str(X.rhs()[0]), None)
                            bp_i_s = bp_i_s.get(str(X.rhs()[0]), None)
                            pi_s_j = pi_s_j.get(str(X.rhs()[1]), None)
                            bp_s_j = bp_s_j.get(str(X.rhs()[1]), None)

                            if pi_i_s is not None and pi_s_j is not None:
                                pi_i_j = prob + pi_i_s + pi_s_j
                                if str(X.lhs()) not in pi[(i,j)] or pi_i_j > pi[(i,j)][str(X.lhs())]:
                                    pi[(i,j)][str(X.lhs())] = pi_i_j
                                    bp[(i,j)][str(X.lhs())] = Tree(str(X.lhs()), [bp_i_s,bp_s_j])

        lp = pi[(1,n)][str(start)]
        tree = bp[(1,n)][str(start)]

        return (lp, tree)
