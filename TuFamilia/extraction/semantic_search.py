# -*- coding: utf-8 -*-
from pattern.search import Pattern


class SemanticMatch:
    """ Store all the matches for this sentence """
    def __init__(self, sentence, matches):
        self.sentence = sentence
        self.matches = matches


class TaxonomySearch:    
    def __init__(self, taxonomy, pattern, strict=False):
        self.taxonomy = taxonomy
        self.pattern_str = pattern
        self.strict = strict
        
    def search(self, parsed_document):
        """ Return all the matches for the document """
        pattern = Pattern.fromstring(self.pattern_str, taxonomy=self.taxonomy.pat_taxonomy, strict=self.strict)
        
        semantic_matches = []
        for sentence in parsed_document.sentences:
            matches = pattern.search(sentence)
            if matches:
                semantic_matches.append(SemanticMatch(sentence, matches))
        
        return semantic_matches


