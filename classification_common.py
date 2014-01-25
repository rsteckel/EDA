import numpy as np
import sys, os, csv, string

#from shared.config.Config import Config
#from shared.lwbd.Solr import Solr

csv.field_size_limit(sys.maxsize)

def run_solr_query(concept_name, concept_query):
    out_file_path = os.environ['NM_HOME']+'/Data/'+concept_name+'_corpus.tdf'
    
    try:
        os.remove(out_file_path)
    except OSError:
        pass    

    query_list = concept_query.split()
    if len(query_list) == 1:  #single term
        term_query = 'long_desc_text_only:'+concept_query
    else:
        term_query = ' AND '.join(['long_desc_text_only:'+q for q in query_list])
        
    query_string = 'extract_date:"2013-09-21T22:31:19.000000000" '+term_query

    print 'Pulling documents for', concept_name, 'using query', query_string

    max_records = None # or None for all records
    collection = 'neiman_marcus_raw_catalog'
    field_string = ','.join(
        (
        'cmos_item_code',
        'long_desc_text_only',
        'detail_bullets',
        'score'
        )
    )
    delim = '\t'
    multi_value_delim = '.'
    escape_newlines = False
    
    config = Config()
    config.http_debug = True
    solr = Solr(config)

    worked = solr.query_to_file(
        out_file_path=out_file_path,
        query_string=query_string,
        max_records=max_records,
        collection=collection,
        field_string=field_string,
        delim=delim,
        multi_value_delim=multi_value_delim,
        escape_newlines=escape_newlines,
        )

    if worked:
        print out_file_path + ' Done!'
    else:
        print 'ERROR'
        
    return out_file_path


def convert_concept(concept_name, solr_corpus_path, label):
    infile = open(solr_corpus_path, 'r')

    reader = csv.reader(infile, delimiter='\t')

    replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))

    documents = []
    labels = []

    for row in reader:
        #item = row[0]
        desc_text = row[1]
        bullets = row[2]
        #score = row[3]
        
        clean_bullets = bullets.translate(replace_punctuation)
        clean_text = desc_text.translate(replace_punctuation)
    
        #writer.writerow([ [item], [clean_bullets] ])
        documents.append([ clean_bullets + ' ' + clean_text ])
        labels.append(label)

    return [documents, labels]


def build_product_desc_corpus(pos_concept, pos_concept_query, neg_concept, neg_concept_query):
    print 'Pulling positive documents with query:', pos_concept_query
    pos_concept_path = run_solr_query(pos_concept, pos_concept_query)
    pos_documents, pos_labels = convert_concept(pos_concept, pos_concept_path, 1)

    print 'Pulling negative documents with query:', neg_concept_query
    neg_concept_path = run_solr_query(neg_concept, neg_concept_query)
    neg_documents, neg_labels = convert_concept(neg_concept, neg_concept_path, 0)

    pos_examples = zip(pos_documents, pos_labels)
    neg_examples = zip(neg_documents, neg_labels)
    
    documents = []
    labels = []
    
    for doc,label in pos_examples:
        documents.append(doc[0])
        labels.append(label)

    for doc, label in neg_examples:
        documents.append(doc[0])
        labels.append(label)

    return [documents, labels]



def show_most_informative_features(vocabulary, clf, n=20):
    if hasattr(clf, 'coef_'):
        c_f = sorted(zip(clf.coef_[0], vocabulary))
        #print '%25s%45s' % tuple(clf.classes_)
        top = zip(c_f[:n], c_f[:-(n+1):-1])
        #for (c1,f1),(c2,f2) in top:
        #    print "\t%.4f\t%-15s\t\t%.4f\t%-15s" % (c1,f1,c2,f2)
        for (c1,f1),(c2,f2) in top:
            print "\t%.4f\t%-15s" % (c2,f2)
    elif hasattr(clf, 'feature_importances_'):
        importances = clf.feature_importances_
        #std = np.std([tree.feature_importances_ for tree in clf.estimators_], axis=0)
        indices = np.argsort(importances)[::-1]
        names = vocabulary
        for i in indices[np.arange(10)]:
            print "\t%-15s\t%.4f" % (names[i], importances[i])
    else:
        print 'Unknown importance'


#def top_terms(classifier, vectorizer, n=50):    
#    c_f = sorted(zip(classifier.coef_[0], vectorizer.get_feature_names()))
#    return [str(t[1]) for t in c_f[:-(n+1):-1] ]
#
#def top_term_scores(classifier, vectorizer, n=50):
#    c_f = sorted(zip(classifier.coef_[0], vectorizer.get_feature_names()))
#    return c_f[:-(n+1):-1]


def concept_training_filename(pos_concept, neg_concept):
    return os.environ['NM_HOME']+'/Data/'+pos_concept+'-'+neg_concept+'-train.txt'

def concept_vectorizer_filename(pos_concept, neg_concept):
    return os.environ['NM_HOME']+'/Models/'+pos_concept+'-'+neg_concept+'-vectorizer.bin'

def concept_classifier_filename(pos_concept, neg_concept):
    return os.environ['NM_HOME']+'/Models/'+pos_concept+'-'+neg_concept+'-classifier.bin'

def concept_pipeline(pos_concept, neg_concept):
    return os.environ['NM_HOME']+'/Models/'+pos_concept+'-'+neg_concept+'-pipeline.bin'

def load_concept_training(pos_concept, neg_concept, filetype='fashion-google'):    
    labels = []
    documents = []    
    
    pos_file = open(os.environ['NM_HOME']+'/Data/'+pos_concept+'-'+filetype+'.txt', 'r')
    pos_reader = csv.reader(pos_file, delimiter='\t')
    for row in pos_reader:
        if len(row) > 0:
            labels.append(1)
            documents.append(row[0])
    pos_file.close()
            
    neg_file = open(os.environ['NM_HOME']+'/Data/'+neg_concept+'-'+filetype+'.txt', 'r')
    neg_reader = csv.reader(neg_file, delimiter='\t')
    for row in neg_reader:
        if len(row) > 0:
            labels.append(0)
            documents.append(row[0])
    neg_file.close()    
    
    return [documents, labels]


def store_concept_training(concept_name, documents, filetype='fashion-google'):
    train_file = open(os.environ['NM_HOME']+'/Data/'+concept_name+'-'+filetype+'.txt', 'w')
    writer = csv.writer(train_file, delimiter='\t')
    
    for i in range(len(documents)):
        writer.writerow([ documents[i] ])
    
    train_file.flush()
    train_file.close()
