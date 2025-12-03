### AI-Driven Dynamic Disaster Response System  
### Predictive Multi-Hazard Reasoning • Future-Aware Routing • Planning • RL • Multilingual LLM Advisory

This repository implements the 5-module AI system required in the course assignment  
**“AI-Driven Dynamic Disaster Response System with Predictive Multi-Hazard Reasoning.”**  
It combines Bayesian inference, search algorithms, automated planning, Q-learning, and multilingual LLM-based early-warning generation.  
All code is complete, functional, and independently runnable as required in the project PDF. :contentReference[oaicite:1]{index=1}

# Repository Structure

disaster_alarm_llm/
│
├── data/
│ ├── odisha_data.csv
│ ├── queries.csv
│ ├── graphplan_output.dot
│ ├── qtable.csv
│
├── disaster_ai/
│ ├── bayesian_module.py
│ ├── search_module.py
│ ├── graphplan_module.py
│ ├── qlearning_module.py
│ ├── pop_llm_integrated.py
│ ├── POPFlood_Manage.py
│ ├── integrated_module.py
│ ├── llm_module.py
│ ├── llm_final.py
│ └── init.py
│
├── README.md
└── requirements.txt


Every module is explained below in detail.


#  Installation & Setup

##  Install Python (3.9–3.11 recommended)

## dependencies:

python3 --version

python3 -m venv venv
source venv/bin/activate     # Linux/Mac
venv\Scripts\activate       # Windows
requirements.txt (Recommended)

sudo apt install graphviz

##Add this file to your repo:

numpy
pandas
matplotlib
networkx
tqdm
pydot
ollama
graphviz

pip install -r requirements.txt

##Download Ollama
Linux (Ubuntu/Debian)
curl -fsSL https://ollama.com/install.sh | sh

##MacOS

Download from:
https://ollama.com/download

##Windows

Official Windows installer:
https://ollama.com/download/windows

install manually:

pip install pandas numpy networkx matplotlib tqdm ollama pydot

 Start Ollama Service

##After installation:

ollama serve


Run in a separate terminal window.

 Download a Model (LLaMA-3 recommended)
ollama pull llama3


##Verify Ollama Installation
ollama list
ollama run llama3

If you see a prompt, Ollama works.

##Module 1 — Bayesian Multi-Hazard Risk Forecasting

File: bayesian_module.py

#Purpose

Implements a Bayesian Network predicting hazards such as:

Imminent Flood

Landslide Risk

Bridge Failure Risk

Disease Outbreak Risk

Uses real-time evidence from odisha_data.csv.

What the file contains

Definition of Bayesian nodes

CPT handling

Evidence loading

Posterior probability computation

Generates disaster risk scores

##Run Module 1

python -m disaster_ai.bayesian_module

##Output

Posterior probabilities for each hazard

Reasoning steps

A structured risk summary

##Module 2 — Future-Risk-Aware Search for Rescue Routing

File: search_module.py

#Purpose

Simulates affected region as a graph and computes safest routing using:

Uniform-Cost Search (UCS) — baseline

A* Search with Future Risk Heuristic — advanced

What the file contains

Graph construction

Edge risk modelling

A* heuristic predicting future road/bridge failures

Detailed path comparison

##Run Module 2

python -m disaster_ai.search_module

#Output

UCS path + cost

A* path + predicted future failures

Best safe route

##Module 3 — Disaster Planning using GraphPlan & POP

Files:

graphplan_module.py

POPFlood_Manage.py

pop_llm_integrated.py

#Purpose

Implements deterministic and partial-order planning for proactive response.

What each file does
graphplan_module.py

Defines actions

Constructs multi-level planning graph

Saves .dot visualization output

POPFlood_Manage.py

Partial-Order Planner (POP)

Generates flexible disaster plans

pop_llm_integrated.py

Passes GraphPlan/POP plans into LLM for advisory text

##Run Module 3
python -m disaster_ai.graphplan_module


Generate graph image:

dot -Tpng data/graphplan_output.dot -o planning_graph.png

#Output

Plan graph

Action sequence

Optional LLM-ready formatted plan

##Module 4 — Reinforcement Learning (Q-Learning)

File: qlearning_module.py

#Purpose

Learns optimal decision policy for disaster response.

System modeled as MDP with:

States → hazard severity + resources

Actions → evacuation/observe/drone/relocate

Rewards → life-saving efficiency vs resource conservation

What the file contains

Q-table initialization

Learning loop

Visualization support

Comparison with naïve strategy

##Run Module 4
python -m disaster_ai.qlearning_module

#Output

Learned Q-table (data/qtable.csv)

Recommended optimal action

##Module 5 — Multilingual LLM Predictive Early Warning

Files:

llm_module.py

llm_final.py

#Purpose

Generates a multilingual early-warning advisory in:

English

Odia

What the files contain
llm_module.py

Converts hazard + routing + planning + RL outputs into prompt

Sends prompt to Ollama LLaMA-3 model

Ensures calm, safe, factual advisory 

llm_final.py

Enhanced formatting

Additional Odia-only response option

Can be called independently

##Run Module 5
python -m disaster_ai.llm_module


If you want the final polished advisory:

python -m disaster_ai.llm_final

#Output

Full multilingual public advisory

Includes predictions, preventive instructions, and urgency level

##Integrated System Controller

File: integrated_module.py

#Purpose

Runs all modules in order and returns a combined dictionary of results.

##Run the Whole AI System
python -m disaster_ai.integrated_module

#Output

Hazard probabilities

Optimal safe route

Selected disaster plan

RL recommended action





