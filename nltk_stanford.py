# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 13:28:35 2014

@author: rsteckel
"""


#TODO:  Fix....

import nltk
nltk.internals.config_java("/Library/Java/Home/bin/java", verbose=True)
from nltk.tag.stanford import NERTagger

st = NERTagger('/usr/share/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', '/usr/share/stanford-ner/stanford-ner.jar') 

st.tag(u'A casual day with my red belt. Red, yellow and blue, a color combination that makes me feel like Snow White maybe just in my head, but i really love it, when I was Little my dad\u2019s family always call me Snow White because I always have a red head band with my short black hair, and that really make me feel special, who doesn\u2019t want to be a princess, hope you have a great day.'.split()) 


st.tag(tokenize(documents[0]))


_java_bin = nltk.internals.find_binary('java', env_vars=['JAVAHOME', 'JAVA_HOME'], verbose=True, binary_names=['java'])
nltk.internals.config_java("/Library/Java/Home/bin/java", verbose=True)


