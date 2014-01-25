import csv
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet as wn


def synonyms(words):
    all_syns = []        
    for word in words:
        all_syns.extend([l.name for s in wn.synsets(word) for l in s.lemmas])
    return all_syns


concept_vec = synonyms(['luxury'])

print concept_vec

infile = open('/Users/rsteckel/Workspace/NM/product_catalog_features-1000.tdf', 'r')
inreader = csv.reader(infile, delimiter='\t')

corpus = []
corpus.append( ' '.join(concept_vec) )

index = 1
for row in inreader:
    corpus.append(row[9])
    if index % 100 == 0:
        print index
    index += 1

print 'Built corpus'

#corpus = [ ' '.join(romance_vec),
#'This is the first document.',
#'This is the second second document.',
#'And the third romantic one.',
#'Is this the first document?']

print 'Vectorizing...'
#vectorizer = CountVectorizer(ngram_range=(1, 2), token_pattern=r'\b\w+\b', min_df=1) #bigrams
vectorizer = CountVectorizer(token_pattern=r'\b\w+\b', min_df=1)
analyze = vectorizer.build_analyzer()

#analyze('Bi-grams are cool!') == (['bi', 'grams', 'are', 'cool', 'bi grams', 'grams are', 'are cool'])

print 'Running TfIdf...'
X_2 = vectorizer.fit_transform(corpus).toarray()
transformer = TfidfTransformer()
tfidf = transformer.fit_transform(X_2)

print 'Calculating cosines...'
cosines = cosine_similarity(tfidf[0:1], tfidf)

df = pd.DataFrame(cosines.transpose(), columns=['sim'])
print df[df['sim'] > .02].index

print corpus[20]