
import networkx as nx


def get_actions():
    """
    A minimal but realistic set of disaster-response actions.
    These match your academic requirements.
    """

    actions = {
        "PreDeployRescueTeam": {
            "pre": {"FloodWarning"},
            "add": {"RescueTeamReady"},
            "del": set()
        },
        "ShiftRouteDueToBridgeRisk": {
            "pre": {"Bridge_Collapse_Risk"},
            "add": {"AlternateRouteActive"},
            "del": set()
        },
        "StockMedicalKitsInAdvance": {
            "pre": {"DiseaseRisk"},
            "add": {"MedicalSuppliesReady"},
            "del": set()
        },
        "EvacuateBeforeFlood": {
            "pre": {"RescueTeamReady"},
            "add": {"PopulationEvacuated"},
            "del": set()
        },
        "OpenShelters": {
            "pre": {"FloodWarning"},
            "add": {"SheltersOpen"},
            "del": set()
        },
        "SendDroneForAssessment": {
            "pre": set(),
            "add": {"DroneAssessmentDone"},
            "del": set()
        }
    }

    return actions



def build_planning_graph(levels=3):
    """
    Returns a NetworkX planning graph.
    Structure:
        S0 → A0 → S1 → A1 → S2 …
    """

    graph = nx.DiGraph()
    actions = get_actions()

    
    S0 = {
        "FloodWarning",
        "Bridge_Collapse_Risk",
        "DiseaseRisk"
    }

   
    for fact in S0:
        graph.add_node(f"F0_{fact}", label=fact, type="fact", level=0)

    
    prev_facts = S0

    for lvl in range(levels):

        
        for act_name, act_data in actions.items():

            
            if act_data["pre"].issubset(prev_facts):

                act_node = f"A{lvl}_{act_name}"
                graph.add_node(act_node, label=act_name, type="action", level=lvl)

                
                for pre in act_data["pre"]:
                    graph.add_edge(f"F{lvl}_{pre}", act_node)

                
                for addf in act_data["add"]:
                    next_fact_node = f"F{lvl+1}_{addf}"
                    graph.add_node(next_fact_node, label=addf, type="fact", level=lvl+1)
                    graph.add_edge(act_node, next_fact_node)

        
        next_facts = set()
        for n, d in graph.nodes(data=True):
            if d.get("type") == "fact" and d.get("level") == lvl+1:
                next_facts.add(d["label"])
        prev_facts = next_facts

    return graph



def extract_action_list(graph):
    """
    Returns a list of action labels from the planning graph.
    Only first 5 needed for LLM Module.
    """
    actions = []
    for n, d in graph.nodes(data=True):
        if d.get("type") == "action":
            actions.append(d["label"])

    return actions[:5]




def save_graph_as_dot(graph, path="data/graphplan_output.dot"):
    nx.drawing.nx_pydot.write_dot(graph, path)
    return path




def run_planning_module(levels=3):
    """
    Build planning graph, extract actions, save DOT.
    Returns: list of actions
    """
    G = build_planning_graph(levels)
    actions = extract_action_list(G)
    save_graph_as_dot(G)
    return actions



if __name__ == "__main__":
    acts = run_planning_module()
    print("\nRecommended Planning Actions:")
    for a in acts:
        print("-", a)
