"""Isolation Forest model for optional event anomaly scoring."""

from collections import Counter
from typing import Any, Iterable


def _features(events: Iterable[dict[str, Any]]):
    rows = list(events)
    counts = Counter(event["source_ip"] for event in rows)
    return [[counts[event["source_ip"]], len(event.get("username", "")),
             1 if event.get("event") == "ssh_login_failure" else 0]
            for event in rows]


def train_isolation_forest(events: Iterable[dict[str, Any]], **kwargs):
    from sklearn.ensemble import IsolationForest
    rows = list(events)
    if not rows:
        raise ValueError("at least one event is required")
    model = IsolationForest(random_state=kwargs.pop("random_state", 42), **kwargs)
    model.fit(_features(rows))
    return model


def score_events(model: Any, events: Iterable[dict[str, Any]]) -> list[float]:
    return list(model.decision_function(_features(events)))
