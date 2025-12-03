

from disaster_ai.bayesian_module import run_bayesian_module
from disaster_ai.search_module import run_search_module
from disaster_ai.graphplan_module import run_planning_module
from disaster_ai.qlearning_module import run_qlearning_module



def run_full_system():
     official interface for Module 5 (LLM Advisory Generator).
   

    bayes = run_bayesian_module(
        data_path="data/odisha_data.csv",
        queries_path="data/queries.csv"
    )

    
    search_out = run_search_module()
    
    planning_actions = run_planning_module(levels=3)

    
    rl_action = run_qlearning_module()

    return {
        "bayesian": bayes,
        "search": search_out,
        "planning": planning_actions,
        "rl_action": rl_action
    }



if __name__ == "__main__":
    results = run_full_system()
    print("\n========= FULL SYSTEM OUTPUT =========\n")
    for k, v in results.items():
        print(f"\n--- {k.upper()} ---")
        print(v)
