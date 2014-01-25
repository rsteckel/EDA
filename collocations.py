# -*- coding: utf-8 -*-
import numpy as np
import scipy.sparse as s

from sklearn.preprocessing import LabelBinarizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans, AffinityPropagation, DBSCAN

import datasets.concept_datasets as cd



dataset = cd.DomainConceptCorpus('highfashion')


dataset.load()


vectorizer = CountVectorizer()

documents = [ doc for doc in dataset.documents() ]

X_vec = vectorizer.fit_transform(documents)

fnames = set(vectorizer.get_feature_names())
findex = {f:i for i,f in enumerate(fnames) }
iindex = {i:f for i,f in enumerate(fnames) }

analyze = vectorizer.build_analyzer()



N = len(fnames)
wsums = s.csr_matrix((N,N))
wsumofsquares = s.csr_matrix((N,N))
wcounts = s.csr_matrix((N,N))


def add_term_distances(term1, dists):
    for dist in dists:
        term2 = dist[0]
        distance = dist[1]

        i = findex[term1]
        j = findex[term2]
        
        wsums[i,j] += distance
        wcounts[i,j] += 1
        
        M2 = wsumofsquares[i,j]
        n = wcounts[i,j]
        mean = wsums[i,j]/n
        delta = distance - mean
        mean = mean + delta/n
        M2 = M2 + delta*(distance - mean)
        
        wsumofsquares[i,j] = M2

def train(width=5):
    for d in range(5):   #range(len(documents)):
        print "%d of %d" % (d, len(documents))
        terms = np.array(analyze(documents[d]))
        for i,term in enumerate(terms):    
            try:
                if i > 0:
                    pre_range = np.array(range(np.max([0,(i-width)]),i))
                    pre_terms = terms[pre_range]
                    pre_dists = zip(pre_terms, i - pre_range)
                    add_term_distances(term, pre_dists)
                    
                if i < len(terms)-1:
                    post_range = np.array(range((i+1),np.min([len(terms),(i+width+1)])))
                    post_terms = terms[post_range]
                    post_dists = zip(post_terms, post_range - i)
                    add_term_distances(term, post_dists)
                    
            except IndexError:
                print "index error: i=%d  term=%s" % (i, term)


def collocation(term, min_count=1):
    i = findex[term]
    
    for j in range(N):
        c = wcounts[i,j]
        if c > min_count:
            t = iindex[j]
            s = wsums[i,j]
            
            mu = s/c
            sigma = np.sqrt( wsumofsquares[i,j]/(c-1) )
            print t, c, mu, sigma, (mu/sigma)



train()
collocation('trendy', min_count=1)


#---------Use NLTK collocations--------------


import nltk
import re
import HTMLParser

h = HTMLParser.HTMLParser()

for i,d in enumerate(documents):
    documents[i] = h.unescape(documents[i]).encode('utf-8')


def tokenize(documents):
    for i,doc in enumerate(documents):
        if i % 100 == 0:
            print '%d of %d' % (i, len(documents))
        for sent in nltk.sent_tokenize(doc.lower()):
            for word in nltk.word_tokenize(sent):
                yield word


text = nltk.Text(tkn for tkn in tokenize(documents))

text.collocations(num=200, window_size=3)


phrases = ['haute couture','new york','fashion week','plus size','red carpet',
'los angeles','prom dresses','wedding dresses','hong kong','marc jacobs',
'dolce gabbana','formal dresses','louis vuitton','marks spencer','ralph lauren',
'street style','victoria secret','dorothy perkins','elie saab','united kingdom',
'alexander mcqueen','christian dior','michael kors','salwar kameez','miss selfridge',
'wedding dress','evening dresses','fashion industry','nail art','boho chic',
'saint laurent','freedom topshop','designer sarees','relaxed fit','eye makeup',
'calvin klein','cocktail dresses','cocktail dress','new look','bridesmaid dresses',
'kim kardashian','fashion show','evening dress','formal dress','high quality',
'long sleeve','condé nast','fashion designers','kate mack','yves laurent',
'karl lagerfeld','maxi dress','giorgio armani','miranda kerr','skin care',
'zuhair murad','luxury','fashion','kate moss','yves saint','fashion geek']


phrases.sort()

doc_index = []
doc_labels = []
for i,document in enumerate(documents):
    phrase_labels = []
    for phrase in phrases:
        tokens = phrase.split(' ')
        count = 0    
        for token in tokens:
            if document.find(token) >= 0:
                count += 1
        if count == len(tokens):
            phrase_labels.append(phrase)
            
    if len(phrase_labels) > 0:
        doc_labels.append(tuple(phrase_labels))
        doc_index.append(i)


lb = LabelBinarizer()
lb.fit(phrases)
X = lb.fit_transform(doc_labels)


Xt = np.transpose(X)

clusterer = KMeans(n_clusters=30)

clusterer = DBSCAN(eps=.01, min_samples=5, metric='jaccard')

clusterer.fit(Xt)


zip(phrases, clusterer.labels_)


from sklearn.metrics.pairwise import euclidean_distances
import sklearn.metrics.pairwise as pd
D = euclidean_distances(X, X)
db = DBSCAN(metric="precomputed").fit(D)
