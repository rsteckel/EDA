from shared.config.Config import Config
from shared.lwbd.Solr import Solr

__author__ = 'sterrell'

######### EDIT THESE ###########
out_file_path = '/Users/rsteckel/Workspace/NM/blog_crawl_features.tdf'
#query_string = 'ListPrice_Amount:[20001 TO *] AND (Feature:* OR EditorialReview_Content:*)'
query_string = '*'
max_records = 10000    #None # or None for all records
collection = 'nutch_fashion_crawl'
field_string = ','.join(   
    ( '', 'content')  
)
delim = '\t'
multi_value_delim = '.'
escape_newlines = False
#################################

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
