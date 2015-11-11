from nltk.grammar import induce_pcfg, Nonterminal
from parsing.cky_parser import CKYParser
from parsing.util import unlexicalize, lexicalize
from nltk.tree import Tree


class UPCFG:
    """Unlexicalized PCFG.
    """

    def __init__(self, parsed_sents, start='sentence',
                 horzMarkov=None, unary=False):
        """
        parsed_sents -- list of training trees.
        """
        start = Nonterminal(start)
        prods = []
        for tree in parsed_sents:
            ntree = tree.copy(deep=True)
            unlexicalize(ntree)
            ntree.chomsky_normal_form(horzMarkov=horzMarkov)
            if not unary:
                ntree.collapse_unary(collapsePOS=True)
            prods += ntree.productions()

        pcfg = induce_pcfg(start=start, productions=prods)
        self._prods = pcfg.productions()
        self._parser = CKYParser(pcfg)
        self._start = pcfg.start()  # start para construir el flat en parse

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
        if tree is None and lp == float('-inf'):
            tree = Tree(self._start.symbol(),
                        [Tree(tag, [word]) for word, tag in tagged_sent])
        else:
            tree.un_chomsky_normal_form()
            tree = lexicalize(tree, sent)

        return tree
