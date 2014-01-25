# -*- coding: utf-8 -*-
from datastore import *


import csv
import collections
import requests

SOLR_HOST = 'ec2-50-17-144-252.compute-1.amazonaws.com'
SOLR_PORT = 8888

def update_classififications(company, post=False):
    UPDATE_URL = ''
    if company == 'saks':
        classification_filename = '/Users/rsteckel/o360Projects/highfashion/saks_dresses/classifications/20131210-104607-classifications.csv'
        SOLR_COLLECTION = 'saks_20131201_day_dresses'
        UPDATE_URL = 'http://'+SOLR_HOST+':'+str(SOLR_PORT)+'/solr/'+SOLR_COLLECTION+'/update'    
    elif company == 'nordstroms':
        classification_filename = '/Users/rsteckel/o360Projects/highfashion/nordstrom_dresses/classifications/20131210-105733-classifications.csv'
        SOLR_COLLECTION = 'nordstrom-catalog'
        UPDATE_URL = 'http://'+SOLR_HOST+':'+str(SOLR_PORT)+'/solr/'+SOLR_COLLECTION+'/update'    
    else:
        return
      
    concept_map = load_concept_id_map()      
      
    classified_products = []
    with open(classification_filename, 'r') as f:
        reader = csv.reader(f)
        try:
            for row in reader:
                solr_id = row[1]
                concept_id = row[2]
                concept_name = concept_map[int(concept_id)]
                score = row[3]
                classified_products.append( (solr_id, concept_name, score) )
        except:
            print concept_id
            
    products = collections.defaultdict(lambda: {})
    
    for prod in classified_products:
        solr_id = prod[0]
        concept_name = prod[1]
        score = prod[2]
        
        product = products[solr_id]        
        product['id'] = solr_id
        product['fashion_'+concept_name+'_f'] = { "set" : score }
    
    if post:
        header = { 'Content-type' : 'application/json' }
        r = requests.post(UPDATE_URL, data=json.dumps(products.values()), headers=header)    
        print 'Response:', r

    return products



updates = update_classififications('saks')


updates = update_classififications('nordstroms')






