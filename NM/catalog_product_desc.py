import os, csv
import sunburnt

HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
PORT = '8888'
BASE_DIR = os.environ['NM_HOME']+'/Data/'
COLLECTION = 'neiman_marcus_raw_catalog'

SOLR_COLLECTION_URL = 'http://'+HOST+':'+PORT+'/solr/'+COLLECTION


class NMItem:
    def __init__(self, cmos_item_code=None, product_desc=None):
        self.cmos_item_code = cmos_item_code
        self.product_desc = product_desc


def query_collection():
    si = sunburnt.SolrInterface(SOLR_COLLECTION_URL)
    solq = si.query( extract_date="2013-09-21T22:31:19.000000000" )
    solq = solq.field_limit(['cmos_item_code', 'product_desc'])

    chunk_size = 500
    start_index = 0

    solq = solq.paginate(start=start_index, rows=chunk_size)
    response = solq.execute(constructor=NMItem)
    num_results = response.result.numFound

    print 'Found', num_results
    product_descs = []
    
    num_retrieved = 0
    while num_retrieved < num_results:    
        results = list(response)
        for result in results:
            item_code = result.cmos_item_code[0]
            desc = result.product_desc
            if desc is not None and len(desc[0].strip()) > 0:
                desc = desc[0].encode('utf-8').replace('\n', ' ')
                product_descs.append( (item_code, desc) )  
            num_retrieved += 1   

        if num_retrieved % 10000 == 0:
            print 'retrieved', num_retrieved
        
        start_index += chunk_size
        solq = solq.paginate(start=start_index, rows=chunk_size)
        response = solq.execute(constructor=NMItem)
        if response.result.numFound == 0:
            break

    return product_descs

if __name__ == '__main__':
    product_descs = query_collection()

    with open(BASE_DIR+'product_only_desc.txt', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        for desc in product_descs:
            writer.writerow([ desc[0], desc[1] ])
            
