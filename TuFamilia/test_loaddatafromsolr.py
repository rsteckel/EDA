__author__ = 'sriWork'
import datastores.datastore as ds

COLLECTION = 'Health_Crawl_RSS_Feeds'
#COLLECTION = 'Health_Crawl_RSS_Feeds'
FIELDS = ['id', 'title', 'content', 'pubDate_dt', 'tags_s', 'lang','author']
QUERY = None

#####  Read solr data into 'dataframe' #####
dataframe = ds.solr_data_frame(COLLECTION, FIELDS, QUERY)
##print(dataframe['content'][373])
length_dataframe=len(dataframe)

#### Count the number of english and spanish documents and print the other language tags
"""
cnt_eng=0
cnt_es=0
for i in range(0,length_dataframe):
    #content_currentframe=dataframe['content'][i]
    #print(dataframe['lang'][i])
    if dataframe['lang'][i]==[u'en']:
        cnt_eng=cnt_eng+1
    elif dataframe['lang'][i]==[u'es']:
        cnt_es=cnt_es+1
    else:
        print i
        print(dataframe['lang'][i])

    #print(content_currentframe)
    #dataframe['content_english'][i]=content_currentframe
#print((dataframe['content_english']))
print 'Total number of documents = %d' %(length_dataframe)
print 'Number of english documents = %d' %(cnt_eng)
print 'Number of spanish documents = %d' %(cnt_es)
"""
### For each blog pick the top 'n' medical ailments ###
from nltk.corpus import framenet as fn
from pattern.en import parsetree


NOUN = {'NN','NNS','NNP','NNPS'}
VERB = {'VB','VBZ','VBP','VBD','VBN','VBG'}
ADJECTIVE = {'JJ','JJR','JJS'}
ADVERB = {'RB','RBR','RBS'}
SIMPLE_TAGS = {}
for tag in NOUN:
    SIMPLE_TAGS[tag] = 'n'
for tag in VERB:
    SIMPLE_TAGS[tag] = 'v'

f=fn.frame(239)
set_lex_units=set(f.lexUnit)
print(set_lex_units)
doc_content=dataframe['content'][2]
ptree = parsetree(doc_content, tokenize=True, tags=True, chunks=False, relations=False, lemmata=True, encoding='utf-8')
list_lex_units=[]
for sentence in ptree:
    for word in sentence.words:
        pos_tag=word.pos
        lemma=word.lemma
        simple_tag = None
        if SIMPLE_TAGS.has_key(pos_tag):
            simple_tag = SIMPLE_TAGS[pos_tag]

        if simple_tag:
            key = lemma+'.'+simple_tag
        else:
            key = lemma

        if (key in set_lex_units):
            list_lex_units.append(key)

print(doc_content)
print(list_lex_units)


"""
def get_medical_ailments(doc_content):


    return topics_medical_ailments




dict_blog_medical_ailments={}
n=3 ## number of medical ailments
for i in range(0,length_dataframe):
    if dataframe['lang'][i]==[u'en']: ## Right now performed only for english documents
        topics_medical_ailments=get_medical_ailments(dataframe['content'][i])
"""

"""
from nltk.corpus import framenet as fn
fn.lu(3238).frame.lexUnit['glint.v'] is fn.lu(3238)


fn.frame_by_name('Replacing') is fn.lus('replace.v')[0].frame

fn.lus('prejudice.n')[0].frame.frameRelations == fn.frame_relations('Partiality')


fn.lus('look.n')[0].frame
fn.lus('look.n')[1].frame


result = fn.frames(r'(?i)erception')

print result
f = fn.frame(1301)

f.ID
f.definition
for u in f.lexUnit:
    print u

fn.lexical_units('r(?i)look')
"""