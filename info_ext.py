# -*- coding: utf-8 -*-
import nltk
from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.datasets import fetch_20newsgroups
from nltk.corpus import framenet as fn            
import regex as re

newsgroups = fetch_20newsgroups(subset='test', remove=('headers', 'footers', 'quotes'))

for rawtext in [newsgroups.data[0],]:
    sentences = sent_tokenize(rawtext)
    sentences = [word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]

chunks = nltk.chunk.batch_ne_chunk(sentences)






from nltk import sent_tokenize, word_tokenize, pos_tag, ne_chunk
 
 
def extract_entities(text):
	entities = []
	for sentence in sent_tokenize(text):
	    chunks = ne_chunk(pos_tag(word_tokenize(sentence)))
	    entities.extend([chunk for chunk in chunks if hasattr(chunk, 'node')])
	return entities
 
 

text = """
A multi-agency manhunt is under way across several states and Mexico after
police say the former Los Angeles police officer suspected in the murders of a
college basketball coach and her fiancÃ© last weekend is following through on
his vow to kill police officers after he opened fire Wednesday night on three
police officers, killing one.
"In this case, we're his target," Sgt. Rudy Lopez from the Corona Police
Department said at a press conference.
The suspect has been identified as Christopher Jordan Dorner, 33, and he is
considered extremely dangerous and armed with multiple weapons, authorities
say. The killings appear to be retribution for his 2009 termination from the
 Los Angeles Police Department for making false statements, authorities say.
Dorner posted an online manifesto that warned, "I will bring unconventional
and asymmetrical warfare to those in LAPD uniform whether on or off duty."
"""
print extract_entities(text)







doccollections = ['NYT_19980407','NYT_19980403','NYT_19980315','APW_19980429','APW_19980424','APW_19980314']

IN = re.compile(r'.*\bin\b(?!\b.+ing)')

for doccol in doccollections:
    for doc in nltk.corpus.ieer.parsed_docs(doccol):
        relations = nltk.sem.extract_rels('PER', 'LOC', doc, corpus='ieer', pattern = IN)
        for relation in relations:
            print nltk.sem.relextract.rtuple(relation)
            


f = fn.frames(r'(?i)perception')
len(fn.frames())
f = fn.frame(66)

f.ID
f.definition
set(f.lexUnit.keys())

[x.name for x in f.FE]

f.frameRelations


fn.frames_by_lemma(r'(?i)a little')




fn.lu(256).name
fn.lu(256).definition
fn.lu(256).frame
fn.lu(256).lexeme



docs = fn.documents()
len(docs)
docs[0].keys()
docs[0].filename

docs[0].annotated_document()


