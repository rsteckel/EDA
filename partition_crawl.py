import os
import sunburnt
import uuid

from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser


HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
PORT = '8888'
BASE_DIR = os.environ['NM_HOME']+'/Data/Temporal'
COLLECTION = 'fashion_crawl_try_20131015'

SOLR_COLLECTION_URL = 'http://'+HOST+':'+PORT+'/solr/'+COLLECTION


class FashionPage:
    def __init__(self, content=' ', date_url=None, date_header_last_modified=None):
        self.content = content
        self.date_url = date_url
        self.date_header_last_modified = date_header_last_modified
        if date_url is not None:
            self.pub_date = dateutil.parser.parse(date_url[0])
        elif date_header_last_modified is not None:
            self.pub_date = dateutil.parser.parse(date_header_last_modified[0])
        else:
            self.pub_date = None
        
    def __repr__(self):
        return 'Page(pub date: "%s")' % (self.pub_date)



def write_result(result, min_date, min_length=100):
    pub_date = result.pub_date
    pub_date = pub_date.replace(tzinfo=None)
    content = result.content[0].strip()

    contentutf8 = content.encode('utf-8')
    
    if pub_date > min_date and len(content) > min_length:
        weekstart = pub_date - relativedelta(days=pub_date.weekday())
        date_dir = BASE_DIR+'/'+COLLECTION+'/'+str(weekstart.date())           
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)
        
        filename = date_dir+'/'+str(uuid.uuid4())
        with open(filename, 'w') as f:
            f.write(contentutf8)



def query_collection(start_date):
    si = sunburnt.SolrInterface(SOLR_COLLECTION_URL)
    solq = si.query( si.Q(date_url__gt=start_date.isoformat()) | si.Q(date_header_last_modified__gt=start_date.isoformat()))
    solq = solq.field_limit(['content', 'date_url', 'date_header_last_modified'])

    chunk_size = 500
    start_index = 0

    solq = solq.paginate(start=start_index, rows=chunk_size)
    response = solq.execute(constructor=FashionPage)
    num_results = response.result.numFound

    print 'Found', num_results

    num_retrieved = 0
    while num_retrieved < num_results:    
        results = list(response)
        for result in results:
            write_result(result, start_date)
            num_retrieved += 1   

        if num_retrieved % 10000 == 0:
            print 'retrieved', num_retrieved
        
        start_index += chunk_size
        solq = solq.paginate(start=start_index, rows=chunk_size)
        response = solq.execute(constructor=FashionPage)
        if response.result.numFound == 0:
            break


start = datetime(2008,1,1)
start = start.replace(tzinfo=None)
query_collection(start)