from __future__ import annotations

import time
from collections import deque

from pitft_oob.models import InputEvent


class QueueInput:
    def __init__(self, events: tuple[InputEvent, ...] = ()) -> None:
        self._events = deque(events)

    def push(self, event: InputEvent) -> None:
        self._events.append(event)

    def poll(self, timeout: float) -> tuple[InputEvent, ...]:
        if not self._events:
            time.sleep(timeout)
            return ()
        return (self._events.popleft(),)

    def close(self) -> None:
        self._events.clear()
