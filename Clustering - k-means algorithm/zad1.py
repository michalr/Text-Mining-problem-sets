# -*- encoding: utf-8 -*-

from progressbar import Percentage, Bar, RotatingMarker, ETA, FileTransferSpeed, ProgressBar
import marshal

def split_line(line):
    sentences = []
    sent = line.split(".")
    for s in sent:
        if s:
            tmp = s.split(",")
            for t in tmp:
                if t:
                    sentences.append(t)
    return sentences
    
def can_be_noun(word, morfo):
    intepretations = []
    if not morfo.get(word, ''):
        return intepretations
    for info in morfo[word]:
        base = info[0]
        props = info[1].split(":") 
        if props[0] == 'subst':
            try:
                i = 0
                while props[i + 1] not in ["sg", "pl"]:
                    i += 1
                intepretations.append((base, props[i + 1], props[i + 2], props[i + 3]))
            except IndexError:
                pass
    return intepretations
    
def can_be_adj(word, morfo):
    intepretations = []
    if not morfo.get(word, '') or word.istitle():
        return intepretations
    for info in morfo[word]:
        base = info[0]
        props = info[1].split(":")
        if props[0] == 'adj':
            try:
                i = 0
                while props[i + 1] not in ["sg", "pl"]:
                    i += 1
                intepretations.append((base, props[i + 1], props[i + 2], props[i + 3]))
            except IndexError:
                pass
    return intepretations

def can_be_verb(word, morfo):
    intepretations = []
    if not morfo.get(word, '') or word.istitle():
        return intepretations
    for info in morfo[word]:
        base = info[0]
        props = info[1].split(":")
        if props[0] == 'verb':
            try:
                i = 0
                while props[i + 1] not in ["sg", "pl"]:
                    i += 1
                intepretations.append((base, props[i + 1], props[i + 2], props[i + 3]))
            except IndexError:
                pass
    return intepretations
    
def get_stats(article, zgoda, orzeczenie, biernik, posiada, jest_posiadany, morfo):
    for sent in article:
        words = sent.split()
        for word in words:
            props = can_be_noun(word, morfo)
            if not props:
                props =  can_be_noun(word.lower(), morfo)
            if props:
                candidate = word
                for word in words:
                    if word != candidate and word != candidate.lower():
                        adj = can_be_adj(word, morfo)
                        if not adj:
                            adj = can_be_adj(word.lower(), morfo)
                        if adj:
                            common = []
                            for i in range(len(props)):
                                for j in range(len(adj)):
                                    if props[i][1] == adj[j][1]:
                                        common.append((i, j)) 
                            if common:
                               common2 = [p for p in common if set(props[p[0]][2].split(".")) & set(adj[p[1]][2].split("."))]   
                               if common2:
                                   common3 = [p for p in common2 if set(props[p[0]][3].split(".")) & set(adj[p[1]][3].split("."))]   
                                   if common3:
                                       for p in common3:
                                           if zgoda.get(props[p[0]][0], ""):
                                               if zgoda[props[p[0]][0]].get(adj[p[1]][0], ""):
                                                   zgoda[props[p[0]][0]][adj[p[1]][0]] += 1
                                               else:
                                                   zgoda[props[p[0]][0]][adj[p[1]][0]] = 1
                                           else:
                                               zgoda[props[p[0]][0]] = {}
                                               zgoda[props[p[0]][0]][adj[p[1]][0]] = 1
                        verb = can_be_verb(word, morfo)
                        if not verb:
                            verb = can_be_verb(word.lower(), morfo)
                        if verb:
                            props2 = [prop for prop in props if 'nom' in prop[2].split(".")]
                            verb2 = [prop for prop in verb if 'ter' in prop[2].split(".")]
                            common = []
                            for i in range(len(props2)):
                                for j in range(len(verb2)):
                                    if props2[i][1] == verb2[j][1]:
                                        common.append((i, j))
                            for p in common:
                                if orzeczenie.get(props2[p[0]][0], ""):
                                    if orzeczenie[props2[p[0]][0]].get(verb2[p[1]][0], ""):
                                        orzeczenie[props2[p[0]][0]][verb2[p[1]][0]] += 1
                                    else:
                                        orzeczenie[props2[p[0]][0]][verb2[p[1]][0]] = 1
                                else:
                                    orzeczenie[props2[p[0]][0]] = {}
                                    orzeczenie[props2[p[0]][0]][verb2[p[1]][0]] = 1
                            props3 = [prop for prop in props if 'acc' in prop[2].split(".")]
                            common = []
                            for i in range(len(props3)):
                                for j in range(len(verb)):
                                    common.append((i, j))
                            for p in common:
                                if biernik.get(props3[p[0]][0], ""):
                                    if biernik[props3[p[0]][0]].get(verb[p[1]][0], ""):
                                        biernik[props3[p[0]][0]][verb[p[1]][0]] += 1
                                    else:
                                        biernik[props3[p[0]][0]][verb[p[1]][0]] = 1
                                else:
                                    biernik[props3[p[0]][0]] = {}
                                    biernik[props3[p[0]][0]][verb[p[1]][0]] = 1
                        noun = can_be_noun(word, morfo)
                        if not noun:
                            noun = can_be_noun(word.lower(), morfo)
                        if noun:
                            props = [prop for prop in props if 'nom' in prop[2].split(".")]
                            noun = [prop for prop in props if 'gen' in prop[2].split(".")]
                            common = []
                            for i in range(len(props)):
                                for j in range(len(noun)):
                                    common.append((i, j))
                            for p in common:
                                if posiada.get(props[p[0]][0], ""):
                                    if posiada[props[p[0]][0]].get(noun[p[1]][0], ""):
                                        posiada[props[p[0]][0]][noun[p[1]][0]] += 1
                                    else:
                                        posiada[props[p[0]][0]][noun[p[1]][0]] = 1
                                else:
                                    posiada[props[p[0]][0]] = {}
                                    posiada[props[p[0]][0]][noun[p[1]][0]] = 1
                                if jest_posiadany.get(props[p[0]][0], ""):
                                    if jest_posiadany[props[p[0]][0]].get(noun[p[1]][0], ""):
                                        jest_posiadany[props[p[0]][0]][noun[p[1]][0]] += 1
                                    else:
                                        jest_posiadany[props[p[0]][0]][noun[p[1]][0]] = 1
                                else:
                                    jest_posiadany[props[p[0]][0]] = {}
                                    jest_posiadany[props[p[0]][0]][noun[p[1]][0]] = 1
                                
MAX_ON_LIST = 10                            
                                       
if __name__ == "__main__":
    morfo = {}
    f = open("morfologik.txt", "rt")
    widgets = ['Parsing Morfologik: ', Percentage(), ' ', 
               Bar(marker=RotatingMarker()), ' ', ETA(), 
               ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=3662366).start()
    i = 0
    for line in f:
        l = line.split("\t")
        l[-1] = l[-1].rstrip("\n")
        l[0] = l[0].decode('iso-8859-2').encode('utf-8')
        l[1] = l[1].decode('iso-8859-2').encode('utf-8')
        if morfo.get(l[0], ""):
            morfo[l[0]].append(l[1:])
        else:
            morfo[l[0]] = [l[1:]]
        i += 1
        pbar.update(i)
    pbar.finish()
    f.close()
    f = open("wikipedia_dla_wyszukiwarek.txt", "rt")
    article = ""
    widgets[0] = "Parsing Articles: "
    pbar = ProgressBar(widgets=widgets, maxval=811205).start()
    i = 0
    zgoda = {}
    orzeczenie = {}
    biernik = {}
    posiada = {}
    jest_posiadany = {}        
    for line in f:
        if line.startswith("##TITLE##"):
            if article:
                get_stats(article, zgoda, orzeczenie, biernik, posiada, jest_posiadany, morfo)
                i += 1
                pbar.update(i)
            article = split_line(line.lstrip("##TITLE##").strip())
        else:
            article.extend(split_line(line.strip()))
    pbar.finish()
    f.close()
    print "Dumping resulting dictionaries"
    marshal.dump(zgoda, open("zgoda.msl", "wb"))
    marshal.dump(orzeczenie, open("orzeczenie.msl", "wb"))
    marshal.dump(biernik, open("biernik.msl", "wb"))
    marshal.dump(posiada, open("posiada.msl", "wb"))
    marshal.dump(jest_posiadany, open("jest_posiadany.msl", "wb"))
    """
    zgoda = marshal.load(open("zgoda.msl", "rb"))
    orzeczenie = marshal.load(open("orzeczenie.msl", "rb"))
    biernik = marshal.load(open("biernik.msl", "rb"))
    posiada = marshal.load(open("posiada.msl", "rb"))
    jest_posiadany = marshal.load(open("jest_posiadany.msl", "rb"))
    """
    print "Creating res file"
    all_nouns = set(zgoda.keys()) | set(orzeczenie.keys()) | set(biernik.keys()) | set(posiada.keys()) | set(jest_posiadany.keys())
    f = open("res", "wt")
    for noun in sorted(all_nouns):
        f.write("RZECZOWNIK: %s\n" % noun)
        f.write("\tPRZYMIOTNIKI:")
        try:
            top = sorted(zgoda[noun].items(), key=lambda(k,v):(v,k), reverse = True)[:MAX_ON_LIST]
            for word in top:
                f.write(" %s (%d)" % (word[0], word[1]))
        except KeyError:
            pass
        f.write("\n")
        f.write("\tORZECZENIE:")
        try:
            top = sorted(orzeczenie[noun].items(), key=lambda(k,v):(v,k), reverse = True)[:MAX_ON_LIST]
            for word in top:
                f.write(" %s (%d)" % (word[0], word[1]))
        except KeyError:
            pass
        f.write("\n")
        f.write("\tDOPEŁNIENIE BIERNIK:")
        try:
            top = sorted(biernik[noun].items(), key=lambda(k,v):(v,k), reverse = True)[:MAX_ON_LIST]
            for word in top:
                f.write(" %s (%d)" % (word[0], word[1]))
        except KeyError:
            pass
        f.write("\n")
        f.write("\tPOSIADA:")
        try:
            top = sorted(posiada[noun].items(), key=lambda(k,v):(v,k), reverse = True)[:MAX_ON_LIST]
            for word in top:
                f.write(" %s (%d)" % (word[0], word[1]))
        except KeyError:
            pass
        f.write("\n")
        f.write("\tJEST_POSIADANY:")
        try:
            top = sorted(jest_posiadany[noun].items(), key=lambda(k,v):(v,k), reverse = True)[:MAX_ON_LIST]
            for word in top:
                f.write(" %s (%d)" % (word[0], word[1]))
        except KeyError:
            pass
        f.write("\n")
        f.write("\n")
    f.close()
        
    
            
