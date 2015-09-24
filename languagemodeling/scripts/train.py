"""Train an n-gram model.

Usage:
  train.py -n <n> [-m <model>] -o <file>
  train.py -n <n> -m inter [-g <gamma>] [--addone] -o <file>
  train.py -n <n> -m backoff [-b <beta>] [--addone] -o <file>
  train.py -h | --help

Options:
  -n <n>        Order of the model.
  -m <model>    Model to use [default: ngram]:
                  ngram: Unsmoothed n-grams.
                  addone: N-grams with add-one smoothing.
                  inter: N-gramas with interpolation.
                  backoff: N-gramas with back-off and discounting.
  -g <gamma>    Gamma value for Interpolation.
  --addone      Use addone for Interpolation
  -b <beta>     Beta value for Back-off
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from nltk import RegexpTokenizer
from nltk.corpus import PlaintextCorpusReader
from nltk.data import LazyLoader
from languagemodeling.ngram import NGram, AddOneNGram, InterpolatedNGram
from languagemodeling.ngram import BackOffNGram


if __name__ == '__main__':
    opts = docopt(__doc__)

    pattern = r'''(?ix)    # set flag to allow verbose regexps
            sr(es)?\. | sras?\. | etc\.
            | ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
            | \w+(-\w+)*        # words with optional internal hyphens
            | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
            | \.\.\.            # ellipsis
            | [][.,;"'?():-_`]  # these are separate tokens; includes ],
            '''
    tokenizer = RegexpTokenizer(pattern)
    lazyloader = LazyLoader('tokenizers/punkt/spanish.pickle')
    # load the data
    sents = PlaintextCorpusReader('../corpus',
                                  '.*\.txt',
                                  word_tokenizer=tokenizer,
                                  sent_tokenizer=lazyloader).sents()

    # slice data 90% train data
    sents = sents[:int(0.9*len(sents))]

    # train the model
    n = int(opts['-n'])
    m = (opts['-m'])

    if m == "ngram":
        model = NGram(n, sents)
    elif m == "addone":
        model = AddOneNGram(n, sents)
    elif m == "inter":
        gamma = opts['-g']
        addone = opts['--addone']
        if gamma is not None:
            gamma = float(gamma)
        model = InterpolatedNGram(n, sents, gamma, addone)
    elif m == "backoff":
        beta = opts['-b']
        if beta is not None:
            beta = float(beta)
        addone = opts['--addone']
        model = BackOffNGram(n, sents, beta, addone)
    else:
        print(__doc__)
        exit(0)

    # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
