# -*- coding: utf-8 -*-
from taxonomy import Taxonomy, print_taxonomy




frames = fn.frames('Medical_conditions')
frames = fn.frames('Causation')
frame = frames[0]  #Take first match

lus = frame['lexUnit'].values()
for lu in lus:
    if lu.has_key('incorporatedFE'):
        print '%20s %10s' % (lu.name, lu['incorporatedFE'])
    else:
        print '%20s %10s' % (lu.name, 'No IFE')




frame = frames[0]  #Take first match


for relation in frame['frameRelations']:
    print '  ', relation 
    
    
for fe in frame['FE']:
    ailment_lus = [x for x in frame.lexUnit.values() if 'incorporatedFE' in x and x.incorporatedFE == fe]
    print fe, '  ', [x.name for x in ailment_lus]


fe = 'Ailment'
fe_lus = [x for x in frame.lexUnit.values() if 'incorporatedFE' in x and x.incorporatedFE == fe]


lu = fe_lus[3]






taxonomy = Taxonomy('o360')

taxonomy.add_category('cat.n', 'animal', synonyms=['feline', 'tomcat', 'kitten'])
taxonomy.add_category('dog', 'animal', synonyms=['puppy', 'mutt'])
taxonomy.add_category('car', 'auto')
taxonomy.add_category('truck', 'auto')

taxonomy.add_framenet_frame('Medical_conditions', 'medical', related='subFrame')
taxonomy.add_framenet_frame(r'^Causation$', 'reasons')
taxonomy.add_framenet_frame('Emotions_of_mental_activity', 'wellness', related='subFrame')





frames = fn.frames()

frame = frames[0]  #Take first match


lus = frame['lexUnit'].keys()  
for lu in lus:
    tokens = lu.split('.')
    self.add_category(tokens[0], frame.name, pos=tokens[1])

if related:
    relations = frame['frameRelations']
    for relation in relations:
        related_frame = relation[related]
        if related_frame.name != frame.name:
            self.add_category(related_frame.name, frame.name)
            
            lus = related_frame['lexUnit'].keys()
            for lu in lus:
                tokens = lu.split('.')
                self.add_category(tokens[0], related_frame.name, pos=tokens[1])











print_taxonomy(taxonomy)


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











import Orange
data = Orange.data.Table("market-basket.basket")

rules = Orange.associate.AssociationRulesSparseInducer(data, support=0.3)
print "%4s %4s  %s" % ("Supp", "Conf", "Rule")
for r in rules[:5]:
    print "%4.1f %4.1f  %s" % (r.support, r.confidence, r)



