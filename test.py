# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 20:05:09 2013

@author: rsteckel
"""
import pickle 

from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import RFE
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.svm import SVC
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.feature_extraction.text import TfidfVectorizer

import dataset as ds
import vocabulary

domain = 'highfashion'

corpus = ds.FashionConceptCorpus()
corpus.load()
corpus.store()

vectorizer = TfidfVectorizer(vocabulary=vocabulary.domain_vocabulary(domain),
                                 stop_words=vocabulary.domain_stopwords(domain), 
                                 ngram_range=(1,2),
                                 strip_accents='unicode', sublinear_tf=True)

#print 'vectorizing'
#vect = vectorizer.fit_transform(corpus.documents())
#print 'saving'
#corpus.save_vectorizer(vectorizer)        
#        
#with open(corpus.vector_filename(),'w') as vect_f, open(corpus.id_filename(),'w') as id_f:
#    pickle.dump(vect, vect_f)
#    pickle.dump(corpus.docids(), id_f)

ids, X = corpus.vectors()

print 'selecting'
ch2 = SelectKBest(chi2, k=500)
X_sel = ch2.fit_transform(X, ids)


X_train, X_test, Y_train, Y_test = train_test_split(X_sel, ids, test_size=.15, random_state=0)  


print 'classifiying'
classifier = OneVsRestClassifier(SGDClassifier(loss='log'))
classifier.fit(X_train, Y_train)

Yhat = classifier.predict(X_test)

Yhat.shape
Y_test.shape

print confusion_matrix(Y_test, Yhat)

print classification_report(Y_test, Yhat)

    