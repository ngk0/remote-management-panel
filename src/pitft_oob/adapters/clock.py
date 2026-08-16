from __future__ import annotations

import time
from datetime import datetime


class SystemClock:
    def now(self) -> datetime:
        return datetime.now().astimezone()

    def monotonic(self) -> float:
        return time.monotonic()
