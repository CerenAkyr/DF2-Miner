"""Aggregate certain DF² graphs into observed frequency intervals."""

from dataclasses import dataclass


@dataclass
class IntervalGraph:
    edges: dict[tuple[str, str], tuple[int, int]]
    starts: dict[str, tuple[int, int]]
    ends: dict[str, tuple[int, int]]

    def metrics(self) -> dict:
        widths = [high - low for low, high in self.edges.values()]
        return {
            "edges": len(self.edges),
            "always_present_edges": sum(low > 0 for low, _ in self.edges.values()),
            "possible_only_edges": sum(low == 0 for low, _ in self.edges.values()),
            "variable_edges": sum(width > 0 for width in widths),
            "total_edge_interval_width": sum(widths),
            "widest_edge_interval": max(widths, default=0),
            "start_activities": len(self.starts),
            "end_activities": len(self.ends),
        }


def _bounds(mappings):
    keys = set().union(*(mapping.keys() for mapping in mappings))
    return {
        key: (min(mapping.get(key, 0) for mapping in mappings),
              max(mapping.get(key, 0) for mapping in mappings))
        for key in keys if any(mapping.get(key, 0) for mapping in mappings)
    }


def aggregate_graphs(graphs: list) -> IntervalGraph:
    if not graphs:
        raise ValueError("At least one world graph is required")
    return IntervalGraph(
        _bounds([graph.graph for graph in graphs]),
        _bounds([graph.start_activities for graph in graphs]),
        _bounds([graph.end_activities for graph in graphs]),
    )
