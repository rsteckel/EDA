# -*- coding: utf-8 -*-
from extraction.taxonomy import Taxonomy, print_taxonomy
from extraction.semantic_search import TaxonomySearch
from nltk.corpus import framenet as fn

import pattern.search as PS
from pattern.search import Pattern, Classifier, search
from pattern.en import parse, parsetree
from pattern.en import wordnet as pwn
from nltk.corpus import wordnet as wn
from nltk.corpus import framenet as fn
import pandas as pd
import numpy as np

from datasets.customers.tufamilia_dataset import TuFamilia



frames = fn.frames('Medical_conditions')
frames = fn.frames('Causation')
frame = frames[0]  #Take first match

lus = frame['lexUnit'].values()
for lu in lus:
    if lu.has_key('incorporatedFE'):
        print '%20s %10s' % (lu.name, lu['incorporatedFE'])
    else:
        print '%20s %10s' % (lu.name, 'No IFE')

for relation in frame['frameRelations']:
    print '  ', relation 
    
    
for fe in frame['FE']:
    ailment_lus = [x for x in frame.lexUnit.values() if 'incorporatedFE' in x and x.incorporatedFE == fe]
    print fe, '  ', [x.name for x in ailment_lus]


fe = 'Ailment'
fe_lus = [x for x in frame.lexUnit.values() if 'incorporatedFE' in x and x.incorporatedFE == fe]


lu = fe_lus[3]



frames = fn.frames(r'^Causation$')

frames = fn.frames(r'Perception_active')
frame = frames[0]  #Take first match
lus = frame['lexUnit'].values()  
for lu in lus:
    print lu.name




relations = frame['frameRelations']
for relation in relations:
    related_frame = relation['subFrame']
    if related_frame.name != frame.name:
        print related_frame.name
        lus = related_frame['lexUnit'].keys()
        for lu in lus:
            print '  ', lu









s.search(document, pattern='disease') #Search for the word 'disease'

s.search(document, pattern='DISEASE') #Search for anything in the DISEASE taxonomy category

s.search(document, pattern='{JJ} DISEASE') #Search for adjectives in front of anything in the DISEASE taxonomy category

s.search(document, pattern='EXERCISE') #Search for anything in the EXERCISE taxonomy category






dataset = TuFamilia('health')
dataset.load()
#dataset.store()

documents = dataset.documents()
documents = documents[:5]



for document in documents:
    matches = s.document_contains(document, ['DISEASE', 'TREATMENT'])
    if matches:
        print matches

            


for document in documents:
    matches = s.sentence_contains(document, ['DISEASE', 'TARGET'])
    for m in matches:
        print m[0], m[1]
        print m[2]
        print ''







perception = 'functional'

for synset in pwn.synsets(perception, pwn.ADJECTIVE):
    print synset
    print synset.gloss
    print synset.synonyms
    print synset.hypernyms()
    print ''
print '-'*20            
for synset in wn.synsets(perception, 'a'):
    print synset.name()
    print synset.definition()
    print expand_hyponyms(synset.name())
    print ''
    
    



taxonomy = PS.Taxonomy()
taxonomy.append('looks', type='perception')
taxonomy.append('appears', type='perception')


s = "Kiko foreign glitter that looks great in the shade."
s = "I'm also thinking this polish would look amazing over black!"
s = "Oh this is a great brush. Fluffy soft bristles and works like a charm."

pattern = Pattern.fromstring('{SBJ?} * {PERCEPTION} * {JJ?} * {OBJ?} {OBJ?}', taxonomy=taxonomy, strict=True)

#documents = [s]

for document in documents:
    parsed = parsetree(document, lemmata=True, relations=True)
    for sentence in parsed.sentences:
        matches = pattern.search(sentence)
        if matches:
            print sentence.string
            for match in matches:
                for c in match.constituents():
                    print c
            print ''




