import pysolr
import uuid
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
PORT = '8888'
BASE_DIR = os.environ['NM_HOME']+'/Data/Temporal'



def query_weeks(start_date, end_date, fields):    
    day_i = start_date
    results = None    

    solr = pysolr.Solr('http://'+HOST+':'+PORT+'/solr/'+collection)

    while day_i < end_date:
        skip=0
        chunk=100

        d1 = day_i
        d2 = d1 + relativedelta(weeks=1)
        
        #query = 'timestamp:['+d1.isoformat()+'Z TO '+d2.isoformat()+'Z]'
        query = 'dateCreated:['+d1.isoformat()+'Z TO '+d2.isoformat()+'Z]'

        results = solr.search(query, rows=chunk, start=skip, fl=fields)
        total_hits = results.hits
        print str(d1.date()), str(total_hits), 'results'            

        date_dir = BASE_DIR+'/'+ str(d1.date()) + '/'            
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)
                
        if total_hits > 0:            
            results_retrieved = 0  #TODO   Handle initial results smaller than chunk
            while results_retrieved < total_hits:            
                    
                for result in results:
                    results_retrieved += 1
                    filename = date_dir + str(uuid.uuid4())
                    #print result['score']
                    with open(filename, 'w') as f:
                        content = result['body'][0].strip()                        
                        if len(content) > 100:
                            f.write(content)

                skip += chunk
                print '\trequesting additional', chunk, 'results from', skip 
                results = solr.search(query, rows=chunk, start=skip, fl=fields)                
        day_i = d2



#collection = 'fashion_crawl_try_20131015'
collection = 'sterrell_amazon_shoe_reviews'

start = datetime(2013,6,3)
end = datetime(2013,9,30)
query_weeks(start, end, 'body')



solr = pysolr.Solr('http://'+HOST+':'+PORT+'/solr/neiman_marcus_cleaned_crawl')
results = solr.search('romance', rows=100, start=0, fl='score')
print results.hits

for result in results:
    #print result['score'], result['total_score'], result['id']
    print result['score']


