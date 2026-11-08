"""Notebook-ready summaries and mode comparisons."""

import pandas as pd


def log_metrics(log) -> dict:
    return {
        "events": len(log.events),
        "objects": len(log.objects),
        "event_object_relations": len(log.relations),
        "uncertain_activity_events": len(log.uncertain_choices),
        "activity_candidates": sum(len(x) for x in log.uncertain_choices.values()),
        "possible_worlds": log.possible_worlds,
        "uncertainty_types": ["activity"] if log.uncertain_choices else [],
    }


def interval_table(intervals, kind="edges") -> pd.DataFrame:
    mapping = getattr(intervals, kind)
    if kind == "edges":
        rows = [{"source": a, "target": b, "min": low, "max": high, "width": high-low}
                for (a,b),(low,high) in mapping.items()]
        columns = ["source", "target", "min", "max", "width"]
    else:
        rows = [{"activity": a, "min": low, "max": high, "width": high-low}
                for a,(low,high) in mapping.items()]
        columns = ["activity", "min", "max", "width"]
    return pd.DataFrame(rows, columns=columns).sort_values(columns[:2] if kind == "edges" else columns[:1]).reset_index(drop=True)


def compare_modes(per_world, global_result) -> dict:
    if per_world.selected_world_indices != global_result.selected_world_indices:
        raise ValueError("Mode comparisons require the same selected worlds")
    exact, approx = per_world.intervals, global_result.intervals
    all_keys = set(exact.edges) | set(approx.edges)
    changed = {key: (exact.edges.get(key, (0, 0)), approx.edges.get(key, (0, 0)))
               for key in all_keys if exact.edges.get(key, (0, 0)) != approx.edges.get(key, (0, 0))}
    return {
        "changed_edges": len(changed),
        "changed_edge_bounds": changed,
        "per_world_seconds": per_world.elapsed_seconds,
        "global_seconds": global_result.elapsed_seconds,
    }
