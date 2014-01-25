import pickle, sys, os, math
import pandas as pd

from classification_common import *
from concept_datastore import *
from text_utils import *


def extract_feature_weights(vectorizer, selector, classifier, X_vect, X_sel, probs, min_score):    
    fnames = vectorizer.get_feature_names()
    pos_indices = [ i for i in range(len(probs)) if probs[i] > min_score]
    sel_i = selector.get_support(True)
    coef_i = np.where( classifier.coef_ > 0 )[1]
    
    print 'Extracting important terms...'
    feature_weights = []
    for p in pos_indices:
        selected_term_i = [ sel_i[i] for i in coef_i ]    
        terms = [ fnames[i] for i in selected_term_i if X_vect[p,i] > 0 ]
        weights = [ classifier.coef_[0,i] for i in coef_i if X_sel[p,i] > 0]
        
        feature_weights.append( zip(terms, weights) )        
        
        if len(feature_weights) % math.ceil(len(pos_indices) / 5) == 0:
            print '\t', len(feature_weights), 'of', len(pos_indices)
            
    return feature_weights



def classify_catalog(pos_concept, neg_concept, product_ids, descs, min_score, use_cache=True):      
    print 'Loading Pipeline'
    pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))

    vectorizer = pipeline.named_steps['vectorizer']
    selector = pipeline.named_steps['selector']
    classifier = pipeline.named_steps['classifier']
    
    veccache_filename = vectorized_catalog_filename()
    if use_cache ==  True and os.path.exists(veccache_filename):
        print 'Using cached vectorized catalog'
        X_vect = pickle.load(open(veccache_filename, 'r'))
    else:
        print 'Vectorizing catalog descriptions...'
        X_vect = vectorizer.transform(descs)    
        print '\tcaching'
        pickle.dump(X_vect, open(veccache_filename,'w'))
    
    print 'Selecting top features...'
    X_sel = selector.transform(X_vect)
    
    print 'Classifying...'
    probs = classifier.predict_proba(X_sel)[:,1]
    
    #feature_weights = extract_feature_weights(vectorizer, selector, classifier, X_vect, X_sel, probs, min_score)
    
    pos_indices = [ i for i in range(len(probs)) if probs[i] > min_score]
    pos_prod_ids = [ product_ids[i] for i in pos_indices ]
    pos_prod_scores = [ probs[i] for i in pos_indices ]
    
    return [pos_prod_ids, pos_prod_scores ]



def run_classifier(concept_id, concept_name, product_ids, descs, min_score=0.0, 
                   store_class=False, store_features=False):
    pos_concept = concept_name
    neg_concept = 'random'

    pos_prod_ids, pos_prod_scores, feature_weights = classify_catalog(pos_concept, neg_concept, 
                                                                      product_ids, descs, min_score)

    df = pd.DataFrame([concept_name, pos_prod_ids, pos_prod_scores], columns=['concept_name', 'cmos_item_code', 'score'])
    
    #if store_class:
    #    print 'Storing scores'
    #    save_concept_scores(concept_id, pos_prod_ids, pos_prod_scores)
    #
    #if store_features:
    #    print 'Storing features'
    #    save_features(concept_id, pos_prod_ids, feature_weights)
    
    with open('/Users/rsteckel/concept_scores.csv', 'w') as f:
        df.to_csv(f, index=False)    