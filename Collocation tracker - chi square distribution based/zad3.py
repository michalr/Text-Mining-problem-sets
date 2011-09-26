#! /usr/bin/env python
# -*- coding: utf-8 -*-

# poczatki wikipiedii
# filtr zliczajacy liczbe wariantow, im wiecej wystapieword1_lists[0][0], word2_lists[0][0]n w roznych formach tym wyzej w rankingu 

ALFA = 0.05

CRITICAL = 3.841

BONUS_POS = 5

BONUS_NEG = 5

def matching_forms(word1_info, word2_info):
    il1 = word1_info.split(":")
    il2 = word2_info.split(":")
    #print (il1, il2)
    complement = False
    try:
    	complement = il1[0] == il2[0] == 'subst' and il1[1] == il2[1] and set(il1[2].split(".")) & set(il2[2].split(".")) 
    	if complement:
        	return (complement, il1[1], ' '.join(list(set(il1[2].split(".")) & set(il2[2].split(".")))))
        return (False, None, None)
    except IndexError:
    	complement = il1[0] == il2[0] == 'subst' and il1[1] == il2[1]
    	if complement: 
        	return (complement, il[1] , None)
        return (False, None, None)
        
def are_words_complement(word1, word2, morfologik, bigrams_forms):
    try:
        word1_lists = morfologik[word1]
        word2_lists = morfologik[word2]
    except KeyError:
        return (None, None)
    if len(word1_lists) > 1 or len(word2_lists) > 1:
        return (None, None)
    words_matching, prz, li = matching_forms(word1_lists[0][1], word2_lists[0][1])
    if words_matching:
    	new_form = False 
    	if bigrams_forms.get((word1_lists[0][0], word2_lists[0][0]), ''):
    		if not (prz, li) in bigrams_forms[(word1_lists[0][0], word2_lists[0][0])]: 
    			bigrams_forms[(word1_lists[0][0], word2_lists[0][0])].add((prz, li))
    			new_form = True
    	else:
    		bigrams_forms[(word1_lists[0][0], word2_lists[0][0])] = set([(prz, li)])
    		new_form = True
        return ((word1_lists[0][0], word2_lists[0][0]), new_form) 
    return (None, None)

def create_bigrams_dict(corpora, morfologik):
    n_n_bigrams = {}
    bigrams_forms = {}
    words_bigrams_freq = {}
    word1 = ''
    word2 = ''
    tokens = 0
    for line in corpora:
        tokens += 1
        word1, word2 = word2, word1 # swap words
        word2 = line.split("|")[0]
        if word1:
            #print (word1, word2)
            (base_words, new_form) = are_words_complement(word1, word2, morfologik, bigrams_forms)
            if base_words:
                if n_n_bigrams.get(base_words, ''):
                    n_n_bigrams[base_words] += 1
                else:
                    n_n_bigrams[base_words] = 1
                if new_form:
                    n_n_bigrams[base_words] *= float(BONUS_POS)
                if words_bigrams_freq.get(base_words[0], ''):
                    words_bigrams_freq[base_words[0]] += 1
                else:
                    words_bigrams_freq[base_words[0]] = 1
                if new_form:
                    words_bigrams_freq[base_words[0]] /= float(BONUS_NEG)
                if words_bigrams_freq.get(base_words[1], ''):
                    words_bigrams_freq[base_words[1]] = words_bigrams_freq[base_words[1]] + 1
                else:
                    words_bigrams_freq[base_words[1]] = 1
                if new_form:
                    words_bigrams_freq[base_words[1]] /= float(BONUS_NEG)                    
    return (n_n_bigrams, words_bigrams_freq, tokens)
    
def create_chi_table(no_bigrams, word1_freq, word2_freq, tokens):
    table = []
    table.append([])
    table.append([])
    table[0].append(no_bigrams)
    table[0].append(word2_freq - no_bigrams)
    table[1].append(word1_freq - no_bigrams)
    table[1].append(tokens - word1_freq - word2_freq + no_bigrams)
    return table
    
def compute_chi_coefficient(chi_table, no_bigrams):
    return ((float)(no_bigrams * (chi_table[0][0] * chi_table[1][1] - chi_table[0][1] * chi_table[1][0]) ** 2)) / ((chi_table[0][0] + chi_table[0][1]) * (chi_table[0][0] + chi_table[1][0]) * (chi_table[0][1] + chi_table[1][1]) * (chi_table[1][0] + chi_table[1][1]))

if __name__ == '__main__':
    corpora = open("korpus_utf8.txt", "rt")
    morfologik = {}
    f = open("morfologik.txt", "rt")
    for line in f:
        parts = line.split()
        u_word = parts[0].decode('iso-8859-2').encode('utf-8')
        if morfologik.get(u_word, ''):
            morfologik[u_word].append(parts[1:])
        else:
            morfologik[u_word] = [parts[1:]]
    f.close()
    n_n_bigrams, words_bigrams_freq, tokens = create_bigrams_dict(corpora, morfologik)
    corpora.close()
    no_bigrams = 0
    for key, value in n_n_bigrams.items():
        no_bigrams = no_bigrams + value
    collocations = []
    for key, value in n_n_bigrams.items():
        tab = create_chi_table(value, words_bigrams_freq[key[0]], words_bigrams_freq[key[1]], tokens)
        x = compute_chi_coefficient(tab, no_bigrams)
        if x >= CRITICAL:
            collocations.append((x, key))
    for col in sorted(collocations, reverse = True):
        print '*' * 70
        print col[1][0]
        print col[1][1]
        print '*' * 70
    print len(collocations)
