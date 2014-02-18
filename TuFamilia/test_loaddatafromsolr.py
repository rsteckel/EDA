__author__ = 'sriWork'
import datastores.datastore as ds

COLLECTION = 'Health_Crawl_RSS_Feeds'
#COLLECTION = 'Health_Crawl_RSS_Feeds'
FIELDS = [ 'title','content,' 'pubDate_dt', 'tags_s', 'lang','author']
QUERY = None

#####  Read solr data into 'dataframe' #####
dataframe = ds.solr_data_frame(COLLECTION, FIELDS, QUERY)
##print(dataframe['content'][373])
length_dataframe=len(dataframe)

#### Count the number of english and spanish documents and print the other language tags

cnt_eng=0
cnt_es=0
for i in range(0,length_dataframe):
    #content_currentframe=dataframe['content'][i]
    #print(dataframe['lang'][i])
    if dataframe['lang'][i]==[u'en']:
        cnt_eng=cnt_eng+1
    elif dataframe['lang'][i]==[u'es']:
        cnt_es=cnt_es+1
    #else:
        #print i
        #print(dataframe['lang'][i])

    #print(content_currentframe)
    #dataframe['content_english'][i]=content_currentframe
#print((dataframe['content_english']))
print 'Total number of documents = %d' %(length_dataframe)
print 'Number of english documents = %d' %(cnt_eng)
print 'Number of spanish documents = %d' %(cnt_es)

### For each blog pick the top 'n' medical ailments ###
from nltk.corpus import framenet as fn
from pattern.en import parsetree
from collections import Counter
import pandas as pd


NOUN = {'NN','NNS','NNP','NNPS'}
VERB = {'VB','VBZ','VBP','VBD','VBN','VBG'}
ADJECTIVE = {'JJ','JJR','JJS'}
ADVERB = {'RB','RBR','RBS'}
SIMPLE_TAGS = {}
for tag in NOUN:
    SIMPLE_TAGS[tag] = 'n'
for tag in VERB:
    SIMPLE_TAGS[tag] = 'v'
for tag in ADJECTIVE:
    SIMPLE_TAGS[tag] = 'a'
for tag in ADVERB:
    SIMPLE_TAGS[tag] = 'adv'

f=fn.frame(239)
print(f.name)
set_lex_units=set(f.lexUnit)
print(set_lex_units)
#doc_content=dataframe['content'][5]

"""
#### Write contents to excel file from framenet lexical units ####
import xlwt
book = xlwt.Workbook(encoding="utf-8")
sheet1 = book.add_sheet("Sheet 1")
cnt=0
class_lexunit=1
for i in f.lexUnit:
    sheet1.write(cnt,0,i)
    sheet1.write(cnt,1,class_lexunit)
    cnt=cnt+1
book.save("/Users/sriWork/Desktop/health_first_classifier.xls")
#####
"""

#### Add Contents to excel file
from xlrd import open_workbook
from xlutils.copy import copy
import xlwt
class_lexunit=1
add_list=['fibromyalgia.n']
book = open_workbook("/Users/sriWork/Desktop/health_first_classifier.xls")
sheet=book.sheet_by_index(0)
wb = copy(book)
sheet1=wb.get_sheet(0)

list_lexunits=[]
for row_index in range(sheet.nrows):
    col_index=0
    list_lexunits.append(sheet.cell(row_index,col_index).value)
set_lexunits=set(list_lexunits)

total_rows=sheet.nrows
for i in add_list:
    if i not in set_lexunits:

        sheet1.write(total_rows,0,i)
        sheet1.write(total_rows,1,class_lexunit)
        total_rows=total_rows+1
wb.save("/Users/sriWork/Desktop/health_first_classifier.xls")
#######


def get_medical_ailments(doc_content,n):

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

    counts_lex_units=Counter(list_lex_units)
    topics_medical_ailments=counts_lex_units.most_common(n)
    return topics_medical_ailments

    #print(doc_content)
    #print(list_lex_units)
    #print(counts_lex_units)







dict_blog_medical_ailments={}
n=1 ## number of medical ailments
#cnt_incomplete_blogs=0;
for i in range(0,length_dataframe):
    if dataframe['lang'][i]==[u'en']: ## Right now performed only for english documents
        #pd.set_option('display.max_columns', len(dataframe['content'][i]))
        #print(int(len(dataframe['content'][i])))
        #pd.set_printoptions('max_columns',str(len(dataframe['content'][i])))
        print([dataframe['content'][i]])
        print([dataframe['id'][i]])
        #pd.reset_option('display.max_columns')
        topics_medical_ailments=get_medical_ailments(dataframe['content'][i],n)
        #if topics_medical_ailments[1]==[u'healthy.a']:
            #cnt_incomplete_blogs=cnt_incomplete_blogs+1
            #print([dataframe['content'][i]])
            #print([dataframe['id'][i]])
        print i
        print(topics_medical_ailments)
        print ('/n')
#print 'Number of english documents = %d' %(cnt_incomplete_blogs)

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