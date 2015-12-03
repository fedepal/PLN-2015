# https://docs.python.org/3/library/unittest.html
from unittest import TestCase
from math import log2

from nltk.tree import Tree
from nltk.grammar import PCFG

from parsing.cky_parser import CKYParser


class TestCKYParser(TestCase):

    def test_ambiguity(self):
        self.maxDiff = None
        grammar = PCFG.fromstring(
            """
                S -> NP VP          [1.0]
                VP -> Vt NP         [0.9]
                VP -> VP PP         [0.1]
                NP -> DT NN         [0.8]
                NP -> NP PP         [0.2]
                PP -> IN NP         [1.0]
                Vi -> 'sleeps'      [1.0]
                Vt -> 'saw'         [1.0]
                NN -> 'man'         [0.1]
                NN -> 'woman'       [0.1]
                NN -> 'telescope'   [0.3]
                NN -> 'dog'         [0.5]
                DT -> 'the'         [1.0]
                IN -> 'with'        [0.6]
                IN -> 'in'          [0.4]
            """)

        parser = CKYParser(grammar)

        sent = "the man saw the dog with the telescope".split()

        lp, t = parser.parse(sent)

        # check tree
        t2 = Tree.fromstring(
            """
                (S
                    (NP (DT the)(NN man))
                    (VP
                        (Vt saw)
                        (NP
                            (NP (DT the)(NN dog))
                            (PP (IN with)
                                (NP (DT the)(NN telescope))))))""")

        self.assertEqual(t, t2)

        # check prob
        p = log2(1.0 * 0.8 * 1.0 * 0.1 * 0.9 * 1.0 * 0.2 * 0.8 *
                 1.0 * 0.5 * 1.0 * 0.6 * 0.8 * 1.0 * 0.3)

        self.assertEqual(lp, p)

        # check pi
        pi = {
            (1, 1): {'DT': log2(1.0)},
            (2, 2): {'NN': log2(0.1)},
            (3, 3): {'Vt': log2(1.0)},
            (4, 4): {'DT': log2(1.0)},
            (5, 5): {'NN': log2(0.5)},
            (6, 6): {'IN': log2(0.6)},
            (7, 7): {'DT': log2(1.0)},
            (8, 8): {'NN': log2(0.3)},

            (1, 2): {'NP': log2(0.8 * 1.0 * 0.1)},
            (1, 3): {},
            (1, 4): {},
            (1, 5): {'S': log2(1.0 * 0.8 * 1.0 *
                               0.1 * 0.8 * 1.0 *
                               0.9 * 1.0 * 0.5
                               )},
            (1, 6): {},
            (1, 7): {},
            (1, 8): {'S': log2(1.0 * 0.8 * 1.0 * 0.1 * 0.9 *
                               1.0 * 0.2 * 0.8 * 1.0 * 0.5 *
                               1.0 * 0.6 * 0.8 * 1.0 * 0.3
                               )},
            (2, 3): {},
            (2, 4): {},
            (2, 5): {},
            (2, 6): {},
            (2, 7): {},
            (2, 8): {},
            (3, 4): {},
            (3, 5): {'VP': log2(0.9 * 1.0 * 0.8 * 1.0 * 0.5)},
            (3, 6): {},
            (3, 7): {},
            (3, 8): {'VP': log2(0.9 * 1.0 * 0.2 * 0.8 *
                                1.0 * 0.5 * 1.0 * 0.6 *
                                0.8 * 1.0 * 0.3
                                )},
            (4, 5): {'NP': log2(0.8 * 1.0 * 0.5)},
            (4, 6): {},
            (4, 7): {},
            (4, 8): {'NP': log2(0.2 * 0.8 * 1.0 *
                                0.5 * 1.0 * 0.6 *
                                0.8 * 1.0 * 0.3
                                )},
            (5, 6): {},
            (5, 7): {},
            (5, 8): {},
            (6, 7): {},
            (6, 8): {'PP': log2(1.0 * 0.6 * 0.8 * 1.0 * 0.3)},
            (7, 8): {'NP': log2(0.8 * 1.0 * 0.3)}
        }
        self.assertEqualPi(parser._pi, pi)

        # check bp
        bp = {
            (1, 1): {'DT': Tree.fromstring("(DT the)")},
            (2, 2): {'NN': Tree.fromstring("(NN man)")},
            (3, 3): {'Vt': Tree.fromstring("(Vt saw)")},
            (4, 4): {'DT': Tree.fromstring("(DT the)")},
            (5, 5): {'NN': Tree.fromstring("(NN dog)")},
            (6, 6): {'IN': Tree.fromstring("(IN with)")},
            (7, 7): {'DT': Tree.fromstring("(DT the)")},
            (8, 8): {'NN': Tree.fromstring("(NN telescope)")},

            (1, 2): {'NP': Tree.fromstring("(NP (DT the) (NN man))")},
            (1, 3): {},
            (1, 4): {},
            (1, 5): {'S': Tree.fromstring(
                """(S
                        (NP (DT the) (NN man))
                        (VP (Vt saw) (NP (DT the) (NN dog))))
                """
                )},
            (1, 6): {},
            (1, 7): {},
            (1, 8): {'S': Tree.fromstring(
                """
                    (S
                        (NP (DT the)(NN man))
                        (VP
                            (Vt saw)
                            (NP
                                (NP (DT the)(NN dog))
                                (PP (IN with)
                                    (NP (DT the)(NN telescope))))))
                """)},
            (2, 3): {},
            (2, 4): {},
            (2, 5): {},
            (2, 6): {},
            (2, 7): {},
            (2, 8): {},
            (3, 4): {},
            (3, 5): {'VP': Tree.fromstring(
                "(VP (Vt saw) (NP (DT the) (NN dog)))")},
            (3, 6): {},
            (3, 7): {},
            (3, 8): {'VP': Tree.fromstring(
                """
                (VP
                    (Vt saw)
                    (NP
                        (NP (DT the) (NN dog))
                        (PP
                            (IN with)
                            (NP
                                (DT the)
                                (NN telescope)))))
                """)},
            (4, 5): {'NP': Tree.fromstring("(NP (DT the) (NN dog))")},
            (4, 6): {},
            (4, 7): {},
            (4, 8): {'NP': Tree.fromstring(
                """
                (NP
                    (NP
                        (DT the)
                        (NN dog))
                    (PP (IN with)
                        (NP
                            (DT the)
                            (NN telescope))))
                """)},
            (5, 6): {},
            (5, 7): {},
            (5, 8): {},
            (6, 7): {},
            (6, 8): {'PP': Tree.fromstring(
                """
                    (PP
                        (IN with)
                        (NP
                            (DT the)
                            (NN telescope)))
                """)},
            (7, 8): {'NP': Tree.fromstring("(NP (DT the) (NN telescope))")}
        }

        self.assertEqual(parser._bp, bp)

    def test_parse(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP              [1.0]
                NP -> Det Noun          [0.6]
                NP -> Noun Adj          [0.4]
                VP -> Verb NP           [1.0]
                Det -> 'el'             [1.0]
                Noun -> 'gato'          [0.9]
                Noun -> 'pescado'       [0.1]
                Verb -> 'come'          [1.0]
                Adj -> 'crudo'          [1.0]
            """)

        parser = CKYParser(grammar)

        lp, t = parser.parse('el gato come pescado crudo'.split())

        # check chart
        pi = {
            (1, 1): {'Det': log2(1.0)},
            (2, 2): {'Noun': log2(0.9)},
            (3, 3): {'Verb': log2(1.0)},
            (4, 4): {'Noun': log2(0.1)},
            (5, 5): {'Adj': log2(1.0)},

            (1, 2): {'NP': log2(0.6 * 1.0 * 0.9)},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': log2(0.4 * 0.1 * 1.0)},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': log2(1.0) + log2(1.0) + log2(0.4 * 0.1 * 1.0)},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S':
                     log2(1.0) +  # rule S -> NP VP
                     log2(0.6 * 1.0 * 0.9) +  # left part
                     log2(1.0) + log2(1.0) + log2(0.4 * 0.1 * 1.0)},  # R part
        }
        self.assertEqualPi(parser._pi, pi)

        # check partial results
        bp = {
            (1, 1): {'Det': Tree.fromstring("(Det el)")},
            (2, 2): {'Noun': Tree.fromstring("(Noun gato)")},
            (3, 3): {'Verb': Tree.fromstring("(Verb come)")},
            (4, 4): {'Noun': Tree.fromstring("(Noun pescado)")},
            (5, 5): {'Adj': Tree.fromstring("(Adj crudo)")},

            (1, 2): {'NP': Tree.fromstring("(NP (Det el) (Noun gato))")},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': Tree.fromstring("(NP (Noun pescado) (Adj crudo))")},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': Tree.fromstring(
                "(VP (Verb come) (NP (Noun pescado) (Adj crudo)))")},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S': Tree.fromstring(
                """(S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                   )
                """)},
        }
        self.assertEqual(parser._bp, bp)

        # check tree
        t2 = Tree.fromstring(
            """
                (S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                )
            """)
        self.assertEqual(t, t2)

        # check log probability
        lp2 = log2(1.0 * 0.6 * 1.0 * 0.9 * 1.0 * 1.0 * 0.4 * 0.1 * 1.0)
        self.assertAlmostEqual(lp, lp2)

    def assertEqualPi(self, pi1, pi2):
        self.assertEqual(set(pi1.keys()), set(pi2.keys()))

        for k in pi1.keys():
            d1, d2 = pi1[k], pi2[k]
            self.assertEqual(d1.keys(), d2.keys(), k)
            for k2 in d1.keys():
                prob1 = d1[k2]
                prob2 = d2[k2]
                self.assertAlmostEqual(prob1, prob2)

    def test_unaries(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP [0.9]
                S -> VP  [0.1]
                VP -> V NP [0.5]
                VP -> V  [0.1]
                VP -> V VP_V [0.3]
                VP -> V PP [0.1]
                VP_V -> NP PP [1.0]
                NP -> NP NP [0.1]
                NP -> NP PP [0.2]
                NP -> N  [0.7]
                PP -> P NP [1.0]
                N -> 'people' [0.5]
                N -> 'fish'   [0.2]
                N -> 'tanks'  [0.2]
                N -> 'rods'  [0.1]
                V -> 'people'  [0.1]
                V -> 'fish'    [0.6]
                V -> 'tanks'   [0.3]
                P -> 'with'  [1.0]
            """)
        parser = CKYParser(grammar, True)

        lp, t = parser.parse('fish people fish tanks'.split())

        pi = {
            (1, 1): {'N': log2(0.2),
                     'NP': log2(0.14),
                     'S': log2(0.006),
                     'V': log2(0.6),
                     'VP': log2(0.06)
                     },
            (1, 2): {'NP': log2(0.0049),
                     'S': log2(0.0105),
                     'VP': log2(0.105)
                     },
            (1, 3): {'NP': log2(0.0000686),
                     'S': log2(0.000882),
                     'VP': log2(0.00147)
                     },
            (1, 4): {'NP': log2(0.0000009604),
                     'S': log2(0.00018522),
                     'VP': log2(0.00002058)
                     },
            (2, 2): {'N': log2(0.5),
                     'NP': log2(0.35),
                     'S': log2(0.001),
                     'V': log2(0.1),
                     'VP': log2(0.01)
                     },
            (2, 3): {'NP': log2(0.0049),
                     'S': log2(0.0189),
                     'VP': log2(0.007)
                     },
            (2, 4): {'NP': log2(0.0000686),
                     'S': log2(0.01323),
                     'VP': log2(0.000098)
                     },
            (3, 3): {'N': log2(0.2),
                     'NP': log2(0.14),
                     'S': log2(0.006),
                     'V': log2(0.6),
                     'VP': log2(0.06)
                     },
            (3, 4): {'NP': log2(0.00196),
                     'S': log2(0.0042),
                     'VP': log2(0.042)
                     },
            (4, 4): {'N': log2(0.2),
                     'NP': log2(0.14),
                     'S': log2(0.003),
                     'V': log2(0.3),
                     'VP': log2(0.03)
                     }
            }

        bp = {
            (1, 1): {'N': Tree('N', ['fish']),
                     'NP': Tree('NP', [Tree('N', ['fish'])]),
                     'S': Tree('S', [Tree('VP', [Tree('V', ['fish'])])]),
                     'V': Tree('V', ['fish']),
                     'VP': Tree('VP', [Tree('V', ['fish'])])
                     },
            (1, 2): {'NP': Tree('NP',
                                [Tree('NP', [Tree('N', ['fish'])]),
                                 Tree('NP', [Tree('N', ['people'])])]),
                     'S': Tree('S',
                               [Tree('VP', [Tree('V', ['fish']),
                                Tree('NP', [Tree('N', ['people'])])])]),
                     'VP': Tree('VP',
                                [Tree('V', ['fish']),
                                 Tree('NP', [Tree('N', ['people'])])])
                     },
            (1, 3): {'NP': Tree('NP',
                                [Tree('NP',
                                      [Tree('NP', [Tree('N', ['fish'])]),
                                       Tree('NP', [Tree('N', ['people'])])]),
                                 Tree('NP', [Tree('N', ['fish'])])]),
                     'S': Tree('S',
                               [Tree('NP', [Tree('N', ['fish'])]),
                                Tree('VP', [Tree('V', ['people']),
                                     Tree('NP', [Tree('N', ['fish'])])])]),
                     'VP': Tree('VP',
                                [Tree('V', ['fish']),
                                 Tree('NP',
                                 [Tree('NP', [Tree('N', ['people'])]),
                                  Tree('NP', [Tree('N', ['fish'])])])])
                     },
            (1, 4): {'NP': Tree('NP',
                                [Tree('NP', [Tree('N', ['fish'])]),
                                 Tree('NP',
                                      [Tree('NP',
                                            [Tree('NP',
                                                  [Tree('N', ['people'])]),
                                             Tree('NP',
                                                  [Tree('N', ['fish'])])]),
                                       Tree('NP', [Tree('N', ['tanks'])])])]),
                     'S': Tree('S',
                               [Tree('NP',
                                     [Tree('NP', [Tree('N', ['fish'])]),
                                      Tree('NP', [Tree('N', ['people'])])]),
                                Tree('VP', [Tree('V', ['fish']),
                                     Tree('NP', [Tree('N', ['tanks'])])])]),
                     'VP': Tree('VP',
                                [Tree('V', ['fish']),
                                 Tree('NP',
                                      [Tree('NP',
                                            [Tree('NP',
                                                  [Tree('N', ['people'])]),
                                             Tree('NP',
                                                  [Tree('N', ['fish'])])]),
                                       Tree('NP', [Tree('N', ['tanks'])])])])
                     },
            (2, 2): {'N': Tree('N', ['people']),
                     'NP': Tree('NP', [Tree('N', ['people'])]),
                     'S': Tree('S', [Tree('VP', [Tree('V', ['people'])])]),
                     'V': Tree('V', ['people']),
                     'VP': Tree('VP', [Tree('V', ['people'])])
                     },
            (2, 3): {'NP': Tree('NP',
                                [Tree('NP', [Tree('N', ['people'])]),
                                 Tree('NP', [Tree('N', ['fish'])])]),
                     'S': Tree('S',
                               [Tree('NP', [Tree('N', ['people'])]),
                                Tree('VP', [Tree('V', ['fish'])])]),
                     'VP': Tree('VP',
                                [Tree('V', ['people']),
                                 Tree('NP', [Tree('N', ['fish'])])])
                     },
            (2, 4): {'NP': Tree('NP',
                                [Tree('NP',
                                      [Tree('NP', [Tree('N', ['people'])]),
                                       Tree('NP', [Tree('N', ['fish'])])]),
                                 Tree('NP', [Tree('N', ['tanks'])])]),
                     'S': Tree('S',
                               [Tree('NP', [Tree('N', ['people'])]),
                                Tree('VP', [Tree('V', ['fish']),
                                     Tree('NP', [Tree('N', ['tanks'])])])]),
                     'VP': Tree('VP',
                                [Tree('V', ['people']),
                                 Tree('NP',
                                      [Tree('NP', [Tree('N', ['fish'])]),
                                       Tree('NP', [Tree('N', ['tanks'])])])])
                     },
            (3, 3): {'N': Tree('N', ['fish']),
                     'NP': Tree('NP', [Tree('N', ['fish'])]),
                     'S': Tree('S', [Tree('VP', [Tree('V', ['fish'])])]),
                     'V': Tree('V', ['fish']),
                     'VP': Tree('VP', [Tree('V', ['fish'])])
                     },
            (3, 4): {'NP': Tree('NP',
                                [Tree('NP', [Tree('N', ['fish'])]),
                                 Tree('NP', [Tree('N', ['tanks'])])]),
                     'S': Tree('S',
                               [Tree('VP', [Tree('V', ['fish']),
                                Tree('NP', [Tree('N', ['tanks'])])])]),
                     'VP': Tree('VP',
                                [Tree('V', ['fish']),
                                 Tree('NP', [Tree('N', ['tanks'])])])
                     },
            (4, 4): {'N': Tree('N', ['tanks']),
                     'NP': Tree('NP', [Tree('N', ['tanks'])]),
                     'S': Tree('S', [Tree('VP', [Tree('V', ['tanks'])])]),
                     'V': Tree('V', ['tanks']),
                     'VP': Tree('VP', [Tree('V', ['tanks'])])
                     }
            }

        t2 = Tree('S',
                  [Tree('NP', [Tree('NP', [Tree('N', ['fish'])]),
                        Tree('NP', [Tree('N', ['people'])])]),
                   Tree('VP', [Tree('V', ['fish']),
                        Tree('NP', [Tree('N', ['tanks'])])])])
        self.maxDiff = None
        self.assertEqualPi(parser._pi, pi)
        self.assertEqual(parser._bp, bp)
        self.assertEqual(t, t2)
        self.assertAlmostEqual(lp,
                               log2(0.9 * 0.1 * 0.7 *
                                    0.2 * 0.7 * 0.5 *
                                    0.5 * 0.6 * 0.7 * 0.2))
