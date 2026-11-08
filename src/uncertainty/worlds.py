"""Stable mixed-radix indexing of global activity realizations."""

from random import Random
import sys


def world_count(choices: dict[str, tuple[str, ...]]) -> int:
    count = 1
    for values in choices.values():
        count *= len(values)
    return count


def selected_indices(total: int, max_worlds: int | None, seed: int) -> list[int]:
    if max_worlds is not None and max_worlds < 1:
        raise ValueError("max_worlds must be positive or None")
    if max_worlds is None or max_worlds >= total:
        if total > 10000:
            raise ValueError("More than 10,000 worlds; set max_worlds explicitly")
        return list(range(total))
    rng = Random(seed)
    if total <= sys.maxsize:
        return sorted(rng.sample(range(total), max_worlds))
    picked = set()
    while len(picked) < max_worlds:
        picked.add(rng.randrange(total))
    return sorted(picked)


def realize_index(choices: dict[str, tuple[str, ...]], index: int) -> dict[str, str]:
    total = world_count(choices)
    if not 0 <= index < total:
        raise ValueError("World index is out of range")
    result = {}
    for event_id in sorted(choices):
        values = tuple(sorted(choices[event_id]))
        index, digit = divmod(index, len(values))
        result[event_id] = values[digit]
    return result
