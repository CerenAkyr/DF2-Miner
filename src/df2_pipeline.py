"""Reusable certain DF² construction, also used for realized worlds."""

from dataclasses import dataclass

import pandas as pd

from src.divergence_free_graph import get_divergence_free_graph
from src.interaction_properties import get_interaction_patterns


@dataclass
class CertainResult:
    graph: object
    properties: tuple[dict, dict, dict, dict]
    relations: pd.DataFrame


def keep_most_frequent_activities(relations: pd.DataFrame, coverage: float):
    if not 0 < coverage <= 1:
        raise ValueError("activity_coverage must be in (0, 1]")
    counts = relations.groupby("ocel:activity")["ocel:eid"].nunique()
    if counts.empty:
        return relations.copy()
    counts = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    selected = set()
    cumulative = 0
    total = sum(count for _, count in counts)
    for activity, count in counts:
        selected.add(activity)
        cumulative += count
        if cumulative / total >= coverage:
            break
    return relations[relations["ocel:activity"].isin(selected)].copy()


def build_certain_df2(relations: pd.DataFrame, activity_coverage: float = 1.0,
                      properties: tuple | None = None) -> CertainResult:
    filtered = keep_most_frequent_activities(relations, activity_coverage)
    if filtered.empty:
        raise ValueError("No event-object relations remain after filtering")
    used_properties = properties if properties is not None else get_interaction_patterns(filtered)
    div, con, rel, defi = used_properties
    graph = get_divergence_free_graph(filtered, div, rel)
    return CertainResult(graph, used_properties, filtered)
