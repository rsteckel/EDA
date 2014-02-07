# -*- coding: utf-8 -*-
import string
from collections import defaultdict
import nltk
import pandas as pd

from nltk.corpus import framenet as fn
from textblob import TextBlob

from pattern.en import suggest, parse, parsetree, sentiment
from pattern.en import conjugate, lemma, lexeme
from pattern.search import search, taxonomy


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



#def taxonomy_normalize(sentence):    
#    bp_match = search('BEAUTY_PARTS', parsetree(sentence, lemmata=True))
#    facial_match = search('MAKEUP', parsetree(sentence, lemmata=True))
#    feet_match = search('FEET', parsetree(sentence, lemmata=True))
#    body_match = search('BODY', parsetree(sentence, lemmata=True))    
#    
#    matches = [ [ 'BEAUTY_PARTS-'+word.lemma for word in m] for m in bp_match ] \
#                + [ [ 'MAKEUP-'+word.lemma for word in m] for m in facial_match ] \
#                + [ [ 'FEET-'+word.lemma for word in m] for m in feet_match ] \
#                + [ [ 'BODY-'+word.lemma for word in m] for m in body_match ]
#
#    return matches


def taxonomy_normalize(sentence):    
    bp_match = search('BEAUTY_PARTS', parsetree(sentence, lemmata=True))
    facial_match = search('MAKEUP', parsetree(sentence, lemmata=True))
    feet_match = search('FEET', parsetree(sentence, lemmata=True))
    body_match = search('BODY', parsetree(sentence, lemmata=True))    
    
    matches = ''
    
    if len(bp_match) > 0:
        matches += 'BEAUTY_PARTS-'     
    if len(facial_match) > 0:
        matches += 'MAKEUP-'              
    if len(feet_match) > 0:
        matches += 'FEET-'
    if len(body_match) > 0:
        matches += 'BODY-'

    return matches
    


def noun_phrases(sentence):
    sentence = 'Kate Hudson and now our editor have had their hair done by Pantene is Celebrity Hairstylist.'
    tree = parsetree(sentence)
    search('NP', tree)




    
def find_descriptors(blob, themeword):        
    words = blob.words
    tags = blob.tags
    
    assert(len(tags) == len(words))
    adjs = set(['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'])
    
    descriptors = ''
    for i,word in enumerate(blob.words):
        if word.lower() == themeword.lower():
            if tags[i-1][1] in adjs:
                descriptors += '%s' % (tags[i-1][0])
            if tags[i+1][1] in adjs:
                descriptors += '%s' % (tags[i+1][0])

    if len(descriptors) == 0:
        descriptors = 'None'

    return descriptors



def find_sentiment(blob):
    polarity = blob.sentiment.polarity
    if polarity > .1:
        return 'Pos'
    elif polarity < -.1:
        return 'Neg'        
    return 'None'









s = parsetree('It adds the perfect amount of shimmer to your skin , while protecting it from the sun ( it comes in SPF 20 and 40 ).',
                relations=True, lemmata=True)
for sentence in s:
    for chunk in sentence.chunks:
        print chunk.type, [(w.string, w.type) for w in chunk.words]


s = sentiment('It adds the perfect amount of shimmer to your skin , while protecting it from the sun ( it comes in SPF 20 and 40 ).')



filename = '/Users/rsteckel/tmp/Observable_body_parts-sentences-BODYPART1.tsv'
df = pd.read_csv(filename, sep='\t')


df['themeword'] = df['themeword'].apply(lambda x: x.strip(string.punctuation).lower())
df['lemmas'] = df['themeword'].apply(lambda x: lemma(x))


grby = df.groupby(['lemmas']).count()
sorted_df = grby.sort(['lemmas'], ascending=0)
sorted_df[ sorted_df.lemmas >= 10 ]




records = []
for i,row in df.iterrows():
    try:
        sentence = row.iloc[1]    
        themeword = row.iloc[2] 
        
        blob = TextBlob(sentence)            
        blob = blob.correct()
        
        print '%8s %5s %15s - %s' % (themeword, find_sentiment(blob), find_descriptors(blob, themeword),  sentence)
    except:
        pass
    









##______________________________Pattern______________________________

from pattern.search import taxonomy, WordNetClassifier

taxonomy.classifiers.append(WordNetClassifier())

print taxonomy.parents('hair', pos='NN')
print taxonomy.parents('skin', pos='NN')

print taxonomy.parents('feline', pos='NN')



print taxonomy.children('PRODUCT', recursive=True)
 
from pattern.search import taxonomy, search

taxonomy.append('chicken', type='food')
taxonomy.append('chicken', type='bird')
taxonomy.append('penguin', type='bird')
taxonomy.append('bird', type='animal')

print taxonomy.parents('product')

print taxonomy.children('aspect', recursive=False)
print
print search('FOOD', "I'm eating chicken.")


taxonomy.children('label')


from pattern.search import taxonomy, search
from pattern.search import Classifier

def parents(term):
    return ['quality'] if term.endswith('ness') else []  

taxonomy.classifiers.append(Classifier(parents))
taxonomy.append('cat', type='animal')
 
print search('QUALITY of a|an|the ANIMAL', 'the litheness of a cat')
 



constraint = Constraint.fromstring('JJ?')    #matches any adjective tagged JJ, but it is optional.
constraint = Constraint.fromstring('NP|SBJ')     #matches subject noun phrases.
constraint = Constraint.fromstring('QUANTITY')    #matches siblings of QUANTITY in the taxonomy.











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






##______________________________Framenet______________________________

from nltk.corpus import framenet as fn
fn.lu(3238).frame.lexUnit['glint.v'] is fn.lu(3238)

fn.frame_by_name('Replacing') is fn.lus('replace.v')[0].frame

fn.lus('prejudice.n')[0].frame.frameRelations == fn.frame_relations('Partiality')


fn.lus('look.n')[0].frame
fn.lus('look.n')[1].frame


result = fn.frames(r'(?i)erception')

print result
f = fn.frame(1301)

f.ID
f.definition
for u in f.lexUnit:
    print u

fn.lexical_units('r(?i)look')


from pattern.en import wordnet


[x for x in f.FE]
f.frameRelations

all_lu = set()
for f in fn.frames():    
    lus = [ lu.split('.')[1] for lu in fn.frame(f.ID).lexUnit ]
    for lu in lus:
        all_lu.add(lu)


import nltk
from nltk.tag.simplify import simplify_wsj_tag

from nltk import simple

tagged_sent = nltk.pos_tag(tokens)
simplified = [(word, simplify_wsj_tag(tag)) for word, tag in tagged_sent]




