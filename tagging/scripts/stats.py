"""Print corpus statistics.

Usage:
  stats.py
  stats.py -h | --help

Options:
  -h --help     Show this screen.
"""
from docopt import docopt

from corpus.ancora import SimpleAncoraCorpusReader
from itertools import chain


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    corpus = SimpleAncoraCorpusReader('ancora/ancora-2.0/')
    sents = corpus.tagged_sents()

    # compute the statistics
    print('sents: {}'.format(len(sents)))
    #compute ocurrences

    sents = list(chain.from_iterable(sents))
    words = defaultdict(int)
    tags = defaultdict(int)
    for w, t in sents:
        words[w] += 1
        tags[t] += 1
    ocurrences = sum(words.values())
    # compute vocabulary
    v = len(words)
    # compute tags vocabulary
    s = len(tags)

    # Tags more frecuents

    

# l1,l2 = zip(*c)
#*t desarma tuplas
#**d desarma diccionarios
#calcular tokens: la cantidad de ocurrencias de palabras

#tag freq % top
#nc 999 17.79 (años,presidente....)5

# n words % top5
