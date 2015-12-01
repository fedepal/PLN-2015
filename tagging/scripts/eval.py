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
from collections import defaultdict
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
    conf_matrix = defaultdict(lambda: defaultdict(int))
    conf_count = 0

    for i, sent in enumerate(sents):
        word_sent, gold_tag_sent = zip(*sent)

        model_tag_sent = model.tag(word_sent)
        for (w, gt), mt in zip(sent, model_tag_sent):
            # si la palabra es desconocida
            if model.unknown(w):
                # la cuento
                unknown += 1
                if gt == mt:
                    # cuento el hit, y el hit de desconocida
                    hits += 1
                    hits_unk += 1
                else:
                    # Si no hay hit, cuento el error, y agrego a la celda de
                    # la matriz que corresponde.
                    conf_count += 1
                    conf_matrix[gt][mt] += 1
            else:
                # La palabra es conocida
                if gt == mt:
                    # Contamos el hit
                    hits += 1
                else:
                    # no hay hit, contamos el error
                    conf_count += 1
                    conf_matrix[gt][mt] += 1
        # global score
        # hits_sent = [m == g for m, g in zip(model_tag_sent, gold_tag_sent)]
        # hits += sum(hits_sent)
        total += len(sent)
        acc = float(hits) / total
        acc_u = float(hits_unk) / unknown
        acc_k = float(hits - hits_unk) / (total - unknown)
        progress('{:3.1%} ({:2.2%} / {:2.2%} / {:2.2%})'.format(float(i) / n,
                                                                acc,
                                                                acc_k,
                                                                acc_u
                                                                ))

    acc = float(hits) / total
    acc_u = float(hits_unk) / unknown
    acc_k = float(hits - hits_unk) / (total - unknown)

    print('\nAccuracy: {:2.2%} known {:.2%}\tunknown {:.2%}'.format(acc,
                                                                    acc_k,
                                                                    acc_u))

    # Matriz de confusion
    # 10 etiquetas frecuentas extraidas de stats.py
    most_frq_tags = ('nc', 'sp', 'da', 'vm', 'aq', 'np', 'rg', 'cc', 'di', 'cs')

    print('   ', end='')
    print('   |'.join(most_frq_tags))
    for gtag in most_frq_tags:
        # Normalizamos los conteos con la suma de la fila
        norm = sum(conf_matrix[gtag].values())
        print("{}|".format(gtag), end='')
        for ptag in most_frq_tags:
            print("{:.2}|".format(conf_matrix[gtag][ptag]/norm), end=' ')
        print('\n')
