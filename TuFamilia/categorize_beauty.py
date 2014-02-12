# -*- coding: utf-8 -*-
import csv
import pandas as pd
import numpy as np
from collections import Counter

from pattern.en import suggest, parse, parsetree, sentiment
from pattern.en import conjugate, lemma, lexeme, wordnet
from pattern.search import search, taxonomy

from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.sparse import csr_matrix
import scipy.spatial.distance as ssd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import LabelBinarizer

import nltk
from nltk.corpus import framenet as fn
from nltk.metrics.distance import edit_distance, jaccard_distance, masi_distance





def load_taxonomy(filename, use_stem=True):    
    stemmer = nltk.stem.PorterStemmer()
    
    taxdf = pd.read_csv(filename)
    for i,row in taxdf.iterrows():        
        for synonym in row['Syns'].split(','):
            if use_stem:
                taxonomy.append(stemmer.stem(synonym), type=row['Category'])
            else:
                taxonomy.append(synonym, type=row['Category'])
                
        taxonomy.append(row['Category'], type=row['Parent'])



def extract_noun_phrases(body_part_name):
    body_part_name = 'skin'
    
    stop = nltk.corpus.stopwords.words('english')    
    filename = '/Users/rsteckel/tmp/Observable_body_parts-sentences-BODYPART1.tsv'
    
    df = pd.read_csv(filename, sep='\t', encoding='utf-8')
    df['lemmas'] = df['themeword'].apply(lambda x: lemma(x))
    
    sentences = df[ df['lemmas'] == body_part_name]['sentence'].tolist()
    
    phrases = []
    for sentence in sentences:
        ptree = parsetree(sentence)
        matches = search('NP', ptree)        
        for match in matches:
            filtered_np = [ word for word in match if word.string.lower() not in stop ]
            if len(filtered_np) > 0:
                phrases.append( (sentence, filtered_np) )
    
    return pd.DataFrame(phrases, columns=['sentence', 'phrase'])



def categorize_phrases(phrases, body_part_name, use_stem=True):
    stemmer = nltk.stem.PorterStemmer()
    
    records = []    
    for phrase in phrases:
        matches = []      
        parent = 'NA'
        for word in phrase:
            if use_stem == True:
                match = taxonomy.classify(stemmer.stem(word.string))
            else:
                match = taxonomy.classify(word.string)
                        
            #if word.string == body_part_name:
            #    match = body_part_name
                
            if match:
                parent = ' '.join(taxonomy.parents(match))
                matches.append(match)
        
        score = 1.*len(matches) * (len(matches) / (1. * len(phrase)))
        
        phrase_str = ' '.join([ w.string+'/'+w.tag for w in phrase ])
        match_str = ' '.join([ m for m in matches ])
        
        records.append( ( phrase_str, match_str, score, parent) )
            
    df = pd.DataFrame( records, columns=['phrase', 'category', 'score', 'parent'])
                
    return df
 

 
def cluster_categories(category_tags):    
    catlabels = pd.Categorical.from_array(category_tags)

    N = len(category_tags)
    distanceMatrix = csr_matrix((N,N))
    
    distance_cache = {}    
    
    for i in range(N):
        if i % 100 == 0:
            print '%d of %d' % (i, N)
                
        for j in range(i, N):                
            if i == j:
                distanceMatrix[i,j] = 0
            else:
                a = category_tags.iloc[i].split('_')
                b = category_tags.iloc[j].split('_')
                
                a = [ w for w in a if w != 'skin']
                b = [ w for w in b if w != 'skin']

                a.sort()
                b.sort()
                
                key = ''.join(a)+'-'+''.join(b)
                if distance_cache.has_key(key):
                    distance = distance_cache[key]
                else:                    
                    distance = edit_distance(a,b)
                    distance_cache[key] = distance
                
                distanceMatrix[i,j] = distance
                distanceMatrix[j,i] = distance
                

    dm = ssd.squareform(distanceMatrix.todense())

    dendrogram(linkage(dm, method='complete'), 
               color_threshold=0.3, 
               leaf_label_func=lambda x: catlabels[x],
               leaf_font_size=8)

    f = gcf()
    f.set_size_inches(8, 4);



def binarize(category_tags, filename):
    lb = LabelBinarizer()    
    
    records = []
    for t in category_tags:
        records.append(t.split())
    
    lb.fit(records)
    
    X = lb.transform(records)    
    df = pd.DataFrame(X, columns=lb.classes_)
    df.to_csv(filename, index=False)
    
 
load_taxonomy('/Users/rsteckel/tmp/EYE_TAXONOMY.csv') 
load_taxonomy('/Users/rsteckel/tmp/SKIN_TAXONOMY.csv')
load_taxonomy('/Users/rsteckel/tmp/HAIR_TAXONOMY.csv')

body_part = 'skin'

noun_phrases = extract_noun_phrases(body_part)
noun_phrases.head()
category_df = categorize_phrases(noun_phrases, body_part)



category_df.to_excel('/Users/rsteckel/desktop/categories.xlsx', index=False)



category_tags = category_df['category']
category_tags = category_tags.astype('str')
mask = category_tags.str.len() > 0
category_tags = category_tags.loc[mask]



binarize(category_tags, '/tmp/tags.csv')






gby = category_df.groupby(['category']).agg({'parent': np.size,
                                             'score': np.sum})
                                                                                         
sorted_df = gby.sort(['score'], ascending=0)











from pattern.search import Pattern
from pattern.en import parsetree

t = parsetree('Chuck Norris is cooler than Dolph Lundgren.', lemmata=True)
p = Pattern.fromstring('{NP} be * than {NP}')
m = p.match(t)
print m.group(1)
print m.group(2)





from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()
lmtzr.lemmatize('humidity')


from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()
st.stem('luminous') 



lemma('humidity')

frames = fn.frames_by_lemma(r'skin')
for f in frames:
    print '%s - %s\n' % (f.name, f.definition)

fn.lexical_units(r'')
    
fn.frames_by_lemma(r'(?i)a little')    
    




for f in ('reflect', 'bank'):
    taxonomy.append(f, type='angle')

for f in ('bank', 'financial-institution'):
    taxonomy.append(f, type='finance')
    

t = parsetree('A field of daffodils is white.', lemmata=True)
print search('PLANT', t) 

taxonomy.parents('daffodil', recursive=True)
taxonomy.children('plant', recursive=False)

taxonomy.classify('bank')





from pattern.en import wordnet


a = wordnet.synsets('tone')[4]

b = wordnet.synsets('color')[0]

wordnet.similarity(a,b)




a = ['this', 'is', 'a', 'test']
b = ['this', 'was', 'a', 'test']

edit_distance(a, b)

jaccard_distance(set(a), set(b))

masi_distance(set(a), set(b))






