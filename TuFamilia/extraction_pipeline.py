# -*- coding: utf-8 -*-
from datasets.customers.tufamilia_dataset import TuFamilia

from pattern.en import parsetree

import enchant


dataset = TuFamilia('health', query={'lang':'en'})
dataset.load()
#dataset.store()

documents = dataset.documents()[:1]


#corpus_terms = CorpusTerms(documents)
#corpus_terms.term_prob('diet', alpha=1)
#term_probs = corpus_terms.vocabulary_prob(alpha=1)
#term_set = [t[0] for t in term_probs[:1000]]

#test_docs1 = ['The bank of the river was flooded after the rainstorm']
#test_docs2 = ['I put my money in the bank to earn interest']

#sense_tag1(test_docs1)
#sense_tag1(test_docs2)
#print '-'*10
#sense_tag2(test_docs1)
#sense_tag2(test_docs2)


#TODO: Spellcheck
d = enchant.Dict("en_US")
d.check("Hello")
d.check("Helo")
d.suggest("Helo")

for document in documents:
    #TODO: spellcheck

    parsed_doc = parsetree(document, lemmata=True)
    
    #docs = sense_tag1(parsed)
    docs = sense_tag2(parsed_doc)




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
            
            
            
