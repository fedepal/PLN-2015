"""Train a sequence tagger.

Usage:
  train.py [-m <model>] [-n <n>] -o <file>
  train.py -h | --help

Options:
  -m <model>    Model to use [default: base]:
                  base: Baseline
                  mlhmm: MLHMM
  -n <n>        n-gram [default: 2]
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from corpus.ancora import SimpleAncoraCorpusReader
from tagging.baseline import BaselineTagger
from tagging.hmm import MLHMM
from tagging.memm import MEMM


models = {
    'base': BaselineTagger,
    'mlhmm': MLHMM,
    'memm': MEMM
}


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    files = 'CESS-CAST-(A|AA|P)/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)
    sents = list(corpus.tagged_sents())

    # train the model
    model = opts['-m']
    n = int(opts['-n'])
    if model == 'base':
        model = models[model](sents)
    if model == 'mlhmm':
        model = models[model](n, sents)
    if model == 'memm':
        model = models[model](n, sents)
    # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
