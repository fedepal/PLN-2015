from nltk.tree import Tree


class CKYParser:

    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """
        # assert(grammar.is_chomsky_normal_form())
        assert(grammar.is_binarised())

        self.grammar = grammar
        self._pi = {}
        self._bp = {}
        term = self._term = []  # Producciones con terminales
        nonterm = self._nonterm = {}  # Producciones con no terminales
        unaries = self._unaries = []  # Producciones con nonterm unarias
        for prod in grammar.productions():
            if prod.is_lexical():
                term.append(prod)
            elif(len(prod.rhs()) == 1):
                unaries.append(prod)
            elif(len(prod.rhs()) == 2):
                y = prod.rhs()[0].symbol()
                z = prod.rhs()[1].symbol()
                x = prod.lhs().symbol()
                lprob = prod.logprob()
                if (y, z) not in nonterm:
                    nonterm[(y, z)] = [(x, lprob)]
                else:
                    nonterm[(y, z)] += [(x, lprob)]

    def parse(self, sent):
        """Parse a sequence of terminals.

        sent -- the sequence of terminals.
        """
        grammar = self.grammar
        start = grammar.start()  # Start symbol
        n = len(sent)  # number of words in the sentence
        term = self._term
        nonterm = self._nonterm
        unaries = self._unaries
        pi = self._pi
        bp = self._bp
        # Init
        for i in range(1, n+1):
            pi[(i, i)] = {}
            bp[(i, i)] = {}
            for t in term:
                word = t.rhs()[0]
                if sent[i-1] == word:
                    nt = t.lhs().symbol()
                    pi[(i, i)][nt] = t.logprob()
                    bp[(i, i)][nt] = Tree(nt, list(t.rhs()))
            # Manejo de unarios
            added = True
            while added:
                added = False
                for p in unaries:
                    A = p.lhs().symbol()
                    B = p.rhs()[0].symbol()
                    if pi[(i,i)].get(B,None) is not None:
                        prob = p.logprob() + pi[(i,i)][B]
                        prob_l = pi[(i,i)].get(A)
                        if prob > prob_l:
                            pi[(i,i)][A] = prob
                            bp[(i,i)][A].set_label(B)
                            added = True
        for l in range(1, n):
            for i in range(1, (n-l)+1):
                j = i + l
                pi[(i, j)] = {}
                bp[(i, j)] = {}

                for s in range(i, j):
                    pi_i_s = pi.get((i, s), None)
                    bp_i_s = bp.get((i, s), None)
                    pi_s_j = pi.get((s+1, j), None)
                    bp_s_j = bp.get((s+1, j), None)
                    if pi_i_s is not None and pi_s_j is not None:
                        for Y in pi_i_s.keys():
                            for Z in pi_s_j.keys():
                                list_X = nonterm.get((Y, Z), None)
                                if list_X is not None:
                                    for X in list_X:
                                        x = X[0]
                                        prob = X[1]
                                        prob_pi_i_s = pi_i_s.get(Y, None)
                                        tree_bp_i_s = bp_i_s.get(Y, None)
                                        prob_pi_s_j = pi_s_j.get(Z, None)
                                        tree_bp_s_j = bp_s_j.get(Z, None)
                                        if prob_pi_i_s is not None and prob_pi_s_j is not None:
                                            pi_i_j = prob + prob_pi_i_s + prob_pi_s_j

                                            if x not in pi[(i, j)] or pi_i_j > pi[(i, j)][x]:  # faltaria ver el empate
                                                pi[(i, j)][x] = pi_i_j
                                                bp[(i, j)][x] = Tree(x, [tree_bp_i_s, tree_bp_s_j])
                # manejo de unarios
                added = True
                while added:
                    added = False
                    for p in unaries:
                        A = p.lhs().symbol()
                        B = p.rhs()[0].symbol()
                        if pi[(i, j)].get(B, None) is not None:
                            prob = pi[(i, j)][B] + p.logprob()
                            prob_l = pi[(i,j)].get(A, None)
                            if prob_l is not None and prob > prob_l:
                                pi[(i,j)][A] = prob
                                bp[(i,j)][A].set_label(B)
                                added = True
        lp = pi[(1, n)].get(str(start), float('-inf'))
        tree = bp[(1, n)].get(str(start), None)

        return (lp, tree)
