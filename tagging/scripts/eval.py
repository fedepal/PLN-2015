"""Evaulate a tagger.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Tagging model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle
import sys

from corpus.ancora import SimpleAncoraCorpusReader


def progress(msg, width=None):
    """Ouput the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the model
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    # load the data
    files = '3LB-CAST/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/', files)
    sents = list(corpus.tagged_sents())

    # tag
    hits, total = 0, 0
    n = len(sents)
    unknown = 0
    hits_unk = 0
    for i, sent in enumerate(sents):
        word_sent, gold_tag_sent = zip(*sent)

        model_tag_sent = model.tag(word_sent)
        for (w, gt), mt in zip(sent,model_tag_sent):
            if model.unknown(w):
                unknown += 1
                if gt == mt:
                    hits_unk += 1
        # global score
        hits_sent = [m == g for m, g in zip(model_tag_sent, gold_tag_sent)]
        hits += sum(hits_sent)
        total += len(sent)
        acc = float(hits) / total
        acc_u = float(hits_unk) / unknown
        acc_k = float(hits - hits_unk) /  (total - unknown)
        progress('{:3.1%} ({:2.2%} / {:2.2%} / {:2.2%})'.format(float(i)/ n,
                                                                acc,
                                                                acc_k,
                                                                acc_u
                                                                ))

    acc = float(hits) / total
    acc_u = float(hits_unk) / unknown
    acc_k = float(hits - hits_unk) /  (total - unknown)

    print('\nAccuracy: {:2.2%} known {:.2%}\tunknown {:.2%}'.format(acc, acc_k, acc_u))

    # Matriz de confusion
