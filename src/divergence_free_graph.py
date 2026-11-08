import pm4py

def get_divergence_free_graph(relations, div, rel):

    activities = set(rel) | set(relations["ocel:activity"].unique())
    global_dfg = {(a,b):0 for a in activities for b in activities}
    global_start = {a:0 for a in activities}
    global_end = {a:0 for a in activities}

    non_starts = []
    non_ends = []


    for ot in relations["ocel:type"].unique():

        sub_log = relations[relations["ocel:type"] == ot].copy()
        local_dfg, local_start, local_end = pm4py.discover_dfg(sub_log,"ocel:activity",
                                                "ocel:timestamp","ocel:oid")

        for key,value in local_dfg.items():
            if value and not (ot in div.get(key[0], set()) & div.get(key[1], set())):
                global_dfg[key] += value

        for key,value in local_start.items():
            if value:
                global_start[key] += value

        for key,value in local_end.items():
            if value:
                global_end[key] += value

        non_starts += [a for a in rel.keys() if not local_start.get(a,0) and ot in rel[a]]
        non_ends += [a for a in rel.keys() if not local_end.get(a,0) and ot in rel[a]]

    global_dfg = {key:value for key,value in global_dfg.items() if value}
    global_start = {key:value for key,value in global_start.items() if value and key not in non_starts}
    global_end = {key:value for key,value in global_end.items() if value and key not in non_ends}

    return pm4py.objects.dfg.obj.DFG(global_dfg,global_start,global_end)
