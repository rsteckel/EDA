# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%m-%d %H:%M')
                    
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
import nltk

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


def parents(term):
    print 'parents:', term
    return [term,]


def children(term):
    print 'children', term
    return [term,]


    
class Taxonomy:
    def __init__(self, root_name='root', pos_sensitive=False):
        self.root = root_name
        self.pat_taxonomy = PS.Taxonomy()
        self.pat_taxonomy.append(PS.Classifier(parents, children))
        
        self.pos_category = POSCategory()
        self.pos_sensitive = pos_sensitive
    
    def add_insight(self, name, domain):
        if not self._exists(domain):
            self.add_category(domain)
            
        self.add_category(name, domain)
            
    def add_entity(self, name, insight):
        if not self._exists(insight):
            raise Exception('Need to add insight before entity')
            
        self.add_category(name, insight)
    
    def add_example(self, wn_example, entity):
        if not self._exists(entity):
            raise Exception('Need to add entity before example')
            
        self.add_hyponyms(wn_example, entity)
    
    def add_framenet_frame(self, framename, parent=None, frame_alias=None):
        """ related: frame relation name (i.e. subFrame)"""
        frames = fn.frames(framename)
        if frames:
            if len(frames) > 1:
                raise Exception('Frame name given resulted in multiple frames')
                
            frame = frames[0]  #Take first match
            if frame_alias:                
                self.add_category(frame_alias, parent)
            else:
                self.add_category(frame.name, parent)
            
            lus = frame['lexUnit'].keys()  
            for lu in lus:
                tokens = lu.split('.')
                if frame_alias:
                    self.add_category(tokens[0], frame_alias, pos=tokens[1])
                else:
                    self.add_category(tokens[0], frame.name, pos=tokens[1])
            
#            if related:
#                relations = frame['frameRelations']
#                for relation in relations:
#                    related_frame = relation[related]
#                    if related_frame.name != frame.name:
#                        self.add_category(related_frame.name, frame.name)
#                        
#                        lus = related_frame['lexUnit'].keys()
#                        for lu in lus:
#                            tokens = lu.split('.')
#                            self.add_category(tokens[0], related_frame.name, pos=tokens[1])
        
    def add_hyponyms(self, synset_id, parent):
        expanded = expand_hyponyms(synset_id)
        for hyponym in expanded:
            self.add_category(hyponym.name(), parent, pos=hyponym.pos())
            
    def add_category(self, name, parent=None, pos=None, synonyms=[]):            
        term_key = self._build_term_key(name, pos)                
        if not parent:   
            parent = self.root
            
        parent_key = self._build_term_key(parent)
        #if not self.pat_taxonomy.has_key(parent_key): #Add parent to the root if it doesn't exist
        #    logging.debug('Adding %s to root', parent_key)
        #    self.pat_taxonomy.append(parent_key, type=self.root)
        
        if not self.pat_taxonomy.has_key(term_key):
            logging.debug('Adding %s to %s', term_key, parent_key)
            self.pat_taxonomy.append(term_key, type=parent_key)
        
        if synonyms:
            for synonym in synonyms:
                synonym_key = self._build_term_key(synonym, pos='na', lem=True)
                logging.debug('Adding synonym %s for %s', synonym_key, term_key)
                self.pat_taxonomy.append(synonym_key, type=term_key)           

    def search(self, name, pos=None, retry=False):
        match = self.taxonomy.classify(self._build_term_key(name, pos))
        if not match and retry:             
            match = self.pat_taxonomy.classify(self._build_term_key(name, None))
        if match:
            match = match.split('.')[0]
        return match
        
    def search_text(self, name, text):
        return PS.search(name, text)

    def parents(self, name, pos=None, recurse=False):
        matches = self.pat_taxonomy.parents(self._build_term_key(name, pos), recursive=recurse)
        if matches:
            matches = [ match.split('.')[0] for match in matches]
        return matches

    def children(self, name, pos=None, recurse=False, simplify=False):
        matches = self.pat_taxonomy.children(self._build_term_key(name, pos), recursive=recurse)
        if matches:
            if simplify:
                matches = [ match.split('.')[0] for match in matches]
            matches.sort()
        return matches

    def frame_relations(self):
        return fn.fe_relations()

    def lexical_units(self, lu_name):
        return fn.lus(lu_name)

    def frames(self, lu_name):
        return fn.frames_by_lemma(lu_name)                

    def category(self, term, pos=None):
        term_key = self._build_term_key(term, pos)
        return self.pat_taxonomy.classify(term_key)
                
    def _exists(self, name, pos=None):
        term_key = self._build_term_key(name, pos)
        return self.pat_taxonomy.has_key(term_key)

    def _build_term_key(self, name, pos=None, lem=False):
        #Don't do any normaliztion/transformation to root category
        if name == self.root: 
            return name

        tokens = name.split('.')
        if len(tokens) == 3:  #Wordnet format given
            name = tokens[0]
            pos = tokens[1]
            synid = tokens[2]
        elif len(tokens) == 2:  #Word.pos given
            name = tokens[0]
            pos = tokens[1]

        if lem:
            term = lemma(name.lower())
        else:
            term = name.lower()        
        
        if self.pos_sensitive:
            tag = 'na'
            if pos: #Normalize to the simplified tag (if a tag was given)
                if pos not in self.pos_category.SIMPLIFIED:
                    tag = self.pos_category.simplify_tag(pos)
                else:
                    tag = pos
            return term+'.'+tag
        else:
            return term



def expand_hyponyms(synset_id):
    def _dfs(synset_id, visited=set()):
        ss = None
        try:
            ss = wn.synset(synset_id)
        except:
            pass
        
        if ss is None:
            return []
            
        for s in ss.hyponyms():
            if s not in visited:
                _dfs(s.name(), visited)
                visited.add(s)
                
        return visited
        
    return _dfs(synset_id)



        
def print_taxonomy(taxonomy):    
    def print_children(name, spacing='|-'):    
        print spacing+name
        nodes = taxonomy.children(name)
        spacing += '--'
        for node in nodes:            
            print_children(node, spacing)

    print_children(taxonomy.root)


