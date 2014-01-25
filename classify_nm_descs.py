# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import os

import datasets.customers.nm_datasets as nmd
import datastores.datastore as ds



def classify_catalog(pos_concept, neg_concept, product_ids, descs, min_score, use_cache=True):      
    print 'Loading Pipeline'
    pipeline_filename = os.environ['NM_HOME']+'/Models/'+pos_concept+'-'+neg_concept+'-pipeline.bin'
    pipeline = pickle.load(open(pipeline_filename, 'rb'))

    vectorizer = pipeline.named_steps['vectorizer']
    selector = pipeline.named_steps['selector']
    classifier = pipeline.named_steps['classifier']
    
    veccache_filename = '/Users/rsteckel/nm_descs.vect'
    if use_cache == True and os.path.exists(veccache_filename):
        print 'Using cached vectorized catalog'
        X_vect = pickle.load(open(veccache_filename, 'r'))
    else:
        print 'Vectorizing catalog descriptions...'
        vectorizer.stop_words = None
        X_vect = vectorizer.transform(descs)    
        print '\tcaching'
        pickle.dump(X_vect, open(veccache_filename,'w'))
    
    print 'Selecting top features...'
    X_sel = selector.transform(X_vect)
    
    print 'Classifying...'
    probs = classifier.predict_proba(X_sel)[:,1]
    
    pos_indices = [ i for i in range(len(probs)) if probs[i] > min_score]
    pos_prod_ids = [ product_ids[i] for i in pos_indices ]
    pos_prod_scores = [ probs[i] for i in pos_indices ]
    
    return [pos_prod_ids, pos_prod_scores ]



def run_classifier(concept_id, concept_name, product_ids, descs, min_score=0.0):
    pos_concept = concept_name
    neg_concept = 'random'

    pos_prod_ids, pos_prod_scores = classify_catalog(pos_concept, neg_concept, product_ids, descs, min_score)

    name_column = [concept_name for i in range(len(pos_prod_scores))]
    df = pd.DataFrame(name_column, columns=['concept_name'])

    df['cmos_item_code'] = pos_prod_ids
    df['scores'] = pos_prod_scores
    
    return df
        
        

desc_filename = '/Users/rsteckel/nm_descs.csv'

if not os.path.exists(desc_filename):
    dataset = nmd.NMTemporalDataset()
    dataset.load()
    with open(desc_filename, 'w') as f:
        dataset.dataframe.to_csv(f, index=False)
    df = dataset.dataframe
else:
    df = pd.read_csv(desc_filename)

ids = df['cat_item_number']
descs = df['ldesc']


def load_descs():    
    for i,d in enumerate(descs):
        cdesc = d.replace('"""', ' ')    
        decoded = cdesc.decode('utf-8', errors='ignore')
        if i % 1000 == 0:
            print i
        yield decoded


concepts = ds.load_concepts('highfashion')

all_df = pd.DataFrame(columns=['concept_name', 'cmos_item_code', 'scores'])

for concept in concepts:
    if concept.name == 'random':
        continue
    print 'Running %s' % (concept.name)    
    concept_id = concept.id
    concept_name = concept.name
    
    concept_df = run_classifier(concept_id, concept_name, ids, load_descs())
    all_df = pd.concat([concept_df, all_df])

    with open('/Users/rsteckel/concept_scores.csv', 'w') as f:
        all_df.to_csv(f, index=False) 