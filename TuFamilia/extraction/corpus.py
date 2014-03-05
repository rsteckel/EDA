# -*- coding: utf-8 -*-
import collections

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


class CorpusTerms:
    def __init__(self, documents):
        self._corpus_probability(documents)
        
    def vocabulary_prob(self, alpha=0):       
        vocab = self.TERM_COUNTS.keys()
        term_probs = []
        for term in vocab:
            term_probs.append( (term, self.term_prob(term, alpha)) )
            
        return sorted(term_probs, key=lambda idx: idx[1])
        
    def term_prob(self, term, alpha=0):
        alpha = float(alpha)
        return (alpha + self.TERM_COUNTS[term]) / (self.SUM_COUNTS + (alpha * self.NUM_TERMS))

    def _corpus_probability(self, documents):    
        es_stopwords = sw.words('spanish')
        en_stopwords = sw.words('english')
        stopwords = es_stopwords + en_stopwords

        vectorizer = TfidfVectorizer(ngram_range=(1,1), stop_words=stopwords)
        #vectorizer = CountVectorizer(ngram_range=(1,1), stop_words=stopwords)
                
        X = vectorizer.fit_transform(documents)
        
        self.TERM_COUNTS = collections.defaultdict(lambda: 0)
        
        totaltf = float(X.sum())
        tfs = zip(vectorizer.get_feature_names(), np.asarray(X.sum(axis=0)).ravel())
        for wordtfidf in sorted(tfs, key=lambda idx: idx[1]):
            #(wordtfidf[0], wordtfidf[1], wordtfidf[1]/totaltf) term, count, probability
            self.TERM_COUNTS[wordtfidf[0]] = wordtfidf[1]
            
        self.SUM_COUNTS = totaltf
        self.NUM_DOCS = len(documents)
        self.NUM_TERMS = len(self.TERM_COUNTS)            



#corpus_terms = CorpusTerms(documents)
#corpus_terms.term_prob('diet', alpha=1)
#term_probs = corpus_terms.vocabulary_prob(alpha=1)
#term_set = [t[0] for t in term_probs[:1000]]