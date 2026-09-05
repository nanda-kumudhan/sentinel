"""Small Kafka producer adapter; importing this module never requires Kafka."""

import json
import logging
from typing import Any

log = logging.getLogger(__name__)


class EventProducer:
    def __init__(self, bootstrap_servers: str, topic: str = "security-events") -> None:
        self.topic = topic
        self._producer = None
        try:
            from kafka import KafkaProducer
            self._producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(","),
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                retries=3,
            )
        except Exception as exc:  # local logging must continue if Kafka is unavailable
            log.warning("Kafka producer unavailable: %s", exc)

    def send(self, event: dict[str, Any]) -> bool:
        if self._producer is None:
            return False
        try:
            self._producer.send(self.topic, event)
            self._producer.flush(timeout=5)
            return True
        except Exception as exc:
            log.warning("Kafka send failed: %s", exc)
            return False

    def close(self) -> None:
        if self._producer is not None:
            self._producer.close()
