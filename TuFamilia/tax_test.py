# -*- coding: utf-8 -*-
from taxonomy import Taxonomy, print_taxonomy
from semantic_search import TaxonomySearch
from nltk.corpus import framenet as fn


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






document = """Cancer is a serious disease that affects many people. Tumors are 
                the most common sign of cancer. Aerobics can prevent it."""


taxonomy = Taxonomy('o360')
taxonomy.add_category('disease', 'health')
taxonomy.add_hyponyms('disease.n.01', 'disease')
taxonomy.add_hyponyms('ill_health.n.01', 'disease')
taxonomy.add_category('exercise', 'health')
taxonomy.add_hyponyms('exercise.n.01', 'exercise')





taxonomy = Taxonomy('o360')
taxonomy.add_insight('treat-insight', 'health') #Add insight (relation) to 'health' domain

taxonomy.add_entity('disease', 'treat-insight')  
taxonomy.add_example('ill_health.n.01', 'disease')
taxonomy.add_example('disease.n.01', 'disease')


taxonomy.add_entity('target', 'treat-insight')  
taxonomy.add_example('treat.v.03', 'target')
taxonomy.add_example('cure.v.01', 'target')
taxonomy.add_example('heal.v.01', 'target')
taxonomy.add_example('alleviate.v.01', 'target')
taxonomy.add_example('better.v.03', 'target')


taxonomy.add_entity('treatment', 'treat-insight')  
taxonomy.add_example('treatment.n.01', 'treatment')
taxonomy.add_example('care.n.01', 'treatment')
taxonomy.add_example('medicine.n.02', 'treatment')
taxonomy.add_example('surgery.n.04', 'treatment')
taxonomy.add_example('roentgenogram.n.01', 'treatment')
taxonomy.add_example('remedy.n.02', 'treatment')



print_taxonomy(taxonomy)



s = TaxonomySearch(taxonomy)

s.search(document, pattern='disease') #Search for the word 'disease'

s.search(document, pattern='DISEASE') #Search for anything in the DISEASE taxonomy category

s.search(document, pattern='{JJ} DISEASE') #Search for adjectives in front of anything in the DISEASE taxonomy category

s.search(document, pattern='EXERCISE') #Search for anything in the EXERCISE taxonomy category




from datasets.customers.tufamilia_dataset import TuFamilia

dataset = TuFamilia('beauty')

dataset.load()
dataset.store()

documents = dataset.documents()
documents = documents[:250]

for document in documents:
    s.search(document, pattern='TREATMENT * DISEASE or DISEASE * TREATMENT')






