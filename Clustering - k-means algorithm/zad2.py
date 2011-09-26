# -*- encoding: utf-8 -*-
from progressbar import Percentage, Bar, RotatingMarker, ETA, FileTransferSpeed, ProgressBar
from random import sample
import marshal
import re
from math import log10, sqrt

k = 10

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

def k_means(nouns, clusters_no, steps):
    centroids_keys = sample(nouns.keys(), clusters_no)
    centroids = []
    for key in centroids_keys:
        centroids.append(nouns[key])
    for i in range(steps):
        #print "STEP: %d/%d" % (i + 1, steps)
        clusters = [[] for k in range(clusters_no)]
        widgets = ['Computing clusters: ', Percentage(), ' ', 
                   Bar(marker=RotatingMarker()), ' ', ETA(), 
                   ' ', FileTransferSpeed()]
        pbar = ProgressBar(widgets=widgets, maxval=len(nouns.keys())).start()
        p = 0
        for noun in nouns.keys():
            max_sim = -1
            closest_centroid = -1
            for j in range(len(centroids)):
                d = vectors_sim(centroids[j], nouns[noun]) 
                if d > max_sim:
                    max_sim = d
                    closest_centroid = j
            clusters[closest_centroid].append(noun)
            pbar.update(p)
            p += 1
        pbar.finish()
        widgets[0] = "Computing centorids: "
        pab = ProgressBar(widgets=widgets, maxval=clusters_no).start()
        for k in range(clusters_no):
            #print "CLUSTER: %d/%d" % (k + 1, clusters_no)
            #print "CLUSTER LENGTH: %d" % (len(clusters[k]),)
            vec_sum = {}
            for word in clusters[k]:
                for key, value in nouns[word].iteritems():
                    vec_sum[key] = vec_sum.setdefault(key, 0.0) + value
            centroids[k] = {}
            for key, value in vec_sum.iteritems():
                centroids[k][key] = value / len(clusters[k])
            pbar.update(k)
        pbar.finish()
    return clusters
    
def rss_k(nouns, cluster):
    vec_sum = {}
    for word in cluster:
        for key, value in nouns[word].iteritems():
            vec_sum[key] = vec_sum.setdefault(key, 0.0) + value
        centroid = {}
        for key, value in vec_sum.iteritems():
            centroid[key] = value / len(cluster)
    res = 0.0
    for noun in cluster:
        res += (vectors_sim(centroid, nouns[noun]) ** 2)
    return res
   
def rss(nouns, clusters):
    res = 0.0
    for cluster in clusters:
        res += rss_k(nouns, cluster)
    return res
            
if __name__ == "__main__":
    """
    morfo = {}
    f = open("morfologik.txt", "rt")
    widgets = ['Parsing Morfologik: ', Percentage(), ' ', 
               Bar(marker=RotatingMarker()), ' ', ETA(), 
               ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=3662366).start()
    i = 0
    for line in f:
        l = line.split("\t")
        l[0] = l[0].decode('iso-8859-2').encode('utf-8')
        l[1] = l[1].decode('iso-8859-2').encode('utf-8')
        part = l[-1].split(":")[0]
        if part == "subst":
            if morfo.get(l[0], ""):
                morfo[l[0]].append(l[1])
            else:
                morfo[l[0]] = [l[1]]
        pbar.update(i)
        i += 1
        
    pbar.finish()
    f.close()   
    f = open("wikipedia_dla_wyszukiwarek.txt", "rt")
    freqs = {}
    regex = re.compile("[a-zA-Z0-9_ąśćęźżółńĄŚĆĘŹŻÓŁŃ]+") 
    i = 0
    widgets[0] = "Parsing wikipedia: "
    pbar = ProgressBar(widgets=widgets, maxval=15255080).start()
    for line in f:
        words = regex.findall(line)
        for word in words:
            try:
                bases = morfo[word]
            except KeyError:
                continue
            for base in bases:
                if freqs.get(base, ''):
                    freqs[base] += 1
                else:
                    freqs[base] = 1
        pbar.update(i)
        i += 1
    pbar.finish()
    f.close()
    frequent_words = [key for key in freqs.keys() if freqs[key] >= k]
    marshal.dump(frequent_words, open("frequent_words", "wb"))
    biernik = marshal.load(open("biernik.msl", "rb"))
    orzeczenie = marshal.load(open("orzeczenie.msl", "rb"))
    zgoda = marshal.load(open("zgoda.msl", "rb"))
    res = biernik
    widgets = ['Parsing Orzeczenie: ', Percentage(), ' ', 
               Bar(marker=RotatingMarker()), ' ', ETA(), 
               ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=len(orzeczenie.keys())).start()
    i = 0
    for key in orzeczenie.keys():
        if res.get(key, None):
            for key2 in orzeczenie[key].keys():
                if res[key].get(key2, None):
                    res[key][key2] += orzeczenie[key][key2]
                else:
                    res[key][key2] = orzeczenie[key][key2]
        else:
            res[key] = orzeczenie[key]
        pbar.update(i)
        i += 1
    widgets[0] = "Parsing Zgoda: "
    pbar = ProgressBar(widgets=widgets, maxval=len(zgoda.keys())).start()
    i = 0
    for key in zgoda.keys():
        if res.get(key, None):
            for key2 in zgoda[key].keys():
                if res[key].get(key2, None):
                    res[key][key2] += zgoda[key][key2]
                else:
                    res[key][key2] = zgoda[key][key2]
        else:
            res[key] = zgoda[key]
        pbar.update(i)
        i += 1            
    df = {}
    widgets[0] = "Computing df: "
    pbar = ProgressBar(widgets=widgets, maxval=len(res.keys())).start()
    i = 0
    for key, value in res.iteritems():
        for k in value.keys():
            df[k] = df.setdefault(k, 0) + 1
        pbar.update(i)
        i += 1            
    marshal.dump(res, open("clustering_vectors", "wb"))
    marshal.dump(df, open("clustering_df", "wb"))           
    vectors = marshal.load(open("clustering_vectors", "rb"))
    df = marshal.load(open("clustering_df", "rb"))
    N = len(vectors.keys())
    tf_idf_matrix = {}
    for key, value in vectors.iteritems():
        tf_idf_vector = {}
        for k, v in value.iteritems():
            tf_idf_vector[k] = v * log10(float(N) / df[k])
        tf_idf_matrix[key] = tf_idf_vector
    marshal.dump(tf_idf_matrix, open("clustering_tf_idf", "wb"))
    """
    """
    frequent_words = marshal.load(open("frequent_words", "rb"))
    tf_idf_matrix = marshal.load(open("clustering_tf_idf", "rb"))
    freq_tf_idf = {}
    for key in tf_idf_matrix.keys():
        if key in frequent_words:
            freq_tf_idf[key] = tf_idf_matrix[key]
    marshal.dump(freq_tf_idf, open("clustering_freq_tf_idf", "wb"))
    """
    nouns = marshal.load(open("clustering_freq_tf_idf", "rb"))
    clusters = k_means(nouns, 2, 1)
