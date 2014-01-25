import psycopg2
import numpy as np
import pandas as pd
import pandas.io.sql as psql
import matplotlib.pyplot as plt

from sklearn import mixture
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import euclidean_distances

db='o360'
username='ryan'
hostname='192.168.11.31'


def dp_cluster(X):
    max_clusters = 15
    dpgmm = mixture.DPGMM(n_components = max_clusters, alpha=1.0)        
    N = pt.shape[0]
    cluster_sizes = np.zeros((max_clusters,1))
    for i in range(max_clusters):
        print i
        dpgmm.fit(X)
        clusters = dpgmm.predict(X)
        cluster_sizes[i] = len(unique(clusters))

    #plt.hist(cluster_sizes)    
    #dpgmm = mixture.DPGMM(n_components = max_clusters, alpha=1.0)    
    #dpgmm.fit(pt)  


def dbscan_cluster(X, max_dist=.75):
    dbscan = DBSCAN(eps=max_dist, min_samples=100)    
    clusters = dbscan.fit_predict(X)
    return clusters    


def kmeans_cluster(X):
    kmeans = KMeans(n_clusters=20)
    clusters = kmeans.fit_predict(X)    
    return clusters



def load_rows(sql):
    conn = psycopg2.connect(dbname=db, user=username, host=hostname)
    
    try:                              
        df = psql.frame_query(sql, conn)        
    finally:
        conn.close()

    return df




def segment():
    sql = """select t.ncust_curr_cs_key cust_id,
                   c.name concept,
                   case when ca.allocation > 0 then 1 else 0 end count
            from nm_min_transactions t
            inner join nm_catalog cat on (cat.cmos_item_code = t.cat_item_number)
            inner join concept_allocation ca on (ca.catalog_id = cat.id)
            inner join concept c on (c.id = ca.concept_id)  
            """
               
    df = load_rows(sql)
    
    pt = pd.tools.pivot.pivot_table(df, values='count', rows='cust_id',
                                    cols='concept', aggfunc='sum',
                                    fill_value=0)    
    X = array(pt)
    
    



