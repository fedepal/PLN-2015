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
from collections import defaultdict, Counter

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
        words[(w,t)] += 1
        tags[t] += 1

    ocurrences = sum(words.values())
    print('ocurrences: {}'.format(ocurrences))
    # compute vocabulary
    v = len(words)
    print('V: {}'.format(v))
    # compute tags vocabulary
    k = len(tags)
    print('K: {}'.format(k))

    # Tags more frecuents

    words = sorted(words.items(), key=lambda x: x[1], reverse=True)
    tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)

    freq = defaultdict(tuple)
    for tag in tags[:10]:
        i = 0
        while len(freq[tag[0]]) < 5 and i < len(words):
            if words[i][0][1] == tag[0]:
                freq[tag[0]] += (words[i][0][0],)
            i += 1
    print("\nTags")
    print('tag\tfreq\t%\ttop5')
    i = 0
    while i in range(0,10):
        print('{0}\t{1}\t{2:2.2%}\t{3}\t'.format(tags[i][0],tags[i][1],tags[i][1]/ocurrences,' '.join(freq[tags[i][0]])))
        i += 1

    #ambiguity

    t1, t2 = zip(*words)  # t1 (x1,x2), x1 = word, x2 = tag t2 = (counts)
    a1, a2 = zip(*t1)  # a1: Words, a2: tags, words with repeats(repetitions)
    t1 = None
    a2 = None
    words_counts = zip(a1,t2)
    t2 = None
    c = Counter(a1)  # Cuenta palabras repetidas en a1
    a1 = None
    amb = Counter(c.values())  # Cuenta cantidad de repeticiones de palabras

    l_amb = defaultdict(lambda : ('',0,0))
    for w,co in words_counts:
        l_amb[w] = (w,l_amb[w][1] + co, c[w])
    l_amb = l_amb.values()

    l_amb = sorted(l_amb, key=lambda x:(x[2],x[1]),reverse=True)

    # Ya ordenadas por frecuencia y ambiguedad, deshacemos de los counts

    l_amb, a, b = zip(*l_amb)
    a = None
    b = None
    result = defaultdict(tuple)
    i = 10
    index = 0
    while len(result) < 10:  # FIX las palabras no son las más frecuentes
        i -= 1
        index += amb[i]
        result[i]
        if index != 0 and amb[i]>=5:
            result[i] = tuple(l_amb[:5])
        else:
            result[i] = tuple(l_amb[0:amb[i]])
        l_amb = l_amb[amb[i]:]
    print("\nWords")
    print('n\twords\t%\texamples')
    for i in range(1,10):
        print('{0}\t{1}\t{2:2.2%}\t{3}'.format(i,amb[i],amb[i]/v,' '.join(result[i])))


# l1,l2 = zip(*c)
#*t desarma tuplas
#**d desarma diccionarios
#calcular tokens: la cantidad de ocurrencias de palabras

#tag freq % top
#nc 999 17.79 (años,presidente....)5

# n words % top5
