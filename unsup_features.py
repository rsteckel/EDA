# -*- coding: utf-8 -*-
import collections
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import SGDClassifier
from sklearn.utils import shuffle

import datasets.text_dataset as td
import datasets.customers.ugam_datasets as ud
import datasets.concept_datasets as cd

#dataset = ud.UgamReviews()
#dataset = td.TextDataset('fashioncorpus', 'highfashion')
dataset = cd.DomainConceptCorpus('highfashion')



dataset.load()

vectorizer = TfidfVectorizer(stop_words='english', token_pattern=u'[a-zA-Z]{3}[a-zA-Z]*', ngram_range=(1,1))
selector = SelectKBest(chi2, k=500)
classifier = SGDClassifier(loss='log', shuffle=True, penalty='elasticnet')


X_vec = vectorizer.fit_transform(dataset.documents())

print X_vec.shape

X_vec = np.transpose(X_vec)

top_n = 25

selected_terms = []
for i in xrange(25):
    print i

    clusterer = KMeans(n_clusters=np.random.randint(5,10), init='random', max_iter=200, n_init=1)

    print 'clustering'
    clusterer.fit(X_vec)

    #TODO: Check within/between cluster metrics, ignore weak clusters

    print 'selecting features'
    X_sel = selector.fit_transform(X_vec, clusterer.labels_)
    
    print 'classifying'
    classifier.fit_transform(X_sel, clusterer.labels_)
    
    print 'extracting terms'    
    fnames = vectorizer.get_feature_names()
    feature_terms = [ fnames[i] for i in selector.get_support(True) ]
    for c in range(clusterer.n_clusters):
        c_f = sorted(zip(classifier.coef_[c,:], feature_terms), reverse=True)
        for w,t in c_f[:5]:
            if w > 0:
                selected_terms.append(t)
            else:
                break
    

counter = collections.Counter(selected_terms)
counter.most_common(50)


