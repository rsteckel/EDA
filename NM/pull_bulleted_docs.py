from shared.config.Config import Config
from shared.lwbd.Solr import Solr

__author__ = 'sterrell'

######### EDIT THESE ###########
out_file_path = '/Users/rsteckel/Workspace/NM/nm_bullets_corpus.tdf'

query_string = 'extract_date:"2013-09-21T22:31:19.000000000"'

max_records = None # or None for all records
collection = 'neiman_marcus_raw_catalog'
field_string = ','.join(
	(
        'cmos_item_code',
        'long_desc_text_only',
        'detail_bullets'        
	)
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
