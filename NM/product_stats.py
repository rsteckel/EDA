#curl -v http://ec2-50-17-144-252.compute-1.amazonaws.com:8888/solr/neiman_marcus_raw_catalog/update -H 'Content-type:application/json' -d '
#[ 
#	{ 
#	  "id": "df38656be859f2931ebde60d6bd005ff",
#	  "unique_customers_i" : { "set" : 2 },
#	  "unique_record_i" : { "set" : 278 }
#	}
#]'
#
#curl -v http://ec2-50-17-144-252.compute-1.amazonaws.com:8888/solr/neiman_marcus_raw_catalog/get?id=df38656be859f2931ebde60d6bd005ff
#item_code: H2Q3L

import psycopg2
import simplejson as json
import requests

db='o360'
username='ryan'
hostname='192.168.11.31'

SOLR_HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
SOLR_PORT = 8888
SOLR_COLLECTION = 'neiman_marcus_raw_catalog'
SOLR_UPDATE_URL = 'http://'+SOLR_HOST+':'+str(SOLR_PORT)+'/solr/'+SOLR_COLLECTION+'/update'


def export_product_stats():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select c.solr_id,
                            p.annual_revenue, 
                            p.annual_products_sold,
                            p.unique_customers
                    from nm_catalog c
                    inner join nm_product p on (p.nm_product_id = c.cmos_item_code)""")
                    
        rows = cur.fetchall()          
    finally:
        cur.close()
        conn.close()

    docs = []
    for row in rows:
        doc = {}
        doc['id'] = row[0]
        doc['annual_revenue_f'] = { "set" : row[1] }
        doc['annual_products_sold_i'] = { "set" : row[2] }
        doc['unique_customers_i'] = { "set" : row[3] }
        docs.append(doc)
        
    return docs
    

def append_concept_stats(stats):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select solr_id,
                               c.name,
                               pc.score
                        from product_concept pc
                        inner join nm_catalog cat on (cat.id = pc.product_id)
                        inner join concept c on (c.id = pc.concept_id)""")
                    
        rows = cur.fetchall()          
    finally:
        cur.close()
        conn.close()

    products = {}
    for s in stats:
        products[ s['id'] ] = s

    for row in rows:
        solr_id = row[0]
        if products.has_key(solr_id):
            product = products[solr_id]            
            concept = row[1]
            score = row[2]
            
            product['fashion_'+concept+'_f'] = { "set" : score }
            
    return products.values()




def write_file(stats, filename):   
    with open(filename, 'w') as f:
        f.write(json.dumps(stats, sort_keys=True, indent=4))
        f.flush()    


def post_update(stats):
    header = { 'Content-type' : 'application/json' }
    r = requests.post(SOLR_UPDATE_URL, data=json.dumps(stats), headers=header)
    return r
    
    

if __name__ == '__main__':
    stats = export_product_stats()
    print 'Exported', len(stats), 'stats'
    stats = append_concept_stats(stats)
    print 'Appended concepts'
    resp = post_update(stats)
    print 'Returned:', resp.status_code


