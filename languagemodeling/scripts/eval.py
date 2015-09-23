"""Evaulate a language model using the test set.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Language model file.
  -h --help     Show this screen.
 """
from docopt import docopt
import pickle

from nltk import RegexpTokenizer
from nltk.corpus import PlaintextCorpusReader
from nltk.data import LazyLoader

if __name__ == '__main__':
    opts = docopt(__doc__)

    pattern = r'''(?ix)    # set flag to allow verbose regexps
             sr(es)?\. | sras?\. | etc\.
             | ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
             | \w+(-\w+)*        # words with optional internal hyphens
             | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
             | \.\.\.            # ellipsis
             | [][.,;"'?():-_`]  # these are separate tokens; includes [],
             '''
    tokenizer = RegexpTokenizer(pattern)

    # load the data
    lazyloader = LazyLoader('tokenizers/punkt/spanish.pickle')
    sents = PlaintextCorpusReader('../corpus', '.*\.txt', word_tokenizer=tokenizer,
                                  sent_tokenizer=lazyloader).sents()

    # Slice data 10% test data

    held_out = sents[int(0.9*len(sents)):]

    filename = opts['-i']
    f = open(filename, "rb")

    model = pickle.load(f)

    l_prob = model.log_probability(held_out)
    c_entr = model.cross_entropy(held_out)
    perpl = model.perplexity(held_out)

    print("Log Probability: ", l_prob)
    print("Cross Entropy: ", c_entr)
    print("Perplexity: ", perpl)
