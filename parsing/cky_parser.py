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
        term = self._term = {}  # Producciones con terminales
        nonterm = self._nonterm = {}  # Producciones con no terminales
        unaries = self._unaries = {}  # Producciones con nonterm unarias
        for prod in grammar.productions():
            if prod.is_lexical():
                word = prod.rhs()[0]
                if word not in term:
                    term[word] = [(prod.lhs().symbol(), prod.logprob())]
                else:
                    term[word] += [(prod.lhs().symbol(), prod.logprob())]
            elif(len(prod.rhs()) == 1):
                # un diccionario con prods A -> B y su logprob
                B = prod.rhs()[0].symbol()
                if B not in unaries:
                    unaries[B] = [(prod.lhs().symbol(), prod.logprob())]
                else:
                    unaries[B] += [(prod.lhs().symbol(), prod.logprob())]
                # unaries.append(prod)
            elif(len(prod.rhs()) == 2):
                # un diccionario con prods X -> Y Z con (Y,Z) como key
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
            ts = term.get(sent[i-1],[])
            for t in ts:
                nt = t[0]
                pi[i, i][nt] = t[1]
                bp[i, i][nt] = Tree(nt, [sent[i-1]])
                added = True
                while added:
                    added = False
                    nts = list(pi[i, i].keys())
                    for nt in nts:
                        uns = unaries.get(nt, [])
                        for A, pA_B in uns:
                            prob = pA_B + pi[i,i][nt]
                            Aprob = pi[i, i].get(A, None)
                            if Aprob is None or prob > Aprob:
                                pi[i, i][A] = prob
                                bp[i, i][A] = Tree(A, [bp[i, i][nt]])
                                added = True

        for l in range(1, n):
            for i in range(1, (n-l)+1):
                j = i + l
                pi[(i, j)] = {}
                bp[(i, j)] = {}
                for s in range(i, j):
                    # Obtenemos los valores anteriores de pi y bp
                    pi_i_s = pi.get((i, s), None)
                    bp_i_s = bp.get((i, s), None)
                    pi_s_j = pi.get((s+1, j), None)
                    bp_s_j = bp.get((s+1, j), None)
                    if pi_i_s is not None and pi_s_j is not None:
                        for Y in pi_i_s.keys():
                            # Para Y en pi del subarbol izquierdo
                            for Z in pi_s_j.keys():
                                # Para Z en pi del subarbol derecho
                                list_X = nonterm.get((Y, Z), [])
                                # Buscamos el no term X de la forma X -> Y Z
                                # Es una lista por la amibiguedad
                                for x, prob in list_X:
                                    # x tiene el string del no terminal
                                    # prob la probabilidad de esa prod
                                    # extraemos las probs y los trees de
                                    # cada pi(i,s) pi(s+1, j) para Y y Z
                                    prob_pi_i_s = pi_i_s.get(Y, None)
                                    tree_bp_i_s = bp_i_s.get(Y, None)
                                    prob_pi_s_j = pi_s_j.get(Z, None)
                                    tree_bp_s_j = bp_s_j.get(Z, None)
                                    if prob_pi_i_s is not None and prob_pi_s_j is not None:
                                        # Calculamos pi(i,j)
                                        pi_i_j = prob + prob_pi_i_s + prob_pi_s_j
                                        if x not in pi[(i, j)] or pi_i_j > pi[(i, j)][x]:  # faltaria ver el empate
                                            # Nos quedamos con el máximo
                                            pi[(i, j)][x] = pi_i_j
                                            bp[(i, j)][x] = Tree(x, [tree_bp_i_s, tree_bp_s_j])
                                            # Manejo de unarios
                                            added = True
                                            while added:
                                                added = False
                                                nts = list(pi[i, j].keys())
                                                for nt in nts:
                                                    uns = unaries.get(nt, [])
                                                    for A, pA_B in uns:
                                                        prob = pA_B + pi[i,j][nt]
                                                        Aprob = pi[i, j].get(A, None)
                                                        if Aprob is None or prob > Aprob:
                                                            pi[i, j][A] = prob
                                                            bp[i, j][A] = Tree(A, [bp[i, j][nt]])
                                                            added = True


        lp = pi[(1, n)].get(str(start), float('-inf'))
        tree = bp[(1, n)].get(str(start), None)

        return (lp, tree)
