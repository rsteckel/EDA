# -*- coding: utf-8 -*-
from taxonomy import Taxonomy

from pattern.en import parse, parsetree
from pattern.search import Pattern


class TaxonomySearch:    
    def __init__(self, taxonomy):
        self.taxonomy = taxonomy
        
    def search(self, document, pattern='*'):
        pattern = Pattern.fromstring(pattern, taxonomy=self.taxonomy.pat_taxonomy)
        
        parsed = parsetree(document, lemmata=True)
        for sentence in parsed.sentences:            
            matches = pattern.search(sentence)
            if matches:
                for match in matches:
                    print match
        




