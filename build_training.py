import sys, re

from googletrain import build_google_corpus
from classification_common import *

if len(sys.argv) != 5:
    print 'usage:', sys.argv[0], '<pos name> <pos query> <neg name> <neg query>'


#pos_concept =  'romantic'
#pos_concept_query = 'fashion romantic'
#neg_concept = 'sporty'
#neg_concept_query = 'fashion sporty'


pos_concept =  sys.argv[1]  # 'romantic'
pos_concept_query = sys.argv[2]  # 'romantic'
neg_concept = sys.argv[3]  # 'sporty'
neg_concept_query = sys.argv[4]  # 'sporty'


print '\nBuilding labeled corpus'
documents, labels = build_google_corpus(pos_concept_query, neg_concept_query, 250)
print str(len(documents))+' documents, '+str(len(labels))+' labels'

web_stopwords = set(['http', 'www', 'google', 'facebook', 'twitter', 'wordpress', 'com', 'newsletter',
                     'posted', 'comment', 'comments', 'tumblr', 'posted', 'rss', 'blogger',
                     'javascript', 'instagram', 'login', 'quot'])

filtered_docs = []
for i in range(len(documents)):
    words = re.findall('[a-z]+', documents[i].lower())
    filtered_words = [w for w in words if not w in web_stopwords]
    filtered_docs.append( ' '.join(filtered_words) )


if len(filtered_docs) != len(labels):
    print 'Error filtering docs'
    sys.exit(1)


#desc_documents, desc_labels = build_product_desc_corpus(pos_concept, pos_concept_query, neg_concept, neg_concept_query)
#train_docs = filtered_docs + desc_documents
#train_labels = labels + desc_labels

train_docs = filtered_docs
train_labels = labels

print 'Writing training file'
store_concept_training(pos_concept, neg_concept, filtered_docs, labels)

inv_labels = np.array( np.invert(labels, dtype='bool'), dtype='int32') 
store_concept_training(neg_concept, pos_concept, filtered_docs, inv_labels)
    