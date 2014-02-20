# -*- coding: utf-8 -*-
from taxonomy import Taxonomy, print_taxonomy

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






taxonomy = Taxonomy('o360')


taxonomy.add_category('disease', 'health')
taxonomy.add_hyponyms('disease.n.01', 'disease')

print_taxonomy(taxonomy)

taxonomy.add_category('cat.n', 'animal', synonyms=['feline', 'tomcat', 'kitten'])
taxonomy.add_category('dog.n', 'animal', synonyms=['puppy', 'mutt'])
taxonomy.add_category('car', 'auto')
taxonomy.add_category('truck', 'auto')

print_taxonomy(taxonomy)

taxonomy.add_category('medical', 'health')
taxonomy.add_framenet_frame('Medical_conditions', 'medical')


print_taxonomy(taxonomy)



taxonomy.add_framenet_frame(r'^Causation$', 'reasons')
taxonomy.add_framenet_frame('Emotions_of_mental_activity', 'wellness', related='subFrame')

print_taxonomy(taxonomy)







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


taxonomy.frames('approach')


taxonomy.children('causation')







print taxonomy.search('kitten', 'NN')
print taxonomy.search('kitten')
print taxonomy.search('kitten', 'NN', retry=True)

print taxonomy.parents('cancer.n', recurse=True)
print taxonomy.parents('cancer', 'n', recurse=True)
print taxonomy.parents('cancer', 'NN', recurse=False)

print taxonomy.search('hernia', 'NN')
print taxonomy.parents('hernia', 'NN', recurse=False)
print taxonomy.parents('hernia', 'NN', recurse=True)

print taxonomy.children('Medical_conditions')







from nltk.corpus import framenet as fn
docs = fn.documents()
len(docs)
doc = docs[0]



import Orange
data = Orange.data.Table("market-basket.basket")

rules = Orange.associate.AssociationRulesSparseInducer(data, support=0.3)
print "%4s %4s  %s" % ("Supp", "Conf", "Rule")
for r in rules[:5]:
    print "%4.1f %4.1f  %s" % (r.support, r.confidence, r)



