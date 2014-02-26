# -*- coding: utf-8 -*-
import itertools
import collections
import numpy as np
import pandas as pd

from taxonomy import POSCategory
from pattern.en import parsetree

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords as sw
from nltk.corpus import wordnet_ic 
from nltk import FreqDist



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



def compare_synsets(t1, pos1, t2, pos2, top_n=5, min_sim=.2):    
    syns1 = wn.synsets(t1.lower(), pos=pos1)
    syns2 = wn.synsets(t2.lower(), pos=pos2)
    simscores = []
    for pair in itertools.product(syns1, syns2):
        s1 = pair[0]
        s2 = pair[1]
        sim = s1.wup_similarity(s2)
        if sim >= min_sim:
            simscores.append( (s1.name(), s2.name(), sim) )
            
    descending = sorted(simscores, key=lambda x: x[2], reverse=True)
    results = descending[:top_n]        
    return results
        


def synset_pos_probability(synset, alpha=1.0):
    corpus_ic = wordnet_ic.ic('ic-brown.dat')     
    #corpus_ic = wordnet_ic.ic('ic-semcor.dat')
    
    try:
        icpos = corpus_ic[synset._pos]
    except KeyError:
        msg = 'Information content file has no entries for part-of-speech: %s'
        raise Exception(msg % synset._pos)
    
    counts = icpos[synset._offset]
    return (alpha + counts) / (alpha + icpos[0]) #Divided by number of pos's
    

def window(fseq, window_size=5):
    for i in xrange(len(fseq) - window_size + 1):
        yield fseq[i:i+window_size]


def word_windows(docwords, window_width=6):    
    for i,word in enumerate(docwords):
        window = docwords[i-(window_width/2):i+(window_width/2)]        
        yield (i, word, window)


def resolve_synsets(possible_syns):
    freq_dist = FreqDist(possible_syns)
    
    def PSyn(syn):
        #return freq_dist.freq(syn) * synset_pos_probability(wn.synset(syn))
        return freq_dist.freq(syn)
    
    return max(set(possible_syns), key=PSyn)


def sense_tag1(parsed_document, window_width=10):
    """ Sense tag using a window (Possibly across sentences) """
    poscat = POSCategory()
    
    es_stopwords = sw.words('spanish')
    en_stopwords = sw.words('english')
    stopwords = set(es_stopwords + en_stopwords)
    
    words = [ w for w in parsed_document.words if w.string.lower() not in stopwords and len(w.string) > 1 and (w.pos.startswith('N') or w.pos.startswith('V'))]
            
    for wi,target_word in enumerate(words):
        window_words = words[wi-(window_width/2):wi+(window_width/2)]
        possible_syns = []
        for neighbor_word in window_words:
            synsets = compare_synsets(target_word.string, poscat.simplify_tag(target_word.pos), neighbor_word.string, poscat.simplify_tag(neighbor_word.pos), min_sim=.2)
            if synsets:
                top_synset = synsets[0]
                possible_syns.append(top_synset[0])
        if possible_syns:
            best_syn = resolve_synsets(possible_syns)
            target_word.custom_tags['WN_SYN'] = best_syn
            print '%10s %15s - %s' % (target_word.string, best_syn, wn.synset(best_syn).definition())
        else:
            print '%10s %s' % (target_word.string, 'Unknown')



def sense_tag2(parsed_document):
    """ Sense tag within a sentence """
    poscat = POSCategory()
    
    es_stopwords = sw.words('spanish')
    en_stopwords = sw.words('english')
    stopwords = set(es_stopwords + en_stopwords)
    
    for sentence in parsed_document.sentences:
        sentence_words = [ w for w in sentence.words if w.string.lower() not in stopwords and len(w.string) > 1 and (w.pos.startswith('N') or w.pos.startswith('V'))]
            
        for wi,target_word in enumerate(sentence_words):
            possible_syns = []
            for wj,neighbor_word in enumerate(sentence_words):
                synsets = compare_synsets(target_word.string, poscat.simplify_tag(target_word.pos), neighbor_word.string, poscat.simplify_tag(neighbor_word.pos), min_sim=.2)
                if synsets:
                    top_synset = synsets[0]
                    possible_syns.append(top_synset[0]) #first item in first synset
            if possible_syns:
                best_syn = resolve_synsets(possible_syns)
                target_word.custom_tags['WN_SYN'] = best_syn
                print '%10s %15s - %s' % (target_word.string, best_syn, wn.synset(best_syn).definition())
            else:
                print '%10s %s' % (target_word.string, 'Unknown')

    return parsed_document



