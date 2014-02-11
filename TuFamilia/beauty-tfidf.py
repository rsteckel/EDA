# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from pattern.en import suggest, parse, parsetree, sentiment
from pattern.en import conjugate, lemma, lexeme
from pattern.search import search, taxonomy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2

from nltk.corpus import wordnet as wn


filename = '/Users/rsteckel/tmp/Observable_body_parts-sentences-BODYPART1.tsv'
df = pd.read_csv(filename, sep='\t', encoding='utf-8')
df['lemmas'] = df['themeword'].apply(lambda x: lemma(x))




grby = df.groupby(['lemmas']).agg({'sentence': lambda x: ' '.join(x),
                                   'lemmas': np.size })
     
                              
sorted_df = grby.sort(['lemmas'], ascending=0)
bpdf = sorted_df[ sorted_df.lemmas >= 50 ]
bpdf.columns = ['BP', 'doc']

vectorizer = TfidfVectorizer(ngram_range=(1,3), use_idf=False,
                    stop_words='english', min_df=3, max_df=.95)
X = vectorizer.fit_transform(bpdf['doc'])

row = 1
H = X[row,:].data.flatten()

inds = np.argsort(H)

fnames = vectorizer.get_feature_names()

for i,x in enumerate(np.nditer(inds)):
    print i, x, H[x], fnames[x]
    if i > 100:
        break







bps = set(['hair','skin','eye'])
df['bps'] = df['lemmas'].apply(lambda x: x if x in bps else 'other')


vectorizer = TfidfVectorizer(ngram_range=(1,3))
X = vectorizer.fit_transform(df['sentence'])

selector = SelectKBest(chi2, k=500)
selector.fit_transform(X, df['bps'].tolist())

fnames = vectorizer.get_feature_names()
    
indices = selector.get_support(True)                 
selected_terms = [ fnames[i] for i in indices ]






wn.synsets('skin')
