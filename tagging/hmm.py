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
        self.tagset = tagset
        self.trans = trans
        self.out = out
        # tagset -> {D,N,V} los distintos tags.
        # trans -> las trancisiones y el peso de los tags, n-1 grama y el peso en un dicc
                # trans = {(tuple):{tag:peso}}
        # out = {tag:{word:prob}}



    def tagset(self):
        """Returns the set of tags.
        """
        return self.tagset

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        assert len(prev_tags) == self.n - 1

        return self.trans[prev_tags][tag] # CORREGIR

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        return self.out[tag][word] # CORREGIR

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
        return log2(self.tag_prob(y))

    def log_prob(self, x, y):
        """
        Joint log-probability of a sentence and its tagging.

        x -- sentence.
        y -- tagging.
        """
        return log2(self.prob(x,y))

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

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
