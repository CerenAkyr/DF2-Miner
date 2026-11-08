"""Evaluate activity worlds using exact or representative interaction properties."""

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from src.df2_pipeline import build_certain_df2
from src.interaction_properties import get_interaction_patterns
from src.df2_pipeline import keep_most_frequent_activities
from src.uncertainty.intervals import IntervalGraph, aggregate_graphs
from src.uncertainty.parsing import AnnotatedLog, load_annotated_ocel
from src.uncertainty.worlds import realize_index, selected_indices


@dataclass
class UncertainResult:
    intervals: IntervalGraph
    total_worlds: int
    evaluated_worlds: int
    selected_world_indices: list[int]
    property_mode: str
    elapsed_seconds: float
    log: AnnotatedLog
    png_path: Path | None = None

    @property
    def exhaustive(self):
        return self.evaluated_worlds == self.total_worlds

    @property
    def exact(self):
        return self.exhaustive and (self.property_mode == "per_world" or self.total_worlds == 1)


def run_uncertain_df2(path: str | Path, *, uncertainty_enabled: bool = True,
                      uncertainty_kinds: tuple[str, ...] = ("activity",),
                      property_mode: str = "per_world", activity_coverage: float = 1.0,
                      max_worlds: int | None = None, seed: int = 0,
                      save_png: bool = False, output_dir: str | Path = "output") -> UncertainResult:
    if set(uncertainty_kinds) != {"activity"}:
        raise ValueError("Only activity uncertainty is supported")
    if property_mode not in {"per_world", "global"}:
        raise ValueError("property_mode must be 'per_world' or 'global'")
    started = perf_counter()
    log = load_annotated_ocel(path)
    choices = log.choices if uncertainty_enabled else {eid: (label,) for eid, label in log.recorded.items()}
    total = 1
    for values in choices.values():
        total *= len(values)
    indices = selected_indices(total, max_worlds, seed)

    global_properties = None
    if property_mode == "global":
        representative = keep_most_frequent_activities(log.relations, activity_coverage)
        global_properties = get_interaction_patterns(representative)

    graphs = []
    for index in indices:
        activities = realize_index(choices, index)
        relations = log.relations.copy()
        relations["ocel:activity"] = relations["ocel:eid"].map(activities)
        certain = build_certain_df2(relations, activity_coverage, global_properties)
        graphs.append(certain.graph)

    result = UncertainResult(aggregate_graphs(graphs), total, len(indices), indices,
                             property_mode, perf_counter() - started, log)
    if save_png:
        from src.uncertainty.rendering import save_interval_png
        result.png_path = save_interval_png(result, output_dir)
    return result
