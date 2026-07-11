import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend", "agents"))
from vidhi_agent import smart_match, G, SYNONYMS

q = "my certificates have not been issued by my collage i want to file a case or complaint on my collage".lower()
stopwords = {'i','am','me','my','is','are','a','an','the','by','to','in','of','for','on','with','and','or','was','were','been','being'}
words = [w for w in q.split() if w not in stopwords and len(w) > 1]
print("Words:", words)

for node_id, data in G.nodes(data=True):
    if data.get("type") != "Law": continue
    kws  = [k.lower() for k in data.get("keywords", [])]
    title = data.get("title", "").lower()
    desc  = data.get("description", "").lower()
    cat   = data.get("category", "").lower()
    score = 0
    reasons = []

    for w in words:
        if any(w in k for k in kws): 
            score += 3
            reasons.append(f"Word '{w}' in keywords {kws}")
        if w in title:
            score += 2
            reasons.append(f"Word '{w}' in title '{title}'")
        if w in desc:
            score += 1
            reasons.append(f"Word '{w}' in desc '{desc}'")

    for group_key, synonyms in SYNONYMS.items():
        if any(s in q for s in synonyms):
            if any(s in " ".join(kws) for s in synonyms): 
                score += 4
                reasons.append(f"Synonym group '{group_key}' matches query & keywords")
            if group_key in cat:
                score += 3
                reasons.append(f"Synonym group '{group_key}' matches category '{cat}'")

    for kw in kws:
        if kw in q: 
            score += 5
            reasons.append(f"Full phrase '{kw}' in query")

    if score > 0:
        print(f"\n{data['title']} (Score: {score})")
        for r in reasons: print("  -", r)
