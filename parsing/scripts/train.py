"""Train a parser.

Usage:
  train.py [-m <model>] -o <file>
  train.py -m upcfg [--horzMarkov=<n>] [-u | --unary] -o <file>
  train.py -h | --help

Options:
  -m <model>        Model to use [default: flat]:
                      flat: Flat trees
                      rbranch: Right branching trees
                      lbranch: Left branching trees
                      upcfg: Unlexicalized PCFG
  --horzmMarkov=<n> Use Markov n
  -u --unary        Unary productions in upcfg
  -o <file>         Output model file.
  -h --help         Show this screen.
"""
from docopt import docopt
import pickle

from corpus.ancora import SimpleAncoraCorpusReader

from parsing.baselines import Flat, RBranch, LBranch
from parsing.upcfg import UPCFG


models = {
    'flat': Flat,
    'rbranch': RBranch,
    'lbranch': LBranch,
    'upcfg': UPCFG
}


if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading corpus...')
    files = 'CESS-CAST-(A|AA|P)/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)

    print('Training model...')
    markov = opts['--horzMarkov']
    m = opts['-m']
    unary = opts['--unary']
    if m == 'upcfg':
        if markov is not None:
            print("UPCFG with Markov order {} \
                   and Unary productions = {}".format(markov, unary))
            model = models[m](corpus.parsed_sents(),
                              horzMarkov=int(markov),
                              unary=unary)
        else:
            print("UPCFG with Unary productions = {}".format(unary))
            model = models[m](corpus.parsed_sents(), unary=unary)

    else:
        model = models[m](corpus.parsed_sents())

    # if markov is not None:
    #     model = models[opts['-m']](corpus.parsed_sents(), markov=int(markov))
    # else:
    #     model = models[opts['-m']](corpus.parsed_sents())

    print('Saving...')
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
