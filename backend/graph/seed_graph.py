"""
VIDHI — Sovereign Legal Knowledge Graph (NetworkX Local)
Builds and saves the full Indian law graph to disk.
"""
import json, pickle, os, sys
import networkx as nx
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

LAWS = [
    {"id":"L001","act":"Payment of Wages Act 1936","category":"Labour","section":"Section 3","title":"Responsibility for payment of wages","description":"Every employer is responsible for payment of wages to persons employed by them.","remedy":"File complaint before Payment of Wages Authority","authority":"Labour Commissioner","penalty":"Fine up to Rs 7,500 and imprisonment up to 1 year","keywords":["wages","salary","payment","employer","worker","daily wage"]},
    {"id":"L002","act":"Payment of Wages Act 1936","category":"Labour","section":"Section 4","title":"Fixation of wage periods","description":"No wage period shall exceed one month. Wages must be paid within 7 days of end of wage period.","remedy":"Claim delayed wages with compensation before Labour Court","authority":"Labour Commissioner / Labour Court","penalty":"Fine up to Rs 7,500 per instance of delay","keywords":["delayed salary","monthly wages","unpaid salary","employer delay"]},
    {"id":"L003","act":"Minimum Wages Act 1948","category":"Labour","section":"Section 12","title":"Payment of minimum rates of wages","description":"An employer must pay every employee not less than the minimum rate of wages fixed by the government.","remedy":"File claim before Minimum Wages Authority for difference + 10x penalty","authority":"Labour Commissioner / Minimum Wages Authority","penalty":"Imprisonment up to 6 months OR fine up to Rs 500 OR both","keywords":["minimum wage","underpayment","low salary","below minimum","labour rights"]},
    {"id":"L004","act":"Code on Wages 2019","category":"Labour","section":"Section 9","title":"Prohibition of deductions from wages","description":"No deduction shall be made from wages except those authorized under this Code.","remedy":"File application before Appellate Authority for restoration of deducted wages","authority":"Appellate Authority under Code on Wages","penalty":"Fine up to Rs 50,000 for first offence; Rs 1,00,000 for repeat","keywords":["wage deduction","salary cut","illegal deduction","bonus","overtime"]},
    {"id":"L005","act":"Mahatma Gandhi NREGA 2005","category":"Labour","section":"Schedule II","title":"Right to work and unemployment allowance","description":"Every adult member of rural household entitled to 100 days guaranteed wage employment per year.","remedy":"File complaint at Block Programme Officer; claim unemployment allowance if work denied","authority":"Block Programme Officer / District Programme Coordinator","penalty":"Unemployment allowance payable by State Government","keywords":["MGNREGA","NREGA","job card","rural employment","100 days work","unemployment"]},
    {"id":"L006","act":"Transfer of Property Act 1882","category":"Tenant","section":"Section 108(q)","title":"Tenant right to recover security deposit","description":"Tenant is entitled to recovery of security deposit at end of tenancy if property returned in good condition.","remedy":"Send legal notice; file suit in Civil Court for recovery with interest","authority":"Civil Court / Rent Control Tribunal","penalty":"Landlord liable to return deposit with 12% interest per annum","keywords":["security deposit","deposit refund","landlord","tenant","rent","eviction"]},
    {"id":"L007","act":"Model Tenancy Act 2021","category":"Tenant","section":"Section 21","title":"Landlord cannot cut essential services","description":"Landlord shall not withhold essential services like water, electricity to force eviction.","remedy":"Approach Rent Authority for immediate restoration of services + compensation","authority":"Rent Authority / District Collector","penalty":"Fine up to Rs 10,000 per day of deprivation","keywords":["water cut","electricity cut","landlord harassment","illegal eviction","services"]},
    {"id":"L008","act":"Rent Control Act","category":"Tenant","section":"Section 14","title":"Protection against illegal eviction","description":"Tenant cannot be evicted except through Court order. Self-help eviction by landlord is illegal.","remedy":"File FIR under IPC 441; apply for injunction in Civil Court","authority":"Civil Court / Rent Controller","penalty":"Landlord liable for criminal trespass + damages","keywords":["illegal eviction","forced eviction","lock change","thrown out","landlord eviction"]},
    {"id":"L009","act":"Consumer Protection Act 2019","category":"Consumer","section":"Section 2(7)","title":"Right to Consumer Redress","description":"Any person who buys goods/services for personal use is a consumer with right to file complaint.","remedy":"File complaint in District Consumer Disputes Redressal Commission (free up to Rs 50 lakh)","authority":"District Consumer Commission","penalty":"Refund + compensation + punitive damages up to Rs 10 lakh","keywords":["consumer","cheating","defective product","fraud","refund","service deficiency"]},
    {"id":"L010","act":"Consumer Protection Act 2019","category":"Consumer","section":"Section 19","title":"Product Liability","description":"Manufacturer/seller liable for harm caused by defective product or deficient service.","remedy":"File product liability complaint; claim compensation for injury/loss","authority":"District Consumer Commission","penalty":"Compensation commensurate with damage suffered","keywords":["product defect","bad product","damaged goods","online shopping","e-commerce fraud"]},
    {"id":"L011","act":"Sexual Harassment of Women at Workplace Act 2013","category":"Women Protection","section":"Section 4","title":"Internal Complaints Committee","description":"Every workplace with 10+ employees must have an ICC for harassment complaints.","remedy":"File written complaint to ICC within 3 months of incident","authority":"Internal Complaints Committee / Local Complaints Committee","penalty":"Fine up to Rs 50,000; cancellation of business license for repeat offence","keywords":["workplace harassment","sexual harassment","POSH","ICC","women rights","office harassment"]},
    {"id":"L012","act":"Protection of Women from Domestic Violence Act 2005","category":"Women Protection","section":"Section 12","title":"Application for protection order","description":"Aggrieved woman can file application before Magistrate for protection, residence, and monetary relief.","remedy":"Approach Protection Officer / Magistrate Court for emergency protection order","authority":"Judicial Magistrate / Protection Officer","penalty":"Breach of protection order punishable with 1 year jail or Rs 20,000 fine","keywords":["domestic violence","abuse","husband","in-laws","protection order","DV Act"]},
    {"id":"L013","act":"Agricultural Produce Market Committee Act","category":"Farmer","section":"Section 26","title":"Prohibition of unauthorized deduction by traders","description":"No trader can make unauthorized deductions from payment due to farmer for produce sold.","remedy":"File complaint with APMC Market Committee; claim recovery of deducted amount","authority":"APMC Market Committee / Agricultural Marketing Board","penalty":"Cancellation of trader license + recovery of amount","keywords":["farmer","crop","trader","cheating","produce","mandi","agricultural fraud"]},
    {"id":"L014","act":"Indian Penal Code 1860","category":"Criminal","section":"Section 406","title":"Criminal breach of trust","description":"Whoever is entrusted with property and dishonestly misappropriates it commits criminal breach of trust.","remedy":"File FIR at police station; complaint before Magistrate under CrPC 190","authority":"Police / Judicial Magistrate","penalty":"Imprisonment up to 3 years + fine","keywords":["breach of trust","money taken","stolen","misappropriation","fraud","cheating"]},
    {"id":"L015","act":"Indian Penal Code 1860","category":"Criminal","section":"Section 420","title":"Cheating and fraud","description":"Whoever cheats and thereby dishonestly induces the person deceived to deliver property is liable.","remedy":"File FIR at police station; attach evidence of deception and loss","authority":"Police / Magistrate Court","penalty":"Imprisonment up to 7 years + fine","keywords":["cheating","fraud","scam","deceived","money fraud","online fraud","property fraud"]},
    {"id":"L016","act":"Bharatiya Nyaya Sanhita 2023","category":"Criminal","section":"Section 316","title":"Cheating under new criminal code","description":"Under BNS 2023, cheating and fraud offences covered under Section 316 with enhanced penalties.","remedy":"File FIR citing BNS 2023 Section 316; provide documentary evidence","authority":"Police / Judicial Magistrate","penalty":"Imprisonment up to 7 years + fine","keywords":["BNS","cheating","fraud","new law 2024","Bharatiya Nyaya Sanhita"]},
    {"id":"L017","act":"Right to Information Act 2005","category":"Governance","section":"Section 6","title":"Right to request government information","description":"Any citizen can request information from any public authority within 30 days response time.","remedy":"File RTI application online at rtionline.gov.in or in person; free for BPL card holders","authority":"Public Information Officer / Central/State Information Commission","penalty":"Rs 250/day penalty on PIO for delay, up to Rs 25,000 total","keywords":["RTI","government information","transparency","public records","corruption"]},
    {"id":"L018","act":"Bharatiya Nyaya Sanhita 2023","category":"Criminal","section":"Section 74","title":"Assault or criminal force to woman with intent to outrage her modesty","description":"Whoever assaults or uses criminal force to any woman, intending to outrage her modesty, commits a serious criminal offence.","remedy":"Dial 112 immediately. File a police FIR under BNS Sec 74 (formerly IPC Sec 354).","authority":"Police / Judicial Magistrate","penalty":"Imprisonment of 1 to 5 years, and fine.","keywords":["sexual harassment","outrage modesty","assault","molestation","neighbour","stranger","stalking"]},
    {"id":"L019","act":"Indian Penal Code 1860","category":"Criminal","section":"Section 354D","title":"Stalking","description":"Any man who follows a woman and contacts her repeatedly despite her disinterest commits the offence of stalking.","remedy":"File FIR at nearest police station or via National Cyber Crime portal.","authority":"Police / Women Cell","penalty":"Imprisonment up to 3 years for first conviction + fine.","keywords":["stalking","following","harassment","neighbour","repeated messages"]}
]

RELATIONSHIPS = [
    ("Payment of Wages Act 1936",  "Code on Wages 2019",                                    "SUPERSEDED_BY"),
    ("Indian Penal Code 1860",     "Bharatiya Nyaya Sanhita 2023",                          "SUPERSEDED_BY"),
    ("Payment of Wages Act 1936",  "Minimum Wages Act 1948",                                "COMPLEMENTS"),
    ("Consumer Protection Act 2019","Indian Penal Code 1860",                               "COMPLEMENTS"),
    ("Sexual Harassment of Women at Workplace Act 2013","Protection of Women from Domestic Violence Act 2005","COMPLEMENTS"),
    ("Transfer of Property Act 1882","Model Tenancy Act 2021",                              "AMENDED_BY"),
    ("Mahatma Gandhi NREGA 2005",  "Minimum Wages Act 1948",                                "COMPLEMENTS"),
]

def build_graph():
    G = nx.DiGraph()

    # Add category, act, and law nodes
    for law in track(LAWS, description="[cyan]Building legal knowledge graph...[/cyan]"):
        cat_id  = f"CAT:{law['category']}"
        act_id  = f"ACT:{law['act']}"
        law_id  = law["id"]

        G.add_node(cat_id,  type="Category", name=law["category"])
        G.add_node(act_id,  type="Act",      name=law["act"], category=law["category"])
        G.add_node(law_id,  type="Law",      **law)

        G.add_edge(cat_id, act_id, relation="CONTAINS")
        G.add_edge(act_id, law_id, relation="HAS_SECTION")

    # Add act-to-act relationships
    for src_act, dst_act, rel in RELATIONSHIPS:
        G.add_edge(f"ACT:{src_act}", f"ACT:{dst_act}", relation=rel)

    return G

def search_graph(G, query: str):
    """Keyword search across law nodes."""
    query_words = query.lower().split()
    matches = []
    for node_id, data in G.nodes(data=True):
        if data.get("type") != "Law":
            continue
        kws = [k.lower() for k in data.get("keywords", [])]
        title = data.get("title","").lower()
        desc  = data.get("description","").lower()
        score = sum(1 for w in query_words if any(w in k for k in kws) or w in title or w in desc)
        if score > 0:
            matches.append((score, data))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:3]]

if __name__ == "__main__":
    console.print("\n[bold magenta]⚡ VIDHI — Sovereign Legal Knowledge Graph (Local)[/bold magenta]\n")

    G = build_graph()

    # Save graph to disk
    out_dir = os.path.join(os.path.dirname(__file__))
    graph_path = os.path.join(out_dir, "vidhi_graph.pkl")
    laws_path  = os.path.join(out_dir, "vidhi_laws.json")

    with open(graph_path, "wb") as f:
        pickle.dump(G, f)
    with open(laws_path, "w", encoding="utf-8") as f:
        json.dump(LAWS, f, indent=2, ensure_ascii=False)

    # Stats table
    table = Table(title="Graph Statistics", style="cyan")
    table.add_column("Metric",  style="bold white")
    table.add_column("Value",   style="bold green")
    table.add_row("Total Nodes",      str(G.number_of_nodes()))
    table.add_row("Total Edges",      str(G.number_of_edges()))
    table.add_row("Law Provisions",   str(len(LAWS)))
    table.add_row("Act Relationships",str(len(RELATIONSHIPS)))
    table.add_row("Graph File",       graph_path)
    console.print(table)

    # Live demo search
    console.print("\n[bold yellow]🔍 Demo Search: 'employer not paying salary'[/bold yellow]")
    results = search_graph(G, "employer not paying salary")
    for r in results:
        console.print(f"  ✅ [green]{r['act']} — {r['section']}[/green]: {r['title']}")
        console.print(f"     Remedy: [cyan]{r['remedy']}[/cyan]\n")

    console.print("[bold green]✅ Graph seeded and saved successfully![/bold green]")
    console.print("[bold cyan]   Next: Reply 'Done' for STEP 3 — AI Agent Core[/bold cyan]\n")

