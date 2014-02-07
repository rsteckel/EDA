import psycopg2
import simplejson as json

db='o360'
username='ryan'
hostname='192.168.11.31'


def concept_dept_allocation():
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select d.dept,
                           d.concept,
                           coalesce(dc.annual_rev_allocation,0) annual_rev_allocation,
                           coalesce(dc.items_sold_allocation,0) items_sold_allocation,
                           coalesce(dc.unique_buyers_allocation,0) unique_buyers_allocation
                    from dept_concept dc
                    right join
                      (select distinct dept, name concept
                      from concept,nm_dept) d on (d.dept = dc.dept and d.concept = dc.concept)""")
                    
        rows = cur.fetchall()          
    finally:
        cur.close()
        conn.close()

    depts = {}
    for row in rows:    
        dept_name = row[0]
        if not depts.has_key(dept_name):
            dept = {}
            dept['id'] = dept_name
            dept['name'] = dept_name
            depts[dept_name] = dept
            
        dept = depts[dept_name]
        concept = row[1]
        
        concept_annual_revenue = row[2]
        concept_annual_items_sold = row[3]
        concept_unique_buyers = row[4]
        
        dept[concept+'_revenue'] = concept_annual_revenue
        dept[concept+'_items_sold'] = concept_annual_items_sold
        dept[concept+'_unique_buyers'] = concept_unique_buyers

    return depts



def append_dept_stats(depts):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select dept,
                              annual_revenue,
                              annual_products_sold,
                              unique_customers
                    from nm_dept""")
        rows = cur.fetchall()          
    finally:
        cur.close()
        conn.close()

    for row in rows:
        annual_revenue = row[1]
        annual_products_sold = row[2]
        unique_buyers = row[3]
        
        dept = depts[row[0]]
        dept['total_revenue'] = annual_revenue
        dept['total_items_sold'] = annual_products_sold
        dept['total_unique_buyers'] = unique_buyers
        
    return depts



def append_top_brands(depts):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    cur = conn.cursor()
    
    try:
        cur.execute("""select dept, concept, array_to_string(array_agg(brand), ';') 
                        from (
                        	select d.dept, d.concept, brand,
                        		row_number() over (partition by d.dept, d.concept order by annual_rev_allocation desc) rownum
                        	from dept_concept_brand dcb
                        	right join
                        	      (select distinct dept, name concept
                        	      from concept,nm_dept) d on (d.dept = dcb.dept and d.concept = dcb.concept)                
                        ) s where rownum <= 3
                        group by dept, concept""")
        rows = cur.fetchall()          
    finally:
        cur.close()
        conn.close()

    for row in rows:
        dept_name = row[0]
        concept = row[1]
        top_brands = row[2]
        
        dept = depts[dept_name]
        dept[concept+'_top_brands'] = top_brands
                
    return depts


    
def write_file(depts, filename):    
    with open(filename, 'w') as f:
        f.write(json.dumps(depts.values(), sort_keys=True, indent=4))
        f.flush()



if __name__ == '__main__':
    depts = concept_dept_allocation()
    depts = append_dept_stats(depts)
    depts = append_top_brands(depts)

    write_file(depts, '/tmp/dept_concept_export.json')