from collections import defaultdict
from math import log2
from itertools import chain
from collections import Counter

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
        assert (len(x)==len(y))
        result = 1
        for t in zip(x,y):
            result = result * self.out_prob(t[0], t[1])

        return result * self.tag_prob(y)

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
        return result + self.tag_log_prob(y)

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        tagger = ViterbiTagger(self)
        return tagger.tag(sent)

class ViterbiTagger:

    def __init__(self, hmm):
        """
        hmm -- the HMM.
        """
        self.hmm = hmm

    def tag(self, sent):
        """Returns the most probable tagging for a sentence.

        sent -- the sentence.
        """
        hmm = self.hmm
        n = hmm.n
        tagset = hmm.tagset()
        self._pi = pi = {}

        init = (n-1) * ('<s>',)
        pi[0] = {init : (0.0,[])}

        for k in range(1, len(sent)+1):
            pi[k] = {}
            for prev_tags, (prob, bkp) in pi[k-1].items():
                for tag in tagset:
                    pi_ant = prob
                    q = hmm.trans_prob(tag,prev_tags)
                    e = hmm.out_prob(sent[k-1],tag)
                    # falta buscar el maximo
                    if q > 0 and e > 0:
                        pi_k = pi_ant + log2(q) + log2(e)
                        newprev = (prev_tags+(tag,))[1:]
                        if newprev not in pi[k] or pi_k > pi[k][newprev][0]:
                            pi[k][newprev] = (pi_k, bkp + [tag])

        # Devolver el max pi[len(sent)]
        max_p = float('-inf')
        result = None
        for prev_tags, (prob, bkp) in pi[len(sent)].items():
            p = hmm.trans_prob('</s>',prev_tags)
            if p > 0.0:
                pi_k = prob + log2(p)
                if pi_k > max_p:
                    max_p = pi_k
                    result = bkp

        return result

class MLHMM(HMM):

    def __init__(self, n, tagged_sents, addone=True):
        """
        n -- order of the model.
        tagged_sents -- training sentences, each one being a list of pairs.
        addone -- whether to use addone smoothing (default: True).
        """
        # trans -- transition probabilities dictionary.
        # out -- output probabilities dictionary.
        # trans = {(tuple):{tag:peso}}
        # out = {tag:{word:prob}}
        self.addone = addone
        self.n = n
        self.tag_counts = defaultdict(int)
        # Calcular tagset, todo este calculo se puede hacer dentro del for CORREGIR
        list_ta_se = list(chain.from_iterable(tagged_sents))
        self.word_tag_counts = Counter(list_ta_se)
        w, t = zip(*list_ta_se)
        self.t_set = set(t)
        # Contar words
        self.words_counts = Counter(w)
        self.V = len(self.words_counts)
        self.words_counts = dict(self.words_counts)
        tag_counts = self.tag_counts
        # tag_counts[('<s>',)] = (n-1) * len(tagged_sents)
        # Contar tags
        for sent in tagged_sents:
            if sent != []:
                words, tags = zip(*sent)
                # Contar las words tambien
                words = list(words)
                tags = list(tags)
                tags[0:0] += (n-1)*['<s>']
                tags.append('</s>')
                tag_counts[()] += len(tags)
                for i in range(len(tags) - n + 1):
                    # Contar words aca corregir
                    ngram = tuple(tags[i: i + n])
                    # tag_counts[ngram] += 1  # Cuento ngrama
                    for j in range(1, n+1):
                        tag_counts[ngram[:j]] += 1
                for i in range(1,n):
                    tag_counts[tuple(tags[-n+i:])] += 1
        self.tag_counts = dict(tag_counts)

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        if len(prev_tags) == 0:
            prev_tags = ()
        result = self.tag_counts.get(prev_tags,0.0)
        if result != 0:
            tc = self.tag_counts.get(prev_tags + (tag,),0.0)
            if self.addone:
                V = self.V
                result = tc + 1 / result + V
            else:
                result = tc / result
        return result

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        if self.unknown(word):
            result = 1/self.V
        else:
            result = self.tag_counts.get((tag,),0.0)
            if result is not 0:
                result = self.word_tag_counts[(word,tag)] / result

        return result

    def tcount(self, tokens):
        """Count for an n-gram or (n-1)-gram of tags.

        tokens -- the n-gram or (n-1)-gram tuple of tags.
        """
        return self.tag_counts.get(tokens, 0)

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        result = self.words_counts.get(w, True)
        if result is not True:
            result = False
        return result
