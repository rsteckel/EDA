
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


def run_counts():
    catalog_items, catalog_descs = load_catalog('Data/product_desc_text.txt')
    vec = CountVectorizer(stop_words='english', strip_accents='unicode')
    data = vec.fit_transform(catalog_descs)
    vocab = vec.get_feature_names()
    dist = data.sum(axis=0).transpose()
    
    f = open('Data/nm_vocab_counts.csv', 'w')
    for term, count in zip(vocab, dist):
        f.write(str(count[0,0])+', '+term+'\n')
    f.flush()
    f.close()
    
run_counts()
    