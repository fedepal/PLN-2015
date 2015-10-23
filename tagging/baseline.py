from collections import defaultdict
from itertools import chain


class BaselineTagger:

    def __init__(self, tagged_sents):
        """
        tagged_sents -- training sentences, each one being a list of pairs.
        """
        tagged_sents = list(chain.from_iterable(tagged_sents))
        tag_sents = defaultdict(lambda: defaultdict(int))
        tags = defaultdict(int)

        for w, t in tagged_sents:
            tag_sents[w][t] += 1
        self.tag_sents = dict(tag_sents)

        # Calculate most frequent tag
        for w, t in tagged_sents:
            tags[t] += 1
        tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
        self.tag_frequent = tags[0][0]

    def tag(self, sent):
        """Tag a sentence.

        sent -- the sentence.
        """
        return [self.tag_word(w) for w in sent]

    def tag_word(self, w):
        """Tag a word.

        w -- the word.
        """
        r = self.tag_sents.get(w)
        if r is None:
            r = self.tag_frequent
        else:
            r = max(r, key=lambda k: r[k])
        return r

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        r = self.tag_sents.get(w)

        if r is None:
            r = True
        else:
            r = False
        return r
