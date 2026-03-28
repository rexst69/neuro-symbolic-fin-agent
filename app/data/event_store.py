from typing import Any, Dict, List


class EventStore:
    """Singleton in-memory append-only event store for topic-based lineage."""

    _instance = None
    _topics: Dict[str, List[Dict[str, Any]]] = {
        "fin.bank.raw": [],
        "fin.stripe.raw": [],
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def append(self, topic: str, payload: Dict[str, Any]) -> None:
        """Append a payload to a topic, creating the topic if it does not exist."""
        if topic not in self._topics:
            self._topics[topic] = []
        self._topics[topic].append(dict(payload))

    def get_all(self, topic: str) -> List[Dict[str, Any]]:
        """Return all payloads stored for a topic."""
        return list(self._topics.get(topic, []))
