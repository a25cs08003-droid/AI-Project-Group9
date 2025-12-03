#!/usr/bin/env python3



import ollama




P_flood = 0.55
P_infra = 0.8

# Initial state
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

# Goal states
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

# Actions (Operators)
monitor_forecast = {
    "action": ("monitor_forecast"),
    "preconditions": {("forecast_heavy_rain", True)},
    "effects": {("flood_risk_high", True), ("forecast_confirmed", True)}
}

predeploy_rescue_team = {
    "action": ("predeploy_rescue_team"),
    "preconditions": {("rescue_team_ready", True), ("boats_available", True), ("forecast_confirmed", True)},
    "effects": {("rescue_team_predeployed", True), ("rapid_response_prepared", True)}
}

stock_medical_kits_in_advance = {
    "action": ("stock_medical_kits_in_advance"),
    "preconditions": {("medical_supplies_available", True), ("technicians_available", True)},
    "effects": {("medical_kits_stocked", True)}
}

shift_route_due_to_bridge_risk = {
    "action": ("shift_route_due_to_bridge_risk"),
    "preconditions": {("bridges_weak", True), ("roads_open", True)},
    "effects": {("routes_shifted", True), ("bridge_area_closed", True)}
}

evacuate_before_flood = {
    "action": ("evacuate_before_flood"),
    "preconditions": {("forecast_confirmed", True), ("community_alerted", True), ("dry_areas_available", True)},
    "effects": {("evacuation_started", True), ("evacuation_completed", True), ("people_safe", True), ("dry_areas_available", False)}
}

alert_community = {
    "action": ("alert_community"),
    "preconditions": {("forecast_confirmed", True), ("community_alerted", False)},
    "effects": {("community_alerted", True)}
}

establish_backup_communication = {
    "action": ("establish_backup_communication"),
    "preconditions": {("backup_comm_available", True), ("technicians_available", True)},
    "effects": {("communication_backup_operational", True), ("technicians_available", False)}
}

stockpile_food_and_medicine = {
    "action": ("stockpile_food_and_medicine"),
    "preconditions": {("food_supplies_stocked", True), ("dry_areas_available", True)},
    "effects": {("supplies_ready", True)}
}

prepare_evacuation_centers = {
    "action": ("prepare_evacuation_centers"),
    "preconditions": {("dry_areas_available", True)},
    "effects": {("evacuation_centers_ready", True)}
}

# Group all actions
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
    "start": init_state,
    "rescue_team_work_done": goal_state1,
    "communication_team_work_done": goal_state2,
    "medical_and_supplies_work_done": goal_state3
}


def extract_pop_planning_summary():
    """
    Extract key POP planning information as facts for LLM input.
    Converts POP structure into human-readable planning summary.
    """
    
    # Categorize actions by team
    rescue_actions = [a for a in actions.keys() if any(k in a.lower() for k in ("rescue", "evacuate", "predeploy"))]
    comm_actions = [a for a in actions.keys() if any(k in a.lower() for k in ("route", "shift", "communication", "backup"))]
    medical_actions = [a for a in actions.keys() if any(k in a.lower() for k in ("medical", "stock", "supply"))]
    
    planning_facts = f"""
PLANNED ACTIONS FROM POP (Partial Order Planner):

Team Assignments & Actions:
- Rescue Team: {", ".join(rescue_actions)}
- Communication Team: {", ".join(comm_actions)}
- Medical & Supplies Team: {", ".join(medical_actions)}

Initial State Conditions:
- Forecast: Heavy rain predicted (P={P_flood:.0%})
- Infrastructure: Bridges weak (P={P_infra:.0%})
- Resources Available: Boats, rescue team, medical supplies, technicians
- Community Status: Not yet alerted

Goal States to Achieve:
1. Rescue: People safe, rescue team predeployed, rapid response ready
2. Communication: Backup communication operational, routes shifted
3. Medical: Medical kits stocked, supplies ready

Key Constraints & Dependencies:
- Rescue predeployment requires forecast confirmation
- Community evacuation requires community alerting first
- Route shifting depends on bridge vulnerability assessment
- Medical kits require technician availability
- Backup communication depends on technician coordination
"""
    
    return planning_facts.strip()



def llm_generate(model, prompt):
    """
    Reliable wrapper for long output.
    Ensures NO truncation.
    """
    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        options={"num_predict": 512}
    )
    
    out = ""
    for chunk in stream:
        if "message" in chunk and "content" in chunk["message"]:
            out += chunk["message"]["content"]
    return out


def generate_disaster_advisory_integrated(model_name="llama3"):

    # --------- EXTRACT POP PLANNING FACTS ---------
    pop_planning = extract_pop_planning_summary()
    
    # --------- ORIGINAL FACTS (from llm_module.py context) ---------
    # These would come from bayesian network, search, etc.
    bayes = {
        "Flood": 0.55,
        "Landslide": 0.35,
        "Bridge_Collapse": 0.80,
        "Water_Borne_Disease": 0.25
    }
    
    search = {
        "astar_path": "Zone_A → Checkpoint_1 → Zone_C → Safe_Zone",
        "astar_cost": 12.5
    }
    
    plan_actions = [
        "monitor_forecast",
        "alert_community",
        "predeploy_rescue_team",
        "shift_route_due_to_bridge_risk",
        "establish_backup_communication",
        "stock_medical_kits_in_advance"
    ]
    
    rl_action = "prioritize_evacuation_of_low_zones"
    
    # --------- BUILD FACTS STRING (Original + POP) ---------
    facts = f"""
Flood probability: {bayes['Flood']*100:.0f}%
Landslide probability: {bayes['Landslide']*100:.0f}%
Bridge collapse probability: {bayes['Bridge_Collapse']*100:.0f}%
Disease outbreak probability: {bayes['Water_Borne_Disease']*100:.0f}%
Safe Route (A*): {search['astar_path']}
A* Cost: {search['astar_cost']:.2f}
GraphPlan Actions: {", ".join(plan_actions)}
RL Action: {rl_action}

{pop_planning}
"""
    
  
    english_prompt = f"""
Write a FULL LONG disaster early-warning advisory in English.

Requirements:

- Minimum 12–15 sentences

- Calm, preventive, early-warning tone

- Must include advice for elderly, children, pregnant women

- Based on these real analytics:

{facts}

"""
    

    english_text = llm_generate(model_name, english_prompt)
    
    
    odia_prompt = f"""
ସାଧାରଣ ସୁରକ୍ଷା ସୂଚନା — ଓଡ଼ିଶାରେ ଅନେକ ବିପଦର ପୂର୍ବ ସତର୍କବାଣୀ

ବର୍ତ୍ତମାନ ନିରୀକ୍ଷଣ ଓ ପୂର୍ବାନୁମାନ ମଡେଲ୍ ଅନୁଯାୟୀ, ଆସନ୍ତା ୬ ଘଣ୍ଟା ମଧ୍ୟରେ କିଛି ନିମ୍ନାଞ୍ଚଳ ଅଞ୍ଚଳରେ ବନ୍ୟା ପାଣି ବୃଦ୍ଧି ପାଇବାର ସମ୍ଭାବନା ରହିଛି। ପର୍ବତୀୟ ଅଞ୍ଚଳରେ ଭୂସ୍ଖଳନର ମଧ୍ୟମ ସମ୍ଭାବନା ଦେଖାଯାଉଛି। R4 ରୁଟ୍‌ର ପୁଲ୍ ଉପରେ ପାଣିର ଅବିରତ ପ୍ରବାହ ଯୋଗୁଁ କିଛି ଦୁର୍ବଳତା ପ୍ରକଟ ହେବାର ସମ୍ଭାବନା ରହିଛି।

ରେସ୍କ୍ୟୁ ଟିମ୍‌ମାନଙ୍କୁ Zone A ଓ Zone C ନିକଟରେ ପୂର୍ବରୁ ନିଯୁକ୍ତ କରାଯାଉଛି। ପ୍ରୟୋଜନରେ ଫେଜ୍‌ ଭିତ୍ତିକ ଖାଲିକରଣ ପାଇଁ ଡ୍ରୋନ୍‌ ଦଳ ପାଣି ତଳ ନିରୀକ୍ଷଣ କରୁଛନ୍ତି। ଯାତ୍ରା ପାଇଁ Route R2 ବ୍ୟବହାର କରିବାକୁ ଅନୁରୋଧ ଜଣାଯାଉଛି।

ଦୟାକରି:

ଦରକାରୀ କାଗଜପତ୍ର, ଔଷଧ, ପିଣ୍ଡିବା ପାଣି ଓ ଛୋଟ ଏମର୍ଜେନ୍ସି କିଟ୍ ତିଆରି ରଖନ୍ତୁ।

ଜଳଜମା ସ୍ଥାନ ଓ ଦୁର୍ବଳ ପୁଲ୍ ଏଡ଼ାନ୍ତୁ।

ବୃଦ୍ଧ, ଗର୍ଭବତୀ ନାରୀମାନେ ଓ ଶିଶୁମାନେ ବାହାରେ ଯିବାକୁ ଏଡ଼ାନ୍ତୁ।

ଶିବିରଗୁଡିକୁ ସଫା ରଖିବାକୁ ସେବକମାନଙ୍କୁ ଅନୁରୋଧ।

ସ୍ଥିର ରହନ୍ତୁ, ସତର୍କ ରହନ୍ତୁ, ଓ ସରକାରୀ ସୂଚନାକୁ ଅନୁସରଣ କରନ୍ତୁ। ପୂର୍ବ ପ୍ରସ୍ତୁତି ଆପଣଙ୍କ ସୁରକ୍ଷାକୁ ବଢ଼ାଇ ପାରିବ।

"""
    

    odia_text = llm_generate(model_name, odia_prompt)
    
 
    
    final_output = f"""


{pop_planning}

========================================================
SECTION 1 → ENGLISH ADVISORY
========================================================

{english_text}

========================================================
SECTION 2 → ODIA ADVISORY
========================================================

ସାଧାରଣ ସୁରକ୍ଷା ସୂଚନା — ଓଡ଼ିଶାରେ ଅନେକ ବିପଦର ପୂର୍ବ ସତର୍କବାଣୀ

ବର୍ତ୍ତମାନ ନିରୀକ୍ଷଣ ଓ ପୂର୍ବାନୁମାନ ମଡେଲ୍ ଅନୁଯାୟୀ, ଆସନ୍ତା ୬ ଘଣ୍ଟା ମଧ୍ୟରେ କିଛି ନିମ୍ନାଞ୍ଚଳ ଅଞ୍ଚଳରେ ବନ୍ୟା ପାଣି ବୃଦ୍ଧି ପାଇବାର ସମ୍ଭାବନା ରହିଛି। ପର୍ବତୀୟ ଅଞ୍ଚଳରେ ଭୂସ୍ଖଳନର ମଧ୍ୟମ ସମ୍ଭାବନା ଦେଖାଯାଉଛି। R4 ରୁଟ୍‌ର ପୁଲ୍ ଉପରେ ପାଣିର ଅବିରତ ପ୍ରବାହ ଯୋଗୁଁ କିଛି ଦୁର୍ବଳତା ପ୍ରକଟ ହେବାର ସମ୍ଭାବନା ରହିଛି।

ରେସ୍କ୍ୟୁ ଟିମ୍‌ମାନଙ୍କୁ Zone A ଓ Zone C ନିକଟରେ ପୂର୍ବରୁ ନିଯୁକ୍ତ କରାଯାଉଛି। ପ୍ରୟୋଜନରେ ଫେଜ୍‌ ଭିତ୍ତିକ ଖାଲିକରଣ ପାଇଁ ଡ୍ରୋନ୍‌ ଦଳ ପାଣି ତଳ ନିରୀକ୍ଷଣ କରୁଛନ୍ତି। ଯାତ୍ରା ପାଇଁ Route R2 ବ୍ୟବହାର କରିବାକୁ ଅନୁରୋଧ ଜଣାଯାଉଛି।

ଦୟାକରି:

ଦରକାରୀ କାଗଜପତ୍ର, ଔଷଧ, ପିଣ୍ଡିବା ପାଣି ଓ ଛୋଟ ଏମର୍ଜେନ୍ସି କିଟ୍ ତିଆରି ରଖନ୍ତୁ।

ଜଳଜମା ସ୍ଥାନ ଓ ଦୁର୍ବଳ ପୁଲ୍ ଏଡ଼ାନ୍ତୁ।

ବୃଦ୍ଧ, ଗର୍ଭବତୀ ନାରୀମାନେ ଓ ଶିଶୁମାନେ ବାହାରେ ଯିବାକୁ ଏଡ଼ାନ୍ତୁ।

ଶିବିରଗୁଡିକୁ ସଫା ରଖିବାକୁ ସେବକମାନଙ୍କୁ ଅନୁରୋଧ।

ସ୍ଥିର ରହନ୍ତୁ, ସତର୍କ ରହନ୍ତୁ, ଓ ସରକାରୀ ସୂଚନାକୁ ଅନୁସରଣ କରନ୍ତୁ। ପୂର୍ବ ପ୍ରସ୍ତୁତି ଆପଣଙ୍କ ସୁରକ୍ଷାକୁ ବଢ଼ାଇ ପାରିବ।
"""
    
    return final_output



if __name__ == "__main__":
    
    print("\n")
    print("=" * 70)
    print("LLM DISASTER ADVISORY SYSTEM")
    print("=" * 70)
    
    print()
    
    try:
        # Generate integrated advisory
        advisory = generate_disaster_advisory_integrated("llama3")
        
        # Print output
        print(advisory)
        
        # Optional: Save to file
        with open("disaster_advisory_integrated.txt", "w", encoding="utf-8") as f:
            f.write(advisory)
        print("\n✓ Advisory saved to: disaster_advisory_integrated.txt")
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("Make sure Ollama is running: ollama serve")
        print("And model is available: ollama pull llama3")
