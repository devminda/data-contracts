from dataclasses import dataclass, field
from datetime import datetime

from data_contracts.diff import MigrationReport


@dataclass
class Consumer:
    name: str
    contact: str
    subscribed_schemas: list[str] = field(default_factory=list)


class NotificationBus:
    def __init__(self) -> None:
        self._consumers: list[Consumer] = []
        self._log: list[dict] = []

    def register(self, consumer: Consumer) -> None:
        self._consumers.append(consumer)

    def notify(self, report: MigrationReport) -> None:
        if not report.is_breaking:
            return
        for consumer in self._consumers:
            if report.schema_name in consumer.subscribed_schemas:
                entry = {
                    "to": consumer.name,
                    "contact": consumer.contact,
                    "schema": report.schema_name,
                    "breaking_fields": [c.field_name for c in report.breaking_changes],
                    "timestamp": datetime.now().isoformat(),
                }
                self._log.append(entry)
                print(
                    f"Notified {consumer.name} ({consumer.contact}): "
                    f"breaking change in '{report.schema_name}'"
                )

    def get_log(self) -> list[dict]:
        return list(self._log)
