import collections, itertools
import nltk.classify.util, nltk.metrics
from nltk.corpus import movie_reviews, stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
 
from googletrain import build_google_corpus 
 

pos_concept =  'romantic'
pos_concept_query = 'fashion romantic blog'
neg_concept = 'sporty'
neg_concept_query = 'fashion sporty blog'


print '\nBuilding labeled corpus'
documents, labels = build_google_corpus(pos_concept_query, neg_concept_query)
print str(len(documents))+' documents, '+str(len(labels))+' labels' 
 
word_fd = FreqDist()
label_word_fd = ConditionalFreqDist()

for i in range(len(documents)):
    print 'Doc', i
    doc = documents[i]
    label = labels[i]
    tokens = nltk.word_tokenize(doc)
    for token in tokens:
        if label == 0:
            word = token.lower()
            word_fd.inc(word)
            label_word_fd['neg'].inc(word)
        else:
            word = token.lower()
            word_fd.inc(word)
            label_word_fd['pos'].inc(word)
            
pos_word_count = label_word_fd['pos'].N()
neg_word_count = label_word_fd['neg'].N()
total_word_count = pos_word_count + neg_word_count
 
word_scores = {}
 
for word, freq in word_fd.iteritems():
    pos_score = BigramAssocMeasures.chi_sq(label_word_fd['pos'][word],
        (freq, pos_word_count), total_word_count)
    neg_score = BigramAssocMeasures.chi_sq(label_word_fd['neg'][word],
        (freq, neg_word_count), total_word_count)
    word_scores[word] = pos_score + neg_score
 
best = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True)[:10000]
bestwords = set([w for w, s in best])
 
print bestwords
 
#def best_word_feats(words):
#    return dict([(word, True) for word in words if word in bestwords])
 
#print 'evaluating best word features'
#evaluate_classifier(best_word_feats)
 
#def best_bigram_word_feats(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
#    bigram_finder = BigramCollocationFinder.from_words(words)
#    bigrams = bigram_finder.nbest(score_fn, n)
#    d = dict([(bigram, True) for bigram in bigrams])
#    d.update(best_word_feats(words))
#    return d
 
#print 'evaluating best words + bigram chi_sq word features'
#evaluate_classifier(best_bigram_word_feats)