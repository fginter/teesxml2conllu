import xml.etree.ElementTree as ET
import sys
import collections


TokenInfo=collections.namedtuple("TokenInfo","id,form,POS,heads,deprels")

def get_id(s):
    """From something like bt_0 return 0"""
    return int(s.rsplit("_",1)[1])

def get_deps(ti):
    """Given token info, pick one head, one deprel, and stick rest to deps. Return head, deprel, deps"""
    all_deps=list(zip(ti.heads,ti.deprels))
    all_deps.sort(key=lambda h_deprel:(abs(ti.id-h_deprel[0]),h_deprel[1])) #sort by closest first, then alphabetically
    if not all_deps: #attach to root
        return -1,"root","_"
    head,deprel=all_deps[0]
    all_deps=all_deps[1:]
    all_deps.sort() #deps must be sorted by head by CoNLL-U spec
    if not all_deps:
        deps="_"
    else:
        deps="|".join("{}:{}".format(h+1,drel) for h,drel in all_deps)
    return head,deprel,deps

def doc2conllu(doc_elem):
    for sid,sent_elem in enumerate(doc_elem):
        # list of TokenInfo tuples
        tokens=[TokenInfo(id,token_elem.get("text"),token_elem.get("POS"),[],[]) for id,token_elem in enumerate(sent_elem.iterfind("analyses/tokenization/token"))]
        for dep_elem in sent_elem.iterfind("analyses/parse/dependency"):
               gov,dep,deprel=get_id(dep_elem.get("t1")),get_id(dep_elem.get("t2")),dep_elem.get("type")
               tokens[dep].heads.append(gov)
               tokens[dep].deprels.append(deprel)
        if tokens:
            #So now I should have all I need
            print("#pmid.sid {}.{}".format(doc_elem.get("origId"),sid))
            for tok in tokens:
                head,deprel,deps=get_deps(tok)
                print(tok.id+1,tok.form,"_",tok.POS,"_","_",head+1,deprel,deps,"_",sep="\t")
            print()
               
        
            

if __name__=="__main__":

    for (event,elem) in ET.iterparse(sys.stdin,["end"]):
        if elem.tag!="document":
            continue
        #We have a document tag done
        doc2conllu(elem)
        
        
