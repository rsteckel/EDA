import os, sys, re, warnings, time, random
import chardet
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import gevent

from gevent import monkey
import google
import bing_client
import nltk
import sunburnt

from classification_common import *

from shared.config.Config import Config
from shared.lwbd.Solr import Solr

import simplejson

monkey.patch_all()
import urllib2


SOLR_HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
SOLR_PORT = '8888'
SOLR_COLLECTION = 'sterrell_tmp'
SOLR_COLLECTION_URL = 'http://'+SOLR_HOST+':'+SOLR_PORT+'/solr/'+SOLR_COLLECTION

replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))


def clean_pages(pages):
    documents = []    
    for i in range(len(pages)):
        doc = pages[i].lower()

        try:                     
            char_detection = chardet.detect(doc)
            charset = char_detection['encoding']
            if charset == None:
                charset = 'utf-8'

            decoded_text = doc.decode(charset, errors='ignore')
            text = nltk.clean_html(decoded_text)                        
            utf8_text = text.encode('utf-8')            
            text_page = utf8_text.translate(replace_punctuation)
            words = re.findall('[a-z]+', text_page)            
            #check words???
            documents.append( ' '.join(words) )    
            
            if len(documents) % 100 == 0:
                print '\t', len(documents), 'of', len(pages)
        except LookupError as le:
            print le #Bad/unknown charset
        except UnicodeError as inst:
            print "string is not UTF-8"
            print inst
            
    return documents    
    


def download_doc(urls):
    pages = []
    for url in urls:
        try:                   
            req = urllib2.Request(url) 
            response = urllib2.urlopen(req)
            page = response.read()
            
            #Try and use http header for decoding
            charset = response.headers.getparam('charset')   
            if charset == None:
                char_detection = chardet.detect(page)            
                charset = char_detection['encoding']
                if charset == None:
                    charset = 'utf-8'
            
            decoded_page = page.decode(charset, errors='ignore')
            pages.append(decoded_page.encode('utf-8', errors='ignore'))
            
        except Exception as inst:
            print 'Error pulling document', url
            print inst

    return pages
    


def web_query(query, num_docs):
    results = []
    #uas = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    #       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2']           
    #google.Request.add_header('User-Agent', uas[ random.randint(0, len(uas)-1) ])
    #print 'Searching Google'
    #for r in google.search(query, stop=num_docs): #Google search
    #    results.append(r)    
#    print 'Sleeping 30 secs'
#        time.sleep(30)
    print 'Searching Bing'    
    for r in bing_client.bing_search(query, 'Web', num_docs):
        results.append(r)
    
    return results


def partition_list(l, n):
    lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    return lol(l, n)


def google_training_docs(query, num_docs):
    print 'Running web search,', query, num_docs
    urls = web_query(query, num_docs)    
    print 'Web search returned', len(urls), 'results'    

    pages = []    
    try:
        jobs = [gevent.spawn(download_doc, urlset) for urlset in partition_list(urls,5)]
        gevent.joinall(jobs)
    
        for job in jobs:
            pages += job.value
    
    except Exception as inst:
        print inst
    finally:
        gevent.shutdown()
        
    return pages


def lucid_training_docs(query, num_records=1000):        
    query_list = query.split()
    if len(query_list) == 1:  #single term
        term_query = 'content:'+query
    else:
        term_query = ' AND '.join(['content:'+q for q in query_list])

    #collection = 'crawl_from_long_fashion_blogs_list'
    collection = 'fashion_crawl_try_20131015'
    field_string = ','.join( ('content', 'score') )
    
    config = Config()
    config.http_debug = True
    solr = Solr(config)

    json_response = solr.query_solr(
        collection=collection,
        query=term_query,
        field_string=field_string,
        start=0,
        rows=num_records)

    response = simplejson.loads(json_response)
    response['response']['numFound']

    docs = response['response']['docs']
    
    pages = []
    for i in range(len(docs)):
        page = docs[i]['content'][0]
        pages.append(page.encode('utf-8') )

    return pages
    


def lucid_sunburnt_docs(query, num_records=1000):
    si = sunburnt.SolrInterface(SOLR_COLLECTION_URL)
    solq = si.query(query)
    solq = solq.field_limit(['body'])

    chunk_size = 100
    start_index = 0

    solq = solq.paginate(start=start_index, rows=chunk_size)
    response = solq.execute()
    num_results = response.result.numFound

    print 'Found', num_results

    pages = []
    while len(pages) < num_results:    
        results = list(response)
        for result in results:
            page = result['body'][0]
            pages.append(page.encode('utf-8')) 

        if len(pages) % 1000 == 0:
            print 'retrieved', len(search_results)
    
        start_index += chunk_size
        solq = solq.paginate(start=start_index, rows=chunk_size)
        response = solq.execute()
        if response.result.numFound == 0:
            break
        
    return pages


def build_corpus(concept, concept_query, training_generator, filetype, num_docs=100):                             
    pages = training_generator(concept_query, num_docs)

    print 'Cleaning HTML'    
    documents = clean_pages(pages)

    print 'Writing', concept, 'training file', ' type=', filetype, len(documents), 'documents'
    store_concept_training(concept, documents, filetype)



def usage_exit(name):
    print 'usage:', name, '<concept name> <concept query>'
    sys.exit(1)
    


if __name__ == '__main__':    
    if len(sys.argv) != 3:
        usage_exit(sys.argv[0])
        
    universe = 'fashion'    
    use_web_search = True
    
    concept = sys.argv[1]
    concept_query = sys.argv[2]
    
    print 'Building corpus: concept =', concept, '; query =', concept_query

    if use_web_search:
        filetype = universe+'-bing'
        training_generator = google_training_docs
        build_corpus(concept, concept_query, training_generator, filetype, 250)            
    else:        
        filetype = universe+'-lucid'
        training_generator=lucid_sunburnt_docs    
        build_corpus(concept, concept_query, training_generator, filetype, 500)    
                                 

