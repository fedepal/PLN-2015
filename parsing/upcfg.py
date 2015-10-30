from nltk.grammar import induce_pcfg, Nonterminal
from parsing.cky_parser import CKYParser
from parsing.util import unlexicalize, lexicalize
class UPCFG:
    """Unlexicalized PCFG.
    """

    def __init__(self, parsed_sents, start='sentence'):
        """
        parsed_sents -- list of training trees.
        """
        start = Nonterminal(start)
        prods = []
        for tree in parsed_sents:
            sent, tags = zip(*tree.pos())
            tree = unlexicalize(tree)
            tree.chomsky_normal_form()
            prods += tree.productions()
            tree = lexicalize(tree, sent)

        #
        # prods_counts = Counter(prods) # Cambiar la forma de contar
        # nonterm_counts = Counter(nonterm)
        #
        # prods = set(prods)
        # pprods = [] # is_terminal is_nonterminal nltk.grammar
        # for prod in prods:
        #     pprods.append(ProbabilisticProduction(prod.lhs(),
        #                                       prod.rhs(),
        #                                       prob=(prods_counts[prod] / nonterm_counts[prod.lhs()])))

        # Calcular start

        pcfg = induce_pcfg(start=start, productions=prods)
        self._prods = pcfg.productions()
        self._parser = CKYParser(pcfg)

    def productions(self):
        """Returns the list of UPCFG probabilistic productions.
        """
        return self._prods

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        sent, tags = zip(*tagged_sent)
        lp, tree = self._parser.parse(tags)
        tree = lexicalize(tree, sent)
        # lpos = tree.treepositions('leaves')
        # for i in range(len(sent)):
        #     tree[lpos[i]] = sent[i]

        return tree
