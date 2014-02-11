# -*- coding: utf-8 -*-
import csv
import pandas as pd
from collections import Counter

from pattern.en import suggest, parse, parsetree, sentiment
from pattern.en import conjugate, lemma, lexeme, wordnet
from pattern.search import search, taxonomy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2

import nltk
from nltk.corpus import framenet as fn



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
                phrases.append( filtered_np )

    return phrases



def categorize_phrases(phrases, use_stem=True):
    stemmer = nltk.stem.PorterStemmer()
    
    records = []    
    for phrase in phrases:        
        matches = []
        for word in phrase:
            if use_stem == True:
                match = taxonomy.classify(stemmer.stem(word.string))
            else:
                match = taxonomy.classify(word.string)
                
            matches.append(match)
            
        phrase_str = ' '.join([ w.string+'/'+w.tag for w in phrase ])
        match_str = ' '.join([ m for m in matches if m ])
        records.append( ( phrase_str, match_str) )
            
    df = pd.DataFrame( records, columns=['phrase', 'category'])
                
    return df
 

 
 

 
 
load_taxonomy('/Users/rsteckel/tmp/SKIN_TAXONOMY.csv')


noun_phrases = extract_noun_phrases('skin')

category_df = categorize_phrases(noun_phrases)


category_df.to_excel('/Users/rsteckel/desktop/categories.xlsx', index=False)


gby = category_df.groupby(['category']).count()
sorted_df = gby.sort(['category'], ascending=0)


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


