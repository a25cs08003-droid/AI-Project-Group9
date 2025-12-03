

import numpy as np
import random
import pandas as pd

STATES = [
    "LowRisk_HighRes",
    "LowRisk_MidRes",
    "LowRisk_LowRes",
    "MedRisk_HighRes",
    "MedRisk_MidRes",
    "MedRisk_LowRes",
    "HighRisk_HighRes",
    "HighRisk_MidRes",
    "HighRisk_LowRes",
]

ACTIONS = ["EvacuateNow", "WaitAndObserve", "SendDrone", "PreDeployTeams"]


def next_state(state, action):


    risk, res = state.split("_")

    # Risk transition model
    if action == "SendDrone":
        # Drone reduces uncertainty → reduces risk slightly
        if risk == "HighRisk":   risk = "MedRisk"
        elif risk == "MedRisk":  risk = "LowRisk"

    elif action == "WaitAndObserve":
        # Waiting increases risk
        if risk == "LowRisk":    risk = "MedRisk"
        elif risk == "MedRisk":  risk = "HighRisk"

    elif action == "EvacuateNow":
        # Evacuation stabilizes or reduces risk
        if risk == "HighRisk":   risk = "MedRisk"

    elif action == "PreDeployTeams":
        # Better preparedness reduces risk
        if risk == "MedRisk":    risk = "LowRisk"

    # Resource transition model
    if action in ["EvacuateNow", "PreDeployTeams"]:
        res = "LowRes" if res == "MidRes" else "MidRes"
    elif action == "SendDrone":
        if res == "HighRes": res = "MidRes"

    next_s = f"{risk}_{res}"
    return next_s if next_s in STATES else random.choice(STATES)



def reward(state, action):
    risk, res = state.split("_")

    # Save lives in high-risk conditions
    if risk == "HighRisk" and action == "EvacuateNow":
        return 50

    if risk == "HighRisk" and action == "SendDrone":
        return 25

    # Good preparedness
    if action == "PreDeployTeams":
        return 10

    # Penalty for waiting when risk is high
    if action == "WaitAndObserve" and risk == "HighRisk":
        return -40

    # Default small penalty (time passes)
    return -1



def train_qlearning(
        episodes=2000,
        alpha=0.1,
        gamma=0.9,
        epsilon=0.1):
    
    Q = {s: {a: 0 for a in ACTIONS} for s in STATES}

    for _ in range(episodes):
        s = random.choice(STATES)

        for __ in range(20):  # max steps per episode
            # ε-greedy choice
            if random.random() < epsilon:
                a = random.choice(ACTIONS)
            else:
                a = max(Q[s], key=Q[s].get)

            r = reward(s, a)
            s_next = next_state(s, a)

            # Q-update
            Q[s][a] += alpha * (r + gamma * max(Q[s_next].values()) - Q[s][a])
            s = s_next

    return Q


def save_qtable(Q, path="data/qtable.csv"):
    df = pd.DataFrame(Q).T
    df.to_csv(path)

def load_qtable(path="data/qtable.csv"):
    df = pd.read_csv(path, index_col=0)
    return df.to_dict("index")



def extract_best_action(Q):

    return max(Q[state], key=Q[state].get)



def run_qlearning_module(train_if_missing=True):

    import os

    qpath = "data/qtable.csv"

    if os.path.exists(qpath):
        Q = load_qtable(qpath)
    else:
        Q = train_qlearning()
        save_qtable(Q, qpath)

    best = extract_best_action(Q)
    return best




if __name__ == "__main__":
    action = run_qlearning_module()
    print("\nOptimal RL Action:", action)
