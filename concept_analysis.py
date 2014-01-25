from concept_datastore import *
from text_utils import *
#from wordvectors import *

import re, collections, operator



#Save POS file to DB
save_item_pos_tags("Data/pos-1.json")
save_item_pos_tags("Data/pos-2.json")
save_item_pos_tags("Data/pos-3.json")


save_item_modifiers('Data/pos-1.json')
save_item_modifiers('Data/pos-2.json')
save_item_modifiers('Data/pos-3.json')




def top_terms_by_tags(items, concept, tags, top_n=100, include_counts=False):    
    counts = collections.defaultdict(lambda: 1)
    concept_items = [ it for it in items.values() if concept in it.concepts() ]

    for i in range(len(concept_items)):        
        concept_tags = [ tag[0] for tag in concept_items[i].pos_tags() if tag[1] in tags ]
        for tag in concept_tags:
            counts[tag.lower()] += 1

    st = sorted(counts.iteritems(), key=operator.itemgetter(1), reverse=True)[:top_n]
    if include_counts:
        return st

    return [t[0] for t in st]    
    
    
def top_terms_by_modifiers(items, concept, top_n=1e6, include_counts=False):    
    counts = collections.defaultdict(lambda: 1)
    _items = [ it for it in items.values() if concept in it.concepts() ]

    for i in range(len(_items)):        
        concept_mods = [ mod[0].lower()+'|'+mod[1].lower() for mod in _items[i].modifiers() ]
        for mod in concept_mods:
            counts[mod.lower()] += 1

    st = sorted(counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    st = st[:min(top_n, len(st))]
    if include_counts:
        return st

    return [t[0] for t in st]    
    


def top_modified_nouns(items, concept, top_n=100, include_counts=False):    
    counts = collections.defaultdict(lambda: 1)
    _items = [ it for it in items.values() if concept in it.concepts() ]

    for i in range(len(_items)):        
        mod_nouns = [ mod[0].lower() for mod in _items[i].modifiers() ]
        for n in mod_nouns:
            counts[n] += 1

    st = sorted(counts.iteritems(), key=operator.itemgetter(1), reverse=True)[:top_n]
    if include_counts:
        return st

    return [t[0] for t in st]    
    



def concept_tag_intersect(concept_items, conceptA, conceptB, set_tags=['NN'], top_n=100):    
    aset = set([ bt for bt in top_terms_by_tags(concept_items, conceptA, set_tags, top_n ) ])
    bset = set([ rt for rt in top_terms_by_tags(concept_items, conceptB, set_tags, top_n ) ])

    return [ d for d in aset.intersection(bset) ]


def concept_tag_overlap(concept_items, conceptA, conceptB, set_tags=['NN'], top_n=100):    
    aset = set([ bt for bt in top_terms_by_tags(concept_items, conceptA, set_tags, top_n ) ])
    bset = set([ rt for rt in top_terms_by_tags(concept_items, conceptB, set_tags, top_n ) ])

    print conceptA, 'unique:', [ d for d in aset.difference(bset) ], '\n'
    print conceptB, 'unique:', [ d for d in bset.difference(aset) ], '\n'
    intersect = concept_tag_intersect(concept_items, conceptA, conceptB, set_tags, top_n)
    print 'Intersection:', intersect




def concept_modifier_overlap(concept_items, conceptA, conceptB, top_n=100):    
    aset = set([ bt for bt in top_terms_by_modifiers(concept_items, conceptA, top_n ) ])
    bset = set([ rt for rt in top_terms_by_modifiers(concept_items, conceptB, top_n ) ])

    uniqueA = [ d for d in aset.difference(bset) ]
    uniqueB = [ d for d in bset.difference(aset) ]
    intersect = [d for d in aset.intersection(bset) ]
    
    uniqueA.sort(); uniqueB.sort(); intersect.sort()    
    
    print conceptA, 'unique:', uniqueA, '\n'
    print conceptB, 'unique:', uniqueB, '\n'

    print 'Concept intersection', intersect



def concept_modified_noun_intersection(concept_items, conceptA, conceptB, top_n=100):    
    aset = set([ bt for bt in top_modified_nouns(concept_items, conceptA, top_n ) ])
    bset = set([ rt for rt in top_modified_nouns(concept_items, conceptB, top_n ) ])

    return [d for d in aset.intersection(bset) ]


def print_modifier_differences(concept_items, conceptA, conceptB, terms, top_n=100):
    aset = set([ bt for bt in top_terms_by_modifiers(concept_items, conceptA, top_n ) ])
    bset = set([ rt for rt in top_terms_by_modifiers(concept_items, conceptB, top_n ) ])
    
    A = set([ a for a in aset if a.split('|')[0] in terms ])
    B = set([ b for b in bset if b.split('|')[0] in terms ])
    
    print '\n', conceptA, A.difference(B)
    print '\n', conceptB, B.difference(A)





wordvecterms = find_wordvector_terms('romantic')


romantic_items = load_items('romantic')


scores = compare_concepts()    
df = pd.DataFrame(scores)
df.columns = ['Concept_A', 'Concept_B', 'Similarity']
df.to_csv('Data/concept_sims.csv', index=False)




concept_items = load_concept_items(min_concept_score=.6)


print_term_vector('romantic')


concept_tag_overlap(concept_items, 'romantic', 'bohemian', ['NN', 'NNP'])

concept_tag_overlap(concept_items, 'romantic', 'bohemian', ['NN'])

concept_tag_overlap(concept_items, 'romantic', 'bohemian', ['JJ'] )

concept_tag_intersect(concept_items, 'romantic', 'bohemian')



concept_modifier_overlap(concept_items, 'romantic', 'bohemian', 1000)





conceptA = 'romantic'

conceptA = 'couture'
conceptB = 'romantic'

common_nouns = concept_tag_intersect(concept_items, conceptA, conceptB, ['NN'], 1000)


modifiersA = top_terms_by_modifiers(concept_items, conceptA, 1000 )
modsA = [ m for m in modifiersA if m.split('|')[0] in common_nouns]
print 'A', modsA


modifiersB = top_terms_by_modifiers(concept_items, conceptB, 1000 )
modsB = [ m for m in modifiersB if m.split('|')[0] in common_nouns ]
print 'B', modsB




nouns = concept_modified_noun_intersection(concept_items, conceptA, conceptB, 10)


print print_modifier_differences(concept_items, 'forward', 'edgy', [ 'neckline' ], 500)

print print_modifier_differences(concept_items, 'forward', 'couture', [ 'neckline' ], 500)

print print_modifier_differences(concept_items, 'couture', 'edgy', [ 'neckline' ], 500)

print print_modifier_differences(concept_items, 'romantic', 'couture', [ 'neckline' ], 500)






all_mods = top_terms_by_modifiers(concept_items, conceptA, 1e6, True)

mod_model = collections.defaultdict(lambda: 1)
_items = [ it for it in concept_items.values() if concept in it.concepts() ]

[ mod[1] for mod in _items[i].modifiers() ]

for i in range(len(_items)):        
    concept_mods = [ mod[1].split(';').lower() for mod in _items[i].modifiers() ]
    for mod in concept_mods:
        mod_model[mod.lower()] += 1
        



f = open('/tmp/concept_terms.json', 'w')
conceptj = load_concepts_json(top_n=30)
f.write(conceptj)
f.close()



concepts = load_concepts()

for concept in concepts:
    name = concept[1]
    terms,weights = load_term_vector(name)
    print name.capitalize()
    for i in range(25):
        print '\t'+terms[i]
    print '\n'
        
        
        
