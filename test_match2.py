import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend", "agents"))
from vidhi_agent import smart_match
query = "my certificates have not been issued by my collage i want to file a case or complaint on my collage"
res = smart_match(query)
for r in res:
    print(f"Matched: {r['title']} | {r['act']}")
