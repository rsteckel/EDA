import os
import pickle, os, csv, operator
from text_utils import *
import nltk
import psycopg2

DB='o360'
USERNAME='ryan'
HOSTNAME='192.168.11.31'


COLORS = color_lookup()
FABRICS = fabric_lookup()


def load_pipeline(pos_concept, neg_concept):
    pipeline = pickle.load(open(concept_pipeline(pos_concept, neg_concept), 'rb'))
    return pipeline
    

def load_docs(dirname):
    listing = os.walk(dirname).next()
    basedir = listing[0]
    filenames = listing[2]
    
    docs = []
    for filename in filenames:
        f = open(basedir+'/'+filename, 'r')
        content = ' '.join(f.readlines())
        docs.append(content)
    return docs
    

def tokenize(doc, use_bigrams=True):
    tokens = nltk.word_tokenize(doc.lower())
    tokens = [token.lower() for token in tokens if len(token) > 1] 

    if len(tokens) > 1 and use_bigrams:
        bi_tokens = [ ' '.join(bigram) for bigram in nltk.bigrams(tokens) ]
        return [ tokens, bi_tokens ]

    return [tokens, [] ]


def extract_attributes(doc, ATTRIBUTE_LOOKUP):
    unigrams,bigrams = tokenize(doc, use_bigrams=True)
    attributes = []    
    if bigrams is not None:
        for bigram in bigrams:
            if ATTRIBUTE_LOOKUP.has_key(bigram):
                attributes.append(bigram)
                [ unigrams.remove(t) for t in bigram.split(' ') if t in unigrams ]
    
    for unigram in unigrams:
        if ATTRIBUTE_LOOKUP.has_key(unigram):
            attributes.append(unigram)

    return attributes



def catalog_colors(items, descs):    
    item_colors = defaultdict(lambda: defaultdict(lambda: 0))
    color_counts = defaultdict(lambda: 0)
    
    index = 0
    for item, desc in zip(items, descs):
        colors = extract_attributes(desc, COLORS)
        for c in colors:
            item_colors[item][c] += 1
            color_counts[c] += 1
                
        index += 1
        if index % 10000 == 0:
            print index
    
    return [ color_counts, item_colors ]        
        
        
        
def catalog_fabrics(items, descs):    
    item_fabrics = defaultdict(lambda: defaultdict(lambda: 0))
    fabric_counts = defaultdict(lambda: 0)
    
    index = 0
    for item, desc in zip(items, descs):
        fabrics = extract_attributes(desc, FABRICS)
        for f in fabrics:
            item_fabrics[item][f] += 1
            fabric_counts[f] += 1
                
        index += 1
        if index % 10000 == 0:
            print index
    
    return [ fabric_counts, item_fabrics ]          
        


def weekly_attributes(project_dir, top_n=5):
    subdirs = os.walk(project_dir).next()[1]
    subdirs.sort()
    
    NORM_COUNT = 5000    
    
    for subdir in subdirs:
        week_color_counts = defaultdict(lambda: 0)    

        docs = load_docs(project_dir+'/'+subdir)
        if len(docs) > 0:
            for doc in docs:
                try:                        
                    colors = extract_attributes(doc, COLORS)
                    for c in colors:
                        week_color_counts[c] += 1
                except Exception as e:
                    print e
        
        #Normalize to NORM_COUNT documents
        for cc in week_color_counts.keys():
            week_color_counts[cc] = np.round((week_color_counts[cc] / float(len(docs))) * NORM_COUNT) 
        
        print "%s,%d" % (subdir, week_color_counts['pink'])
        #color_counts = sorted(week_color_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
        #color_count_str = ';'.join([ tw[0]+','+str(tw[1]) for tw in color_counts[:top_n] ])
        #print color_count_str
        
        #fabric_counts = sorted(fabric_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
        #fabric_count_str = ';'.join([ tw[0]+','+str(tw[1]) for tw in fabric_counts[:top_n] ])
                


def save_color_attributes(color_counts):
    conn = psycopg2.connect(dbname=DB, user=USERNAME, host=HOSTNAME)
    cur = conn.cursor()

    try:
        cur.execute("delete from nm_catalog_attributes where type_id = 1") 
        
        for color in color_counts.keys():
            cur.execute("INSERT INTO nm_catalog_attributes (type_id, name) VALUES (%s, %s)", (1, color))
        conn.commit()
    except Exception as inst:
        print 'Error inserting concept terms'
        print type(inst)
        print inst.args
        print inst 
        
    finally:
        cur.close()
        conn.close()




#def save_product_colors(item_colors, filename):
#    with open(filename, 'w') as f:
#        writer = csv.writer(f)
#        writer.writerow([ 'product_id', 'attribute_id', 'count'])
#        
#        index = 1
#        for items in item_colors.items():
#            item = items[0]
#            color_counts = items[1]
#        
#            if index % 10000 == 0:
#                print index
#            index += 1
#            
#            for color in color_counts.keys():
#                count = color_counts[color]
#
#                writer.writerow([ item, color, count ])


def product_map():
    conn = psycopg2.connect(dbname=DB, user=USERNAME, host=HOSTNAME)
    cur = conn.cursor()
    
    products = {}
    try:
        cur.execute("""select id, cmos_item_code from nm_catalog""") 
        rows = cur.fetchall()
        for row in rows:
            products[ row[1] ] = row[0]
    except Exception as inst:
        print inst 
        
    finally:
        cur.close()
        conn.close()
        
    return products


def color_map():
    conn = psycopg2.connect(dbname=DB, user=USERNAME, host=HOSTNAME)
    cur = conn.cursor()
    
    colors = {}
    try:
        cur.execute("""select id, name from nm_catalog_attributes where type_id = 1""") 
        rows = cur.fetchall()
        for row in rows:
            colors[ row[1] ] = row[0]
    except Exception as inst:
        print inst 
        
    finally:
        cur.close()
        conn.close()
        
    return colors



def fabric_map():
    conn = psycopg2.connect(dbname=DB, user=USERNAME, host=HOSTNAME)
    cur = conn.cursor()
    
    fabrics = {}
    try:
        cur.execute("""select id, name from nm_catalog_attributes where type_id = 2""") 
        rows = cur.fetchall()
        for row in rows:
            fabrics[ row[1] ] = row[0]
    except Exception as inst:
        print inst 
        
    finally:
        cur.close()
        conn.close()
        
    return fabrics



def save_product_colors(item_colors):
    conn = psycopg2.connect(dbname=DB, user=USERNAME, host=HOSTNAME)
    cur = conn.cursor()
    
    product_ids = product_map()
    color_ids = color_map()
    
    try:
        index = 1
        for items in item_colors.items():
            item = items[0]
            color_counts = items[1]
        
            if index % 1000 == 0:
                print index
            index += 1
            
            for color in color_counts.keys():
                color_id = color_ids[color]
                product_id = product_ids[item]
                count = color_counts[color]
                
                cur.execute("""delete from nm_product_attributes
                           where product_id = %s and attribute_id = %s""", (product_id, color_id)) 
                
                cur.execute("""insert into nm_product_attributes (product_id, attribute_id, count)
                                values (%s, %s, %s) """, (product_id, color_id, count))
            conn.commit()
    except Exception as inst:
        print 'Error inserting concept terms'
        print type(inst)
        print inst.args
        print inst 
        
    finally:
        cur.close()
        conn.close()



def save_fabric_attributes(fabric_counts):
    conn = psycopg2.connect(dbname=DB, user=USERNAME, host=HOSTNAME)
    cur = conn.cursor()

    try:
        cur.execute("delete from nm_catalog_attributes where type_id = 2") 
        
        for fabric in fabric_counts.keys():
            cur.execute("INSERT INTO nm_catalog_attributes (type_id, name) VALUES (%s, %s)", (2, fabric))
        conn.commit()
    except Exception as inst:
        print inst 
        
    finally:
        cur.close()
        conn.close()




def save_product_fabrics(item_fabrics):
    conn = psycopg2.connect(dbname=DB, user=USERNAME, host=HOSTNAME)
    cur = conn.cursor()
    
    product_ids = product_map()
    fabric_ids = fabric_map()
    
    try:
        index = 1
        for items in item_fabrics.items():
            item = items[0]
            fabric_counts = items[1]
        
            if index % 1000 == 0:
                print index
            index += 1
            
            for fabric in fabric_counts.keys():
                fabric_id = fabric_ids[fabric]
                product_id = product_ids[item]
                count = fabric_counts[fabric]
                
                cur.execute("""delete from nm_product_attributes
                           where product_id = %s and attribute_id = %s""", (product_id, fabric_id)) 
                
                cur.execute("""insert into nm_product_attributes (product_id, attribute_id, count)
                                values (%s, %s, %s) """, (product_id, fabric_id, count))
            conn.commit()
    except Exception as inst:
        print inst 
        
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    BASE_DIR = os.environ['NM_HOME']+'/Data/Temporal'
    COLLECTION = 'fashion_crawl_try_20131015'
    TEMPORAL_DIR = BASE_DIR+'/'+COLLECTION

    weekly = True

    if weekly:
        weekly_attributes(TEMPORAL_DIR)
    else:
        items, descs = load_prod_desc_only_catalog()    
        print '\tColors..'
        color_counts,item_colors = catalog_colors(items, descs)
        save_color_attributes(color_counts)
        save_product_colors(item_colors)    
        
        print '\tFabrics..'
        fabric_counts,item_fabrics = catalog_fabrics(items, descs)
        save_fabric_attributes(fabric_counts)
        save_product_fabrics(item_fabrics)
    
    