from collections import defaultdict
import numpy as np

#Model for P(Noun|Modifier), P(Noun), P(Concept|Noun), and P(Concept) 
def train_concept_noun_modifier(concepts):
    noun_given_mod_model = defaultdict(lambda: defaultdict(lambda: 0))
    concept_given_noun_model = defaultdict(lambda: defaultdict(lambda: 0))
    noun_model = defaultdict(lambda: 0)    
    modifier_model = defaultdict(lambda: 0)    
    concept_model = defaultdict(lambda: 0)

    for concept in concepts:
        concept_name = concept['name']
        concept_modifiers = concept['modifiers']
                
        for noun_modifiers in concept_modifiers:
            tokens = noun_modifiers.split('|')
            noun = tokens[0]
            mods = tokens[1]

            concept_model[concept_name] += 1
            
            for mod in mods.split(';'):
                noun_mod_dict = noun_given_mod_model[mod]    
                concept_noun_dict = concept_given_noun_model[noun]    
        
                modifier_model[mod] += 1
                noun_mod_dict[noun] += 1
                noun_model[noun] += 1        
                concept_noun_dict[concept_name] += 1                 

    return [noun_given_mod_model, concept_given_noun_model, noun_model, concept_model, modifier_model]


def p_of_noun_given_modifier(models, noun, modifier):
    noun_given_mod_model = models[0]
    return noun_given_mod_model[modifier][noun]
    
def p_of_noun(models, noun):    
    noun_model = models[2]
    #normalizer = np.sum([ noun_model[k] for k in noun_model.keys() ])
    #return noun_model[noun] / float(normalizer)
    return noun_model[noun]

def p_of_concept_given_noun(models, concept, noun):
    concept_given_noun_model = models[1]
    return concept_given_noun_model[noun][concept]

def p_of_concept(models, concept):
    concept_model = models[3]
    #normalizer = np.sum([ concept_model[k] for k in concept_model.keys() ])
    #return concept_model[concept] / float(normalizer)
    return concept_model[concept]
    
def p_of_modifier(models, modifier):
    modifier_model = models[4]
    #normalizer = np.sum([ modifier_model[k] for k in modifier_model.keys() ])
    #return modifier_model[modifier] / float(normalizer)
    return modifier_model[modifier]
    
    
C1 = {}
C1['name'] = 'A'
C1['modifiers'] = ['a|b', 'a|b', 'a|c;b', 'b|c', 'c|a', 'c|b']

C2 = {}
C2['name'] = 'B'
C2['modifiers'] = ['c|a', 'c|b', 'd|a;c', 'd|a', 'd|a', 'd|c', 'd|c']

concepts = [ C1, C2 ]

models = train_concept_noun_modifier(concepts)


def max_descriptors(models, noun=[], modifier=[], concept=[]):
    noun_model = models[2]        
    concept_model = models[3]
    modifier_model = models[4]

    noun_check = lambda n: noun_model.keys() if len(n) == 0 else n
    nouns = noun_check(noun)

    modifier_check = lambda m: modifier_model.keys() if len(m) == 0 else m
    modifiers = modifier_check(modifier)

    concept_check = lambda c: concept_model.keys() if len(c) == 0 else c
    concepts = concept_check(concept) 
    
    max_d = []; max_p = 0.0
    for n in nouns:    
        for m in modifiers:
            for c in concepts:
                p = p_of_noun_given_modifier(models, n, m) * p_of_modifier(models, m) * p_of_concept_given_noun(models, c, n)
                if p > max_p:
                    max_p = p
                    max_d = [n,m,c]
    
    return max_d
    

max_descriptors(models, noun=['d'], concept=['B'])