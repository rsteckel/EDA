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
    

def product_segment():
    
    #sql = """select product_id, c.name concept_name, score
    #            from product_concept pc
    #            inner join concept c on (c.id = pc.concept_id)
    #            where score >= .65
    #            order by product_id, concept_name"""
                
    sql = """select catalog_id product_id, 
                   c.name concept_name, 
                   allocation score
            from concept_allocation ca
            inner join concept c on (c.id = ca.concept_id)
            order by product_id, concept_name"""                    
                        
    df = load_rows(sql)
        
    pt = pd.tools.pivot.pivot_table(df, values='score', rows='product_id',
                                    cols='concept_name', aggfunc='sum',
                                    fill_value=0)    
    X = array(pt)
    #clusters = kmeans_cluster(X)
    clusters = dbscan_cluster(X, max_dist=.35)
    #clusters = dp_cluster(X)
    
    pt['cluster'] = clusters
    pt.to_csv('/tmp/product_clusters.csv')




