# https://docs.python.org/3/library/collections.html
from collections import defaultdict
from math import log2


class NGram(object):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        self.counts = counts = defaultdict(int)
        for sent in sents:
            sent[0:0] += (n-1) * ['<s>']
            sent.append('</s>')
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i: i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1

    def prob(self, token, prev_tokens=None):
        n = self.n
        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == n - 1

        tokens = prev_tokens + [token]
        return float(self.counts[tuple(tokens)]) / self.counts[tuple(prev_tokens)]

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """
        return self.counts[tokens]

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = []
        return float(self.count(tuple(prev_tokens+[token]))) / self.count(tuple(prev_tokens))


    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.

        sent -- the sentence as a list of tokens.
        """
        n = self.n
        sent[0:0] += (n-1) * ['<s>']
        sent.append('</s>')
        result = 1
        for k in range(n-1,len(sent)):
            result = result * self.cond_prob(sent[k],sent[k-n+1:k])
            if result == 0:
                break
        return result

    def sent_log_prob(self, sent):
        """Log-probability of a sentence.

        sent -- the sentence as a list of tokens.
        """
        n = self.n
        sent[0:0] += (n-1) * ['<s>']
        sent.append('</s>')
        result = 0
        for k in range(n-1,len(sent)):
            c_prob = self.cond_prob(sent[k],sent[k-n+1:k])
            if c_prob == 0:
                result = float('-inf')
                break
            result += log2(c_prob)
        return result

class NGramGenerator:

    def __init__(self, model):
        """
        model -- n-gram model.
        """
        self.model = model
    def generate_sent(self):
        """Randomly generate a sentence."""

    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.

        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """

class AddOneNGram:

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        self.counts = counts = defaultdict(int)
        for sent in sents:
            sent[0:0] += (n-1) * ['<s>']
            sent.append('</s>')
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i: i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1


    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """
        return self.counts[tokens]


    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = []
        return float(self.count(tuple(prev_tokens+[token]))+1) / (self.count(tuple(prev_tokens)) + self.V())


    def V(self):
        """Size of the vocabulary.
        """

        v = set()
        for word, count in self.counts.items():
            if count > 0:
                v = v.union(set(word))

        if self.n > 1:
            v.remove('<s>')
        return len(v)
