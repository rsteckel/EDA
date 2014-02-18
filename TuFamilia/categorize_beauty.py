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





def categorize_phrases(sentphrases, body_part_name, use_stem=True):
    stemmer = nltk.stem.PorterStemmer()
    
    records = []    
    for i,row in sentphrases.iterrows():
        sentence = row['sentence']
        phrase = row['phrase']
        
        categories = []
        parents = []
        
        for word in phrase:
            if use_stem == True:
                category = taxonomy.classify(stemmer.stem(word.string))
            else:
                category = taxonomy.classify(word.string)
                
            if category:
                categories.append(category)
                parent = taxonomy.parents(category)
                
                if parent and parent[0] != category:
                    parents.append(parent[0])
                else:
                    parents.append('')
                
                
            #elif word.string == body_part_name:
            #    categories.append(body_part_name)
            #    parents.append(body_part_name)
                
        assert(len(categories) == len(parents))
        
        phrase_str = ' '.join([ w.string+'/'+w.tag for w in phrase ])
        phrase_str = phrase_str.replace(',', '')
        
        sentence_str = sentence.replace(',', '')        
        
        score = len(categories) * (len(categories) / (1.*len(phrase))) 
        for i,category in enumerate(categories):            
            records.append( ( body_part_name, sentence_str, phrase_str, category, parents[i], score) )
            
    df = pd.DataFrame( records, columns=['body_part', 'sentence', 'phrase', 'category', 'parent', 'score'])
                
    return df




def binarize(category_df, filename):
    lb = LabelBinarizer()    

    lb.fit(category_df['category'].unique().tolist())

    #grouped = category_df.groupby(['body_part', 'sentence', 'phrase'])
    grouped = category_df.groupby(['body_part', 'sentence'])
    categories = []
    for key,cats in grouped.category:
        categories.append(list(cats))

    X = lb.fit_transform(categories)    

    Xint = X.astype(int)
    coocc = Xint.T.dot(Xint)
    df = pd.DataFrame(coocc, columns=lb.classes_)
    df.to_csv(filename, index=False)




taxonomy.clear()
load_taxonomy('/Users/rsteckel/tmp/SKIN_TAXONOMY.csv')
body_part = 'skin'
sentphrases = extract_noun_phrases(body_part)
skin_category_df = categorize_phrases(sentphrases, body_part)
binarize(skin_category_df, '/Users/rsteckel/tmp/skin-cooc.csv')


taxonomy.clear()
load_taxonomy('/Users/rsteckel/tmp/EYE_TAXONOMY.csv') 
body_part = 'eye'
sentphrases = extract_noun_phrases(body_part)
eye_category_df = categorize_phrases(sentphrases, body_part)
binarize(eye_category_df, '/Users/rsteckel/tmp/eye-cooc.csv')


taxonomy.clear()
load_taxonomy('/Users/rsteckel/tmp/HAIR_TAXONOMY.csv')
body_part = 'hair'
sentphrases = extract_noun_phrases(body_part)
hair_category_df = categorize_phrases(sentphrases, body_part)
binarize(hair_category_df, '/Users/rsteckel/tmp/hair-cooc.csv')




category_df = pd.concat([skin_category_df, eye_category_df, hair_category_df])
category_df.to_csv('/Users/rsteckel/desktop/categories.csv', index=False, encoding='utf-8')





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








from pattern.web import DBPedia

sparql = '\n'.join((
    'prefix dbo: <http://dbpedia.org/ontology/>',
    'select ?person ?place where {',
    '    ?person a dbo:President.',
 '    ?person dbo:birthPlace ?place.',
 '}'
))
for r in DBPedia().search(sparql, start=1, count=10):
print '%s (%s)' % (r.person.name, r.place.name)

