# -*- coding: utf-8 -*-
from datasets.customers.tufamilia_dataset import TuFamilia
from extraction.senses import sense_tag2
from extraction.semantic_search import TaxonomySearch
from extraction.taxonomy import Taxonomy, POSCategory, print_taxonomy

from pattern.en import parse, parsetree, lemma, Chunk
from pattern.search import Pattern, Classifier, search
from pattern.search import taxonomy, WordNetClassifier

from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

#import enchant
import re
import collections
import nltk
from nltk.corpus import stopwords as sw
import pandas as pd

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%m-%d %H:%M')


class DocumentTransformer(BaseEstimator):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self


# TODO:
#   * Fix you\u2019re type terms
#   * Remove emoticons?
class TextCorrectionTransformer(DocumentTransformer):

    def __init__(self, spellcheck=False):
        #self.spelling = enchant.Dict("en_US")
        self.spellcheck = spellcheck

    def transform(self, document):
        #logging.debug('text correction ')

        # Replace translated unicode characters
        document = document.replace(u'\xa0', u'')

        # Ensure the correct amount of whitespace after sentence endings
        document = re.sub('\.\s*', '. ', document)
        document = re.sub('!\s*', '! ', document)
        document = re.sub('\?\s*', '? ', document)

        document = re.sub('\:\s*', ': ', document)  # Remove ':'
        document = re.sub('\.\s*\.\s*\.\s*', ' ', document)  # (... patterns)
        document = re.sub('\&', ' ', document)  # Remove '&'

        # Run a very simple parse to iterate words
        parsed = parsetree(document, tags=False, chunks=False)

        #if self.spellcheck:
        #    for sentence in parsed.sentences:
        #        for word in sentence:
        #            if not self.spelling.check(word.string):
        #                print 'Misspelled: ' + word.string
        #                # print self.spelling.suggest(word.string)

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
                    word.string = word.string.lower() + '.' + \
                        self.pos_cat.simplify_tag(
                            word.pos)
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
    #perctaxonomy.add_category('look', 'perception')

    return perctaxonomy


class TaxonomySearchTransformer(DocumentTransformer):

    def __init__(self, taxonomy_search):
        self.searcher = taxonomy_search

    def transform(self, parsed_document):
        #logging.debug('search taxonomy')
        sem_matches = self.searcher.search(parsed_document)
        return sem_matches


class SemanticFeaturesTransformer(DocumentTransformer):

    def __init__(self, perception_taxonomy):
        self.taxo = perception_taxonomy

    def transform(self, semantic_matches):
        records = []
        for semantic_match in semantic_matches:
            print semantic_match.sentence.string, '\n'

            # Make one pass to get the perception word index
            perception_index = -1
            for word in semantic_match.sentence:
                parent = self.taxo.parents(lemma(word.string))
                perception = False
                if parent:
                    perception_index = word.index

            for word in semantic_match.sentence:
                parent = self.taxo.parents(lemma(word.string))

                perception_distance = (word.index - perception_index)

                perception = False
                if parent:
                    perception = True

                is_pnp = False
                if word.pnp:
                    is_pnp = True

                if word.chunk:
                    chunktype = word.chunk.type
                    chunkstart = word.chunk.start
                    chunkstop = word.chunk.stop

                    poschunk = "%s-%s" % (word.pos, chunktype)

                    records.append(
                        (perception, parent, word.string, lemma(word.string), word.pos,
                         word.index, perception_distance, is_pnp, chunktype, chunkstart, chunkstop, poschunk))
                else:
                    records.append((perception, parent, word.string, lemma(
                        word.string), word.pos, word.index, perception_distance, is_pnp, '', '', '', word.pos))

        return records


class PerceptionTransformer(DocumentTransformer):

    def __init__(self, perception_type, parents=False):
        from pattern.search import taxonomy
        taxonomy.classifiers.append(WordNetClassifier())
        self.taxo = taxonomy
        self.perception_type = perception_type
        self.parents = parents

    def transform(self, semantic_matches):
        stopwords = set(sw.words('english'))
        perceptions = []
        for semantic_match in semantic_matches:
            perception = self.perception_type(semantic_match)
            print '\n'
            print self.taxo.parents(perception.target()), perception
            for w in perception.desc_words:
                if w.string not in stopwords:
                    print w.string, w.pos, lemma(w.string), self.taxo.parents(w.string.lower(), w.pos)[:3]
                    
            perceptions.append((perception.subj.lower(), perception.percep, perception.desc.lower()))
        return perceptions
            



class Perception(object):

    """  Past patterns
    '{SBJ?} * {PERCEPTION} * {JJ?} * {OBJ?}'
    '{SBJ+} *+ {PERCEPTION} {OBJ+}'
    '{NP} {NNS|NNP|NN+} *+ {JJ?} *+ {PERCEPTION} {JJ?} *+ {NNS|NNP|NN+}'
    'NP+ {PERCEPTION} {ADJP+} *? PP+ NP+'
    '{PERCEPTION} {ADJP+} *? PP+ NP+'
    """

    def __init__(self, semantic_match):
        self.matches = semantic_match.matches
        self.sentence = semantic_match.sentence
        self.percep = 'perception'

    @staticmethod
    def pattern():
        return '{PERCEPTION+}'

    def describe_components(self):
        components = ''
        for match in self.matches:
            for c in match.constituents():
                if isinstance(c, Chunk):
                    components += '\n\t%s: %s' % (c.type, ' '.join([w.string + '/' + w.pos for w in c.words]))
                else:
                    components += '\n\t%s: %s' % (c.tag, c.string)
                    
        return components

    def target(self):
        return self.percep



class DescPerception(Perception):
    def __init__(self, semantic_match):
        super(DescPerception, self).__init__(semantic_match)
        for match in self.matches:
            self.subj = ' '.join([w.string for w in match.group(1)])
            self.percep = ' '.join([w.string for w in match.group(2)])
            self.desc = ' '.join([w.string for w in match.group(3)])
            self.desc_words = [w for w in match.group(3)]

    @staticmethod
    def pattern():
        #return '{NP|VP+} *? {PERCEPTION} *? {ADJP+}'
        return '{NN|NNP|NNS+} *? {PERCEPTION} *? {ADJP+}'

    def __str__(self):
        for match in self.matches:
            description = self.sentence.string
            description += '\n %s' % self.__class__.__name__
            description += self.describe_components()
            description += '\nSubj: %s  Percep: %s  Desc: %s' % (self.subj, self.percep, self.desc)
            return description



class AdjectiveSelector(DocumentTransformer):

    def __init__(self, perception_taxonomy):
        self.taxo = perception_taxonomy

    def transform(self, parsed_document):
        pattern = Pattern.fromstring('*? {PERCEPTION} *?', taxonomy=self.taxo.pat_taxonomy)
        
        percep_adjs = []
        notpercep_adjs = []
        
        percep_sentences = 0
        notpercep_sentences = 0
        
        perception_sentence = False                
        for sentence in parsed_document.sentences:
            matches = pattern.search(sentence)
            if matches:
                perception_sentence = True
                percep_sentences += 1
            else:
                notpercep_sentences += 1
                
            for word in sentence.words:
                if word.pos.startswith('J'):
                    if perception_sentence:
                        percep_adjs.append(word.string.lower())
                    else:
                        notpercep_adjs.append(word.string.lower())
        
        return (percep_adjs, notpercep_adjs, percep_sentences, notpercep_sentences)



def build_perception_pipeline(perception_type, perception_taxonomy):
    searcher = TaxonomySearch(perception_taxonomy, perception_type.pattern(), strict=True)

    steps = [('textcorrect', TextCorrectionTransformer()),
             ('grammerparser', GrammerParser()),
             #('simple-pos', SimplePOSTransformer()),
             #('sensetag', SenseTaggerTransformer()),
             #('search', TaxonomySearchTransformer(searcher)),
             ('perception', PerceptionTransformer(perception_type)),
             #('adj-selector', AdjectiveSelector(perception_taxonomy))
             #('summary', SemanticFeaturesTransformer(perception_taxonomy))
             ]

    pipeline = Pipeline(steps)

    return pipeline






#----------------------------------------------------------------------
dataset = TuFamilia('beauty', query={'lang': 'en'})
dataset.load()
dataset.store()
documents = dataset.documents()



perception_taxonomy = build_taxonomy()
perception_type = DescPerception
pipeline = build_perception_pipeline(perception_type, perception_taxonomy)





records = []
for i, document in enumerate(documents[:5000]):
    if i % 100 == 0:
        print "%d of %d" % (i, len(documents))
    doc_records = pipeline.fit_transform(document)
    if doc_records:
        records += doc_records





percep_adjs = []
notpercep_adjs = []
percep_sentences = 0
notpercep_sentences = 0
for i, document in enumerate(documents[:5000]):
    if i % 100 == 0:
        print "%d of %d" % (i, len(documents))
    (pa, npa, ps, nps) = pipeline.fit_transform(document)
    percep_adjs += pa
    notpercep_adjs += npa
    percep_sentences += ps
    notpercep_sentences += nps


padjs = collections.Counter(percep_adjs)
npadjs = collections.Counter(notpercep_adjs)


def ratio(adj):
    n = padjs[adj] / (1. * percep_sentences)
    d = npadjs[adj] / (1. * notpercep_sentences)
    if d == 0:
        return 0.0
    return (n/d)

perceptions_adjs = []
for k in padjs.keys():
    perceptions_adjs.append( (k, ratio(k)) )

from operator import itemgetter

perceptions_adjs.sort(key=itemgetter(1),reverse=True)
for ap in perceptions_adjs[:50]:
    print ap



df = pd.DataFrame(records, columns=['Subj', 'Percep', 'Desc'])
df.to_excel('/Users/rsteckel/Desktop/records.xlsx')


grouped = df.groupby(['Subj', 'Desc']).size().reset_index()
grouped.to_excel('/Users/rsteckel/Desktop/grouped.xlsx')

grouped = df.groupby(['Desc']).size().reset_index()
grouped.to_excel('/Users/rsteckel/Desktop/grouped.xlsx')
