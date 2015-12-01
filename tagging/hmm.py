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
        assert (len(x) == len(y))
        result = 1
        for t in zip(x, y):
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
        for t in zip(x, y):
            result += log2(self.out_prob(t[0], t[1]))
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
        pi[0] = {init: (0.0, [])}

        for k in range(1, len(sent)+1):
            pi[k] = {}

            outs_probs = [(tag, hmm.out_prob(sent[k-1], tag)) for tag in tagset]
            outs_probs1 = [(tag, prob) for tag, prob in outs_probs if prob > 0]
            for tag, out_prob in outs_probs1:
                for prev_tags, (prob, bkp) in pi[k-1].items():
                    pi_ant = prob
                    q = hmm.trans_prob(tag, prev_tags)
                    e = out_prob
                    if q > 0:
                        pi_k = pi_ant + log2(q) + log2(e)
                        newprev = (prev_tags+(tag,))[1:]
                        if newprev not in pi[k] or pi_k > pi[k][newprev][0]:
                            pi[k][newprev] = (pi_k, bkp + [tag])

        max_p = float('-inf')
        result = None
        for prev_tags, (prob, bkp) in pi[len(sent)].items():
            p = hmm.trans_prob('</s>', prev_tags)
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
        self.addone = addone
        self.n = n

        self.word_tag_counts = defaultdict(lambda: defaultdict(int))
        word_tag_counts = self.word_tag_counts
        self.tag_counts_1 = defaultdict(int)  # Counts tamaño 1
        tag_counts_1 = self.tag_counts_1
        self.tag_counts = defaultdict(int)  # Counts tamaño n y n-1
        tag_counts = self.tag_counts
        w_set = set()
        # Contar tags tamaño n y n-1
        for sent in tagged_sents:
            if sent != []:
                words, tags = zip(*sent)
                words = list(words)
                tags = list(tags)
                for i in range(len(sent)):
                    word_tag_counts[tags[i]][words[i]] += 1
                    tag_counts_1[tags[i]] += 1
                    w_set.add(words[i])

                tags[0:0] += (n-1)*['<s>']
                tags.append('</s>')
                for i in range(len(tags) - n + 1):
                    ngram = tuple(tags[i: i + n])
                    n_1gram = tuple(tags[i:i + n - 1])
                    tag_counts[ngram] += 1
                    tag_counts[n_1gram] += 1

        # tagset
        self.t_set = list(self.tag_counts_1.keys())
        # wordset
        self.w_set = w_set
        # tamaño vocabulario
        self.V = len(self.w_set)
        self.len_t_set = len(self.t_set)
        self.word_tag_counts = dict(word_tag_counts)
        self.tag_counts_1 = dict(tag_counts_1)
        self.tag_counts = dict(tag_counts)

    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.

        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        if len(prev_tags) == 0:
            prev_tags = ()
        result = 0

        p_tc = float(self.tag_counts.get(prev_tags, 0.0))
        tc = self.tag_counts.get(prev_tags + (tag,), 0.0)
        if self.addone:
            result = (tc + 1.0) / (p_tc + self.len_t_set)
        else:
            result = tc / p_tc
        return result

    def out_prob(self, word, tag):
        """Probability of a word given a tag.

        word -- the word.
        tag -- the tag.
        """
        if self.unknown(word):
            result = 1.0 / float(self.V)
        else:
            p = float(self.tag_counts_1.get(tag, 0.0))
            if p is not 0:
                result = self.word_tag_counts.get(tag,{}).get(word,0.0) / p

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
        return w not in self.w_set
