import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def Count_Clusters( X ):

    # Compute DBSCAN
    if len(X) > 0:
        db = DBSCAN(eps=0.1175*480, min_samples=1).fit(X) 
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    else:
        n_clusters = 0
        
    #print('Estimated Number of Clusters: ',  n_clusters)
    return n_clusters

