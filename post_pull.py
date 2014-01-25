import os
import sunburnt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from sklearn import mixture
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import euclidean_distances


HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
PORT = '8888'
COLLECTION = 'fashion_blogs_posts'

SOLR_COLLECTION_URL = 'http://'+HOST+':'+PORT+'/solr/'+COLLECTION


class PostItem:
    def __init__(self, id=None, content=None):
        self.id = id
        self.content = content        


def query_collection():
    si = sunburnt.SolrInterface(SOLR_COLLECTION_URL)
    solq = si.query('*')
    solq = solq.field_limit(['id', 'content'])

    chunk_size = 500
    start_index = 0

    solq = solq.paginate(start=start_index, rows=chunk_size)
    response = solq.execute(constructor=PostItem)
    num_results = response.result.numFound

    print 'Found', num_results

    docs = []

    num_retrieved = 0
    while num_retrieved < num_results:    
        results = list(response)
        for result in results:
            docs.append( result.content[0] )
            num_retrieved += 1   

        if num_retrieved % 10000 == 0:
            print 'retrieved', num_retrieved
        
        start_index += chunk_size
        solq = solq.paginate(start=start_index, rows=chunk_size)
        response = solq.execute(constructor=PostItem)
        if response.result.numFound == 0:
            break

    return docs


docs = query_collection()


vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,3), 
                             min_df=.01, max_df=.99,
                             strip_accents='unicode', sublinear_tf=True)

X_vec = vectorizer.fit_transform(docs)
fnames = vectorizer.get_feature_names()

svd = TruncatedSVD(n_components=50)
X_svd = svd.fit_transform(X_vec.transpose())

kmeans = KMeans(n_clusters=25)
clusters = kmeans.fit_predict(X_svd)    

cnames = np.vstack( (clusters, fnames) ).T

for c in range(25):
    print '\nCluster:', c
    for i in range(len(cnames)):
        if cnames[i][0] == str(c):
            print cnames[i][1]



