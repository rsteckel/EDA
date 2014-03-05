# -*- coding: utf-8 -*-
from datasets.customers.tufamilia_dataset import TuFamilia
from extraction.senses import sense_tag2
from extraction.semantic_search import TaxonomySearch
from extraction.taxonomy import Taxonomy, POSCategory

from pattern.en import parse, parsetree, lemma, Chunk
from pattern.search import Pattern, Classifier, search
from pattern.search import taxonomy, WordNetClassifier

from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

import enchant
import re
import nltk
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%m-%d %H:%M')
                    


class DocumentTransformer(BaseEstimator):
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        return self
        

        
#TODO:  
#   * Fix you\u2019re type terms
#   * Remove emoticons?
class TextCorrectionTransformer(DocumentTransformer):
    def __init__(self, spellcheck=False):
        self.spelling = enchant.Dict("en_US")
        self.spellcheck = spellcheck
        
    def transform(self, document):
        #logging.debug('text correction ')
        
        #Replace translated unicode characters
        document = document.replace(u'\xa0', u'')
        
        #Ensure the correct amount of whitespace after sentence endings
        document = re.sub('\.\s*', '. ', document)
        document = re.sub('!\s*', '! ', document)
        document = re.sub('\?\s*', '? ', document)
        
        document = re.sub('\:\s*', ': ', document) #Remove ':'
        document = re.sub('\.\s*\.\s*\.\s*', ' ', document)  #(... patterns)
        document = re.sub('\&', ' ', document)  #Remove '&'

        #Run a very simple parse to iterate words
        parsed = parsetree(document, tags=False, chunks=False)
        
        if self.spellcheck:
            for sentence in parsed.sentences:
                for word in sentence:                
                    if not self.spelling.check(word.string):
                        print 'Misspelled: '+word.string
                        #print self.spelling.suggest(word.string)
        
        return parsed.string



class GrammerParser(DocumentTransformer):        
    def transform(self, document):
        #logging.debug('grammer parse')
        parsed = parsetree(document, lemma=True, relations=False)        
        return parsed
        


class NLTKGrammerParser(DocumentTransformer):    
    """ Place holder for now """
    def __init__(self):
        patterns = """ 
             NP: {<DT|PP\$>?<JJ>*<NN>} 
                 {<NNP>+} 
                 {<NN>+}
             PRCP: {<LOOKED>} """

        self.chunker = nltk.RegexpParser(patterns)
        
    def transform(self, document):
        sentences = nltk.sent_tokenize(document)
        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(words)
            parsing = self.chunker.parse(tagged)
            print parsing


                
class SenseTaggerTransformer(DocumentTransformer):
    def __init__(self, simple_pos=False):
        self.simple_pos = simple_pos
    
    def transform(self, parsed_document):
        if self.simple_pos:
            for sentence in parsed_document.sentences:
                for word in sentence:                
                    word.string = word.string.lower()+'.'+self.pos_cat.simplify_tag(word.pos)
            return parsed_document
        else:        
            #logging.debug('sense tag')
            return sense_tag2(parsed_document)
        
        
        
def build_taxonomy():
    perctaxonomy = Taxonomy('o360', pos_sensitive=False)
    perctaxonomy.add_category('beauty')
    perctaxonomy.add_category('perception', 'beauty')
    perctaxonomy.add_framenet_frame('Perception_active', 'perception', frame_alias='active')
    perctaxonomy.add_framenet_frame('Perception_body', 'perception', frame_alias='body')
    perctaxonomy.add_framenet_frame('Perception_experience', 'perception', frame_alias='experience')
    perctaxonomy.add_framenet_frame('Cause_to_perceive', 'perception', frame_alias='cause')

    return perctaxonomy
        


class TaxonomySearchTransformer(DocumentTransformer):
    def __init__(self, taxonomy_search):
        self.searcher = taxonomy_search
        
    def transform(self, parsed_document):
        #logging.debug('search taxonomy')
        sem_matches = self.searcher.search(parsed_document)
        return sem_matches



class PerceptionTransformer(DocumentTransformer):
    def __init__(self, perception_type):
        taxonomy.classifiers.append(WordNetClassifier())
        self.taxo = taxonomy
        self.perception_type = perception_type
                
    def transform(self, semantic_matches):
        for match in semantic_matches:
            perception = self.perception_type(match)
            #print self.taxonomy.parents('cat', pos='NN')
            print perception


class Perception(object):
    def __init__(self, semantic_match):
        self.matches = semantic_match.matches
        self.sentence = semantic_match.sentence

    def describe_components(self):
        components = ''
        for match in self.matches:
            for c in match.constituents():
                if isinstance(c, Chunk):
                    components += '\n\t%s: %s' % (c.type, ' '.join([ w.string+'/'+w.pos for w in c.words]))
                else:
                    components += '\n\t%s: %s' % (c.tag, c.string)
        return components


class ActionPerception(Perception):
    def __init__(self, semantic_match):
        super(ActionPerception, self).__init__(semantic_match)

    @staticmethod
    def pattern():
        return '{NP+} {VP} {PERCEPTION+} *? {ADJP+}'

    def __str__(self):
        for match in self.matches:
            description = self.sentence.string
            description += '\n %s' % self.__class__.__name__
            description += self.describe_components()
                    
            actor = ' '.join([ w.string for w in match.group(1) ])
            action = ' '.join([ w.string for w in match.group(2) ])
            percep = ' '.join([ w.string for w in match.group(3) ])
            desc = ' '.join([ w.string for w in match.group(4) ])

            description += '\nActor: %s  Action: %s  Percep: %s  Desc: %s' % (actor, action, percep, desc)
            description += '\n'
            return description


class DescriptionPerception(Perception):
    def __init__(self, semantic_match):
        super(DescriptionPerception, self).__init__(semantic_match)

    @staticmethod
    def pattern():
        return '{PERCEPTION} {ADJP+} *? PP+ {NP+}'

    def __str__(self):
        for match in self.matches:
            description = self.sentence.string
            description += '\n %s' % self.__class__.__name__
            description += self.describe_components()
                    
            percep = ' '.join([ w.string for w in match.group(1) ])
            desc = ' '.join([ w.string for w in match.group(2) ])
            obj = ' '.join([ w.string for w in match.group(3) ])

            description += '\nPercep: %s  Desc: %s  Object: %s' % (percep, desc, obj)
            description += '\n'
            return description




def build_perception_pipeline(perception_type, perception_taxonomy):
    searcher = TaxonomySearch(perception_taxonomy, perception_type.pattern(), strict=True)

    steps = [('textcorrect', TextCorrectionTransformer()),
             #Domain sentence level classifier
             ('grammerparser', GrammerParser()),
             #('simple-pos', SimplePOSTransformer()),
             #('sensetag', SenseTaggerTransformer()),
             ('search', TaxonomySearchTransformer(searcher)),
             ('perception', PerceptionTransformer(perception_type))] #Domain specific taxonomy of perceptions

    pipeline = Pipeline(steps)
    
    return pipeline








dataset = TuFamilia('beauty', query={'lang':'en'})
dataset.load()
#dataset.store()
documents = dataset.documents()


#searcher = TaxonomySearch(build_taxonomy(), '{SBJ?} * {PERCEPTION} * {JJ?} * {OBJ?}')
#searcher = TaxonomySearch(build_taxonomy(), '{SBJ+} *+ {PERCEPTION} {OBJ+}', strict=True)
#searcher = TaxonomySearch(build_taxonomy(), '{NP} {NNS|NNP|NN+} *+ {JJ?} *+ {PERCEPTION} {JJ?} *+ {NNS|NNP|NN+}', strict=True)
#searcher = TaxonomySearch(perception_taxo, 'NP+ {PERCEPTION} {ADJP+} *? PP+ NP+', strict=True)
#searcher = TaxonomySearch(perception_taxo, '{PERCEPTION} {ADJP+} *? PP+ NP+', strict=True)



perception_taxonomy = build_taxonomy()


#perception_type = ActionPerception
perception_type = DescriptionPerception

pipeline = build_perception_pipeline(perception_type, perception_taxonomy)
for i,document in enumerate(documents):
    if i % 100 == 0:
        print "%d of %d" % (i, len(documents))
    pipeline.fit_transform(document)



