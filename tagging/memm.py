from tagging.features import (History, word_lower, word_istitle, word_isupper,
                              word_isdigit, prev_tags, NPrevTags, PrevWord)
from itertools import chain
from featureforge.vectorizer import Vectorizer

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

class MEMM:

    def __init__(self, n, tagged_sents):
        """
        n -- order of the model.
        tagged_sents -- list of sentences, each one being a list of pairs.
        """
        # Calculo V para palabras desconocidas
        words, tags = zip(*list(chain.from_iterable(tagged_sents)))
        tags = None
        self.V = set(words)
        words = None

        self.n = n
        # Pipeline
        features = [word_lower, word_istitle, word_isupper,
                    word_isdigit, prev_tags, NPrevTags(n)]
        f2 = []
        for f in features:
            f2 += [PrevWord(f)]
        features += f2

        vectorizer = Vectorizer(features)
        classif = LogisticRegression()
        pipe = Pipeline([('vect', vectorizer),
                         ('clasif', classif)])
        histories = self.sents_histories(tagged_sents)
        tags = self.sents_tags(tagged_sents)
        pipe = pipe.fit(histories, tags)

        self.pipe = pipe

    def sents_histories(self, tagged_sents):
        """
        Iterator over the histories of a corpus.

        tagged_sents -- the corpus (a list of sentences)
        """
        l_h = []
        for tagged_sent in tagged_sents:
            s_h = self.sent_histories(tagged_sent)
            l_h = l_h + s_h

        return l_h

    def sent_histories(self, tagged_sent):
        """
        Iterator over the histories of a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        # Armar las histories
        n = self.n
        list_histories = []
        if tagged_sent != []:
            sent, tags = list(zip(*tagged_sent))
            sent = list(sent)
            tags = list(tags)
            m = len(sent)
            tags[0:0] = (n-1)*['<s>']
            list_histories = []
            for k, i in zip(range(n - 1, m + n), range(m)):
                hn = History(sent, tuple(tags[k-n+1:k]), i)
                list_histories.append(hn)

        return list_histories

    def sents_tags(self, tagged_sents):
        """
        Iterator over the tags of a corpus.

        tagged_sents -- the corpus (a list of sentences)
        """
        l_t = []
        for tagged_sent in tagged_sents:
            t_i = self.sent_tags(tagged_sent)
            l_t = l_t + t_i

        return l_t

    def sent_tags(self, tagged_sent):
        """
        Iterator over the tags of a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        tags = []
        if tagged_sent != []:
            sent, tags = zip(*tagged_sent)
            tags = list(tags)
        return tags

    def tag(self, sent):
        """Tag a sentence.

        sent -- the sentence.
        """
        n = self.n
        prev_tags = (n-1) * ('<s>',)
        result = []
        for i in range(len(sent)):
            # Contruir una history
            h = History(sent, prev_tags, i)
            tag = self.tag_history(h)
            prev_tags = prev_tags + tuple(tag)
            prev_tags = prev_tags[1:]
            result += tag

        return result

    def tag_history(self, h):
        """Tag a history.

        h -- the history.
        """
        return self.pipe.predict([h])

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return not w in self.V
