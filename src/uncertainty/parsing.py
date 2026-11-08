"""Read the local OCEL 2.0 activity-candidate convention."""

from dataclasses import dataclass
import json
from pathlib import Path

import pm4py


@dataclass
class AnnotatedLog:
    path: Path
    relations: object
    events: list[dict]
    objects: list[dict]
    choices: dict[str, tuple[str, ...]]
    recorded: dict[str, str]

    @property
    def uncertain_choices(self):
        return {event_id: values for event_id, values in self.choices.items() if len(values) > 1}

    @property
    def possible_worlds(self):
        result = 1
        for values in self.uncertain_choices.values():
            result *= len(values)
        return result


def load_annotated_ocel(path: str | Path) -> AnnotatedLog:
    path = Path(path)
    document = json.loads(path.read_text(encoding="utf-8"))
    required = {"eventTypes", "objectTypes", "events", "objects"}
    if not required.issubset(document):
        raise ValueError(f"Expected OCEL 2.0 keys: {sorted(required)}")
    declarations = {
        entry["name"]: {attr["name"]: attr["type"] for attr in entry.get("attributes", [])}
        for entry in document["eventTypes"]
    }
    choices, recorded = {}, {}
    for event in document["events"]:
        event_id, activity = event["id"], event["type"]
        if event_id in choices:
            raise ValueError(f"Duplicate event ID: {event_id}")
        if activity not in declarations:
            raise ValueError(f"Undeclared event type {activity} on {event_id}")
        if any(str(key).startswith("unc::") for relationship in event.get("relationships", [])
               for key in relationship):
            raise ValueError(f"Relationship uncertainty is not supported on {event_id}")
        name = f"unc::{activity}::type::candidates"
        annotation = [attr for attr in event.get("attributes", []) if attr.get("name") == name]
        other_unc = [attr["name"] for attr in event.get("attributes", [])
                     if str(attr.get("name", "")).startswith("unc::") and attr.get("name") != name]
        if other_unc:
            raise ValueError(f"Unsupported uncertainty annotation on {event_id}: {other_unc}")
        if len(annotation) > 1:
            raise ValueError(f"Duplicate activity annotation on {event_id}")
        if annotation:
            if declarations[activity].get(name) != "string":
                raise ValueError(f"Activity annotation is not declared as string for {activity}")
            value = annotation[0]["value"]
            if not isinstance(value, str):
                raise ValueError(f"Activity candidates for {event_id} must be a JSON string")
            try:
                candidates = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid activity candidates for {event_id}") from exc
            if (not isinstance(candidates, list) or not candidates
                    or any(not isinstance(x, str) or x not in declarations for x in candidates)
                    or len(candidates) != len(set(candidates)) or activity not in candidates):
                raise ValueError(f"Invalid activity candidates for {event_id}: {candidates}")
            choices[event_id] = tuple(sorted(candidates))
        else:
            choices[event_id] = (activity,)
        recorded[event_id] = activity
    for obj in document["objects"]:
        if any(str(key).startswith("unc::") for relationship in obj.get("relationships", [])
               for key in relationship):
            raise ValueError(f"Relationship uncertainty is not supported on object {obj['id']}")
    relations = pm4py.read_ocel2(str(path)).relations
    return AnnotatedLog(path, relations, document["events"], document["objects"], choices, recorded)
