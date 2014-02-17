# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%m-%d %H:%M')
                    
import itertools
import numpy as np

from datasets.customers.tufamilia_dataset import TuFamilia

from pattern.en import suggest, parse, parsetree, sentiment
from pattern.en import conjugate, lemma, lexeme
from pattern.search import search, taxonomy

import pattern.en.wordnet as wn

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from nltk.corpus import framenet as fn



NOUN = {'NN','NNS','NNP','NNPS'}
VERB = {'VB','VBZ','VBP','VBD','VBN','VBG'}
ADJECTIVE = {'JJ','JJR','JJS'}
ADVERB = {'RB','RBR','RBS'}

WN_POS = NOUN | VERB | ADJECTIVE | ADVERB

SIMPLE_TAGS = {}
for tag in NOUN:
    SIMPLE_TAGS[tag] = 'n'
for tag in VERB:
    SIMPLE_TAGS[tag] = 'v'
for tag in ADJECTIVE:
    SIMPLE_TAGS[tag] = 'a'
for tag in ADVERB:
    SIMPLE_TAGS[tag] = 'adv'




def corpus_probability(documents):
    term_probs = []
    vectorizer = TfidfVectorizer(ngram_range=(1,1), use_idf=False,
                             stop_words='english', min_df=4, max_df=.90)
                
    X = vectorizer.fit_transform(documents)
    totaltfidf = X.sum()
    tfs = zip(vectorizer.get_feature_names(), np.asarray(X.sum(axis=0)).ravel())
    for wordtfidf in sorted(tfs, key=lambda idx: idx[1]):
        print "%10s %5f %5f" % (wordtfidf[0], wordtfidf[1], wordtfidf[1]/totaltfidf)
        term_probs.append( (wordtfidf[0], wordtfidf[1]/totaltfidf) )
    
    return term_probs


def wordnet_potential_parent(word1, pos1, word2, pos2, min_sim=0.0):
    syns1 = wn.synsets(word1, pos1)
    syns2 = wn.synsets(word2, pos2)

    parents = []
    for s1 in syns1:
        for s2 in syns2:
            family = wn.ancestor(s1,s2)
            if family:
                sim = wn.similarity(s1,s2)
                if sim > min_sim:
                    parents.append( (family, sim) )
    return parents




def parse_phrases(documents):
    for document in documents:
        ptree = parsetree(document, relations=True, lemmata=True)    
        
        for sentence in ptree:
            print i, sentence.string
            for phrase in sentence.phrases:
                for word in phrase.words:
                    if word.pos in WN_POS:
                        print i, phrase, word, word.pos, wn.synsets(word.lemma, word.pos)        
                    else:
                        print i, phrase, word, word.pos
            print '\n'




def print_common_synsets(documents):
    for document in documents:
        ptree = parsetree(document, relations=True, lemmata=True)
        for sentence in ptree:
            for phrase in search('NP', sentence):
                
                #for phrase in sentence.phrases:
                words = phrase.words
                for pair in itertools.combinations(words, 2):
                    word1 = pair[0]
                    word2 = pair[1]
                    if word1.pos in WN_POS and word2.pos in WN_POS:
                        try:
                            parents = wordnet_potential_parent(word1.lemma, word1.pos, word2.lemma, word2.pos)
                            if parents:
                                print 'Parents:', parents[0], word1, word2
            
                            #ff1 = fn.frames_by_lemma(word1.lemma)
                            #ff2 = fn.frames_by_lemma(word2.lemma)                
                            #frame_names = set([ f.name for f in ff1 ]) & set([ f.name for f in ff2 ])
                            #if frame_names:
                            #    print 'Frames:', word1.string, word2.string, frame_names
                        except:
                            print 'Error'



FRAME_CACHE = {}

def find_frames(lemma, pos_tag):      
    simple_tag = None
    if SIMPLE_TAGS.has_key(pos_tag):
        simple_tag = SIMPLE_TAGS[pos_tag] 
        
    if simple_tag:
        key = lemma+'.'+simple_tag
    else:
        key = lemma

    frames = []
    
    if FRAME_CACHE.has_key(key):
        frames.append(FRAME_CACHE[key])
    else:    
        try:
            frames = fn.frames_by_lemma(key)
            if frames:
                for f in frames:
                    FRAME_CACHE[key] = f
        except:
            pass
    return frames


def extract_frames(documents):
    frame_names = []
    for i,document in enumerate(documents):
        if i % 100 == 0:
            print '%d of %d' %(i, len(documents))
        ptree = parsetree(document, tokenize=True, tags=True, chunks=False, relations=False, lemmata=True, encoding='utf-8') 
        for sentence in ptree:
            for word in sentence.words:  
                frames = find_frames(word.lemma, word.pos)
                
                for frame in frames:
                    frame_names.append(frame.name)

    return frame_names







dataset = TuFamilia('health', query={'lang':'en'})
dataset.load()

dataset.store()


dataframe = dataset.dataframe
documents = dataset.documents()



print_common_synsets(documents)

tps = corpus_probability(documents)

    
frames = extract_frames(documents)


from collections import Counter

counter = Counter(frames)


tags ={ 'a.n', 'b.v', 'c.n'}

'a.n' in tags



frames = fn.frames(r'Mental_stimulus_stimulus_focus')
for frame in frames:
    print set(frame.lexUnit.keys())
    print [fe for fe in frame.FE]
    
    

frame = fn.frames(r'Mental_stimulus_stimulus_focus')[0]
    
fes = frame['FE']
for fe in fes:
    print fe
