import re, collections, operator, time, string, os
from itertools import chain

from gensim.models import word2vec
from concept_datastore import *


print 'Loading trained word vectors'
t0 = time.time()
fashion_vectors = os.environ['NM_HOME']+'/Data/word2vec_fashion_2013102113_1150k_phrase.bin'
WORDVEC_MODEL = word2vec.Word2Vec.load_word2vec_format(fashion_vectors, binary=True)
print (time.time() - t0) / 60.0, 'minutes'
 
# "boy" is to "father" as "girl" is to ...?
#model.most_similar(['boy', 'father'], ['girl'], topn=10)
#model.most_similar(positive=['bohemian'] )


 
def top_word_vectors(term, top_n=5):
    try:
        tv_scores = WORDVEC_MODEL.most_similar( [ term ] )
        terms = [ tv[0].translate(string.maketrans("",""), string.punctuation) for tv in tv_scores ]
        top_terms = terms[:min(len(terms), top_n)]
        term_str = ' '.join(set( chain.from_iterable( [ t.split('_') for t in top_terms] )))
        return term_str
    except:
        return term



def print_concept_vectors():
    concepts = ['cute','romantic','subtle','casual','artistic','contemporary',
                'beautiful','gorgeous','sweet','amazing','chic','demure','bohemian',
                'lovely','pretty','modern','dolcissimo','couture','adorable','airy',
                'cleaner','dressy','fantastic','special','stunning','darling',
                'elegant','feminine','futuristic','geek','industrial','sleek',
                'sultry','elemental','luxe','vibrant']
            
    for concept in concepts:
        print concept, '-', top_word_vectors(concept)

