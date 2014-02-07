import os, csv
import sunburnt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from designer_copy import *

HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
PORT = '8888'
COLLECTION = 'saks_20131201_day_dresses'

SOLR_COLLECTION_URL = 'http://'+HOST+':'+PORT+'/solr/'+COLLECTION

print 'Loading designer copy lookup'
brand_copy = load_designer_copy()

class SaksItem:
    def __init__(self, id=None, product_id=None, designer=None, combined_detail=None):
        self.id = id
        self.product_id = product_id
        self.designer = designer
        self.combined_detail = combined_detail        


def query_collection():
    si = sunburnt.SolrInterface(SOLR_COLLECTION_URL)
    solq = si.query('*')
    solq = solq.field_limit(['id', 'product_id', 'designer', 'combined_detail'])

    chunk_size = 500
    start_index = 0

    solq = solq.paginate(start=start_index, rows=chunk_size)
    response = solq.execute(constructor=SaksItem)
    num_results = response.result.numFound

    print 'Found', num_results

    with open( os.environ['NM_HOME'] + '/Data/saks-dresses.tsv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        num_retrieved = 0 
        while num_retrieved < num_results:    
            results = list(response)
            for result in results:
                if result.designer is not None and brand_copy.has_key(result.designer[0].lower()):
                    designer_desc = brand_copy[ result.designer[0].lower() ]
                else:
                    designer_desc = ''
                    
                if result.combined_detail is not None:
                    desc = result.combined_detail.encode('utf-8')                
                    desc_with_designer = desc + '\n' + designer_desc
                
                    writer.writerow([ result.product_id[0], desc_with_designer, result.id ])
                num_retrieved += 1   
    
            if num_retrieved % 10000 == 0:
                f.flush()
                print 'retrieved', num_retrieved
            
            start_index += chunk_size
            solq = solq.paginate(start=start_index, rows=chunk_size)
            response = solq.execute(constructor=SaksItem)
            if response.result.numFound == 0:
                break


query_collection()

