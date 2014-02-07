import pickle, sys, os, math, csv, collections, re
import pandas as pd
import pandas.io.sql as psql
import requests
import simplejson as json

from classification_common import *
from concept_datastore import *
from text_utils import *


SOLR_HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
SOLR_PORT = 8888
SOLR_COLLECTION = 'saks_20131201_day_dresses'
SOLR_UPDATE_URL = 'http://'+SOLR_HOST+':'+str(SOLR_PORT)+'/solr/'+SOLR_COLLECTION+'/update'



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
            
    return feature_weights



def classify_catalog(company, pos_concept, neg_concept, product_ids, descs, solr_ids, min_score, use_cache=True):      
    pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))

    vectorizer = pipeline.named_steps['vectorizer']
    selector = pipeline.named_steps['selector']
    classifier = pipeline.named_steps['classifier']
    
    veccache_filename = os.environ['NM_HOME']+'/Data/'+company+'-dresses-vectorized.cache'
    if use_cache ==  True and os.path.exists(veccache_filename):
        X_vect = pickle.load(open(veccache_filename, 'r'))
    else:
        X_vect = vectorizer.transform(descs)    
        pickle.dump(X_vect, open(veccache_filename,'w'))
    
    X_sel = selector.transform(X_vect)
    
    probs = classifier.predict_proba(X_sel)[:,1]
    
    pos_indices = [ i for i in range(len(probs)) if probs[i] > min_score]
    
    pos_prod_ids = [ product_ids[i] for i in pos_indices ]
    pos_prod_scores = [ probs[i] for i in pos_indices ]
    pos_solr_ids = [ solr_ids[i] for i in pos_indices ]
    
    return [pos_prod_ids, pos_prod_scores, pos_solr_ids]



def run_classifier(company, concept_id, concept_name, product_ids, descs, solr_ids, min_score=0.5):
    pos_concept = concept_name
    neg_concept = 'random'

    pos_prod_ids, pos_prod_scores = classify_catalog(company, pos_concept, neg_concept, product_ids, descs, solr_ids, min_score)
    
    return len(pos_prod_ids)

    
    
def classification_features(company, concept_name, descs, min_score=0.0, use_cache=True): 
    pos_concept = concept_name
    neg_concept = 'random'
     
    pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))

    vectorizer = pipeline.named_steps['vectorizer']
    selector = pipeline.named_steps['selector']
    classifier = pipeline.named_steps['classifier']
    
    veccache_filename = os.environ['NM_HOME']+'/Data/'+company+'-dresses-vectorized.cache'
    if use_cache ==  True and os.path.exists(veccache_filename):
        X_vect = pickle.load(open(veccache_filename, 'r'))
    else:
        X_vect = vectorizer.transform(descs)    
        print 'Writing cache file'
        pickle.dump(X_vect, open(veccache_filename,'w'))
    
    X_sel = selector.transform(X_vect)
    
    probs = classifier.predict_proba(X_sel)[:,1]
    
    pos_indices = [ i for i in range(len(probs)) if probs[i] > min_score]    
    pos_prod_scores = [ probs[i] for i in pos_indices ]
    
    feature_weights = extract_feature_weights(vectorizer, selector, classifier, X_vect, X_sel, probs, min_score)    

    mean_weights = []
    for fw in feature_weights:
        mean_weights.append( np.mean([ f[1] for f in fw ]) )
        
    term_counts = []
    for desc in descs:
        term_counts.append( len(re.findall('[a-z]+', desc.lower())) )
    
    return [ pos_indices, pos_prod_scores, term_counts, feature_weights, mean_weights ]
    
    
    
def compare_classifications():    
    concepts = load_concepts()
    
    saks_product_ids,saks_descs,saks_solr = load_saks_dresses()
    nm_product_ids,nm_descs = load_nm_dresses()
    
    with open( os.environ['NM_HOME']+'/Data/company_feature_compare.csv', 'w') as f:
        writer = csv.writer(f)    
        print 'Saks'
        for concept in concepts:            
            concept_name = concept[1]        
            print '\t', concept_name
            pos_prod_ids, pos_prod_scores, term_counts, feature_weights, mean_weights = classification_features('saks', concept_name, saks_descs)
    
            for i in range(len(pos_prod_scores)):
                writer.writerow( [ 'saks', concept_name, saks_product_ids[i], pos_prod_scores[i], term_counts[i], len(feature_weights[i]), mean_weights[i] ] )
        
        print 'NM'
        for concept in concepts:
            concept_name = concept[1]        
            print '\t', concept_name
            pos_prod_ids, pos_prod_scores, term_counts, feature_weights, mean_weights = classification_features('nm', concept_name, nm_descs)
    
            for i in range(len(pos_prod_scores)):
                writer.writerow( [ 'nm', concept_name, nm_product_ids[i], pos_prod_scores[i], term_counts[i], len(feature_weights[i]), mean_weights[i] ] )


    
def load_saks_dresses():    
    ids = []
    descs = []
    solr_ids = []
    with open(os.environ['NM_HOME']+'/Data/saks-dresses.tsv', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            ids.append(row[0])
            descs.append(row[1])    
            solr_ids.append(row[2])
            
    return [ids, descs, solr_ids]


def load_nm_dresses():
    sql = """select cmos_item_code,
                   long_desc_text_only descs
            from nm_catalog
            where silo_name like 'Women%'
            and categorytype_name = 'Daytime Dresses'"""
            
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    
        ids = []
        descs = []
        for row in rows:
            ids.append(row[0])
            descs.append(row[1])
            
    finally:
        cur.close()
        conn.close()
    
    return [ids,descs]

    

def run_classification():    
    concepts = load_concepts()
    saks_product_ids,saks_descs,saks_solr = load_saks_dresses()
    nm_product_ids,nm_descs = load_nm_dresses()
    
    N_saks = len(saks_product_ids)
    N_nm = len(nm_product_ids)
    
    with open(os.environ['NM_HOME']+'/Data/nm_saks_pct.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow( ['Concept', 'NMPct', 'SaksPct'] )
        for concept in concepts:
            concept_id = concept[0]
            concept_name = concept[1]
            
            saks_pos_dresses = run_classifier('saks', concept_id, concept_name, saks_product_ids, saks_descs)
            nm_pos_dresses = run_classifier('nm', concept_id, concept_name, nm_product_ids, nm_descs)
            
            saks_pct = (saks_pos_dresses / float(N_saks)) * 100.0
            nm_pct = (nm_pos_dresses / float(N_nm)) * 100.0
            
            print concept_name, nm_pct, saks_pct
            writer.writerow( [concept_name, nm_pct, saks_pct] )



def classify_saks_dresses():
    product_ids,descs,solr_ids = load_saks_dresses()
    concepts = load_concepts()
    
    products = collections.defaultdict(lambda: {})
    
    for concept in concepts:
        pos_concept = concept[1]
        neg_concept = 'random'

        print pos_concept

        pos_prod_ids, pos_prod_scores, pos_solr_ids = classify_catalog('saks', pos_concept, neg_concept, product_ids, descs, solr_ids, .5)
    
        for i in range(len(pos_prod_ids)):
            prod_id = pos_prod_ids[i]
            score = pos_prod_scores[i]
            solr_id = pos_solr_ids[i]
            
            product = products[prod_id]
            product['id'] = solr_id
            product['fashion_'+pos_concept+'_f'] = { "set" : score }
    
    return products
    


def post_concept_scores(scores):
    header = { 'Content-type' : 'application/json' }
    r = requests.post(SOLR_UPDATE_URL, data=json.dumps(scores), headers=header)
    return r



if __name__ == '__main__':
    #run_classification()

    #products = classify_saks_dresses()    
    #resp = post_concept_scores(products.values())

    compare_classifications()