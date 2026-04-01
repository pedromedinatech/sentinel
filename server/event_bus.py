from typing import Callable

class EventBus:
    """
    Central event dispatcher, implements the Observer pattern.
    Subscribers register a callback and are notified when an event is published.
    """

    def __init__(self):

        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Register a callback for a given event type."""

        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: dict) -> None:
        """Notify all subscribers registered for the given event type."""

        for callback in self._subscribers.get(event_type, []):
            callback(data)