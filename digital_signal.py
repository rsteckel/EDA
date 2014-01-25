import pickle, os, csv
import numpy as np
from classification_common import *
from text_utils import *


def store_counts(concept_id, weekly_counts):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        for row in weekly_counts:        
            cur.execute("""update concept_signals
                            set signal_count = %s, signal_total = %s
                            where sales_week = %s and concept_id = %s""", 
                            (row[1], row[2], row[0], concept_id,))
            
            conn.commit()
    except Exception as inst:
        print 'Error inserting concept terms'
        print inst 
        
    finally:
        cur.close()
        conn.close()



def classify_week(classifier, vector_dir, vecfile, min_score=.5):
    X_sel = pickle.load(open(vector_dir+'/'+vecfile, 'r'))
    
    probs = classifier.predict_proba(X_sel)[:,1]             
    pos_indices = [ i for i in range(X_sel.shape[0]) if probs[i] > min_score] 
    
    concept_documents = len(pos_indices)
    total_documents = X_sel.shape[0]
    
    return [ concept_documents, total_documents ]
    



def concept_signal(concept_name, vector_dir, min_score=.5):
    pos_concept = concept_name
    neg_concept = 'random'
    
    pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))      
    
    classifier = pipeline.named_steps['classifier']
    
    vecfiles = os.listdir(vector_dir)
    vecfiles.sort()

    weekly_count = []
    
    for vecfile in vecfiles:    
        tokens = vecfile.split('-')
        week_dir = '-'.join(tokens[:3])
        
        concept_docs, total_docs = classify_week(classifier, vector_dir, vecfile)        
        weekly_count.append( (week_dir, concept_docs, total_docs) )
        
    return weekly_count



if __name__ == '__main__':
    VECTOR_DIR_12M = os.environ['NM_HOME']+'/Data/Temporal/vectors'
    
    concepts = load_concepts()
    for concept in concepts: 
        concept_id = concept[0]
        concept_name = concept[1]
        
        print concept_name        
        
        weekly_counts = concept_signal(concept_name, VECTOR_DIR_12M)
        
        store_counts(concept_id, weekly_counts)
        
        
