import sys, re, pickle, warnings
import numpy as np

from classification_common import *
from concept_datastore import *
from text_utils import *
from fashion_vocab import *
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.feature_selection import RFE
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV


vocab = FashionVocabulary()


def build_pipeline(stopwords, k_features=1500, vocabulary=None, use_grid=True):
    if vocabulary is not None:
        print '\tUsing fixed vocabulary'
        vectorizer = TfidfVectorizer(vocabulary=vocabulary, stop_words=stopwords, ngram_range=(1,2),
                                 strip_accents='unicode', sublinear_tf=True)
    else:
        vectorizer = TfidfVectorizer(stop_words=stopwords, ngram_range=(1,2),
                                 strip_accents='unicode', sublinear_tf=True)
                                 
    steps = [('vectorizer', vectorizer),
             #('selector', SelectKBest(chi2, k=k_features)),
             #('selector', SelectKBest(f_classif, k=k_features)),
             ('selector', RFE(SVC(kernel='linear', C=1.), n_features_to_select=k_features, step=0.25)),
             ('classifier', SGDClassifier(loss='log', penalty='l1', shuffle=True))]

    pipeline = Pipeline(steps)
    
    if use_grid:
        parameters = {
            'classifier__alpha': (.001, .0001, .00001),
            'classifier__penalty': ('elasticnet', 'l1', 'l2')
        }
    else:
        parameters = {
            'classifier__alpha': (.0001,),
            'classifier__penalty': ('l1',)
        }
        
    return [pipeline, parameters]


def pipeline_summary(concept_id, pos_concept, neg_concept, pipeline, test_set, predicted, store=False):
    vectorizer = pipeline.named_steps['vectorizer']
    classifier = pipeline.named_steps['classifier']

    fnames = vectorizer.get_feature_names() 
    try:    
        selector = pipeline.named_steps['selector']
        indices = selector.get_support(True)                 
        selected_terms = [ fnames[i] for i in indices ]
    except KeyError:
        print'Selector not used'
        selected_terms = fnames
    
    show_most_informative_features(selected_terms, classifier, n=25)
    
    print classification_report(test_set, predicted)
    print confusion_matrix(test_set, predicted)    
    
    if store:
        print 'Storing pipeline...'
        pickle.dump(pipeline, open(concept_pipeline(pos_concept, neg_concept), 'wb'))

        coefs = np.where( classifier.coef_ > 0)[1]
        concept_terms = [ selected_terms[i] for i in coefs ]
        term_weights = [ classifier.coef_[0,i] for i in coefs ]
        
        feature_weights = sorted(zip(term_weights, concept_terms), reverse=True)        
        
        print 'Storing concept terms'
        save_concept_terms(concept_id, feature_weights)
        


def build_classifier(concept_id, concept_name, neg_concept='random', vocabulary=None, store=False,
                     use_grid=True, filter_attributes=True, filetype='bing'):
    domain = 'fashion'
    train_type = domain+'-'+filetype
    pos_concept = concept_name
    
    documents, labels = load_training_documents(concept_name, neg_concept, train_type)

    nmstopwords = nm_stopwords() + [ domain ]
    nm_vocabulary = build_nm_vocabulary(nmstopwords, use_cache=True)
    
    if filter_attributes:
        print '**Filtering vocabulary to only attributes'
        attribute_vocab = []
        for term in nm_vocabulary.keys():
            if vocab.contains(term):
                attribute_vocab.append(term)
    
    #pipeline, parameters = build_pipeline(nmstopwords, 1500, nm_vocabulary)
    pipeline, parameters = build_pipeline(nmstopwords, 1500, attribute_vocab)

    X_train, X_test, Y_train, Y_test = train_test_split(documents, labels, test_size=.25, random_state=42)  

    if use_grid:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            grid = GridSearchCV(pipeline, parameters, cv=2, n_jobs=4, verbose=4)        
            #***Is GridSearch using corpus vocabulary and Pipeline using NM vocabulary?
            print 'Optimizing pipeline'
            grid.fit(X_train, Y_train)    
        
            print '\n Configuring pipeline with optimal parameters params:', grid.best_params_, '\n'
            best_pipeline = grid.best_estimator_
            pipeline.set_params = best_pipeline.get_params()

    print 'Fittng pipeline'    
    pipeline.fit(X_train, Y_train)    
    
    print 'Predicting'
    Y_predicted = pipeline.predict(X_test)

    pipeline_summary(concept_id, pos_concept, neg_concept, pipeline, Y_test, Y_predicted, store=store)


