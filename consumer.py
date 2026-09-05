"""Kafka consumer and PostgreSQL persistence service."""

import json
import os
import time
from typing import Any

from sentinel.correlation import detect_distributed_bruteforce
from sentinel.event_schema import SecurityEvent

CREATE_EVENTS = """CREATE TABLE IF NOT EXISTS security_events (
 id BIGSERIAL PRIMARY KEY, event JSONB NOT NULL, source_ip TEXT NOT NULL,
 host TEXT NOT NULL, timestamp TIMESTAMPTZ NOT NULL, created_at TIMESTAMPTZ DEFAULT now()
)"""
CREATE_ALERTS = """CREATE TABLE IF NOT EXISTS security_alerts (
 id BIGSERIAL PRIMARY KEY, alert JSONB NOT NULL, created_at TIMESTAMPTZ DEFAULT now()
)"""


def connect_database():
    import psycopg2
    return psycopg2.connect(os.environ.get("DATABASE_URL",
        "postgresql://sentinel:sentinel@postgres:5432/sentinel"))


def store_event(connection, event: dict[str, Any]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO security_events(event, source_ip, host, timestamp) "
            "VALUES (%s, %s, %s, %s)", (json.dumps(event), event["source_ip"],
                                         event["host"], event["timestamp"]))
    connection.commit()


def store_alert(connection, alert: dict[str, Any]) -> None:
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO security_alerts(alert) VALUES (%s)",
                       (json.dumps(alert),))
    connection.commit()


def main() -> None:
    from kafka import KafkaConsumer
    connection = None
    while connection is None:
        try:
            connection = connect_database()
        except Exception as exc:
            print(f"waiting for PostgreSQL: {exc}", flush=True)
            time.sleep(2)
    with connection.cursor() as cursor:
        cursor.execute(CREATE_EVENTS)
        cursor.execute(CREATE_ALERTS)
    connection.commit()
    consumer = KafkaConsumer(
        os.environ.get("KAFKA_TOPIC", "security-events"),
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        auto_offset_reset="earliest", enable_auto_commit=True,
        group_id="sentinel-consumer",
    )
    recent: list[dict[str, Any]] = []
    for message in consumer:
        event = SecurityEvent.from_mapping(message.value).to_dict()
        store_event(connection, event)
        recent.append(event)
        for alert in detect_distributed_bruteforce(recent[-100:]):
            store_alert(connection, alert)
