import psycopg2, os, pickle
import simplejson as json
import pandas as pd
from collections import defaultdict

from classification_common import *
from text_utils import *

db='o360'
username='ryan'
hostname='192.168.11.31'


def concept_export():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select c.name concept_name,
                               initcap(c.name) concept_display,
                               enabled,
                               cd.name domain_name,
                               concept_terms,
                               concept_x,
                               concept_y
                        from concept c
                        inner join concept_terms ct on (ct.concept_id = c.id)
                        inner join concept_domain cd on (cd.id = c.domain_id)
                        inner join concept_xy xy on (xy.concept_name = c.name)""")
                    
        rows = cur.fetchall()          
    finally:
        cur.close()
        conn.close()

    concepts = []
    for row in rows:    
        concept_id = row[0]
        concept = {}
        concept['id'] = concept_id
        concept['name'] = row[1]
        concept['enabled'] = row[2]
        concept['domain'] = row[3]
        
        term_str = row[4]        
        concept['terms'] = [ [ tw.split(';')[0], float(tw.split(';')[1]) ] for tw in term_str.split('|') ]
        concepts.append(concept)

        concept['concept_x'] = row[5]
        concept['concept_y'] = row[6]
    return concepts



def build_series(concepts, vector_dir, min_score=.5):
    concept_series = defaultdict(lambda: [])
    
    for concept in concepts:
        print '\t', concept['id']
        pos_concept = concept['id']
        neg_concept = 'random'
        
        pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))        
        classifier = pipeline.named_steps['classifier']
                
        concept_series[pos_concept].append( ['Week', 'Signal'] )
        
        vecfiles = os.listdir(vector_dir)
        vecfiles.sort()
            
        for vecfile in vecfiles:
            X_sel = pickle.load(open(vector_dir+'/'+vecfile, 'r'))
            tokens = vecfile.split('-')
            week_dir = '-'.join(tokens[:3])
                    
            probs = classifier.predict_proba(X_sel)                
            pos_indices = [ i for i in range(X_sel.shape[0]) if probs[i,1] > min_score]    
            range_pct = (len(pos_indices) / float(X_sel.shape[0])) * 100.0
            
            concept_series[pos_concept].append( [week_dir, range_pct] )

    return concept_series



def append_concept_pcts(concepts):
    SIG_FILE = os.environ['NM_HOME']+'/Data/concept_percentages.csv'
    
    signals = {}
    df = pd.read_csv(SIG_FILE, index_col=0)
    for row in df.iterrows():
        concept = row[0]
        digitalTotalPct = row[1][0]
        nmTotalPct = row[1][1]
        
        digital3month = row[1][2]
        nmRev3month = row[1][3]
        nmRevPct3month = row[1][4]
        nmRevDelta3Month = row[1][5]
        
        signals[concept] = (digitalTotalPct, nmTotalPct, digital3month, nmRev3month, nmRevPct3month, nmRevDelta3Month)

    for concept in concepts:
        ss = signals[ concept['id'] ]
        
        concept['digital_total_pct'] = ss[0]
        concept['nm_total_pct'] = ss[1]  ###*** Temporary (see below)
        
        concept['3m_digital_pct'] = ss[2]
        concept['3m_nm_revenue'] = ss[3]
        concept['3m_nm_revenue_pct'] = ss[4]
        concept['3m_nm_delta_revenue'] = ss[5]
        
        
    return concepts


def append_digital_series(concepts, vector_dir):
    print 'Building weekly series'
    signals = build_series(concepts, vector_dir)
    
    for concept in concepts:
        weekly_signal = signals[ concept['id'] ]
        smoothed_signal = pd.read_csv('/tmp/'+concept['id']+'-smooth-signal.csv')
        
        smoothed = []
        smoothed.append(['Week', 'Signal'])        
        for row in smoothed_signal.itertuples():
            smoothed.append( [ row[1], row[2] ] )
        
        #concept['series_weekly_digital'] = weekly_signal
        concept['smoothed_weekly_digital_pct'] = smoothed
        
    return concepts


def append_saks_dress_pct(concepts):    
    concept_dress = {}
    
    dress_df = pd.read_csv( os.environ['NM_HOME']+'/Data/nm_saks_pct.csv')    
    for row in dress_df.itertuples():
        concept = row[1]
        nm_pct = row[2]
        saks_pct = row[3]
        concept_dress[concept] = (nm_pct, saks_pct)
    
    for concept in concepts:
        ss = concept_dress[ concept['id'] ]    
        concept['nm_product_pct'] = ss[0]  
        concept['saks_product_pct'] = ss[1]
        
    return concepts



def write_file(concepts, filename):    
    with open(filename, 'w') as f:
        f.write(json.dumps(concepts, sort_keys=True, indent=4))
        f.flush()
    


VECTOR_DIR = os.environ['NM_HOME']+'/Data/Temporal/vectors'

concepts = concept_export()
concepts = append_concept_pcts(concepts)
concepts = append_digital_series(concepts, VECTOR_DIR)
concepts = append_saks_dress_pct(concepts)

write_file(concepts, '/tmp/concept_export.json')