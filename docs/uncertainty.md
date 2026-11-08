# Activity uncertainty in DF²

Open `notebooks/uncertain_df2.ipynb` from the repository root and run its cells in order. Its default input is the four-world paper example. The first cell controls the input, property mode, activity coverage, world limit, seed, and PNG output.

An event's recorded `type` is its representative label. An optional declared string attribute named `unc::<recorded type>::type::candidates` contains a JSON-encoded array of admissible labels. The parser requires the recorded label to be included. A missing annotation means a singleton choice. All object traces share an event's one chosen label within a world.

`per_world` recalculates interaction properties and the DF² graph for every world. `global` calculates interaction properties once from the recorded labels, then reuses them while recalculating each world's graph. The latter is an approximation when uncertainty changes the properties. Both modes apply activity coverage filtering within each world.

`max_worlds=None` evaluates all worlds, with a 10,000-world safety limit. A smaller value selects distinct worlds uniformly without replacement. The seed and stable event/candidate ordering reproduce the same selection. Sampled intervals are observed ranges, not guaranteed bounds over every possible world.

The interval graph uses the baseline's `(source activity, target activity)` edge keys. Missing edges count as zero in a world. Start and end intervals retain the baseline's PM4Py counts and related-type suppression. A timestamped PNG is saved in the ignored `output/` directory when enabled.

Run the reference checks with:

```sh
.venv/bin/python -m unittest discover -s tests -v
```
