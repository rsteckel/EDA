import psycopg2
import numpy as np
import pandas as pd
import simplejson as json
from collections import defaultdict
from nltk.corpus import stopwords

from sklearn.metrics.pairwise import cosine_similarity

db='o360'
username='ryan'
hostname='192.168.11.31'

DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)



class ConceptItem:    
    def __init__(self, item_code, pos_tags, modifiers):
        self.cmos_item_code = item_code
        self.all_pos_tags = [ tuple(tagged.split('/')) for tagged in pos_tags.split(';')]
        self.all_modifiers = [ tuple(mod.split('|')) for mod in modifiers.split('^') ]
        self.all_concepts = {}
    
    def add_concept(self, concept_name, score, feature_weights):
        self.all_concepts[concept_name] = (score, feature_weights)
    
    def concepts(self):
        return self.all_concepts.keys()
    
    def concept_score(self, concept):
        score = 0.0
        if self.all_concepts.has_key(concept):
            score = self.all_concepts[concept][0]
        return score
        
    def concept_features(self, concept):
        if self.all_concepts.has_key(concept):
            features = self.all_concepts[concept][1]
            return [ tuple(f.split(';')) for f in features.split('|')]
        return []
    
    def item_code(self):
        return self.cmos_item_code

    def pos_tags(self):
        return self.all_pos_tags
        
    def modifiers(self):
        return self.all_modifiers




def create_id_lookup():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute("select id, cmos_item_code from product_features;")
        rows = cur.fetchall()
    
        ids = {}
        for row in rows:
            ids[row[0]] = row[1]
            
    finally:
        cur.close()
        conn.close()
    
    return ids



def load_product_descs():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute("""select id, long_desc_text_only from nm_catalog order by id""")
        rows = cur.fetchall()
            
    finally:
        cur.close()
        conn.close()
    
    return rows


def load_items(concept):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select cmos_item_code item, score 
                        from concept_item_scores 
                        where concept_name = %s;""", (concept,))
                    
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()
    
    return rows


def save_concept_terms(concept_id, feature_weights):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute("delete from concept_terms where concept_id = %s", (concept_id,)) 
        
        term_string = '|'.join( [ fw[1]+';'+str(round(fw[0],4)) for fw in feature_weights ] )
        cur.execute("INSERT INTO concept_terms (concept_id, concept_terms) VALUES (%s, %s)", (concept_id, term_string))
        conn.commit()
    except Exception as inst:
        print 'Error inserting concept terms'
        print type(inst)
        print inst.args
        print inst 
        
    finally:
        cur.close()
        conn.close()



def save_concept_term_scores(concept_name, concept_terms):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute("delete from concept_term_scores where concept_name = %s", (concept_name,)) 
        
        for score,term in concept_terms:
            cur.execute("""INSERT INTO concept_term_scores (concept_name, concept_term, term_score)
                                VALUES (%s, %s, %s)""", (concept_name, term, score))
        conn.commit()
    except Exception as inst:
        print 'Error inserting concept terms'
        print type(inst)
        print inst.args
        print inst 
        
    finally:
        cur.close()
        conn.close()



def save_features(concept_id, product_ids, feature_weights):    
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        if len(product_ids) != len(feature_weights):
            print 'Error saving features. Items and features don\'t have same length'
            return
        
        cur.execute("delete from product_concept_features where concept_id = %s", (concept_id,)) 
        
        for i in xrange(len(product_ids)):
            product_id = product_ids[i]
            features = feature_weights[i]             
            feature_string = [ ';'.join([f,str(round(w,4))]) for f,w in features]
            
            cur.execute("""INSERT INTO product_concept_features (product_id, concept_id, features)
                                    VALUES (%s, %s, %s)""", (product_id, concept_id, '|'.join(feature_string)))
        
        conn.commit()
        
    except Exception as inst:
        print 'Error inserting concept terms'
        print type(inst)
        print inst.args
        print inst 
        
    finally:
        cur.close()
        conn.close()



def save_concept_scores(concept_id, product_ids, scores):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    if len(product_ids) != len(scores):
        print 'Items and scores have different lengths'
        return

    try:
        cur.execute("delete from product_concept where concept_id = %s", (concept_id,))
        
        for product_id, score in zip(product_ids,scores):        
            cur.execute("""INSERT INTO product_concept (product_id, concept_id, score) 
                            VALUES (%s, %s, %s)""", (product_id, concept_id, score))
        conn.commit()
    except Exception as inst:
        print 'Error inserting concept scores'
        print type(inst)
        print inst.args
        print inst 
    finally:
        cur.close()
        conn.close()
    


def save_item_pos_tags(filename):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        doc_terms = ingest_pos_json(filename)

        pos_items = [ d[0] for d in doc_terms ]
        pos_terms = [ d[1] for d in doc_terms ]
        pos_str = [tp for tp in pos_terms ]

        postags = []
        for i in range(len(pos_str)):
            postags.append(';'.join([t[0]+'/'+t[1] for t in pos_str[i]]))

        for i in range(len(pos_items)):
            cur.execute("delete from item_pos_features where cmos_item_code = %s", (pos_items[i],)) 
            cur.execute("""insert into item_pos_features (cmos_item_code, pos_tags) 
                            values (%s, %s)""", (pos_items[i], postags[i]))
        conn.commit()
    except Exception as inst:
        print 'Error inserting concept scores'
        print type(inst)
        print inst.args
        print inst 
    finally:
        cur.close()
        conn.close()


def save_item_modifiers(filename):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        doc_mods = ingest_modifers_json(filename)

        items = [ d[0] for d in doc_mods ]
        
        mod_terms = [ d[1] for d in doc_mods ]
        mod_str = [tp for tp in mod_terms ]

        mods = []
        for i in range(len(mod_str)):
            mods.append('^'.join([t[0]+'|'+t[1] for t in mod_str[i]]))

        for i in range(len(items)):
            cur.execute("delete from item_modifiers where cmos_item_code = %s", (items[i],)) 
            cur.execute("""insert into item_modifiers (cmos_item_code, modifiers) 
                            values (%s, %s)""", (items[i], mods[i]))
        conn.commit()
    except Exception as inst:
        print 'Error inserting concept scores'
        print type(inst)
        print inst.args
        print inst 
    finally:
        cur.close()
        conn.close()



def delete_concept(concept_name):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute("delete from concept_item_scores where concept_name = %s", (concept_name,))
        cur.execute("delete from concept_terms where concept_name = %s", (concept_name,)) 
        cur.execute("delete from concept_term_scores where concept_name = %s", (concept_name,)) 
        cur.execute("delete from item_concept_features where concept_name = %s", (concept_name,)) 

        conn.commit()
    except Exception as inst:
        print 'Error deleting concept'
        print type(inst)
        print inst.args
        print inst 
    finally:
        cur.close()
        conn.close()


def load_concepts():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    try:
        # Query the database and obtain data as Python objects
        cur.execute("""select id, name 
                        from concept 
                        where enabled = 1
                        order by name""")

        rows = cur.fetchall()

        concepts = [ (row[0],row[1]) for row in rows ]
    finally:
        cur.close()
        conn.close()
    
    return concepts


def load_concept(concept_name):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    try:
        cur.execute("""select id, name 
                        from concept 
                        where name = %s""", (concept_name,))

        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()
    
    return [row]


def load_concepts_json(top_n=None):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    try:
        cur.execute("""select name, concept_terms 
                        from concept_terms ct
                        inner join concept c on (c.id = ct.concept_id)
                        where enabled = 1
                        order by name""")

        rows = cur.fetchall()
        
        concepts = defaultdict(lambda: [])
        for row in rows:         
            term_list = [ (tw.split(';')[0], float(tw.split(';')[1])) for tw in row[1].split('|') ]
            if top_n is not None:
                concepts[ row[0] ] = term_list[:top_n]
            else:
                concepts[ row[0] ] = term_list
        
    finally:
        cur.close()
        conn.close()
    
    return json.dumps(concepts, indent=3, sort_keys=True, ensure_ascii=False)



def load_classified_concepts():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    try:
        # Query the database and obtain data as Python objects
        cur.execute("""select distinct c.id, c.name 
                        from product_concept pc  
                        inner join concept c on (c.id = pc.concept_id)
                        order by name""")

        rows = cur.fetchall()

        concepts = [ (row[0],row[1]) for row in rows ]
    finally:
        cur.close()
        conn.close()
    
    return concepts


def load_term_vector(concept_name):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        # Query the database and obtain data as Python objects
        cur.execute("""select concept_terms 
                        from concept_terms ct
                        inner join concept c on (c.id = ct.concept_id)
                        where c.name = %s""", (concept_name,))

        row = cur.fetchone()
    
        tokens = row[0].split('|')
        terms = [ tw.split(';')[0] for tw in tokens ]
        scores = [ float(tw.split(';')[1]) for tw in tokens ]
    finally:
        cur.close()
        conn.close()
    
    return [terms, scores]



def print_term_vector(concept):
    terms,scores = load_term_vector(concept)
    for tv in zip(terms, scores):
        print "%15s %3.4f" % (tv[0],tv[1])



def concept_cosine(concept1, concept2):
    terms1,scores1 = load_term_vector(concept1)
    terms2,scores2 = load_term_vector(concept2)
    
    terms =  terms1 + terms2 
    terms.sort()
    
    vec1 = np.zeros(len(terms))
    vec2 = np.zeros(len(terms))

    #Use classifer weights
    for i in range(len(terms1)):
        vec1[ terms.index(terms1[i]) ] = scores1[i]
        
    for i in range(len(terms2)):
        vec2[ terms.index(terms2[i]) ] = scores2[i]

    return cosine_similarity(vec1, vec2)[0][0]


def compare_concepts():
    concepts = load_concepts()    
    concept_names = [ c[1] for c in concepts ]

    concept_scores = []
    for i in range(len(concept_names)):
        for j in range(i, len(concept_names)):    
            print i,j
            if i == j:
                concept_scores.append((concept_names[i], concept_names[j], 0))
            else:
                sim = concept_cosine(concept_names[i], concept_names[j])
                concept_scores.append((concept_names[i], concept_names[j], sim))
                
    return concept_scores



def load_concept_items(min_concept_score=.6):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute("""select cis.cmos_item_code,
                           ipf.pos_tags,
                           imf.modifiers,
                           cis.concept_name,
                           icf.feature_weights,
                           cis.score
                    from concept_item_scores cis
                    left join item_pos_features ipf on (ipf.cmos_item_code = cis.cmos_item_code)
                    left join item_modifiers imf on (imf.cmos_item_code = cis.cmos_item_code)
                    left join item_concept_features icf on (icf.cmos_item_code = cis.cmos_item_code
                    					   and icf.concept_name = cis.concept_name)
                    where ipf.pos_tags is not null
                    and imf.modifiers is not null
                    and cis.score >= %s""", (min_concept_score,))
        
        rows = cur.fetchall()
    
        items = {}
        
        for row in rows:
            item_code = row[0]
            pos_tags = row[1]
            modifiers = row[2]
            concept_name = row[3]
            feature_weights = row[4]
            score = row[5]

            if items.has_key(item_code) == False:
                items[item_code] = ConceptItem(item_code, pos_tags, modifiers)

            item = items[item_code]
            item.add_concept(concept_name, score, feature_weights)
            
    finally:
        cur.close()
        conn.close()
    
    return items




def ingest_pos_json(filename, target_pos=['NN','NP','NNP','JJ']):
    with open (filename, "r") as myfile:
        data=myfile.read().replace('\n', '')
    
    page = json.loads(data)
    docs = page['documents']

    ids = create_id_lookup()

    doc_terms = []
    for doc in docs:
        id = doc['name']
        tag_poses = [ (tag['tokenWord'], tag['postag']) for tag in doc['words'] if tag['postag'] in target_pos]
        if len(tag_poses) > 0 and ids.has_key(id):
            doc_terms.append([ ids[id], tag_poses ])
        else:
            print 'Skipping', id
            
    return doc_terms
    


def ingest_modifers_json(filename):
    with open (filename, "r") as myfile:
        data=myfile.read().replace('\n', '')
    
    page = json.loads(data)
    docs = page['documents']

    ids = create_id_lookup()
    all_stopwords = stopwords.words('english') + [ u'\xae' ]
    
    doc_mods = []
    
    for doc in docs:
        doc_id = doc['name']
        docmods = defaultdict(list)
        for w in doc['words']:
            dep = w['depType']
            word = w['tokenWord'].lower()
            if dep == 'NMOD' and word not in all_stopwords:
                docmods[w['parentDice']].append(word)
        modifiers = [ ';'.join(docmods[k]) for k in docmods.keys() ]
        
        if len(modifiers) > 0 and ids.has_key(doc_id):
            doc_mods.append( [ ids[doc_id], zip(docmods.keys(), modifiers) ])
        else:
            print 'Skipping', doc_id
        
    return doc_mods





def mean_dirichlet(A):
    return A / sum(A)

def var_dirichlet(A):
    a0 = sum(A)
    return (A * (a0 - A)) / (a0**2 * (a0 + 1))
    
def update_dirichlet(A, obs):
    return np.add(A, obs)

def dept_concepts(item_threshold=.7):
    concepts = load_concepts()
    
    sql = "select silo_name dept,\n"
    case_stmts = []
    for c in concepts:
        case_stmts.append("COALESCE(sum(case when cs.concept_name = '"+c+"' and cs.score > "+str(item_threshold)+" then 1 end),0) concept_"+c+"\n")
    sql += ','.join(case_stmts)
    sql += "from concept_item_scores cs\n"
    sql += "left join product_features pf on (pf.cmos_item_code = cs.cmos_item_code)\n"
    sql += "group by silo_name\n"

    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute(sql)
        rows = cur.fetchall()

        M = len(concepts)
        uniform_prior = np.ones( M ) #dynamic prior later???
        
        results = []
        for row in rows:
            posterior = update_dirichlet(uniform_prior, row[1:(M+1)] )
            mP = mean_dirichlet(posterior)
            vP = var_dirichlet(posterior)
            dept_name = str(row[0])
            clean_dept_name= dept_name.replace("&apos;","'")
            results.append((clean_dept_name, mP, vP))
    finally:
        cur.close()
        conn.close()
    
    return results



def save_dept_scores(dept_scores):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        concepts = load_concepts()        

        for d in dept_scores:
            dept = d[0]
            concept_scores = d[1] #mean values = 1, std dev values = 2
            if len(concept_scores) == len(concepts):
                for i in range(len(concepts)):
                    concept = concepts[i]
                    score = concept_scores[i]                
                    cur.execute("delete from concept_dept_scores where dept = %s and concept_name = %s", (dept,concept)) 
                    cur.execute("""insert into concept_dept_scores (dept, concept_name, score) 
                                    values (%s, %s, %s)""", (dept, concept, score))
        conn.commit()
    except Exception as inst:
        print 'Error inserting concept scores'
        print type(inst)
        print inst.args
        print inst 
    finally:
        cur.close()
        conn.close()



def annual_dept_revenue():
    sql = """select silo_name dept,
                   round(cast(sum(t.af_pur_amt) as numeric),2) annual_revenue
            from product_features pf
            inner join transactions t on (t.cat_item_number = pf.cmos_item_code)
            where tim_ukey_dt >= (current_date + interval '-1' year)
            group by silo_name"""

    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    try:
        cur.execute(sql)
        rows = cur.fetchall()

        results = []
        for row in rows:
            dept_name = str(row[0])
            clean_dept_name= dept_name.replace("&apos;","'")
            results.append((clean_dept_name, row[1]))
    finally:
        cur.close()
        conn.close()
    
    return results


def solr_id_lookup():
    sql = """select solr_id, 
                   categorytype_name || ' ' || category_name category
            from nm_catalog"""

    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()

    id_map = {}
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        
        for row in rows:
            id_map[ row[0] ] = row[1]
    finally:
        cur.close()
        conn.close()
    
    return id_map

