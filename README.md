# DF2-Miner

To set up the environment, run this once:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Certain DF² miner

```sh
.venv/bin/python main.py
```

This runs the existing certain OCEL example in `data/running-example.jsonocel` and prints the discovered object-centric process tree.

## Uncertain activity-label DF² graph

```sh
.venv/bin/jupyter notebook notebooks/uncertain_df2.ipynb
```

In this notebook, first cell is to configure the pipeline.
The supplied uncertain example has four possible worlds. Run the remaining cells to see the graph and analysis.
Also when enabled, a timestamped interval-graph PNG is saved in `output/`.
