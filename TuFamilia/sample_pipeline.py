# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:36:47 2014

@author: rsteckel
"""


dataset = TuFamilia('health', query={'lang':'en'})
dataset.load()
#dataset.store()

documents = dataset.documents()
documents = documents

corpus_terms = CorpusTerms(documents)
corpus_terms.term_prob('diet', alpha=1)

term_probs = corpus_terms.vocabulary_prob(alpha=1)
term_set = [t[0] for t in term_probs[:1000]]



test_docs1 = ['The bank of the river was flooded after the rainstorm']
test_docs2 = ['I put my money in the bank to earn interest']


sense_tag1(test_docs1)
sense_tag1(test_docs2)
print '-'*10
sense_tag2(test_docs1)
sense_tag2(test_docs2)



sense_tag1(documents[:10])
sense_tag2(documents[:10])

