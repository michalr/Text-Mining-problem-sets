from math import sqrt, log10
from random import sample
from sys import maxint
import marshal
import heapq
import os

INF = maxint
K = 20

def vectors_sim(v1, v2):
    """
        computes vectors cosine similarity
    """
    num = 0.0
    for key in set(v1.keys()) & set(v2.keys()):
        num += (v1[key] * v2[key])
    def sum_of_squares(v):
        tmp = 0.0
        for key in v.keys():
            tmp += v[key] ** 2
        return tmp
    den = sqrt(sum_of_squares(v1)) * sqrt(sum_of_squares(v2))
    return num / den
    
def read_file(input_file):
    res = {}
    freq = {}
    article = ""
    art_hash = {}
    for line in input_file:
        if not line.startswith(' '):
            tmp = line.strip("\n")
            if tmp:
                if article and res.get(article, ''):
                    for doc in set(res[article]):
                        if freq.get(doc, ''):
                            freq[doc] += 1
                        else:
                            freq[doc] = 1
                article = tmp.__hash__()
                art_hash[tmp.__hash__()] = tmp
        else:
            dec_line = line.strip(" \n")
            if dec_line:
                if res.get(article, ''):
                    res[article].append(dec_line.__hash__())
                else:
                    res[article] = [dec_line.__hash__()]
                art_hash[dec_line.__hash__()] = dec_line
    return (res, freq, art_hash)
    
def create_tf_idf_matrix(read_file, freq):
    res = {}
    N = len(read_file.keys())
    i = 0
    for key in sorted(read_file.keys()):
        if i % 1000 == 0:
             print "Done %d / %d" % (i, N)
        links_set = set(read_file[key])
        tf_idf_dict = {}
        for link in links_set:
            tf_idf_dict[link] = read_file[key].count(link) * log10(float(N) / freq[link])
        res[key] = tf_idf_dict
        del read_file[key]
        i += 1
    return res
    
def pick_leaders(tf_idf_matrix):
    return sample(tf_idf_matrix.keys(), int(sqrt(len(tf_idf_matrix.keys()))))
    
def create_clusters(leaders, tf_idf_matrix):
    clusters = {}
    for leader in leaders:
        clusters[leader] = {}
    i = 0
    for doc in tf_idf_matrix.keys():
        if i % 1000 == 0:
            print "%d / %d" % (i, len(tf_idf_matrix.keys()))
        min_dist = INF
        closest_leader = None
        for leader in leaders:
            sim_factor = vectors_sim(tf_idf_matrix[leader], tf_idf_matrix[doc])
            if sim_factor < min_dist:
                closest_leader = leader
        clusters[closest_leader][doc] = tf_idf_matrix[doc]
        i += 1
    return clusters
        
def pick_K_closest(query, clusters, tf_idf_matrix):
    closest_leader = None
    min_dist = INF
    for leader in clusters.keys():
        sim_factor = vectors_sim(tf_idf_matrix[leader], tf_idf_matrix[query])
        if sim_factor < min_dist:
            closest_leader = leader
    sim_factors = []
    for doc in clusters[closest_leader]:
        heappush(sim_factors, (vectors_sim(tf_idf_matrix[doc], tf_idf_matrix[query]), doc))
    return heapq.nlargest(K, sim_factors)
    
if __name__ == "__main__":
    f = open("tf_idf_matrix", "r")
    tf_idf_matrix = marshal.load(f)
    f.close()
    print "tf_idf_matrix loaded"
    leaders = pick_leaders(tf_idf_matrix)
    #import ipdb
    #ipdb.set_trace()
    print "Leaders picked"
    os.mkdir("clusters")
    for leader in leaders:
        os.mkdir("clusters/%s" % str(leader))
    print "Leader dirs created"
    clusters = create_clusters(leaders, tf_idf_matrix)
    for leader in clusters.keys():
        f = open("clusters/%s/%s.cluster" % (str(leader), str(leader)), "w")
        marshal.dump(clusters[leader], f)
        f.close()
        print "Dumped cluster %s" % leader
    print "Clusters created"
