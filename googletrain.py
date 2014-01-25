import urllib2, urllib, re, collections, operator
from google import search
import simplejson as json
import nltk

def pull_documents(query, num_docs):
    documents = []
    index = 1
    for url in search(query, stop=num_docs):
        print index, 'pulling URL:', url
        try:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            the_page = response.read().decode('utf-8')
            
            raw = nltk.clean_html(the_page.encode('utf-8'))              
            documents.append(raw)
            
            index += 1
        except Exception as inst:
            print 'Error pulling document'
            print inst
            
    return documents


def build_google_corpus(pos_concept_query, neg_concept_query, docs_per_label=100):
    documents = []
    labels = []

    print 'Pulling positive documents'
    pos_documents = pull_documents(pos_concept_query, docs_per_label)
    for doc in pos_documents:
        documents.append(doc)
        labels.append(1)
    
    print 'Pulling negative documents'    
    neg_documents = pull_documents(neg_concept_query, docs_per_label)
    for doc in neg_documents:
        documents.append(doc)
        labels.append(0)
    
    return [documents, labels]


def query_google(query, start):
    start = 9
    # http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=Soccer
    # urlencode the query
    query = urllib.quote(query)
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=' + query + '&start=' + str(start) + '&rsz=large'
    
    try:
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        data_string = opener.open(req).read()
    except urllib2.URLError:
        print "------ Error opening " + url + "..... Timed out?"
        return None

    response = json.loads(data_string)

    urls = []
    results = response['responseData']['results']
    for i in range(len(results)):    
        urls.append(results[i]['url'])
        
    return urls



#results = []
#index = 1
#while len(results) < 64:
#    print index
#    urls = query_google("Soccer", start=index)
#    results = results + urls
#    index = index + len(urls)
#print results





#url = 'http://sixteenfashion.blogspot.com/2011/07/romantic-fashion.html'

#req = urllib2.Request(url)
#response = urllib2.urlopen(req)
#the_page = response.read()
#out = html2text.html2text(the_page)



#docs = pull_documents('fashion romantic', 10)
#docs[0]

