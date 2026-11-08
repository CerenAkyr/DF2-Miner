"""Render an interval DF² diagram with boundary nodes and an interval ledger."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch


INK = "#344963"
BLUE = "#1268e8"
PAPER = {"REQUEST", "CHARGE", "REORDER", "SENDOUT"}


def _positions(activities, rows):
    if set(activities) == PAPER:
        return {"REQUEST": (3.4, 5.5), "CHARGE": (7.2, 5.5),
                "REORDER": (3.4, 2.4), "SENDOUT": (7.2, 2.4)}
    return {name: (3.4 + 3.8 * (i % 2), 1.75 + 3.1 * (rows - 1 - i // 2))
            for i, name in enumerate(sorted(activities))}


def _arrow(ax, start, end, *, color=INK, rad=0, patch_a=None, patch_b=None, width=1.5):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=15, linewidth=width,
        color=color, connectionstyle=f"arc3,rad={rad}",
        patchA=patch_a, patchB=patch_b, shrinkA=2, shrinkB=2, zorder=2))


def _label(interval):
    return f"[{interval[0]}, {interval[1]}]"


def _edge_label_position(source, target, positions):
    if set(positions) == PAPER:
        fixed = {
            ("REQUEST", "CHARGE"): (5.3, 5.8),
            ("CHARGE", "SENDOUT"): (7.65, 4.0),
            ("SENDOUT", "CHARGE"): (6.75, 4.0),
            ("REQUEST", "REORDER"): (3.85, 4.0),
            ("REORDER", "REQUEST"): (2.95, 4.0),
            ("REQUEST", "SENDOUT"): (5.1, 4.7),
            ("SENDOUT", "REQUEST"): (5.55, 3.3),
            ("REORDER", "CHARGE"): (5.85, 4.6),
            ("SENDOUT", "REORDER"): (5.3, 2.0),
            ("REORDER", "SENDOUT"): (5.3, 2.8),
        }
        if (source, target) in fixed:
            return fixed[source, target]
    x1, y1 = positions[source]
    x2, y2 = positions[target]
    return ((x1+x2)/2, (y1+y2)/2)


def save_interval_png(result, output_dir: str | Path = "output") -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%Y%m%d_%H%M%S_%f")
    path = output_dir / f"df2_{stamp}.png"

    intervals = result.intervals
    activities = set(intervals.starts) | set(intervals.ends)
    for source, target in intervals.edges:
        activities.update((source, target))
    rows = (len(activities)+1)//2
    height = max(8.2, 3.1 * rows + 2,
                 2.7 + 0.255 * (len(intervals.edges) + len(intervals.starts) +
                                len(intervals.ends)))
    positions = _positions(activities, rows)
    fig, ax = plt.subplots(figsize=(16, height))
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, height)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(5.1, height-0.35, "Possible-world interval DF² graph",
            ha="center", va="top", fontsize=20, fontweight="bold")

    patches = {}
    for activity, (x, y) in positions.items():
        patch = Ellipse((x, y), 1.37, 1.77, facecolor="#f7f9fb",
                        edgecolor=INK, linewidth=1.7, zorder=4)
        ax.add_patch(patch)
        patches[activity] = patch
        ax.text(x, y, activity, ha="center", va="center", fontsize=10,
                fontweight="bold", zorder=5)

    middle_y = (max(y for _, y in positions.values()) +
                min(y for _, y in positions.values())) / 2 if positions else 4
    for name, center in (("START", (1.15, middle_y)), ("END", (9.4, middle_y))):
        ax.add_patch(Ellipse(center, 1.05, 1.25, facecolor="#d8eafd",
                             edgecolor=INK, linewidth=1.7, zorder=4))
        ax.text(*center, name, ha="center", va="center", fontsize=10,
                fontweight="bold", zorder=5)

    for (source, target), interval in sorted(intervals.edges.items()):
        x, y = positions[source]
        if source == target:
            side = 1 if y >= middle_y else -1
            _arrow(ax, (x-0.42, y+side*0.75), (x+0.42, y+side*0.75),
                   rad=-0.85*side)
            label_at = (x, y+side*1.43)
        else:
            reverse = (target, source) in intervals.edges
            _arrow(ax, positions[source], positions[target],
                   rad=0.13 if reverse else 0,
                   patch_a=patches[source], patch_b=patches[target])
            label_at = _edge_label_position(source, target, positions)
        ax.text(*label_at, _label(interval), ha="center", va="center",
                fontsize=9, fontweight="bold", color=INK, zorder=6,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 0.6})

    for activity, interval in sorted(intervals.starts.items()):
        x, y = positions[activity]
        _arrow(ax, (1.67, middle_y), (x-0.69, y), color=BLUE, width=1.8)
        ax.text((1.67+x-0.69)/2, (middle_y+y)/2+0.27, _label(interval),
                color=BLUE, ha="center", fontsize=9.5, fontweight="bold", zorder=6)
    for activity, interval in sorted(intervals.ends.items()):
        x, y = positions[activity]
        _arrow(ax, (x+0.69, y), (8.85, middle_y), color=BLUE, width=1.8)
        ax.text((x+0.69+8.85)/2, (y+middle_y)/2+0.27, _label(interval),
                color=BLUE, ha="center", fontsize=9.5, fontweight="bold", zorder=6)

    ledger_x, ledger_y = 11.1, height-0.9
    ax.text(ledger_x, ledger_y, "EDGE FREQUENCY INTERVALS",
            fontsize=10.5, color=INK, va="top")
    ledger_y -= 0.43
    for (source, target), interval in sorted(intervals.edges.items()):
        ax.text(ledger_x, ledger_y, f"{source} → {target}   {_label(interval)}",
                fontsize=9.5, color=INK, va="top")
        ledger_y -= 0.255
    ledger_y -= 0.3
    ax.text(ledger_x, ledger_y, "BOUNDARIES", fontsize=10.5, color=INK, va="top")
    ledger_y -= 0.35
    for name, mapping in (("START", intervals.starts), ("END", intervals.ends)):
        for activity, interval in sorted(mapping.items()):
            description = f"START → {activity}" if name == "START" else f"{activity} → END"
            ax.text(ledger_x, ledger_y, f"{description}   {_label(interval)}",
                    fontsize=9.5, color=INK, va="top")
            ledger_y -= 0.255

    if result.exact:
        note = "Exact [min, max] over all consistent worlds; absent edges count as 0."
    else:
        note = (f"Observed [min, max] over {result.evaluated_worlds}/{result.total_worlds} worlds; "
                "absent edges count as 0.")
        if result.property_mode == "global":
            note += " Approximation: recorded-label properties are reused."
    ax.text(0.3, 0.35, note, fontsize=9.5, color=INK)
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path
