import pm4py
from src.interaction_properties import get_interaction_patterns
from src.divergence_free_graph import get_divergence_free_graph
from src.oc_process_trees import load_from_pt
from src.df2_pipeline import build_certain_df2, keep_most_frequent_activities




def df2_miner_apply(log_path, activity_coverage):

    try:
        input_log = pm4py.read_ocel2(log_path).relations
    except:
        input_log = pm4py.read_ocel(log_path).relations

    #do any sort of preprocessing of the log here
    #strongly recommended, as no noise is filtered
    #typically, we remove infrequent activities
    result = build_certain_df2(input_log, activity_coverage)
    div, con, rel, defi = result.properties
    print("Interacting Properties Done")
    df2_graph = result.graph
    print("DF2 Graph Done")
    process_tree = pm4py.discover_process_tree_inductive(df2_graph)
    print("Traditional Process Tree Done")
    ocpt = load_from_pt(process_tree,rel,div,con,defi)
    print("Object-Centric Process Tree Done")
    return ocpt



