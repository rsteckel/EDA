from concept_datastore import *
from concept_classifier import *
from classify_nm_catalog import *
from text_utils import *


BUILD = True
CLASSIFY = False
STORE_CLASSIFICATIONS=False
STORE_FEATURES=False
STORE_CLASSIFIER=False
ATTRIBUTES_ONLY=True
RUN_GRID = False
RUN_ALL = True
GIVEN_CONCEPT = None  #'couture'

#TODO: function to clean cache files?
#       nm_vocabulary.cache   vocabulary_cache_filename():    
#       catalog-vectorized.cache    vectorized_catalog_filename()


if __name__ == "__main__":
    
    if GIVEN_CONCEPT is not None:
        concepts = load_concept(GIVEN_CONCEPT)
    elif RUN_ALL == False: #Only run concepts that have not been used to classify
        classified = load_classified_concepts()
        classified_ids = [ c[0] for c in classified ]
        concepts = [ c for c in concepts if c[0] not in classified_ids ]    
    else:
        concepts = load_concepts()
    
    print '\tLoaded', len(concepts), 'concepts'        
    
    if CLASSIFY:
        id_descs = load_product_descs()
        print '\tLoaded', len(id_descs), 'products'
    
    for concept in concepts:
        concept_id = concept[0]
        concept_name = concept[1]
        
        if BUILD:
            print 'Building classifier for concept:', concept_name
            build_classifier(concept_id, concept_name, store=STORE_CLASSIFIER, use_grid=RUN_GRID, filter_attributes=ATTRIBUTES_ONLY)
    
        if CLASSIFY:
            print 'Running classifier for concept:', concept_name
            product_ids = [ idd[0] for idd in id_descs ]
            descs = [ idd[1] for idd in id_descs ]
        
            run_classifier(concept_id, concept_name, product_ids, descs, 
                           store_class=STORE_CLASSIFICATIONS, store_features=STORE_FEATURES)
                           
