import sys, os
BACKEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, BACKEND)

import json, asyncio, random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="VIDHI Legal AI", version="5.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FRONTEND = os.path.join(BACKEND, "..", "frontend")

@app.get("/")
async def serve_ui():
    return FileResponse(os.path.join(FRONTEND, "index.html"))

async def send_thought(ws, node, text):
    await ws.send_json({"event":"thought","node":node,"text":text})

@app.websocket("/ws/analyze")
async def analyze_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        from agents.vidhi_agent import (
            node_graph_search, node_legal_analysis,
            node_notice_generator, node_win_scorer,
            node_case_precedent, node_strategic_advisor, node_geo_locator,
            node_war_room, node_adversary
        )
        data  = await websocket.receive_json()
        query = data.get("query", "")
        lang  = data.get("lang", "en")
        lat   = float(data.get("lat", 0.0))
        lng   = float(data.get("lng", 0.0))
        state = {
            "user_query": query, "lang": lang, "lat": lat, "lng": lng, "matched_laws": [],
            "legal_analysis": "", "legal_notice": "",
            "win_probability": 0.0, "next_steps": [],
            "authority": "", "agent_trace": [], "detected_emotion": "NEUTRAL",
            "case_precedents": [], "strategic_plan": "",
            "risk_assessment": "", "emergency_contacts": [],
            "geo_locations": [],
            "war_room_dialogue": [],
            "adversary_defenses": [],
        }

        # -- Agent 1: Graph Retriever --
        await websocket.send_json({"event":"node_start","node":"graph_search","msg":"Traversing 38-node Legal Knowledge Graph..."})
        await send_thought(websocket, "graph_search", "Embedding query into vector space...")
        await asyncio.sleep(0.05)
        await send_thought(websocket, "graph_search", "Searching 38 knowledge nodes...")
        state = await asyncio.to_thread(node_graph_search, state)
        laws_found = [{"act":l.get("act",""),"section":l.get("section",""),"title":l.get("title","")} for l in state["matched_laws"]]
        await websocket.send_json({"event":"node_done","node":"graph_search",
            "msg":f"Found {len(state['matched_laws'])} matching provisions",
            "data":{"laws":laws_found,"trace":state["agent_trace"],"emotion":state.get("detected_emotion","NEUTRAL")}})
        await asyncio.sleep(0.05)

        # -- Agent Collaboration War Room Debate --
        state = await asyncio.to_thread(node_war_room, state)
        # Send the debate list over WS
        await websocket.send_json({"event":"war_room_debate","dialogue":state["war_room_dialogue"]})
        # Wait 4 seconds total to let the UI display the chat messages sequentially
        await asyncio.sleep(4.0)

        # -- Agents 2 & 3: Legal Reasoner + Notice Drafter (PARALLEL) --
        await websocket.send_json({"event":"node_start","node":"legal_analysis","msg":"AI analyzing legal rights..."})
        await send_thought(websocket, "legal_analysis", "Loading constitutional framework...")
        await websocket.send_json({"event":"node_start","node":"notice_generator","msg":"Drafting formal legal notice..."})
        await send_thought(websocket, "notice_generator", "Structuring formal notice...")

        task_analysis = asyncio.to_thread(node_legal_analysis, dict(state))
        task_notice = asyncio.to_thread(node_notice_generator, dict(state))

        state_analysis, state_notice = await asyncio.gather(task_analysis, task_notice)

        state["legal_analysis"] = state_analysis["legal_analysis"]
        await websocket.send_json({"event":"node_done","node":"legal_analysis",
            "msg":"Legal analysis complete","data":{"analysis":state["legal_analysis"]}})

        state["legal_notice"] = state_notice["legal_notice"]
        state["authority"] = state_notice.get("authority", "")
        await websocket.send_json({"event":"node_done","node":"notice_generator",
            "msg":"Legal notice drafted",
            "data":{"notice":state["legal_notice"],"authority":state["authority"],
                    "act":state["matched_laws"][0].get("act","") if state["matched_laws"] else "",
                    "section":state["matched_laws"][0].get("section","") if state["matched_laws"] else ""}})
        await asyncio.sleep(0.05)

        # -- Agent 4: Monte Carlo --
        await websocket.send_json({"event":"node_start","node":"win_scorer","msg":"Running 100 Monte Carlo simulations..."})
        await send_thought(websocket, "win_scorer", "Initializing Monte Carlo engine...")
        state = asyncio.to_thread(node_win_scorer, dict(state))
        state = await state
        trials = state.get("monte_carlo_trials", [])
        for i, trial_text in enumerate(trials, 1):
            await websocket.send_json({"event":"monte_carlo_trial","trial":i,"text":trial_text})
            await asyncio.sleep(0.005) # Super fast scrolling effect
            
        await websocket.send_json({"event":"node_done","node":"win_scorer",
            "msg":f"Win probability: {state['win_probability']}%",
            "data":{"win_prob":state["win_probability"],"next_steps":state["next_steps"]}})
        await asyncio.sleep(0.05)

        # -- Agents 5, 6 & 7: Precedent, Strategy + GeoLocator (PARALLEL) --
        await websocket.send_json({"event":"node_start","node":"case_precedent","msg":"Searching case law database..."})
        await send_thought(websocket, "case_precedent", "Matching precedent patterns...")
        await websocket.send_json({"event":"node_start","node":"strategic_advisor","msg":"Computing optimal legal strategy..."})
        await send_thought(websocket, "strategic_advisor", "Synthesizing all agent outputs...")
        await websocket.send_json({"event":"node_start","node":"geo_locator","msg":"Locating nearby service centers..."})
        await send_thought(websocket, "geo_locator", "Acquiring live GPS coordinates...")

        task_precedent = asyncio.to_thread(node_case_precedent, dict(state))
        task_strategy = asyncio.to_thread(node_strategic_advisor, dict(state))
        task_geo = asyncio.to_thread(node_geo_locator, dict(state))

        state_prec, state_strat, state_geo = await asyncio.gather(task_precedent, task_strategy, task_geo)

        state["case_precedents"] = state_prec["case_precedents"]
        await websocket.send_json({"event":"node_done","node":"case_precedent",
            "msg":f"Found {len(state['case_precedents'])} precedents",
            "data":{"precedents":state["case_precedents"]}})

        state["strategic_plan"] = state_strat["strategic_plan"]
        state["risk_assessment"] = state_strat["risk_assessment"]
        state["emergency_contacts"] = state_strat["emergency_contacts"]
        await websocket.send_json({"event":"node_done","node":"strategic_advisor",
            "msg":"Strategy complete",
            "data":{"plan":state["strategic_plan"],"risk":state["risk_assessment"],"contacts":state["emergency_contacts"]}})

        state["geo_locations"] = state_geo["geo_locations"]
        await websocket.send_json({"event":"node_done","node":"geo_locator",
            "msg":"Locations found",
            "data":{"locations":state["geo_locations"]}})
        await asyncio.sleep(0.05)

        # -- Agent 8: Adversary Emulator --
        await websocket.send_json({"event":"node_start","node":"adversary","msg":"Simulating opponent defense strategy..."})
        await send_thought(websocket, "adversary", "Compiling opponent arguments...")
        state = await asyncio.to_thread(node_adversary, state)
        await websocket.send_json({"event":"node_done","node":"adversary",
            "msg":"Opponent defenses predicted",
            "data":{"defenses":state["adversary_defenses"]}})

        # -- Complete --
        await websocket.send_json({"event":"complete","state":{
            "win_probability": state["win_probability"],
            "next_steps": state["next_steps"],
            "legal_notice": state["legal_notice"],
            "legal_analysis": state["legal_analysis"],
            "authority": state["authority"],
            "matched_laws": state["matched_laws"],
            "case_precedents": state["case_precedents"],
            "strategic_plan": state["strategic_plan"],
            "geo_locations": state["geo_locations"],
            "adversary_defenses": state["adversary_defenses"],
        }})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try: await websocket.send_json({"event":"error","msg":str(e)})
        except: pass

class PDFRequest(BaseModel):
    citizen_name: str = "Complainant"
    opponent_name: str = "Respondent"
    opponent_addr: str = "Address of Respondent"
    situation: str = ""
    notice_text: str = ""
    act: str = "Indian Law"
    section: str = ""
    authority: str = "Appropriate Court"
    win_prob: float = 75.0

@app.post("/generate-pdf")
async def generate_pdf(req: PDFRequest):
    from pdf_engine.pdf_generator import generate_notice_pdf
    path = generate_notice_pdf(
        citizen_name=req.citizen_name, opponent_name=req.opponent_name,
        opponent_addr=req.opponent_addr, situation=req.situation,
        notice_text=req.notice_text, act=req.act, section=req.section,
        authority=req.authority, win_prob=req.win_prob,
    )
    return FileResponse(path, media_type="application/pdf",
        filename=os.path.basename(path),
        headers={"Content-Disposition":f"attachment; filename={os.path.basename(path)}"})
