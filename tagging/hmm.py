from collections import defaultdict
from math import log2

class HMM:

    def __init__(self, n, tagset, trans, out):
        """
        n -- n-gram size.
        tagset -- set of tags.
        trans -- transition probabilities dictionary.
        out -- output probabilities dictionary.
        """
        self.n = n
        self.t_set = tagset
        self.trans = trans
        self.out = out
        # tagset -> {D,N,V} los distintos tags.
        # trans -> las trancisiones y el peso de los tags, n-1 grama y el peso en un dicc
                # trans = {(tuple):{tag:peso}}
        # out = {tag:{word:prob}}

    def tagset(self):
        """Returns the set of tags.
        """
        return self.t_set

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        result = self.trans.get(prev_tags, 0)
        if result is not 0:
            result = result.get(tag, 0)
        return result

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        result = self.out.get(tag, 0)
        if result is not 0:
            result = result.get(word, 0)

        return result

    def tag_prob(self, y):
        """
        Probability of a tagging.
        Warning: subject to underflow problems.

        y -- tagging.
        """
        # N largo de la sentencia
        # prod (de 1 a N+1 ) P(Yi | Yi-(anteriores n-1 gramas)
        # Agregamos <s>

        n = self.n
        y[0:0] += (n-1) * ['<s>']
        y.append('</s>')
        result = 1.0
        for k in range(n-1, len(y)):
            result = result * self.trans_prob(y[k], tuple(y[k-n+1:k]))

        for i in range(0, n-1):
            y.pop(0)
        y.pop()

        return result

    def prob(self, x, y):
        """
        Joint probability of a sentence and its tagging.
        Warning: subject to underflow problems.

        x -- sentence.
        y -- tagging.
        """
        # prod de 1 a N P(Xi | Yi)

        result = 1
        for t in zip(x,y):
            result = result * self.out_prob(t[0], t[1])
        return result

    def tag_log_prob(self, y):
        """
        Log-probability of a tagging.

        y -- tagging.
        """
        n = self.n
        y[0:0] += (n-1) * ['<s>']
        y.append('</s>')
        result = 0
        for k in range(n-1, len(y)):
            result += log2(self.trans_prob(y[k], tuple(y[k-n+1:k])))

        for i in range(0, n-1):
            y.pop(0)
        y.pop()

        return result

    def log_prob(self, x, y):
        """
        Joint log-probability of a sentence and its tagging.

        x -- sentence.
        y -- tagging.
        """

        result = 0
        for t in zip(x,y):
            result += log2(self.out_prob(t[0],t[1]))
        return result

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        # instanciar un viterbi

class ViterbiTagger:

    def __init__(self, hmm):
        """
        hmm -- the HMM.
        """
        self.n = hmm.n
        self.tagset = hmm.tagset()
        self._pi = defaultdict(lambda: defaultdict(tuple))
        self.hmm = hmm

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """

        n = self.n
        pi = self._pi
        tagset = self.tagset

        init = (n-1)*('<s>',)
        pi[0][init] = (log2(1),[])

        for k in range(1, len(sent)+1):
            for prev_tags, (prob, bkp) in pi[k-1].items():
                for tag in tagset:
                    pi_ant = prob
                    q = self.hmm.trans_prob(tag,prev_tags)
                    e = self.hmm.out_prob(sent[k-1],tag)
                    if q != 0 and e != 0:
                        pi_k = pi_ant + log2(q) + log2(e)
                        pi[k][prev_tags[1:]+(tag,)] = (pi_k, bkp + [tag])
        # Devolver el max pi[len(sent)]
        result = max(pi[len(sent)].values(), key=lambda x: x[0])[1]
        return result
