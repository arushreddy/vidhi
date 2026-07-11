import json
from difflib import SequenceMatcher

def similar(a, b):
    if not a or not b: return 0
    return SequenceMatcher(None, a, b).ratio()

with open('backend/graph/vidhi_laws.json', 'r', encoding='utf-8') as f:
    laws = json.load(f)

query = "my certificates have not been issued by my collage i want to file a case or complaint on my collage"
stopwords = {'i','am','me','my','is','are','a','an','the','by','to','in','of','for','on','with','and','or','was','were','been','being', 'this', 'that'}
words = [w for w in query.split() if w not in stopwords and len(w) > 2]
print(f"Words: {words}")

SYNONYMS = {
    "harass": ["harass","harras","harrased","harassed","harrassing","harassing","abuse","assault","threat","violence","bully","misbehave","stalk","molest","sexual","sexually"],
    "fraud": ["fraud","cheat","scam","deceive","fake","bogus","stolen"],
    "neighbor": ["neighbor","neighbour","neighour","society","resident","local","tenant","adjacent"],
    "consumer": ["buy","bought","purchase","product","refund","defect","online","amazon","flipkart"],
    "salary": ["salary","wage","wages","pay","money","income","job","work","hr"],
    "domestic": ["husband","wife","spouse","domestic","family","home","abuse","violence"]
}

for law in laws:
    score = 0
    kws = [k.lower() for k in law.get('keywords',[])]
    title = law.get('title','').lower()
    desc = law.get('description','').lower()
    cat = law.get('category','').lower()
    
    for w in words:
        for k in kws:
            if w in k or k in w or similar(w, k) > 0.8:
                score += 3
        if w in title or similar(w, title) > 0.8: score += 2
        if w in desc: score += 1
        if w in cat or similar(w, cat) > 0.8: score += 4
        
    for group_key, synonyms in SYNONYMS.items():
        for s in synonyms:
            if s in query.lower() or any(similar(w, s) > 0.85 for w in words):
                if any(s in kw for kw in kws): score += 3
                if group_key in cat: score += 5
                if s in title: score += 2
                
    if score > 0:
        print(f"ID: {law['id']} | Act: {law['act']} | Score: {score}")
