# -*- coding: utf-8 -*-
import pandas as pd


def score_map():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select c.name,
                           (count(*) / 1605.0) * 100.0 score
                    from text_classification tc
                    inner join concept c on (c.id = tc.concept_id)
                    where score >= .5
                    group by c.name""")
                    
        rows = cur.fetchall()          
    finally:
        cur.close()
        conn.close()

    scores = {}
    for row in rows:    
        scores[row[0]] = row[1]
        
    return scores




settings = project_settings('nordstrom_dresses')

df = pd.io.parsers.read_csv(settings.latest_classifications())
df.columns = ['project', 'docid', 'concept', 'score']

N = len(df['docid'].unique())
cdf = df[ df['score'] >= .5 ]

cdf[ ['concept', 'score'].groupby('concept').count() 

/ float(N)





import simplejson as json

with open('/Users/rsteckel/Downloads/concept_export.json', 'r') as oldf:
    oldj = json.load(oldf)


scores = score_map()

for j in oldj:
    concept_name = j['id']
    if scores.has_key(concept_name):
        j['nordstroms_product_pct'] = scores[concept_name]    
    else:
        j['nordstroms_product_pct'] = 0.0
        
        
with open('/Users/rsteckel/Downloads/concept_export-12-9-2013.json', 'w') as newf:
    newf.write(json.dumps(oldj, sort_keys=True, indent=4))