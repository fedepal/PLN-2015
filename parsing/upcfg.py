from collections import Counter
from nltk.grammar import Nonterminal
from nltk.grammar import PCFG
from nltk.grammar import ProbabilisticProduction
from parsing.cky_parser import CKYParser

class UPCFG:
    """Unlexicalized PCFG.
    """

    def __init__(self, parsed_sents, start):
        """
        parsed_sents -- list of training trees.
        """
        start = Nonterminal(start)
        prods = []
        for sents in parsed_sents:
            sents.collapse_unary()
            sents.chomsky_normal_form()
            prods += sents.productions()
        prods_counts = Counter(prods)
        nonterm = []
        for prod in prods:
            nonterm += [prod.lhs()]
        nonterm_counts = Counter(nonterm)

        prods = set(prods)
        pprods = []
        for prod in prods:
            pprods.append(ProbabilisticProduction(prod.lhs(),
                                              prod.rhs(),
                                              prob=(prods_counts[prod] / nonterm_counts[prod.lhs()])))

        # Calcular start
        pcfg = PCFG(start=start, productions=pprods)
        # chomsky_normal_form pcfg??
        self.parser = CKYParser(pcfg)
        self.pprods = pprods

    def productions(self):
        """Returns the list of UPCFG probabilistic productions.
        """
        return self.pprods

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        sent, tags = zip(*tagged_sent)
        return self.parser.parse(sent)
