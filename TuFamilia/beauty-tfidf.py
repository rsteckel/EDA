# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from pattern.en import suggest, parse, parsetree, sentiment
from pattern.en import conjugate, lemma, lexeme, wordnet
from pattern.search import search, taxonomy


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2

from nltk.corpus import wordnet as wn




filename = '/Users/rsteckel/tmp/Observable_body_parts-sentences-BODYPART1.tsv'
df = pd.read_csv(filename, sep='\t', encoding='utf-8')
df['lemmas'] = df['themeword'].apply(lambda x: lemma(x))



#-------------------Pseudo-doc TF-IDF-------------------
grby = df.groupby(['lemmas']).agg({'sentence': lambda x: ' '.join(x),
                                   'lemmas': np.size })
                                   
sorted_df = grby.sort(['lemmas'], ascending=0)
bpdf = sorted_df[ sorted_df.lemmas >= 50 ]
bpdf.columns = ['BP', 'doc']

vectorizer = TfidfVectorizer(ngram_range=(1,1), use_idf=False, sublinear_tf=True,
                    stop_words='english', min_df=4, max_df=.90)
                    
X = vectorizer.fit_transform(bpdf['doc'])

row = 0
H = X[row,:].data.flatten()

H = -1 * H

inds = np.argsort(H)

fnames = vectorizer.get_feature_names()

for i,x in enumerate(np.nditer(inds)):
    print i, x, bpdf.index[row], H[x], fnames[x]
    if i > 100:
        break






#-------------------X^2 Feature selection---------------------
bps = set(['hair','skin','eye'])

def select_bodypart_features(body_part):
    df['bps'] = df['lemmas'].apply(lambda x: x if x in bps else 'other')

    vectorizer = TfidfVectorizer(ngram_range=(1,1), use_idf=False,
                    stop_words='english', min_df=4, max_df=.90, lowercase=True)



    df['sentence-pos'] = df['sentence'].apply(lambda x: parse(x, chunks=False).replace('/', ''))
    X = vectorizer.fit_transform(df['sentence-pos'])

    selector = SelectKBest(chi2, k=100)

    S = selector.fit_transform(X, df['bps'].tolist())

    fnames = vectorizer.get_feature_names()
    
    indices = selector.get_support(True)                 
    selected_terms = [ fnames[i] for i in indices ]

    return selected_terms





a = wordnet.synsets('tone', pos=wordnet.ADJECTIVE)[0]
b = wordnet.synsets('curly', pos=wordnet.ADJECTIVE)[0]
c = wordnet.synsets('box')[0]
 
print wordnet.ancestor(a, b)
 
print wordnet.similarity(a, a) 
print wordnet.similarity(a, b)
print wordnet.similarity(a, c)  


