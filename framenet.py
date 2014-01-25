import simplejson as json
import collections, operator

from concept_datastore import *
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans



def parse_frames(filename, interesting_frames):
    with open(filename, 'r') as f:
        fn = json.load(f)

        #docs were too sparse
        category_frames = collections.defaultdict(lambda: collections.defaultdict(lambda: []))
        id_map = solr_id_lookup()
        
        documents = fn['documents']
        for document in documents:
            doc_name = document['name']
            sentences = document['sentences']
            for sentence in sentences:
                frames = sentence['frames']
                for frame in frames:
                    ftype = frame['frame_type']
                    if ftype in interesting_frames:
                        ftarget = frame['frame_target']
                        elements = frame['frame_elements']
                        for element in elements:                
                            fetype = element['fe_type']
                            fetarget = element['fe_target']
                            if id_map.has_key(doc_name):
                                cat_frames = category_frames[ id_map[doc_name] ]
                                cat_frames[ftype].append(fetarget)
    return category_frames
    
    
    
def filter_frames(category_frames, frame_type):
    docs = []
    for cat,frames in category_frames.items():
        if frames.has_key(frame_type):
            terms = ' '.join(frames[frame_type])
            terms = terms.lower()
            terms = terms.replace('.', '')
            terms = terms.strip()        
            docs.append( (cat, terms) )
    return docs



def cluster_frame_types(doc_terms, num_clusters):
    #vectorizer = CountVectorizer()
    vectorizer = TfidfVectorizer(ngram_range=(1,1), stop_words='english', use_idf=True)
    X_vec = vectorizer.fit_transform(doc_terms)
    
    lsa = TruncatedSVD(10)
    X = lsa.fit_transform(X_vec.transpose())
    X = Normalizer(copy=False).fit_transform(X)
    
    estimator = KMeans(n_clusters=num_clusters)
    estimator.fit(X)
    clusters_labels = estimator.predict(X)
    
    vec_vocab = sorted(vectorizer.vocabulary_.iteritems(), key=operator.itemgetter(1))
    col_names = [ ti[0] for ti in vec_vocab ]
    term_clusters = sorted(zip(col_names, clusters_labels), key=lambda x: x[1])

    clusters = collections.defaultdict(lambda: [])
    for term,cl in term_clusters:
        clusters[cl].append(term)
    
    return clusters




filename = '/Users/rsteckel/Downloads/partial_semafor_cat_data.json'
interesting_frames = ['Abounding_with', 'Clothing', 'Clothing_parts', 'Color', 'Dimension', 'Emotion_directed', 'Shapes']
frames = parse_frames(filename, interesting_frames)

cat_docs = filter_frames(frames, 'Emotion_directed')

doc_terms = [ dt[1] for dt in cat_docs ]

clusters = cluster_frame_types(doc_terms, 10)

for c,terms in clusters.items():
    print c, terms, '\n'
    