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
            for i in range(0, n-1):
                sent.pop(0)
            sent.pop()

    def prob(self, token, prev_tokens=None):
        n = self.n
        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == n - 1

        tokens = prev_tokens + [token]
        tokens = tuple(tokens)
        return float(self.counts[tokens]) / self.counts[tuple(prev_tokens)]

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
        for k in range(n-1, len(sent)):
            result = result * self.cond_prob(sent[k], sent[k-n+1:k])
            if result == 0:
                break
        for i in range(0, n-1):
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
        for k in range(n-1, len(sent)):
            c_prob = self.cond_prob(sent[k], sent[k-n+1:k])
            if c_prob == 0:
                result = -float('inf')
                break
            result += log2(c_prob)
        for i in range(0, n-1):
            sent.pop(0)
        sent.pop()
        return result

    def log_probability(self, sents):
        log_prob = 0
        for sent in sents:
            sent_l_prob = self.sent_log_prob(sent)
            if sent_l_prob == -float('inf'):
                return -float('inf')
            log_prob += sent_l_prob
        return log_prob

    def cross_entropy(self, sents):

        log_prob = self.log_probability(sents)
        if log_prob == -float('inf'):
            return -float('inf')

        num_words = len(list(chain.from_iterable(sents))) + len(sents)  # (+ # </s>)

        return (1.0/num_words)*log_prob

    def perplexity(self, sents):

        cross_entropy = self.cross_entropy(sents)
        if cross_entropy == -float('inf'):
            return float('inf')

        perplexity = pow(2, -cross_entropy)

        return perplexity


class AddOneNGram(NGram):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """

        super().__init__(n, sents)

        # Vocabulary Size
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

        self.probs = probs = defaultdict(dict)
        self.sorted_probs = sorted_probs = defaultdict(dict)
        self.n = model.n

        for k in model.counts.keys():
            if len(k) == model.n:
                # probs[k[:-1]].update({k[model.n-1]:model.cond_prob(k[model.n-1], list(k[:-1]))})
                probs[k[:-1]][k[model.n-1]] = model.cond_prob(k[model.n-1], list(k[:-1]))

        for k, v in probs.items():
            sorted_probs[k] = sorted(v.items(), key=lambda x: (x[1], x[0]), reverse=True)

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

        i = 0
        accum = words[0][1]
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
        self.models = []

        if addone:
            self.models.append(AddOneNGram(1, sents))
        else:
            self.models.append(NGram(1, sents))
        for i in range(2, n+1):
            self.models.append(NGram(i, sents))

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
        for i in range(self.n, 0, -1):
            # N, N-1, .. Unigrama
            if i == 1:
                lamb = 1.0 - lamb_n
            else:
                count = self.models[i-1].count(tuple(prev_tokens))
                lamb = (1.0 - lamb_n) * (count/(count + self.gamma))
                lamb_n = lamb_n + lamb  # VER EL LAMBDA DISTINTO, SE PUEDE SACAR LAMB_N

            result += lamb * self.models[i-1].cond_prob(token, prev_tokens)
            prev_tokens = prev_tokens[1:]

        return result

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """
        size = len(tokens)
        if size == 0:  # Para evitar que () se vaya de rango
            size = 1
        count = self.models[size-1].count(tokens)

        return count

    def estimate_gamma(self, sents, held_out, addone):

        # Minimizar Perplexity

        values = [i*100 for i in range(8, 13)]
        values.reverse()
        n = self.n
        perpl = 0
        model = None
        l_perpl = []
        for gamma in values:
            model = InterpolatedNGram(n, sents, gamma, addone)  # Los counts son lo mismos, se podría obviar el calculo.
            perpl = model.perplexity(held_out)
            l_perpl.append((perpl, gamma))
        r = min(l_perpl)[1]

        return r


class BackOffNGram(NGram):

    def __init__(self, n, sents, beta=None, addone=True):
        """
        Back-off NGram model with discounting as described by Michael Collins.

        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        beta -- discounting hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """
        assert(n > 0)
        self.n = n
        self.counts = counts = defaultdict(int)
        self.beta = beta
        self.addone = addone
        self.A_dict = defaultdict(set)
        self.denom_dict = defaultdict(float)
        self.alpha_dict = defaultdict(float)

        if beta is None:
            held_out = sents[int(0.9*len(sents)):]
            sents = sents[:int(0.9*len(sents))]

        if addone:
            self.v = len(set(list(chain.from_iterable(sents)))) + 1

        for sent in sents:
            sent[0:0] += (n-1) * ['<s>']
            sent.append('</s>')
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i: i + n])
                counts[ngram] += 1
                for j in range(1, n+1):
                    counts[ngram[j:]] += 1
            for i in range(0, n-1):
                sent.pop(0)
            sent.pop()

        len_sents = len(sents)
        for i in range(1, n):
            # (len_sents= 2) bigrama -> <s>:2 | trigrama <s>:4 <s><s>:2 |
            # 4grama <s>:6 <s><s>:4 <s><s><s>:2|
            counts[i*('<s>', )] = (n-i) * len_sents

        self.counts = dict(self.counts)
        # Discounting beta/Falta estimar beta

        if self.beta is None:
            self.beta = self.estimate_beta(held_out)

        self.counts_beta = counts_beta = defaultdict(float)
        for k, v in counts.items():
            counts_beta[k] = v - self.beta

        self.compute_A()
        self.compute_alpha()
        self.compute_denom()

        self.A_dict = dict(self.A_dict)
        self.denom_dict = dict(self.denom_dict)
        self.alpha_dict = dict(self.alpha_dict)

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """
        return self.counts.get(tokens,0)

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        result = 0
        if not prev_tokens:
            if not self.addone:
                result = self.count((token, ))/self.count(tuple())
            else:
                result = (self.count((token, )) + 1)/(self.count(tuple()) + self.v)
        else:
            prev_tokens = tuple(prev_tokens)
            # pt = (pt + [token]) [1]  != pt[1:]+[token]
            if self.count(prev_tokens + (token,)) > 0:
                result = self.counts_beta[prev_tokens+(token, )] / self.count(prev_tokens)
            else:
                alpha = self.alpha(prev_tokens)
                if alpha == 0:
                    result = 0
                else:
                    result = alpha * self.cond_prob(token, list(prev_tokens[1:])) / self.denom(prev_tokens)

        return result

    def compute_alpha(self):
        print("Calculando Alpha")
        for k in self.counts.keys():
            # Calcular el alpha por ej: P(w|v) -> alpha(v). Calculo para prev_tokens
            self.alpha_dict[k] = (self.beta * len(self.A(k))) / self.count(k)
            # self.alpha_dict[k[:-1]] = 1.0 - sum(self.counts_beta[k[:-1] + (w, )]/self.counts[k[:-1]] for w in self.A(k[:-1]))

    def compute_denom(self):  # Se puede mejorar
        print("Calculando denominador normalizador")
        if not self.addone:
            for ngram in self.counts.keys():
                if len(ngram) == 1:
                    self.denom_dict[ngram] = 1.0 - sum(self.count((k,) )/self.count(()) for k in self.A(ngram))
        else:
            for ngram in self.counts.keys():
                if len(ngram) == 1:
                    self.denom_dict[ngram] = 1.0 - sum((self.count((k,)) +1)/(self.count(())+self.v) for k in self.A(ngram))
        for ngram in self.counts.keys():
            if len(ngram) > 1:
                self.denom_dict[ngram] = 1.0 - sum(self.cond_prob(k, list(ngram[1:])) for k in self.A(ngram))


    def compute_A(self):
        print("Calculando A")
        for k, v in self.counts.items():
            if (v > 0):
                try: self.A_dict[k[:-1]].add(k[-1:][0])
                except IndexError:  # Usar un IF
                    continue


    def A(self, tokens):
        """Set of words with counts > 0 for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """
        # if len(tokens) == 0:
        #     return set([])
        # a = []
        # for k in self.counts.keys():
        #     if k[:-1] == tokens:
        #         a.append(k[-1:][0])  # La ultima parte de la tupla y solo la palabra de la tupla
        # return set(a)
        return self.A_dict.get(tokens,set())




    def alpha(self, tokens):
        """Missing probability mass for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """

        # result = 1.0 - sum(self.counts_beta[tokens + (w, )]/self.counts[tokens] for w in self.A(tokens))

        # return result

        return self.alpha_dict.get(tokens,1.0)

    def denom(self, tokens):
        """Normalization factor for a k-gram with 0 < k < n.

        tokens -- the k-gram tuple.
        """

        return self.denom_dict.get(tokens,1.0)

    def estimate_beta(self, held_out):

        print("Estimando beta")
        l_perpl = []

        for b in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]:
            self.counts_beta = counts_beta = defaultdict(float)
            for k, v in self.counts.items():
                counts_beta[k] = v - b
            print("beta,,,,",b)
            self.beta = b
            self.denom_dict = defaultdict(float)
            self.alpha_dict = defaultdict(float)
            self.A_dict = defaultdict(set)
            self.compute_A()
            self.compute_alpha()
            self.compute_denom()

            perpl = self.perplexity(held_out)

            l_perpl.append((perpl, b))
            self.beta = None

        beta = min(l_perpl)[1]
        print("Beta estimado:", beta)
        return beta
