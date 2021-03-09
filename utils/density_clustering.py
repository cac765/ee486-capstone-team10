import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def Count_Clusters( X ):

    # Compute DBSCAN
    db = DBSCAN(eps=0.1*480, min_samples=1).fit(X) 
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    #print('Estimated Number of Clusters: ',  n_clusters)
    return n_clusters

