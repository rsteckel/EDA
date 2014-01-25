from textblob import TextBlob
import csv, os, collections, itertools

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn import mixture


from sklearn.datasets import fetch_20newsgroups


filename = os.environ['NM_HOME']+'/Data/product_catalog_features.tdf'
reader = csv.reader(open(filename,'r'), delimiter='\t')

product_pos = ['NN', 'NNP', 'NNS', 'NNPS']
attributes_pos = ['JJ', 'JJR', ]

nouns = collections.defaultdict(lambda: [])

index = 1
for row in reader:
    desc = row[12]
    desc = desc.replace('..', '. ')
    blob = TextBlob(desc)
    try:
        for sentence in blob.sentences:
            sblob = TextBlob(str(sentence))
            tags = sblob.tags
            for i in range(len(tags)):
                if tags[i][1] in product_pos:
                    #win_tags = tags[max(i,i-6):min(i+6,len(tags))]
                    win_tags = tags[max(0,i-4):i]
                    for wt in win_tags:
                        if wt[1] in attributes_pos:
                            adjs = wt[0].replace('.', ' ').strip()
                            noun = tags[i][0].lower().replace('.', ' ').strip()
                            nouns[ noun ].append(adjs)
    except ValueError:
        pass
    
    if index % 100 == 0: print index
    index += 1
    if index > 2000:
        break

#for k,v in nouns.items():
#    print k, v, '\n'

filtered_nouns = [ na for na in nouns.items() if len(na[1]) > 1 ]

print 'Vectorizing'
adjs =  [ ' '.join(a[1]) for a in filtered_nouns ]
vectorizer = TfidfVectorizer(use_idf=True)
X = vectorizer.fit_transform(adjs)

print 'Running LSA'
lsa = TruncatedSVD(5)
X = lsa.fit_transform(X)
X = Normalizer(copy=False).fit_transform(X)

print X.shape

names = [ na[0] for na in filtered_nouns ]
#neighbors = 5
#for i in range(len(names)):
#    sims = cosine_similarity(X[i,:], X)
#    ii = sims.argsort()[-neighbors:]
#    top_n = ii[0][-neighbors::]
#    print names[i], ':', [ names[n] for n in top_n if n != i]


#km = KMeans(n_clusters=50, init='k-means++', max_iter=100, n_init=1)
#km.fit(X)

dpgmm = mixture.DPGMM(n_components = 50)
dpgmm.fit(X)

clusters = zip(names, dpgmm.predict(X) )
clusters.sort(key = lambda t: t[1])

for c in clusters:
    print c
