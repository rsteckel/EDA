import os
from shared.config.Config import Config
from shared.lwbd.Solr import Solr


######### EDIT THESE ###########
out_file_path = os.environ['NM_HOME']+'/Data/product_catalog_features.tdf'
#query_string = 'ListPrice_Amount:[20001 TO *] AND (Feature:* OR EditorialReview_Content:*)'
#query_string = 'extract_date:"2013-09-21T22:31:19.000000000"'
query_string = '*'
max_records = None # or None for all records
collection = 'NM-catalog'
field_string = ','.join(
	(
        'id',
        'cmos_item_code_t',        
        'categoryType_name_t',
        'category_name_t',
        'edison_dept_t',
        'edison_subclass_t',
        'flg_is_on_promotion_b',
        'flg_is_on_sale_b',
        'sellable_date_dt',
        'regular_price_f',
        'sale_price_f',        
        'silo_name_t',
        'brand_name_t',
        'item_name_t',
        'designer_copy_t',
        'product_desc_t'
	)
)
delim = '\t'
multi_value_delim = '.'
escape_newlines = True
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
