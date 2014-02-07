import pickle, os, csv, operator
import pandas as pd
from collections import defaultdict
from classification_common import *
from text_utils import *
import nltk


COLORS = color_lookup()
FABRICS = fabric_lookup()


def load_pipeline(pos_concept, neg_concept):
    pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))
    return pipeline
    

def load_docs(dirname):
    listing = os.walk(dirname).next()
    basedir = listing[0]
    filenames = listing[2]
    
    docs = []
    for filename in filenames:
        f = open(basedir+'/'+filename, 'r')
        content = ' '.join(f.readlines())
        docs.append(content)
    return docs
    

def classify_range(docs, pipeline, min_score):
    probs = pipeline.predict_proba(docs)

    pos_indices = [ i for i in range(len(probs)) if probs[i,1] > min_score]
    
    return len(pos_indices) / float(len(docs))


def vectorize_weeks(concept_name, project_dir, vector_dir):
    pos_concept = concept_name
    neg_concept = 'random'
    
    pipeline = load_pipeline(pos_concept, neg_concept)
    
    vectorizer = pipeline.named_steps['vectorizer']
    selector = pipeline.named_steps['selector']
    
    subdirs = os.walk(project_dir).next()[1]
    subdirs.sort()
    subdirs = subdirs[-52:]    #********  remove ********
    
    for subdir in subdirs:
        print 'Vectorizing', subdir
        docs = load_docs(project_dir+'/'+subdir)
        if len(docs) > 0:
            X_vec = vectorizer.transform(docs)
            X_sel = selector.transform(X_vec)
            pickle.dump(X_sel, open(vector_dir+'/'+subdir+'-vectorized.pckl', 'w'))
    


def concept_term_count(vectorizer, selector, classifier, X_sel, pos_indices, top_n=5):
    counts = defaultdict(lambda: 0)
    
    for p in pos_indices:
        coef_i = np.where( classifier.coef_ > 0 )[1]
        doc_i = np.where( X_sel[p,:].toarray() > 0 )[1]
        names = np.asarray(vectorizer.get_feature_names())[selector.get_support()]
        terms = [ names[i] for i in np.intersect1d(coef_i, doc_i) ]
        for term in terms:
            counts[term] += 1

    term_counts = sorted(counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    count_str = ';'.join([ tw[0]+','+str(tw[1]) for tw in term_counts[:top_n] ])
    
    return count_str



def concept_attribute_count(vectorizer, selector, classifier, X_sel, pos_indices, top_n=5):
    color_counts = defaultdict(lambda: 0)    
    fabric_counts = defaultdict(lambda: 0)    
    
    for p in pos_indices:        
        coef_i = np.where( classifier.coef_ > 0 )[1]
        doc_i = np.where( X_sel[p,:].toarray() > 0 )[1]
        names = np.asarray(vectorizer.get_feature_names())[selector.get_support()]
        terms = [ names[i] for i in np.intersect1d(coef_i, doc_i) ]
        for term in terms:        
            if(COLORS.has_key(term)):
                color_counts[term] += 1
            elif(FABRICS.has_key(term)):
                fabric_counts[term] += 1

    color_counts = sorted(color_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    color_count_str = ';'.join([ tw[0]+','+str(tw[1]) for tw in color_counts[:top_n] ])
    
    fabric_counts = sorted(fabric_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    fabric_count_str = ';'.join([ tw[0]+','+str(tw[1]) for tw in fabric_counts[:top_n] ])
    
    return [color_count_str, fabric_count_str]



def classify(concept_name, project_dir, min_score=.5):
    pos_concept = concept_name
    neg_concept = 'random'
    
    pipeline = load_pipeline(pos_concept, neg_concept)
        
    outfilename = project_dir+'-'+pos_concept+'-scores.csv'
    with open(outfilename, 'w') as week_file:
        writer = csv.writer(week_file)
        writer.writerow(['Week', 'NumDocs', 'Pct'])
        
        subdirs = os.walk(project_dir).next()[1]
        subdirs.sort()
        for subdir in subdirs:
            docs = load_docs(project_dir+'/'+subdir)
            print 'Classifying', subdir, len(docs), 'documents'
            if len(docs) > 0:
                range_pct = classify_range(docs, pipeline, min_score)
                print '\t'+str(range_pct)
                writer.writerow([subdir, len(docs), range_pct])
                week_file.flush()
            
    return records


def classify_vectors(concept_name, project_dir, vector_dir, min_score=.5):
    pos_concept = concept_name
    neg_concept = 'random'
    
    pipeline = load_pipeline(pos_concept, neg_concept)
    
    vectorizer = pipeline.named_steps['vectorizer']
    classifier = pipeline.named_steps['classifier']
    selector = pipeline.named_steps['selector']
    
    outfilename = project_dir+'-'+pos_concept+'-scores.csv'
    with open(outfilename, 'w') as week_file:
        writer = csv.writer(week_file)  #, delimiter='\t')
        writer.writerow(['Week', 'NumConcept', 'NumDocs'])
        
        vecfiles = os.listdir(vector_dir)
        vecfiles.sort()
        
        for vecfile in vecfiles:
            filename = vector_dir+'/'+vecfile
            X_sel = pickle.load(open(filename, 'r'))
            tokens = vecfile.split('-')
            week_dir = '-'.join(tokens[:3])
            
            print 'Classifying', week_dir, X_sel.shape[0], 'documents'
            if X_sel.shape[0] > 0:                
                probs = classifier.predict_proba(X_sel)                
                pos_indices = [ i for i in range(X_sel.shape[0]) if probs[i,1] > min_score]    
                range_pct = len(pos_indices) / float(X_sel.shape[0])
                
                #week_term_str = concept_term_count(vectorizer, selector, classifier, X_sel, pos_indices)                
                #attribute_strs = concept_attribute_count(vectorizer, selector, classifier, X_sel, pos_indices)                
                #records.append( (week_dir, len(pos_indices), X_sel.shape[0], week_term_str) )
                #print '\t'+str(range_pct)
                #writer.writerow( [ week_dir, len(pos_indices), X_sel.shape[0], week_term_str, attribute_strs[0], attribute_strs[1] ] )
                #week_file.flush()

                print '\t'+str(range_pct)
                writer.writerow( [ week_dir, len(pos_indices), X_sel.shape[0] ] )
                week_file.flush()            




def build_series(concept_name, project_dir, vector_dir, min_score=.5):
    pos_concept = concept_name
    neg_concept = 'random'
    
    pipeline = load_pipeline(pos_concept, neg_concept)
    classifier = pipeline.named_steps['classifier']
    
    concept_series = []
    concept_series.append( ['Week', 'Signal'] )
    
    vecfiles = os.listdir(vector_dir)
    vecfiles.sort()
        
    for vecfile in vecfiles:
        X_sel = pickle.load(open(vector_dir+'/'+vecfile, 'r'))
        tokens = vecfile.split('-')
        week_dir = '-'.join(tokens[:3])
                
        probs = classifier.predict_proba(X_sel)                
        pos_indices = [ i for i in range(X_sel.shape[0]) if probs[i,1] > min_score]    
        range_pct = (len(pos_indices) / float(X_sel.shape[0])) * 100.0
        
        concept_series.append( [week_dir, range_pct] )

    return concept_series



def concept_pct(concept_name, project_dir, vector_dir, min_score=.5):
    pos_concept = concept_name
    neg_concept = 'random'
    
    pipeline = load_pipeline(pos_concept, neg_concept)
    
    vectorizer = pipeline.named_steps['vectorizer']
    classifier = pipeline.named_steps['classifier']
    selector = pipeline.named_steps['selector']
            
    records = []
    vecfiles = os.listdir(vector_dir)
    vecfiles.sort()

    concept_documents = 0    
    total_documents = 0
    
    for vecfile in vecfiles:
        X_sel = pickle.load(open(vector_dir+'/'+vecfile, 'r'))
        tokens = vecfile.split('-')
        week_dir = '-'.join(tokens[:3])
        
        if X_sel.shape[0] > 0:                
            probs = classifier.predict_proba(X_sel)                
            pos_indices = [ i for i in range(X_sel.shape[0]) if probs[i,1] > min_score]    
            concept_documents += len(pos_indices)
            total_documents += X_sel.shape[0]
            
        
    print "%s,%d,%d,%f" % (concept_name, concept_documents, total_documents, (concept_documents/float(total_documents))*100)



def docs_per_week(vector_dir):    
    vecfiles = os.listdir(vector_dir)
    vecfiles.sort()
        
    for vecfile in vecfiles:
        X_sel = pickle.load(open(vector_dir+'/'+vecfile, 'r'))
        tokens = vecfile.split('-')
        week_dir = '-'.join(tokens[:3])
        
        print week_dir, X_sel.shape[0], 'documents'





BASE_DIR = os.environ['NM_HOME']+'/Data/Temporal'
#COLLECTION = 'fashion_crawl_try_20131015'
COLLECTION = 'fashion_crawl_2year'
TEMPORAL_DIR = os.environ['NM_HOME']+'/Data/Temporal/'+COLLECTION
VECTOR_DIR = os.environ['NM_HOME']+'/Data/Temporal/vectors'


concepts = ['adorable','amazing','artistic','beautiful','bohemian','casual','chic',
 'contemporary','couture','cute','darling','demure','dressy','elegant','fantastic',
 'feminine','futuristic','geek','gorgeous','industrial','lovely','luxe','modern',
 'pretty','romantic','sleek','stunning','subtle','sultry','sweet','vibrant']
#
#concepts = ['subtle',]
#
for concept in concepts:
    print 'Running', concept
    records = classify_vectors(concept, TEMPORAL_DIR, VECTOR_DIR)
    #build_series(concept, TEMPORAL_DIR, VECTOR_DIR)
    #concept_pct(concept, TEMPORAL_DIR, VECTOR_DIR)

#docs_per_week(VECTOR_DIR)

#vectorize_weeks('romantic', TEMPORAL_DIR, VECTOR_DIR) #Use random classifier 'romantic'

#weekly_attributes(TEMPORAL_DIR)