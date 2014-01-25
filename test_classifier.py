import sys, re, pickle, warnings
import numpy as np

from classification_common import *
from concept_datastore import *
from text_utils import *

from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.feature_selection import RFE
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn import metrics




pos_concept = 'romantic'
neg_concept = 'random'
library = 'fashion'
filetype = library+'-bing'

documents, labels = load_training_documents(pos_concept, neg_concept, filetype)

nmstopwords = nm_stopwords() + [ pos_concept, library ]
#nm_vocabulary = build_nm_vocabulary(nmstopwords, use_cache=True)

nm_vocabulary = ['romantic', 'lace', 'jeans', 'coats', 'men', 'women']

vectorizer = TfidfVectorizer(vocabulary=nm_vocabulary, stop_words=nmstopwords,                
                             ngram_range=(1,2), strip_accents='unicode', 
                            sublinear_tf=True)
selector = RFE(SVC(kernel='linear', C=1.), n_features_to_select=1500, step=0.25)
classifier = SGDClassifier(loss='log', penalty='l1')


X_train, X_test, Y_train, Y_test = train_test_split(documents, labels, test_size=.25, random_state=42)  

#X_vec = vectorizer.fit_transform(X_train)
#X_sel = selector.fit_transform(X_vec, Y_train)
#classifier.fit_transform(X_sel, Y_train)

#X_prep = vectorizer.transform(X_test)
#X_new = selector.transform(X_prep)
#X_pred = classifier.predict(X_new)

steps = [('vectorizer', vectorizer),
         ('selector', selector),
         ('classifier', classifier)]

pipeline = Pipeline(steps)
pipeline.fit_transform(X_train, Y_train)
X_pred = pipeline.predict(X_test)

fnames = vectorizer.get_feature_names() 
indices = selector.get_support(True)                 
selected_terms = [ fnames[i] for i in indices ]


show_most_informative_features(selected_terms, classifier, n=25)
print classification_report(Y_test, X_pred)
print confusion_matrix(Y_test, X_pred)    
