import simplejson as json
import os, pickle, csv
from sklearn.feature_extraction.text import CountVectorizer

import nltk
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder, BigramAssocMeasures
from nltk.corpus import stopwords

from classification_common import *
from concept_datastore import *




def vocabulary_cache_filename():
    return os.environ['NM_HOME']+'/Data/nm_vocabulary.cache'
    
def catalog_description_filename():
    return os.environ['NM_HOME']+'/Data/product_desc_text.txt'
    
def product_only_description_filename():
    return os.environ['NM_HOME']+'/Data/product_only_desc.txt'
    
def vectorized_catalog_filename():
    return os.environ['NM_HOME']+'/Data/catalog-vectorized.cache'
    
def extended_stopword_filename():
    return os.environ['NM_HOME']+'/Data/extended_stopwords.txt'

def color_db_filename():
    return os.environ['NM_HOME']+'/Data/colors-db.txt'

def fabric_db_filename():
    return os.environ['NM_HOME']+'/Data/fabrics-db.txt'




def month_stopwords():
    months = ['january','february','march','april','may','june','july',
                        'august','september','october','november','december']
    return months

def web_stopwords():
    web = ['http', 'www', 'google', 'facebook', 'twitter', 'wordpress', 'com', 'newsletter',
           'posted', 'comment', 'comments', 'tumblr', 'posted', 'rss', 'blogger',
           'javascript', 'instagram', 'login', 'quot', 'post', 'subscribe', 'rights', 
           'reserved', 'privacy', 'policy', 'copyright', 'contact', 'email', 'online', 
           'account', 'atom', 'subscribe', 'gt', 'lt', 'website', 'image', 'page', 'content',
           'amp', 'review', 'faq']
                     
    return web

def retail_stopwords(): 
    retail = ['designer', 'shop', 'tv', 'video', 'cart', 'tips', 'add', 'service',
              'description', 'rm', 'shipping', 'usd', 'wholesale', 'delivery', 'report',
              'returns', 'customer']
    
    return retail
    
    
def extended_stopwords():
    with open(extended_stopword_filename(), 'r') as f:
        words = [ line.strip() for line in f.readlines() ]
        return words

    
def nm_stopwords():  
    #return stopwords.words('english') + months_stopwords() + web_stopwords() + retail_stopwords()
    return extended_stopwords() + web_stopwords() + retail_stopwords()



def load_training_documents(pos_concept, neg_concept, filetype):
    print 'Loading training data.', 'Filetype=', filetype
    documents, labels = load_concept_training(pos_concept, neg_concept, filetype)
    
    print '\nLoaded', len(documents), 'training documents and labels'
    return [documents, labels]


def load_catalog(filename):    
    item_codes = []
    descs = []
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            item_codes.append(row[0])
            descs.append(row[1])
            
    return [item_codes, descs]


def load_prod_desc_only_catalog():    
    filename = product_only_description_filename()
    item_codes = []
    descs = []
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            item_codes.append(row[0])
            descs.append(row[1])
            
    return [item_codes, descs]


def build_nm_vocabulary(stopwords, use_cache=True):
    cached_vocab_filename = vocabulary_cache_filename()
        
    vocab = {}
    if os.path.exists(cached_vocab_filename) and use_cache:
        with open(cached_vocab_filename, 'r') as f:
            print '\tUsing cached vocabulary'
            vocab = pickle.load(f)
    else:
        catalog_items, desc_documents = load_catalog(catalog_description_filename())   
        print '\tBuilding vocabulary from', len(desc_documents), 'catalog descriptions'     
        cvec = CountVectorizer(stop_words=stopwords, ngram_range=(1,2))
        cvec.fit_transform(desc_documents)
        vocab = cvec.vocabulary_
        print '\tCaching vocabulary'
        if use_cache:
            with open(cached_vocab_filename, 'w') as f:
                pickle.dump(cvec.vocabulary_, f)    

    print 'Using Neiman Marcus catalog vocabulary. Length:', len(vocab)    
    return vocab
    

def collocations(words, window):
    finder = BigramCollocationFinder.from_words(words, window_size = window)
    #finder = TrigramCollocationFinder.from_words(words, window_size = window)
    finder.apply_freq_filter(2)
    ignored_words = nltk.corpus.stopwords.words('english')
    finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in ignored_words)
    bigram_measures = BigramAssocMeasures()
    return finder.nbest(bigram_measures.likelihood_ratio, 10) 



def color_lookup():
    colors = {}
    with open(color_db_filename(), 'r') as color_file:
        for line in color_file.readlines():
            color = line.lower().strip()
            colors[color] = True
            
    return colors


def fabric_lookup():
    fabrics = {}
    with open(fabric_db_filename(), 'r') as fabric_file:
        for line in fabric_file.readlines():
            fabric = line.lower().strip()
            fabrics[fabric] = True
            
    return fabrics


