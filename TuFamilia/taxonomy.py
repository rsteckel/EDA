# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%m-%d %H:%M')
                    
import collections

from nltk.corpus import framenet as fn
import nltk

import pattern.en.wordnet as wn
import pattern.search as PS
from pattern.en import lemma


class POSCategory:
    def __init__(self):
        NOUN = {'NN','NNS','NNP','NNPS'}
        VERB = {'VB','VBZ','VBP','VBD','VBN','VBG'}
        ADJECTIVE = {'JJ','JJR','JJS'}
        ADVERB = {'RB','RBR','RBS'}

        self.WN_POS = NOUN | VERB | ADJECTIVE | ADVERB
        self.SIMPLIFIED = { 'n', 'v', 'a', 'adv' }
        self.SIMPLE_TAGS = {}
        for tag in NOUN:
            self.SIMPLE_TAGS[tag] = 'n'
        for tag in VERB:
            self.SIMPLE_TAGS[tag] = 'v'
        for tag in ADJECTIVE:
            self.SIMPLE_TAGS[tag] = 'a'
        for tag in ADVERB:
            self.SIMPLE_TAGS[tag] = 'adv'

    def simplify_tag(self, tag):
        if self.SIMPLE_TAGS.has_key(tag):
            return self.SIMPLE_TAGS[tag]
        return 'na'


    
class Taxonomy:
    def __init__(self, root_name='root', pos_sensitive=True):
        self.root = root_name
        self.taxonomy = PS.Taxonomy()
        self.pos_category = POSCategory()
        self.pos_sensitive = pos_sensitive
    
    def add_framenet_frame(self, name, parent=None, related=None):
        """ related: frame relation name (i.e. subFrame)"""
        frames = fn.frames(name)
        if frames:
            if len(frames) > 1:
                raise Exception('Frame name given resulted in multiple frames')
                
            frame = frames[0]  #Take first match
            self.add_category(frame.name, parent)
            
            lus = frame['lexUnit'].keys()  
            for lu in lus:
                tokens = lu.split('.')
                self.add_category(tokens[0], frame.name, pos=tokens[1])
            
            if related:
                relations = frame['frameRelations']
                for relation in relations:
                    related_frame = relation[related]
                    if related_frame.name != frame.name:
                        self.add_category(related_frame.name, frame.name)
                        
                        lus = related_frame['lexUnit'].keys()
                        for lu in lus:
                            tokens = lu.split('.')
                            self.add_category(tokens[0], related_frame.name, pos=tokens[1])
        
    def add_category(self, name, parent=None, pos=None, synonyms=[], wn_synonyms=False):            
        term_key = self._build_term_key(name, pos)                
        if not parent:   
            parent = self.root
            
        parent_key = self._build_term_key(str(parent))
        if not self.taxonomy.has_key(parent_key): #Add parent to the root if it doesn't exist
            self.taxonomy.append(parent_key, type=self.root)
        
        print '\tAdding term %s  %s' % (term_key, parent_key)
        self.taxonomy.append(term_key, type=parent_key)
        
        if synonyms:
            for synonym in synonyms:
                synonym_key = self._build_term_key(synonym, pos='na', lem=True)
                self.taxonomy.append(synonym_key, type=term_key) 
                
        if wn_synonyms:
            syns = wn.synsets(name, pos)
            syn = syns[0]
            for synonym in syn.synonyms:
                synonym_key = self._build_term_key(synonym, pos='na', lem=True)
                self.taxonomy.append(synonym_key, type=term_key)                 

    def search(self, name, pos=None, retry=False):
        match = self.taxonomy.classify(self._build_term_key(name, pos))
        if not match and retry:             
            match = self.taxonomy.classify(self._build_term_key(name, None))
        if match:
            match = match.split('.')[0]
        return match

    def parents(self, name, pos=None, recurse=False):
        matches = self.taxonomy.parents(self._build_term_key(name, pos), recursive=recurse)
        if matches:
            matches = [ match.split('.')[0] for match in matches]
        return matches

    def children(self, name, pos=None, recurse=False):
        matches = self.taxonomy.children(self._build_term_key(name, pos), recursive=recurse)
        if matches:
            matches = [ match.split('.')[0] for match in matches]
            matches.sort()
        return matches

    def frame_relations(self):
        return fn.fe_relations()

    def lexical_units(self, lu_name):
        return fn.lus(lu_name)

    def frames(self, lu_name):
        return fn.frames_by_lemma(lu_name)

    def _build_term_key(self, name, pos=None, lem=False):
        if name == self.root:
            return name

        tokens = name.split('.')
        if len(tokens) > 1:
            name = tokens[0]
            pos = tokens[1]

        if lem:
            term = lemma(name.lower())
        else:
            term = name.lower()        
            
        tag = ''
        if pos: #Normalize to the simplified tag (if a tag was given)
            if pos not in self.pos_category.SIMPLIFIED:
                tag = self.pos_category.simplify_tag(pos)
            else:
                tag = pos
        else:
            tag = 'na'
            
        return term+'.'+tag



        
def print_taxonomy(taxonomy):    
    def print_children(name, spacing='|-'):    
        print spacing+name
        nodes = taxonomy.children(name)
        spacing += '--'
        for node in nodes:            
            print_children(node, spacing)

    print_children(taxonomy.root)


