import os
import sunburnt

HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
PORT = '8888'
COLLECTION = 'neiman_marcus_raw_catalog'

SOLR_COLLECTION_URL = 'http://'+HOST+':'+PORT+'/solr/'+COLLECTION


class CatalogItem:
    def __init__(self, brand_name=None, designer_copy=None):
        self.brand_name = brand_name
        self.designer_copy = designer_copy        


def load_designer_copy():
    si = sunburnt.SolrInterface(SOLR_COLLECTION_URL)
    solq = si.query(extract_date='2013-09-21T22:31:19.000000000')
    solq = solq.field_limit(['brand_name', 'designer_copy'])

    chunk_size = 500
    start_index = 0

    solq = solq.paginate(start=start_index, rows=chunk_size)
    response = solq.execute(constructor=CatalogItem)
    num_results = response.result.numFound

    print 'Found', num_results

    brand_copy = {}

    num_retrieved = 0
    while num_retrieved < num_results:    
        results = list(response)
        for result in results:
            if result.brand_name is not None and result.designer_copy is not None:
                if len(result.designer_copy[0]) > 0:
                    brand_copy[ result.brand_name[0].lower() ] = result.designer_copy[0].encode('utf-8')
            num_retrieved += 1   

        if num_retrieved % 10000 == 0:
            print 'retrieved', num_retrieved
        
        start_index += chunk_size
        solq = solq.paginate(start=start_index, rows=chunk_size)
        response = solq.execute(constructor=CatalogItem)
        if response.result.numFound == 0:
            break

    return brand_copy



