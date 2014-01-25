import pickle, os, csv
import numpy as np
import pandas as pd
import pandas.io.sql as psql
from classification_common import *
from text_utils import *

from sklearn import linear_model


#def load_concept_items_3m_series():
#    sql = """select date_trunc('week', t.tim_ukey_dt) salesweek,
#            		c.name,
#            		count(*) cnt
#            	from nm_min_transactions t
#            	inner join nm_catalog cat on (cat.cmos_item_code = t.cat_item_number)
#            	inner join product_concept pc on (pc.product_id = cat.id)
#            	inner join concept c on (c.id = pc.concept_id)
#            	where pc.score >= .5
#            	and t.tim_ukey_dt >= '6/10/2013' and t.tim_ukey_dt < '9/15/2013'
#            	group by date_trunc('week', t.tim_ukey_dt), c.name"""
#    
#    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
#    
#    try:                              
#        df = psql.frame_query(sql, conn)        
#    finally:
#        conn.close()
#
#    return df   

    
def load_concept_revenue_3m_series():
    sql = """select date_trunc('week', t.tim_ukey_dt) salesweek,
            		c.name,
            		sum(t.af_pur_amt) revenue
            	from nm_min_transactions t
            	inner join nm_catalog cat on (cat.cmos_item_code = t.cat_item_number)
            	inner join product_concept pc on (pc.product_id = cat.id)
            	inner join concept c on (c.id = pc.concept_id)
            	where pc.score >= .5
            	and t.tim_ukey_dt >= '6/10/2013' and t.tim_ukey_dt < '9/15/2013'
            	group by date_trunc('week', t.tim_ukey_dt), c.name"""
    
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    
    try:                              
        df = psql.frame_query(sql, conn)        
    finally:
        conn.close()

    return df    
    

def nm_concept_revenue_3m_series():    
    df = load_concept_revenue_3m_series()
    
    pt = pd.tools.pivot.pivot_table(df, values='revenue', rows='salesweek',
                                    cols='name', aggfunc=np.sum, fill_value=0)
    return pt


#def nm_concept_items_3m_series():    
#    df = load_concept_items_series()
#    
#    pt = pd.tools.pivot.pivot_table(df, values='cnt', rows='salesweek',
#                                    cols='name', aggfunc=np.sum, fill_value=0)
#    return pt




def classify_week(classifier, vector_dir, vecfile, min_score=.5):
    X_sel = pickle.load(open(vector_dir+'/'+vecfile, 'r'))
    
    probs = classifier.predict_proba(X_sel)                
    pos_indices = [ i for i in range(X_sel.shape[0]) if probs[i,1] > min_score] 
    
    concept_documents = len(pos_indices)
    total_documents = X_sel.shape[0]
    
    return [ concept_documents, total_documents ]



def nm_signal_concept(concept_name, concept_table, as_pct=True):
    series = concept_table[ concept_name ]

    N = len(series)
    
    X = np.arange(N).reshape((N,-1))
    Y = series

    regr = linear_model.LinearRegression()
    regr.fit(X,Y)
    Yhat = regr.predict(X)
    
    if as_pct:
        return ((Yhat[N-1] - Yhat[0]) / Yhat[0]) * 100.0
    else:
        return (Yhat[N-1] - Yhat[0])
    

def digital_signal_concept_pct(pipeline, concept_name, vector_dir, min_score=.5):
    classifier = pipeline.named_steps['classifier']
    
    vecfiles = os.listdir(vector_dir)
    vecfiles.sort()

    N = len(vecfiles)

    weekly_pct = np.zeros((N, 1))
    index = 0
    for vecfile in vecfiles:    
        tokens = vecfile.split('-')
        week_dir = '-'.join(tokens[:3])
        
        concept_docs,total_docs = classify_week(classifier, vector_dir, vecfile)        

        weekly_pct[index] = (concept_docs / float(total_docs)) * 100.0
        index += 1

    X = np.arange(N).reshape((N,-1))
    Y = weekly_pct

    regr = linear_model.LinearRegression()
    regr.fit(X,Y)
    Yhat = regr.predict(X)
    
    print concept_name, 'Actual:', Y[0], Y[N-1], 'Fit:', Yhat[0], Yhat[N-1]
    
    return ((Yhat[N-1] - Yhat[0]) / Yhat[0]) * 100.0


#def total_nm_concept_pct(pipeline, concept_name, descs, min_score=.5, use_cache=True):
#    vectorizer = pipeline.named_steps['vectorizer']
#    selector = pipeline.named_steps['selector']
#    classifier = pipeline.named_steps['classifier']
#    
#    veccache_filename = vectorized_catalog_filename()
#    if use_cache ==  True and os.path.exists(veccache_filename):
#        X_vect = pickle.load(open(veccache_filename, 'r'))
#    else:
#        X_vect = vectorizer.transform(descs)
#        pickle.dump(X_vect, open(veccache_filename,'w'))
#    
#    X_sel = selector.transform(X_vect)
#    probs = classifier.predict_proba(X_sel)[:,1]
#    
#    pos_indices = [ i for i in range(len(probs)) if probs[i] > min_score]
#    
#    return (len(pos_indices) / float(X_vect.shape[0])) * 100.0


def total_nm_concept_pct(concept_name):
    sql = """select (count(cat.cmos_item_code) / 85096.0) * 100.0 concept_pct
            from nm_catalog cat
            left join product_concept pc on (pc.product_id = cat.id)
            left join concept c on (c.id = pc.concept_id)
            where pc.score >= .5
            and c.name = '"""+concept_name+"""' group by c.name"""

    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    
    try:                              
        df = psql.frame_query(sql, conn)        
    finally:
        conn.close()

    return float(df['concept_pct'])
    

        
def total_digital_concept_pct(pipeline, concept_name, vector_dir, min_score=.5):    
    vectorizer = pipeline.named_steps['vectorizer']
    classifier = pipeline.named_steps['classifier']
    selector = pipeline.named_steps['selector']

    vecfiles = os.listdir(vector_dir)
    vecfiles.sort()

    concept_documents = 0    
    total_documents = 0
    
    for vecfile in vecfiles:
        X_sel = pickle.load(open(vector_dir+'/'+vecfile, 'r'))
        tokens = vecfile.split('-')
        week_dir = '-'.join(tokens[:3])
        
        if X_sel.shape[0] > 0:                
            probs = classifier.predict_proba(X_sel)                
            pos_indices = [ i for i in range(X_sel.shape[0]) if probs[i,1] > min_score]    
            concept_documents += len(pos_indices)
            total_documents += X_sel.shape[0]
              
    return (concept_documents/float(total_documents)) * 100.0
        



VECTOR_DIR_3M = os.environ['NM_HOME']+'/Data/Temporal/shortterm-vectors'
VECTOR_DIR_12M = os.environ['NM_HOME']+'/Data/Temporal/vectors'

concepts = ['adorable','amazing','artistic','beautiful','bohemian','casual','chic',
 'contemporary','couture','cute','darling','demure','dressy','elegant','fantastic',
 'feminine','futuristic','geek','gorgeous','industrial','lovely','luxe','modern',
 'pretty','romantic','sleek','stunning','subtle','sultry','sweet','vibrant']

#concepts = ['subtle',]

print 'Loading concept revenue series'
revenue_concept_table = nm_concept_revenue_3m_series()

print 'Loading catalog descriptions'
id_descs = load_product_descs()
descs = [ idd[1] for idd in id_descs ]
            
            
with open( os.environ['NM_HOME']+'/Data/concept_percentages.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow([ 'concept', 'digitalTotalPct', 'nmTotalPct', 'digitalPct3Month', 'nmRev3Month', 'nmRevPct3Month', 'nmRevDelta3Month'] )
    for concept in concepts: 
        pos_concept = concept
        neg_concept = 'random'
        
        pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))        
                        
        digital_total_pct = total_digital_concept_pct(pipeline, concept, VECTOR_DIR_12M) #pct of crawled data
        nm_total_pct = total_nm_concept_pct(concept)  #pct of NM catalog
        
        digital_3m_pct_change = digital_signal_concept_pct(pipeline, concept, VECTOR_DIR_3M)        
        nm_signal_3m_rev = np.sum( revenue_concept_table[ concept ] )  #3month revenue        
        nm_signal_3m_rev_pct_change = nm_signal_concept(concept, revenue_concept_table, as_pct=True)
        nm_signal_3m_rev_delta = nm_signal_concept(concept, revenue_concept_table, as_pct=False)
        
        print concept, digital_total_pct, nm_total_pct, digital_3m_pct_change[0], nm_signal_3m_rev, nm_signal_3m_rev_pct_change, nm_signal_3m_rev_delta

        writer.writerow([ concept, digital_total_pct, nm_total_pct, digital_3m_pct_change[0], nm_signal_3m_rev, nm_signal_3m_rev_pct_change, nm_signal_3m_rev_delta ] )
        

