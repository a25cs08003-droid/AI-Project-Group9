#!/usr/bin/env python3


import json
import os
import sys
import graphviz
import networkx as nx
import matplotlib.pyplot as plt


P_flood=0.55
P_infra=0.8

init_state = {
    "action": ("start"),
    "effects": {
        ("forecast_heavy_rain", lambda P_flood: P_flood >= 0.5),
        ("flood_not_occurred", lambda P_flood: P_flood < 0.5),
        ("flood_risk_high", lambda P_flood: P_flood >= 0.5),
        ("roads_open", lambda P_flood: P_flood >= 0.5),
        ("bridges_weak", lambda P_infra: P_infra >= 0.5),
        ("boats_available", True),
        ("rescue_team_ready", True),
        ("medical_supplies_available", True),
        ("dry_areas_available", True),
        ("technicians_available", True),
        ("communication_main_up", True),
        ("backup_comm_available", True),
        ("food_supplies_stocked", True),
        ("community_alerted", False),
        ("evacuation_started", False),
        ("medical_kits_stocked", False),
        ("rescue_team_predeployed", False),
        ("routes_shifted", False)
    }
}
goal_state1 = {
    "action": ("rescue_team_work_done"),
    "effects": {
        ("people_safe", True),
        ("rescue_team_predeployed", True),
        ("rapid_response_prepared", True)
    }
}
goal_state2 = {
    "action": ("communication_team_work_done"),
    "effects": {
        ("communication_backup_operational", True),
        ("routes_shifted", True)
    }
}
goal_state3 = {
    "action": ("medical_and_supplies_work_done"),
    "effects": {
        ("medical_kits_stocked", True),
        ("supplies_ready", True)
    }
}
goal_states = {
    "goal_state1": goal_state1,
    "goal_state2": goal_state2,
    "goal_state3": goal_state3
}

monitor_forecast = {
    "action": ("monitor_forecast"),
    "preconditions": {
        ("forecast_heavy_rain", True)
    },
    "effects": {
        ("flood_risk_high", True),
        ("forecast_confirmed", True)
    }
}
predeploy_rescue_team = {
    "action": ("predeploy_rescue_team"),
    "preconditions": {
        ("rescue_team_ready", True),
        ("boats_available", True),
        ("forecast_confirmed", True)
    },
    "effects": {
        ("rescue_team_predeployed", True),
        ("rapid_response_prepared", True)
    }
}
stock_medical_kits_in_advance = {
    "action": ("stock_medical_kits_in_advance"),
    "preconditions": {
        ("medical_supplies_available", True),
        ("technicians_available", True)
    },
    "effects": {
        ("medical_kits_stocked", True)
    }
}
shift_route_due_to_bridge_risk = {
    "action": ("shift_route_due_to_bridge_risk"),
    "preconditions": {
        ("bridges_weak", True),
        ("roads_open", True)
    },
    "effects": {
        ("routes_shifted", True),
        ("bridge_area_closed", True)
    }
}
evacuate_before_flood = {
    "action": ("evacuate_before_flood"),
    "preconditions": {
        ("forecast_confirmed", True),
        ("community_alerted", True),
        ("dry_areas_available", True)
    },
    "effects": {
        ("evacuation_started", True),
        ("evacuation_completed", True),
        ("people_safe", True),
        ("dry_areas_available", False)##for precendence link
    }
}
alert_community = {
    "action": ("alert_community"),
    "preconditions": {
        ("forecast_confirmed", True),
        ("community_alerted", False)
    },
    "effects": {
        ("community_alerted", True)
    }
}
establish_backup_communication = {
    "action": ("establish_backup_communication"),
    "preconditions": {
        ("backup_comm_available", True),
        ("technicians_available", True)
    },
    "effects": {
        ("communication_backup_operational", True),
        ("technicians_available", False)#for precedence link

    }
}
stockpile_food_and_medicine = {
    "action": ("stockpile_food_and_medicine"),
    "preconditions": {
        ("food_supplies_stocked", True),
        ("dry_areas_available", True)
    },
    "effects": {
        ("supplies_ready", True)
    }
}
prepare_evacuation_centers = {
    "action": ("prepare_evacuation_centers"),
    "preconditions": {
        ("dry_areas_available", True)
    },
    "effects": {
        ("evacuation_centers_ready", True)
    }
}
# -------------------------------
# Group all actions for easy access
# -------------------------------
actions = {
    "monitor_forecast": monitor_forecast,
    "predeploy_rescue_team": predeploy_rescue_team,
    "stock_medical_kits_in_advance": stock_medical_kits_in_advance,
    "shift_route_due_to_bridge_risk": shift_route_due_to_bridge_risk,
    "evacuate_before_flood": evacuate_before_flood,
    "alert_community": alert_community,
    "establish_backup_communication": establish_backup_communication,
    "stockpile_food_and_medicine": stockpile_food_and_medicine,
    "prepare_evacuation_centers": prepare_evacuation_centers,
    "start":init_state,
    "rescue_team_work_done":goal_state1,
    "communication_team_work_done":goal_state2,
    "medical_and_supplies_work_done":goal_state3
}


causal_links = [
    { "from_action": init_state,
      "fulfil_precondi": ("forecast_heavy_rain", True),
      "to_action": monitor_forecast
    },

    { "from_action": monitor_forecast,
      "fulfil_precondi": ("forecast_confirmed", True),
      "to_action": predeploy_rescue_team
    },

    { "from_action": init_state,
      #"fulfil_precondi": {("rescue_team_ready", True),("boats_available", True)}
      "fulfil_precondi": ("rescue_team_ready", True),
      "to_action": predeploy_rescue_team
    },

    { "from_action": init_state,
      "fulfil_precondi": ("boats_available", True),
      "to_action": predeploy_rescue_team
    },

    { "from_action": monitor_forecast,
      "fulfil_precondi": ("forecast_confirmed", True),
      "to_action": alert_community
    },

    { "from_action": init_state,
      "fulfil_precondi": ("technicians_available", True),
      "to_action": stock_medical_kits_in_advance
    },

    { "from_action": init_state,
      "fulfil_precondi": ("medical_supplies_available", True),
      "to_action": stock_medical_kits_in_advance
    },

    { "from_action": init_state,
      "fulfil_precondi": ("bridges_weak", True),
      "to_action": shift_route_due_to_bridge_risk
    },

    { "from_action": init_state,
      "fulfil_precondi": ("roads_open", True),
      "to_action": shift_route_due_to_bridge_risk
    },

    { "from_action": init_state,
      "fulfil_precondi": ("backup_comm_available", True),
      "to_action": establish_backup_communication
    },

    { "from_action": init_state,
      "fulfil_precondi": ("food_supplies_stocked", True),
      "to_action": stockpile_food_and_medicine
    },

    { "from_action": init_state,
      "fulfil_precondi": ("dry_areas_available", True),
      "to_action": prepare_evacuation_centers
    },

    { "from_action": alert_community,
      "fulfil_precondi": ("community_alerted", True),
      "to_action": evacuate_before_flood
    },

  
    { "from_action": predeploy_rescue_team,
      "fulfil_precondi": ("rescue_team_predeployed", True),
      "to_action": goal_state1
    },

    { "from_action": establish_backup_communication,
      "fulfil_precondi": ("communication_backup_operational", True),
      "to_action": goal_state2
    },

    { "from_action": shift_route_due_to_bridge_risk,
      "fulfil_precondi": ("routes_shifted", True),
      "to_action": goal_state2
    },

    { "from_action": stock_medical_kits_in_advance,
      "fulfil_precondi": ("medical_kits_stocked", True),
      "to_action": goal_state3
    },

    { "from_action": stockpile_food_and_medicine,
      "fulfil_precondi": ("supplies_ready", True),
      "to_action": goal_state3
    },

    { "from_action": init_state,
     "fulfil_precondi": ("community_alerted", False),
     "to_action": alert_community
    },

    { "from_action": init_state,
     "fulfil_precondi": ("dry_areas_available", True),
     "to_action": evacuate_before_flood
    },

    { "from_action": init_state,
     "fulfil_precondi": ("dry_areas_available", True),
     "to_action": stockpile_food_and_medicine
    },

    { "from_action": evacuate_before_flood,
     "fulfil_precondi": ("people_safe", True),
     "to_action": goal_state1
    },

    { "from_action": monitor_forecast,
      "fulfil_precondi": ("forecast_confirmed", True),
      "to_action": evacuate_before_flood },

    { "from_action": init_state,
      "fulfil_precondi": ("technicians_available", True),
      "to_action": establish_backup_communication },

    { "from_action": predeploy_rescue_team,
      "fulfil_precondi": ("rapid_response_prepared", True),
      "to_action": goal_state1 }

]
precedence_links = [
    { "from_action": stock_medical_kits_in_advance,
      "contradict_precondi": ("technicians_available", True),
      "to_action": establish_backup_communication
    },
    { "from_action": prepare_evacuation_centers,
      "fulfil_precondi": ("dry_area_available", True),
      "to_action": evacuate_before_flood
    },
   
]

print(causal_links)
print("\n")
print(precedence_links)




import graphviz





import networkx as nx
import matplotlib.pyplot as plt

def visualize_pop_network(actions, causal_links, precedence_links, filename="flood_POP_network.png"):
    
    
    G = nx.DiGraph()

    
    for action_name in actions.keys():
        G.add_node(action_name)

    
    for link in causal_links:
        from_name = [k for k, v in actions.items() if v is link["from_action"]][0]
        to_name = [k for k, v in actions.items() if v is link["to_action"]][0]
        G.add_edge(from_name, to_name,
                   label=str(link.get("fulfil_precondi", "")),
                   style="solid")

    
    for link in precedence_links:
        from_name = [k for k, v in actions.items() if v is link["from_action"]][0]
        to_name = [k for k, v in actions.items() if v is link["to_action"]][0]
        G.add_edge(from_name, to_name,
                   label=str(link.get("conflict_fact", "")),
                   style="dotted")

    
    pos = nx.spring_layout(G, seed=42, k=0.8)
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color="#A7C7E7", edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_weight="bold", font_size=9)

    
    solid_edges = [(u, v) for u, v, d in G.edges(data=True) if d["style"] == "solid"]
    dotted_edges = [(u, v) for u, v, d in G.edges(data=True) if d["style"] == "dotted"]

    
    nx.draw_networkx_edges(G, pos, edgelist=solid_edges, edge_color="black", width=2.5)
    nx.draw_networkx_edges(G, pos, edgelist=dotted_edges, edge_color="gray", style="dotted", width=2.0)

    
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    
    plt.title("Flood Preparedness POP — Causal (Bold) & Precedence (Dotted) Links", fontsize=12)
    plt.axis("off")
    plt.tight_layout()

    
    plt.savefig(filename, format="png", dpi=300, bbox_inches="tight")
    print(f"\n✅ POP graph saved as '{filename}'")

    
    plt.show()



visualize_pop_network(actions, causal_links, precedence_links)



import graphviz
from pathlib import Path

def visualize_pop_graphviz_better(actions, causal_links, precedence_links,
                                  filename_base="flood_POP_graph_better",
                                  prog="dot"):
   
    
    
    team_map = {}  # node_name -> team label
   
    rescue_nodes = set()
    comm_nodes = set()
    med_nodes = set()
    
    for gname, g in goal_states.items():
        if gname.lower().startswith("goal_state1") or "rescue" in gname.lower():
            
            for link in causal_links:
                if link["to_action"] is goal_state1:
                    
                    pass
    
    for name in actions.keys():
        lname = name.lower()
        if any(k in lname for k in ("rescue", "evacuate", "deploy")):
            team_map[name] = "rescue"
        elif any(k in lname for k in ("comm", "communication", "route", "shift")):
            team_map[name] = "comm"
        elif any(k in lname for k in ("med", "stock", "supply", "medical")):
            team_map[name] = "medical"
        else:
            team_map[name] = "other"

    dot = graphviz.Digraph(comment="Flood POP (improved)", engine=prog)
    dot.attr(splines="true")
    dot.attr(overlap="false")
    dot.attr(rankdir="LR")
    dot.attr(fontname="Helvetica")

    
    cluster_colors = {"rescue": "#D6EAF8", "comm": "#D4EFDF", "medical": "#FDEBD0", "other": "#F5EEF8"}

    
    clusters = {}
    for node, team in team_map.items():
        clusters.setdefault(team, []).append(node)

    for team, nodes in clusters.items():
        with dot.subgraph(name="cluster_" + team) as c:
            c.attr(style="filled", color=cluster_colors.get(team, "#FFFFFF"), label=team.upper())
            c.attr(fontname="Helvetica", fontsize="10")
            for n in nodes:
                c.node(n, label=n, shape="box", style="filled", fillcolor="white")

   
    for link in causal_links:
        try:
            from_n = [k for k, v in actions.items() if v is link["from_action"]][0]
            to_n = [k for k, v in actions.items() if v is link["to_action"]][0]
        except IndexError:
            continue
        lbl = str(link.get("fulfil_precondi", ""))
        dot.edge(from_n, to_n, label=lbl, color="black", penwidth="2.5", fontname="Helvetica", fontsize="9")

    
    for link in precedence_links:
        try:
            from_n = [k for k, v in actions.items() if v is link["from_action"]][0]
            to_n = [k for k, v in actions.items() if v is link["to_action"]][0]
        except IndexError:
            continue
        lbl = str(link.get("conflict_fact", ""))
        dot.edge(from_n, to_n, label=lbl, color="gray", style="dashed", penwidth="1.5", fontname="Helvetica", fontsize="8")

    
    png_path = f"{filename_base}.png"
    pdf_path = f"{filename_base}.pdf"
    dot.render(filename_base, format="png", cleanup=True)  
    dot.render(filename_base, format="pdf", cleanup=True)  
    print(f"Saved: {png_path} and {pdf_path}")


visualize_pop_graphviz_better(actions, causal_links, precedence_links)



import json, webbrowser, os

def write_vis_network_html(actions, causal_links, precedence_links, filename="flood_POP_interactive.html"):
    
    nodes = []
    for name in actions.keys():
        lname = name.lower()
        if "rescue" in lname or "evacuate" in lname or "predeploy" in lname:
            color = "#4E79A7"      # blue (rescue)
        elif "comm" in lname or "route" in lname or "shift" in lname or "backup" in lname:
            color = "#59A14F"      # green (communication)
        elif "med" in lname or "stock" in lname or "supply" in lname or "medical" in lname:
            color = "#F28E2B"      # orange (medical/supplies)
        else:
            color = "#B07AA1"      # purple (other)
        nodes.append({
            "id": name,
            "label": name,
            "color": {"background": color, "border": "#222"},
            "shape": "box",
            "font": {"size": 16, "face": "Arial"},
            "margin": 12,
            "widthConstraint": {"maximum": 320}
        })

    def safe_name_for(action_ref):
        for k, v in actions.items():
            if v is action_ref:
                return k
        return None

    edges = []
    
    for link in causal_links:
        fr = safe_name_for(link["from_action"])
        to = safe_name_for(link["to_action"])
        if not fr or not to:
            continue
        edges.append({
            "from": fr, "to": to,
            "label": str(link.get("fulfil_precondi","")),
            "color": {"color":"#000"},
            "width": 3,
            "dashes": False,
            "arrows": {"to": {"enabled": True, "type": "arrow"}}
        })
    
    for link in precedence_links:
        fr = safe_name_for(link["from_action"])
        to = safe_name_for(link["to_action"])
        if not fr or not to:
            continue
        edges.append({
            "from": fr, "to": to,
            "label": str(link.get("conflict_fact","")),
            "color": {"color":"#7f7f7f"},
            "width": 1.6,
            "dashes": True,
            "arrows": {"to": {"enabled": True, "type": "arrow"}}
        })

    
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Flood POP Interactive</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
  <link href="https://unpkg.com/vis-network@9.1.2/styles/vis-network.min.css" rel="stylesheet" type="text/css" />
  <style>
    body {{ font-family: Arial, Helvetica, sans-serif; margin: 12px; }}
    #controls {{ margin-bottom: 8px; }}
    #mynetwork {{ width: 100%; height: 85vh; border: 1px solid lightgray; }}
    .legend-swatch {{ display:inline-block; padding:4px 8px; margin-left:6px; border-radius:4px; color:#fff; font-weight:600; }}
    button.control-btn {{ margin-right:8px; padding:6px 10px; font-size:14px; border-radius:6px; cursor:pointer; }}
  </style>
</head>
<body>
  <h2>Flood POP — Causal (thick) & Precedence (dashed)</h2>

  <div id="controls">
    <button id="btn_hier" class="control-btn">Hierarchical (LR)</button>
    <button id="btn_force" class="control-btn">Force Layout</button>
    <button id="btn_fit" class="control-btn">Fit View</button>
    <span style="margin-left:18px;"><b>Legend:</b></span>
    <span class="legend-swatch" style="background:#4E79A7;">Rescue</span>
    <span class="legend-swatch" style="background:#59A14F;">Comm</span>
    <span class="legend-swatch" style="background:#F28E2B;">Medical</span>
    <span class="legend-swatch" style="background:#B07AA1;">Other</span>
  </div>

  <div id="mynetwork"></div>

  <script>
    const nodes = {json.dumps(nodes)};
    const edges = {json.dumps(edges)};

    const container = document.getElementById('mynetwork');
    const data = {{
      nodes: new vis.DataSet(nodes),
      edges: new vis.DataSet(edges)
    }};

    // base options for both modes
    const baseOptions = {{
      interaction: {{
        hover: true,
        navigationButtons: true,
        keyboard: true,
        zoomView: true
      }},
      edges: {{
        smooth: {{ type: "cubicBezier", forceDirection: "horizontal", roundness: 0.35 }},
        font: {{ size: 14, align: "horizontal" }}
      }},
      nodes: {{
        margin: 12
      }}
    }};

    // hierarchical (Left->Right) configuration
    const hierOptions = JSON.parse(JSON.stringify(baseOptions));
    hierOptions.layout = {{
      hierarchical: {{
        enabled: true,
        direction: "LR",
        sortMethod: "hubsize",
        levelSeparation: 320,
        nodeSpacing: 220
      }}
    }};
    hierOptions.physics = {{ enabled: false }};

    // force (physics) configuration for organic layout
    const forceOptions = JSON.parse(JSON.stringify(baseOptions));
    forceOptions.layout = {{ hierarchical: {{ enabled: false }} }};
    forceOptions.physics = {{
      enabled: true,
      barnesHut: {{
        gravitationalConstant: -8000,
        centralGravity: 0.3,
        springLength: 250,
        springConstant: 0.04,
        damping: 0.4
      }},
      stabilization: {{ enabled: true, iterations: 200 }}
    }};

    // start in hierarchical mode
    let network = new vis.Network(container, data, hierOptions);

    // after initial creation, fit to view (with animation)
    network.once("stabilizationIterationsDone", function () {{
      network.fit({{ animation: true }});
    }});

    // control buttons
    document.getElementById("btn_hier").onclick = function() {{
      network.setOptions(hierOptions);
      setTimeout(()=>network.fit({{ animation: true }}), 200);
    }};
    document.getElementById("btn_force").onclick = function() {{
      network.setOptions(forceOptions);
      // allow physics to stabilize then fit
      setTimeout(()=>network.fit({{ animation: true }}), 600);
    }};
    document.getElementById("btn_fit").onclick = function() {{
      network.fit({{ animation: true }});
    }};

    // helpful hover highlight: increase edge width on hover
    network.on("hoverEdge", function(params) {{
      const edgeId = params.edge;
      if (edgeId) {{
        network.body.data.edges.update({{ id: edgeId, width: network.body.data.edges.get(edgeId).width + 1.5 }});
      }}
    }});
    network.on("blurEdge", function(params) {{
      const edgeId = params.edge;
      if (edgeId) {{
        const e = network.body.data.edges.get(edgeId);
        // restore width (avoid negative)
        let base = e.dashes ? 1.6 : 3;
        network.body.data.edges.update({{ id: edgeId, width: base }});
      }}
    }});
  </script>
</body>
</html>
"""

   
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    path = os.path.realpath(filename)
    webbrowser.open("file://" + path)
    print(f"✅ Improved interactive HTML written to {filename} and opened in browser.")


# Call it (will overwrite and open)
write_vis_network_html(actions, causal_links, precedence_links, filename="flood_POP_interactive.html")


from collections import deque
import copy


def eval_effect_value(val, P_flood, P_infra):
    if callable(val):
        try:
            return bool(val(P_flood))
        except TypeError:
            try:
                return bool(val(P_infra))
            except TypeError:
                try:
                    return bool(val(P_flood, P_infra))
                except Exception:
                    return None
    else:
        return val

def effect_matches(effect, desired_fact, P_flood, P_infra):
    if effect[0] != desired_fact[0]:
        return False
    v = eval_effect_value(effect[1], P_flood, P_infra)
    return v is not None and v == desired_fact[1]


def has_cycle(ordering):
    
    adj = {}
    for a,b in ordering:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set())
    visited, stack = set(), set()
    def dfs(u):
        if u in stack: return True
        if u in visited: return False
        stack.add(u)
        for v in adj.get(u, ()):
            if dfs(v): return True
        stack.remove(u); visited.add(u)
        return False
    for n in adj:
        if dfs(n): return True
    return False

def topological_sort(ordering, all_nodes):
    adj = {n:set() for n in all_nodes}
    indeg = {n:0 for n in all_nodes}
    for a,b in ordering:
        if a in adj and b in adj:
            adj[a].add(b); indeg[b]+=1
    q = deque([n for n in all_nodes if indeg[n]==0])
    out=[]
    while q:
        u=q.popleft(); out.append(u)
        for v in list(adj[u]):
            indeg[v]-=1
            if indeg[v]==0:
                q.append(v)
    for n in all_nodes:
        if n not in out:
            out.append(n)
    return out


def Make_Minimal_Plan(initial_name, goal_action_names, operators):
    plan = {
        "actions": set([initial_name]) | set(goal_action_names),
        "ordering": set((initial_name, g) for g in goal_action_names),
        "causal_links": [],            
        "open_preconds": deque()     
    }
    for g in goal_action_names:
        for ef in operators[g].get("effects", set()):
            plan["open_preconds"].append((g, ef))
    return plan


def Select_Subgoal(plan):
    if not plan.get("open_preconds"):
        return None
    return plan["open_preconds"].popleft()


def Solution(plan, init_state, operators, P_flood, P_infra):
   
    if plan.get("open_preconds"):
        return False
    if has_cycle(plan.get("ordering", set())):
        return False
    
    for prov, fact, cons in plan.get("causal_links", []):
        if prov == "start":
            # check init state
            ok = False
            for ef in init_state.get("effects", set()):
                if effect_matches(ef, fact, P_flood, P_infra):
                    ok = True; break
            if not ok: return False
        else:
            op = operators.get(prov)
            if not op: return False
            if not any(effect_matches(ef, fact, P_flood, P_infra) for ef in op.get("effects", set())):
                return False
    return True


def find_providers(fact, operators, plan, init_name, init_state, P_flood, P_infra):
    provs = []
    
    for ef in init_state.get("effects", set()):
        if effect_matches(ef, fact, P_flood, P_infra):
            provs.append(init_name); break
    
    for a in plan["actions"]:
        if a == init_name: continue
        op = operators.get(a)
        if op and any(effect_matches(ef, fact, P_flood, P_infra) for ef in op.get("effects", set())):
            provs.append(a)
    
    for name, op in operators.items():
        if name in plan["actions"]: continue
        if any(effect_matches(ef, fact, P_flood, P_infra) for ef in op.get("effects", set())):
            provs.append(name)
    return provs


def Choose_Operator(plan, operators, S, c, init_name, init_state, P_flood, P_infra):
    
    consumer = S; fact = c
    providers = find_providers(fact, operators, plan, init_name, init_state, P_flood, P_infra)
    children = []
    for prov in providers:
        newplan = copy.deepcopy(plan)
        
        newplan.setdefault("causal_links", []).append((prov, fact, consumer))
        
        newplan.setdefault("ordering", set()).add((prov, consumer))
        
        if prov not in newplan["actions"]:
            newplan["actions"].add(prov)
            newplan["ordering"].add((init_name, prov))
            for pre in operators[prov].get("preconditions", set()):
                newplan.setdefault("open_preconds", deque()).append((prov, pre))
        children.append(newplan)
    return children


def operator_negates(op, fact, P_flood, P_infra):
    if not op: return False
    for ef in op.get("effects", ()):
        if ef[0] == fact[0]:
            v = eval_effect_value(ef[1], P_flood, P_infra)
            if v is not None and v != fact[1]:
                return True
    return False

def Resolve_Threats(plan, operators, P_flood, P_infra):
    ordering = plan.setdefault("ordering", set())
    for (prov, fact, cons) in list(plan.get("causal_links", [])):
        for act in list(plan["actions"]):
            if act == prov or act == cons:
                continue
            if operator_negates(operators.get(act), fact, P_flood, P_infra):
                
                ordering.add((act, prov))
                if not has_cycle(ordering):
                    continue
                ordering.remove((act, prov)) 
               
                ordering.add((cons, act))
                if not has_cycle(ordering):
                    continue
                ordering.remove((cons, act))
              
                return False
    return True


def POP(initial_name, goal_action_names, operators, init_state, P_flood, P_infra, max_nodes=20000, debug=False):

    root = Make_Minimal_Plan(initial_name, goal_action_names, operators)
    stack = [root]
    nodes = 0

    while stack and nodes < max_nodes:
        nodes += 1
        plan = stack.pop()
        if debug:
            print(f"[node {nodes}] actions={plan['actions']}, open_preconds={len(plan['open_preconds'])}")
        if Solution(plan, init_state, operators, P_flood, P_infra):
            if debug: print("Solution found.")
            return plan
        sub = Select_Subgoal(plan)
        if sub is None:
            
            if debug: print("No subgoal but not a solution, skipping node.")
            continue
        S, c = sub
        if debug: print(f" Selected subgoal: {S}, {c}")
        children = Choose_Operator(plan, operators, S, c, initial_name, init_state, P_flood, P_infra)
        if not children:
            if debug: print("  No providers for this subgoal -> dead end")
            continue
        
        for child in children:
            ok = Resolve_Threats(child, operators, P_flood, P_infra)
            if not ok:
                if debug: print("  Child had unresolvable threat -> skip")
                continue
            stack.append(child)
 
    return None


def print_plan(plan):
    if plan is None:
        print("No plan found.")
        return
    print("\n===== PLAN =====")
    print("Actions (unordered):")
    for a in plan["actions"]:
        print(" -", a)
    print("\nCausal links:")
    for prov, fact, cons in plan.get("causal_links", []):
        print(f"  ({prov}) -- {fact} --> ({cons})")
    print("\nOrdering constraints:")
    for b,a in plan.get("ordering", set()):
        print("  ", b, "->", a)
    print("\nOne valid linearization:")
    seq = topological_sort(plan.get("ordering", set()), list(plan["actions"]))
    for i,s in enumerate(seq, 1):
        print(f"  {i}. {s}")
    print("===============\n")


initial_name = "start"
goal_names = [n for n in ["rescue_team_work_done","communication_team_work_done","medical_and_supplies_work_done"] if n in actions]


plan = POP(initial_name, goal_names, actions, init_state, P_flood, P_infra, max_nodes=20000, debug=True)
print_plan(plan)
