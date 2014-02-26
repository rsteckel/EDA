# -*- coding: utf-8 -*-
from taxonomy import Taxonomy

from pattern.en import parsetree
from pattern.search import Pattern


class SemanticMatch:
    def __init__(self, sentence, matches):
        self.sentence = sentence
        self.matches = matches
        
    def __str__(self):
        return self.sentence + self.matches
        
        

class TaxonomySearch:    
    def __init__(self, taxonomy):
        self.taxonomy = taxonomy
        self.doc_counter = 0
        
    def search(self, document, pattern='*'):
        pattern = Pattern.fromstring(pattern, taxonomy=self.taxonomy.pat_taxonomy)
        
        parsed = parsetree(document, lemmata=True)
        
        semantic_matches = []                
        for sentence in parsed.sentences:
            sentence_matches = pattern.search(sentence)
            if sentence_matches:        
                for m in sentence_matches:
                    print m
        
        return semantic_matches


    def document_contains(self, document, categories):
        self.doc_counter += 1
        parsed = parsetree(document, lemmata=True)
        
        #Assume no POS tags for categories
        category_tags = set([ cat.lower()+'.na' for cat in categories ])
        
        results = set()
        matches = set()
        for i,sentence in enumerate(parsed.sentences):
            for word in sentence.words:
                result = self.taxonomy.category(word.string, word.pos)
                if result:
                    results.add(result.lower())
                    word.string = word.string.lower()
                    matches.add( (word, result) )
        
        if results == category_tags:
            return matches

        return []

    def sentence_contains(self, document, categories):
        self.doc_counter += 1
        parsed = parsetree(document, lemmata=True)
        
        #Assume no POS tags for categories
        category_tags = set([ cat.lower()+'.na' for cat in categories ])
        
        sentence_matches = []
        for i,sentence in enumerate(parsed.sentences):
            results = set()
            matches = []
            for word in sentence.words:
                result = self.taxonomy.category(word.string, word.pos)
                if result:
                    results.add(result.lower())
                    word.string = word.string.lower()
                    matches.append( (word, result) )

            if results == category_tags:
                sentence_matches.append( (self.doc_counter, matches, sentence.string) )
                
        return sentence_matches


