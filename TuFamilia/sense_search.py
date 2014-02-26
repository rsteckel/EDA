# -*- coding: utf-8 -*-
from pattern.search import Pattern, Taxonomy, Classifier, search
from pattern.en import parsetree


def parents(term):
    results = []
    if term.endswith('ed'):
        results = ['action']
    return results


classifier = Classifier(parents=parents)

animal_taxonomy = Taxonomy()
animal_taxonomy.classifiers.append(classifier)
animal_taxonomy.append('cat.n.01', type='animal')
animal_taxonomy.append('ran.v.01', type='action')



s = 'The cat.n.01 ran.v.01 across the room before it vomited.'
s = 'The cat.n.01 ran.v.01 across the room before cat.n.01 vomited.' #coref resolved
parsed = parsetree(s, lemmata=True)


valid_chunks = set(['NP', 'VP'])


pattern = Pattern.fromstring('{ACTION}', taxonomy=animal_taxonomy)
pattern = Pattern.fromstring('{ANIMAL?} {ACTION}', taxonomy=animal_taxonomy, strict=True)

for sentence in parsed.sentences:
    matches = pattern.search(sentence)
    if matches:
        for m in matches:
            print m
    print ''
            