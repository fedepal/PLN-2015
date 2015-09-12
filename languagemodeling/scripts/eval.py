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

from math import pow
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
     sents = PlaintextCorpusReader('../../corpus','.*\.txt',word_tokenizer=tokenizer,
                                 sent_tokenizer=LazyLoader('tokenizers/punkt/spanish.pickle')).sents()

     #Slice data 10% test data
     sents = sents[-int(0.1*len(sents)):]

     #Perplexity

     filename = opts['-i']
     f = open(filename,"rb")

     model = pickle.load(f)

     log_prob = 0
     num_words = 0
     for sent in sents:
         log_prob += model.sent_log_prob(sent)
         num_words += len(sent)

     cross-entropy = -(1.0/num_words)*log_prob
     perplexity = pow (2,cross-entropy)

     print ("Perplexity: ", perplexity)
