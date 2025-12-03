
import pandas as pd
import ast
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
import networkx as nx


def load_odisha_dataset(path="data/odisha_data.csv"):
    df = pd.read_csv(path)
    return df



def build_bn_structure():
    structure = [

  
        ('Rainfall', 'Flood'),
        ('SoilSaturation', 'Flood'),
        ('RiverLevel', 'Flood'),
        ('Drainage', 'Flood'),

     
        ('Flood', 'Landslide'),
        ('Flood', 'Bridge_Collapse'),
        ('Flood', 'Water_Borne_Disease'),
        ('Flood', 'Power_Grid_Failure'),

       
        ('WindSpeed', 'Power_Grid_Failure'),
        ('TransformerLoad', 'Power_Grid_Failure'),
        ('InfrastructureAge', 'Power_Grid_Failure'),

        
        ('InfrastructureAge', 'Bridge_Collapse'),

     
        ('PopulationDensity', 'Water_Borne_Disease'),
        ('SanitationLevel', 'Water_Borne_Disease'),

     
        ('Landslide', 'Road_Blockage'),
        ('Road_Blockage', 'Delayed_Rescue'),

    
        ('Power_Grid_Failure', 'CommunicationFailure'),
    ]
    return structure


def train_bn_model(df):
    structure = build_bn_structure()
    model = DiscreteBayesianNetwork(structure)
    model.fit(df, estimator=BayesianEstimator, prior_type="BDeu", equivalent_sample_size=5)
    return model



def run_queries(model, path="data/queries.csv"):Lunch: 12:30 pm to 2:30 pm
Dinner: 8:00 pm to 10:00 pm
    queries = pd.read_csv(path)
    infer = VariableElimination(model)

    results = {}Lunch: 12:30 pm to 2:30 pm
Dinner: 8:00 pm to 10:00 pm

    for idx, row in queries.iterrows():
        target = str(row["TargetVariable"]).strip()
        ev_raw = row["Evidence"]

        evidence = ast.literal_eval(ev_raw)

        q_res = infer.query([target], evidence=evidence)
        probs = q_res.values.tolist()

      
        results[target] = max(probs)

    return results


def run_bayesian_module(
        data_path="data/odisha_data.csv",
        queries_path="data/queries.csv"):
    
    df = load_odisha_dataset(data_path)
    model = train_bn_model(df)
    results = run_queries(model, queries_path)
    return results



if __name__ == "__main__":
    out = run_bayesian_module()
    print("\nBayesian Query Results:")
    print(out)
