# -*- coding: utf-8 -*-
from sklearn import decomposition

import datasets.customers.running_shoe as rs


def discover_topics(dataset, num_topics=5):
    ids,vectors = dataset.vectors()
    
    # Fit the NMF model
    nmf = decomposition.NMF(n_components=num_topics).fit(vectors)
    
    # Inverse the vectorizer vocabulary to be able
    feature_names = dataset.vectorizer.get_feature_names()
    
    for topic_idx, topic in enumerate(nmf.components_):
        print "Topic #%d:" % (topic_idx+1,)
        print " ".join([feature_names[i] for i in topic.argsort()[:-20 - 1:-1]])
        print ''
        

shoe_dataset = rs.RunningShoeDataset()

discover_topics(shoe_dataset, 10)
