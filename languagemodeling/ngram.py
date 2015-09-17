# https://docs.python.org/3/library/collections.html
from collections import defaultdict
from math import log2
from random import random
from itertools import chain

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
            for i in range(0,n-1):
                sent.pop(0)
            sent.pop()

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
        assert len(prev_tokens) == self.n - 1

        prev_count = self.count(tuple(prev_tokens))
        if prev_count == 0:
            return 0

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
        for i in range(0,n-1):
            sent.pop(0)
        sent.pop()
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
                result = -float('inf')
                break
            result += log2(c_prob)
        for i in range(0,n-1):
            sent.pop(0)
        sent.pop()
        return result

    def log_probability(self, sents):
        log_prob = 0
        for sent in sents:
            log_prob += self.sent_log_prob(sent)

        return log_prob

    def cross_entropy(self, sents):

        log_prob = self.log_probability(sents)

        num_words = len(list(chain.from_iterable(sents))) + len(sents) # (+ #</s>)

        return (1.0/num_words)*log_prob

    def perplexity(self,sents):

        cross_entropy = self.cross_entropy(sents)

        perplexity = pow (2,-cross_entropy)

        return perplexity

class AddOneNGram(NGram):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """

        super().__init__(n,sents)

        #Vocabulary Size
        self.v = len(set(list(chain.from_iterable(sents)))) + 1

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
        return self.v

class NGramGenerator:

    def __init__(self, model):
        """
        model -- n-gram model.
        """

        self.probs = probs =defaultdict(dict)
        self.sorted_probs = sorted_probs = defaultdict(dict)
        self.n = model.n
        for k in model.counts.keys():
            if len(k) == model.n:
                probs[k[:-1]].update({k[model.n-1]:model.cond_prob(k[model.n-1],list(k[:-1]))})

        for k,v in probs.items():
            sorted_probs[k] = sorted(v.items(),key=lambda x: (x[1],x[0]),reverse=True)

    def generate_sent(self):
        """Randomly generate a sentence."""

        prev_tokens = (self.n-1) * ['<s>']
        generated = ''
        sent = []
        while not generated == '</s>':
            generated = self.generate_token(prev_tokens)
            prev_tokens.append(generated)
            prev_tokens = prev_tokens[1:]
            sent += [generated]
        return sent[:-1]

    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.

        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """

        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == self.n - 1

        words = self.sorted_probs[tuple(prev_tokens)]
        print(words)
        i=0
        accum = words [0][1]
        r = random()

        while r > accum:
            i += 1
            accum += words[i][1]
        assert(r <= accum)
        return words[i][0]


class InterpolatedNGram(NGram):

    def __init__(self, n, sents, gamma=None, addone=True):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        gamma -- interpolation hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """
        self.n = n
        if not gamma:
            held_out = sents[int(0.9*len(sents)):]
            sents = sents[:int(0.9*len(sents))]
            gamma = self.estimate_gamma(sents, held_out, addone)

        self.gamma = gamma
        self.models=[]

        if addone:
            self.models.append(AddOneNGram(1,sents))
        else:
            self.models.append(NGram(1,sents))
        for i in range(2,n+1):
            self.models.append(NGram(i,sents))

        self.counts = self.models[n-1].counts

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """

        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == self.n - 1
        result = 0
        lamb = 0
        lamb_n = 0
        for i in range(self.n,0,-1):
            #N, N-1, .. Unigrama
            if i == 1:
                lamb = 1.0 - lamb_n
            else:
                count = self.models[i-1].count(tuple(prev_tokens))
                lamb = (1.0 - lamb_n) * (count/(count + self.gamma))
                lamb_n = lamb_n + lamb # VER EL LAMBDA DISTINTO, SE PUEDE SACAR LAMB_N

            result += lamb * self.models[i-1].cond_prob(token,prev_tokens)
            prev_tokens = prev_tokens[1:]

        return result

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """
        size = len(tokens)
        if size == 0: #Para evitar que () se vaya de rango
            size = 1
        count = self.models[size-1].count(tokens)

        return count

    def estimate_gamma(self, sents, held_out, addone):

        #Minimizar Perplexity

        values = [i*100 for i in range(8,13)]
        values.reverse()
        n = self.n
        perpl = 0
        model = None
        l_perpl = []
        for gamma in values:
            model = InterpolatedNGram(n, sents, gamma, addone)
            perpl = model.perplexity(held_out)
            l_perpl.append((perpl,gamma))
        r = min(l_perpl)[1]

        return r

class BackOffNGram:

    def __init__(self, n, sents, beta=None, addone=True):
        """
        Back-off NGram model with discounting as described by Michael Collins.

        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        beta -- discounting hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """

    """
       Todos los métodos de NGram.
    """

    def A(self, tokens):
        """Set of words with counts > 0 for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """

    def alpha(self, tokens):
        """Missing probability mass for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """

    def denom(self, tokens):
        """Normalization factor for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
