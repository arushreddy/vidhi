import os, json, re

root = r"C:\Users\hp\Projects\VIDHI"

# ---------------------------------------------------------
# 1. ADD EMOTION / PRESSURE LAWS TO GRAPH
# ---------------------------------------------------------
laws_path = os.path.join(root, "backend", "graph", "vidhi_laws.json")
with open(laws_path, "r", encoding="utf-8") as f:
    laws = json.load(f)

new_laws = [
    {"id":"L020","act":"Indian Penal Code 1860","category":"Criminal","section":"Section 506","title":"Criminal Intimidation","description":"Whoever commits the offence of criminal intimidation (threatening someone with injury to person, reputation or property) shall be punished.","remedy":"File FIR for criminal intimidation. Seek police protection.","authority":"Police / Judicial Magistrate","penalty":"Imprisonment up to 2 years, or 7 years if threat is to cause death.","keywords":["threat", "blackmail", "pressure", "scared", "fear", "intimidation"]},
    {"id":"L021","act":"Mental Healthcare Act 2017","category":"Health","section":"Section 18","title":"Right to access mental healthcare","description":"Every person shall have a right to access mental healthcare and treatment.","remedy":"Approach nearest government hospital or dial mental health helpline.","authority":"State Mental Health Authority","penalty":"Government obligated to provide free treatment if BPL.","keywords":["depression", "suicide", "trauma", "crying", "mental health", "pressure", "stress"]}
]

existing_ids = [l["id"] for l in laws]
for nl in new_laws:
    if nl["id"] not in existing_ids:
        laws.append(nl)

with open(laws_path, "w", encoding="utf-8") as f:
    json.dump(laws, f, indent=2)


# ---------------------------------------------------------
# 2. INJECT PSYCH-ENGINE INTO THE AGENT CORE
# ---------------------------------------------------------
agent_path = os.path.join(root, "backend", "agents", "vidhi_agent.py")
with open(agent_path, "r", encoding="utf-8") as f:
    acode = f.read()

# Add detected_emotion to State
if "detected_emotion" not in acode:
    acode = acode.replace("agent_trace:     List[str]", "agent_trace:     List[str]\n    detected_emotion: str")

# Add the Emotion Analyzer Function
psych_engine = """
def analyze_emotion(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["suicide", "die", "kill", "hopeless"]): return "CRITICAL DISTRESS"
    if any(w in q for w in ["pressure", "scared", "fear", "terrified", "threat", "blackmail", "helpless", "afraid", "crying"]): return "HIGH STRESS / FEAR"
    if any(w in q for w in ["cheat", "fraud", "stole", "angry", "furious"]): return "ANGER / BETRAYAL"
    return "NEUTRAL"
"""
if "def analyze_emotion" not in acode:
    acode = acode.replace("def smart_match", psych_engine + "\ndef smart_match")

# Modify smart_match to use emotions
if "score = 0" in acode and "emotion =" not in acode:
    acode = acode.replace("scores = {}", "scores = {}\n    emotion = analyze_emotion(q)")
    acode = acode.replace("score = 0", "score = 0\n        if emotion == 'HIGH STRESS / FEAR' and data.get('id') in ['L012','L018','L019','L020','L021']: score += 10\n        if emotion == 'CRITICAL DISTRESS' and data.get('id') == 'L021': score += 15")

# Update node_graph_search to save emotion
acode = acode.replace('state["matched_laws"] = top', 'state["matched_laws"] = top\n    state["detected_emotion"] = analyze_emotion(state["user_query"])')
acode = acode.replace('"agent_trace": [],', '"agent_trace": [], "detected_emotion": "NEUTRAL",')

with open(agent_path, "w", encoding="utf-8") as f:
    f.write(acode)


# ---------------------------------------------------------
# 3. UPDATE FASTAPI WEBSOCKET TO TRANSMIT EMOTIONS
# ---------------------------------------------------------
main_path = os.path.join(root, "backend", "api", "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    mcode = f.read()

mcode = mcode.replace(
    '"data":{"laws":laws_found,"trace":state["agent_trace"]}})',
    '"data":{"laws":laws_found,"trace":state["agent_trace"],"emotion":state.get("detected_emotion", "NEUTRAL")}})'
)
with open(main_path, "w", encoding="utf-8") as f:
    f.write(mcode)


# ---------------------------------------------------------
# 4. UPGRADE UI TO DISPLAY PSYCH-ENGINE HUD
# ---------------------------------------------------------
html_path = os.path.join(root, "frontend", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

hud_ui = """if(m.node === 'graph_search') {
          let badge = '';
          if (m.data.emotion && m.data.emotion !== 'NEUTRAL') {
             let color = m.data.emotion === 'CRITICAL DISTRESS' ? '#ff4757' : (m.data.emotion.includes('FEAR') ? '#ffa502' : '#00f3ff');
             badge = `<div style="margin-bottom:15px; padding:10px 15px; background:rgba(0,0,0,0.4); border-left:4px solid ${color}; border-radius:6px; font-family:JetBrains Mono; font-size:11px; color:${color}; font-weight:bold; letter-spacing:0.5px;">> PSYCH-ENGINE DETECTED: ${m.data.emotion} <br>> Dynamically rerouting Knowledge Graph weights...</div>`;
          }
          document.getElementById(node.resId).innerHTML = badge + m.data.laws.map(l => 
            `<div class="law-item"><div class="law-title">${l.title}</div><div class="law-sec">SOURCE: ${l.act} // ${l.section}</div></div>`
          ).join('');
       }"""

html = re.sub(r"if\(m\.node === 'graph_search'\)\s*\{.*?\}\n\s*else if", hud_ui + "\n       else if", html, flags=re.DOTALL)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
