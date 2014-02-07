# -*- coding: utf-8 -*-
import string
from collections import defaultdict
import nltk
import pandas as pd

from nltk.corpus import framenet as fn
from textblob import TextBlob
from pattern.en import suggest
from pattern.search import search, taxonomy
from pattern.en import parsetree
from pattern.en import sentiment

filename = '/Users/rsteckel/tmp/Observable_body_parts-sentences-BODYPART1.tsv'
df = pd.read_csv(filename, sep='\t')


df['themeword'] = df['themeword'].apply(lambda x: x.strip(string.punctuation).lower())

grby = df.groupby(['themeword']).count()
sorted_df = grby.sort(['themeword'], ascending=0)
sorted_df[ sorted_df.themeword >= 10 ]


#for f in ('rose', 'lily', 'daisy', 'daffodil', 'begonia'):
#    taxonomy.append(f, type='flower')
#t = parsetree('A field of daffodils is white.', lemmata=True)
#print search('FLOWER', t) 


for f in ('hair', 'skin'):
    taxonomy.append(f, type='beauty_parts')

for f in ('face','eye','lip'):
    taxonomy.append(f, type='makeup')

for f in ('ankle', 'toe', 'heel'):
    taxonomy.append(f, type='feet')
    
for f in ('back','neck','body','hand','head','breast','knee'):
    taxonomy.append(f, type='body')



def taxonomy_normalize(sentence):    
    bp_match = search('BEAUTY_PARTS', parsetree(sentence, lemmata=True))
    facial_match = search('MAKEUP', parsetree(sentence, lemmata=True))
    feet_match = search('FEET', parsetree(sentence, lemmata=True))
    body_match = search('BODY', parsetree(sentence, lemmata=True))    
    
    matches = [ [ 'BEAUTY_PARTS-'+word.lemma for word in m] for m in bp_match ] \
                + [ [ 'MAKEUP-'+word.lemma for word in m] for m in facial_match ] \
                + [ [ 'FEET-'+word.lemma for word in m] for m in feet_match ] \
                + [ [ 'BODY-'+word.lemma for word in m] for m in body_match ]

    return matches









result = fn.frames(r'(?i)bservable')

f = fn.frame(119)

f.ID
f.definition
for u in f.lexUnit:
    print u
    
[x for x in f.FE]
f.frameRelations




df.columns

records = []
for i,row in df.iterrows():
    try:
        sentence = row.iloc[1]    
        themeword = row.iloc[2] 
        
        blob = TextBlob(sentence)            
        blob = blob.correct()
        print themeword, blob.sentiment.polarity, taxonomy_normalize(sentence)
    except:
        pass
    







from pattern.web import DBPedia

sparql = '\n'.join((
'prefix dbo: <http://dbpedia.org/ontology/>',
'select ?person ?place where {',
'    ?person a dbo:President.',
'    ?person dbo:birthPlace ?place.',
'}'
))

for r in DBPedia().search(sparql, start=1, count=1000):
    print '%s (%s)' % (r.person.name, r.place.name)









 




