# -*- coding: utf-8 -*-
import itertools
import numpy as np
import pandas as pd

from taxonomy import POSCategory

from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords as sw
from nltk.corpus import wordnet_ic 
from nltk import FreqDist



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



#test_docs1 = ['The bank of the river was flooded after the rainstorm']
#test_docs2 = ['I put my money in the bank to earn interest']

#sense_tag1(test_docs1)
#sense_tag1(test_docs2)
#print '-'*10
#sense_tag2(test_docs1)
#sense_tag2(test_docs2)