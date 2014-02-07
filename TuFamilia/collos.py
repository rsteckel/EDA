# -*- coding: utf-8 -*-
import re
import HTMLParser
import pandas as pd
import numpy as np
from textblob import TextBlob
from collections import Counter
import gensim
import nltk
from nltk.collocations import *
from nltk.metrics.association import *

from sklearn.cross_validation import train_test_split
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.feature_extraction.text import CountVectorizer


import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%m-%d %H:%M')
                    
import datastores.datastore as ds
import datasets.text_dataset as td
import datasets.customers.tufamilia_dataset as tfd



def count_tags(tf_dataset, top_n=25):
    all_tags = [] 

    tags = tf.dataframe['tags_s']
    for doc_tags in tags:
        tokens = set(doc_tags.lower().split(','))
        for token in tokens:
            if len(token) > 0:
                all_tags.append(token)
            
    c = Counter(all_tags)    
    for tag in c.most_common(top_n):
        print 'Tag: %s  (%d)' % tag



def tokenize(documents):
    error_count = 0
    h = HTMLParser.HTMLParser()

    for i,doc in enumerate(documents):
        if i % 1000 == 0:
            print '%d of %d' % (i, len(documents))
            
        try:
            encoded_doc = h.unescape(doc).encode('utf8')
            for sent in nltk.sent_tokenize(encoded_doc.lower()):
                for word in nltk.word_tokenize(sent):
                    yield word
        except:
            error_count += 1




def test_collocations(documents, num=25, window_size=2, min_freq=2):
    tokenized = [tkn for tkn in tokenize(documents)]
    
    from nltk.corpus import stopwords
    ignored_words = stopwords.words('english')
    ignored_words += ['...', "n't"]
    finder = BigramCollocationFinder.from_words(tokenized, window_size)
    finder.apply_freq_filter(min_freq)
    finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
    bigram_measures = BigramAssocMeasures()

    collocations = finder.nbest(bigram_measures.likelihood_ratio, num)  #bigram_measures.pmi
    
#    finder = TrigramCollocationFinder.from_words(tokenized)    
#    finder.apply_freq_filter(min_freq)
#    finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
#    trigram_measures = TrigramAssocMeasures()
#    
#    collocations = finder.nbest(trigram_measures.likelihood_ratio, num)    
#    trigram_colloc_strings = [w1+' '+w2 for w1, w2 in collocations]

    #return bigram_colloc_strings + trigram_colloc_strings
    return collocations


    

def model_topics(documents):    
    results = []
    for i in range(5, 25):
        n_topics = i
        
        train_docs, test_docs = train_test_split(documents, test_size=.1)    
        
        vect = CountVectorizer(min_df=2, ngram_range=(1, 2), stop_words='english')
        corpus_vect = vect.fit_transform(train_docs)    
        
        corpus_vect_gensim = gensim.matutils.Sparse2Corpus(corpus_vect, documents_columns=False)
        
        vocabulary_gensim = {}
        for key, val in vect.vocabulary_.items():
            vocabulary_gensim[val] = key
        
        #tm = gensim.models.LsiModel(corpus_vect_gensim, num_topics=n_topics, id2word=vocabulary_gensim)        
        tm = gensim.models.ldamodel.LdaModel(corpus_vect_gensim, num_topics=n_topics, id2word=vocabulary_gensim)
    
        test_vect = vect.transform(test_docs)
        test_vect_gensim = gensim.matutils.Sparse2Corpus(test_vect, documents_columns=False)
        perp = tm.bound(test_vect_gensim)
        
        results.append( (i, perp) )

    return results
    
    



def filter_collo_docs(documents, collos):
    collo_docs = []
    for doc in documents:    
        phrase_doc = ''
        for collo in collos:
            found = 0
            for term in collo:
                if doc.find(term) > -1:
                    found += 1
            if found == len(collo):
                phrase_doc += ' '.join(collo)
        if len(phrase_doc) > 0:        
            collo_docs.append(phrase_doc)
    return collo_docs




def filter_pos_docs(documents, pos_tags):
    pos_docs = []
    tag_set = set(pos_tags)
    
    for i,doc in enumerate(documents):
        if i % 500 == 0:
            print '%d of %d' % (i, len(documents))
        pseudo_doc = ''
        sent_tokens = nltk.sent_tokenize(doc)
        for sent in sent_tokens: 
            word_tokens = nltk.word_tokenize(sent)
            for t in nltk.pos_tag(word_tokens):
                if t[1] in tag_set:
                    pseudo_doc += ' ' + t[0]
                    
        if len(pseudo_doc) > 0:
            pos_docs.append(pseudo_doc)
        
    return pos_docs


from textblob import TextBlob

blob = TextBlob('I really like chocolate candy')
blob.sentiment



tf = tfd.TuFamilia()
tf.load()
#tf.store()

count_tags(tf, top_n=50)


documents = tf.documents()


tf.write_documents()

dirname = '/tmp/tufamilia'
use_ids = False

ids = tf.docids()
docs = tf.documents()

count = 1
for i,docid in enumerate(ids):                
    if use_ids == False:
        docid = str(count)
        count += 1
      
    with open(os.path.join(dirname, docid), 'w') as f:
        f.write(docs[i])





collos = test_collocations(documents, num=100, window_size=2, min_freq=10)
collo_docs = filter_collo_docs(documents, collos)
model_topics(collo_docs)


pos_tags = ['NN', 'NNP', 'NNS', 'NNPS', 'JJ', 'JJR', 'JJS']

pos_tags = ['NN', 'NNP']
pos_docs = filter_pos_docs(documents, pos_tags)


results = model_topics(pos_docs)

pos_docs[1]


import matplotlib.pyplot as plt

plt.plot([ r[0] for r in results ], [ r[1] for r in results ])
plt.show()




#---------------------------


def cluster(phrases, documents):
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
    
    
    
    D = euclidean_distances(X, X)
    db = DBSCAN(metric="precomputed").fit(D)
