"""Reference checks for global activity choices and DF² interval semantics."""

import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pm4py

from src.uncertainty.analysis import compare_modes
from src.df2_pipeline import build_certain_df2
from src.uncertainty.intervals import aggregate_graphs
from src.uncertainty.parsing import load_annotated_ocel
from src.uncertainty.pipeline import run_uncertain_df2
from src.uncertainty.worlds import realize_index, selected_indices


ROOT = Path(__file__).resolve().parents[1]
CERTAIN = ROOT / "data/paper-example.jsonocel"
UNCERTAIN = ROOT / "data/paper-example-uncertain-activity.jsonocel"


class ActivityUncertaintyTests(unittest.TestCase):
    def test_paper_example_has_four_global_worlds(self):
        log = load_annotated_ocel(UNCERTAIN)
        self.assertEqual(log.possible_worlds, 4)
        self.assertEqual(set(log.uncertain_choices), {"e4", "e7"})
        self.assertEqual({(realize_index(log.choices, i)["e4"],
                           realize_index(log.choices, i)["e7"]) for i in range(4)},
                         {("REORDER", "SENDOUT"), ("REORDER", "CHARGE"),
                          ("REQUEST", "SENDOUT"), ("REQUEST", "CHARGE")})

    def test_selection_is_distinct_and_reproducible(self):
        self.assertEqual(selected_indices(4, 2, 42), selected_indices(4, 2, 42))
        self.assertEqual(len(set(selected_indices(4, 2, 42))), 2)
        self.assertEqual(selected_indices(4, None, 42), list(range(4)))

    def test_recorded_view_matches_certain_file(self):
        certain = run_uncertain_df2(CERTAIN)
        recorded = run_uncertain_df2(UNCERTAIN, uncertainty_enabled=False)
        self.assertEqual(certain.intervals, recorded.intervals)

    def test_world_results_match_explicit_certain_ocel_files(self):
        document = json.loads(UNCERTAIN.read_text())
        log = load_annotated_ocel(UNCERTAIN)
        expected_graphs = []
        with TemporaryDirectory() as directory:
            for index in range(4):
                labels = realize_index(log.choices, index)
                certain_document = json.loads(json.dumps(document))
                for event in certain_document["events"]:
                    event["type"] = labels[event["id"]]
                    event["attributes"] = [attr for attr in event["attributes"]
                                           if not attr["name"].startswith("unc::")]
                path = Path(directory) / f"world-{index}.jsonocel"
                path.write_text(json.dumps(certain_document))
                expected_graphs.append(build_certain_df2(pm4py.read_ocel2(str(path)).relations).graph)
        expected = aggregate_graphs(expected_graphs)
        actual = run_uncertain_df2(UNCERTAIN).intervals
        self.assertEqual(actual, expected)

    def test_interval_aggregation_uses_zero_for_absent_edges(self):
        class Graph:
            def __init__(self, edges, starts, ends):
                self.graph, self.start_activities, self.end_activities = edges, starts, ends
        intervals = aggregate_graphs([
            Graph({("A", "B"): 3}, {"A": 1}, {}),
            Graph({("B", "A"): 2}, {}, {"B": 1}),
        ])
        self.assertEqual(intervals.edges[("A", "B")], (0, 3))
        self.assertEqual(intervals.starts["A"], (0, 1))
        self.assertEqual(intervals.ends["B"], (0, 1))

    def test_property_modes_use_same_worlds_and_can_differ(self):
        per_world = run_uncertain_df2(UNCERTAIN, max_worlds=2, seed=42)
        global_result = run_uncertain_df2(UNCERTAIN, property_mode="global",
                                          max_worlds=2, seed=42)
        self.assertEqual(per_world.selected_world_indices, global_result.selected_world_indices)
        self.assertEqual(per_world.evaluated_worlds, 2)
        self.assertFalse(per_world.exact)
        self.assertIn("changed_edges", compare_modes(per_world, global_result))


if __name__ == "__main__":
    unittest.main()
