from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta

from pitft_oob.models import Health, Observation, Snapshot
from pitft_oob.ports.status import StatusProvider


class ProviderRegistry:
    def __init__(self, providers: tuple[StatusProvider, ...]) -> None:
        ids = tuple(provider.provider_id for provider in providers)
        if len(set(ids)) != len(ids):
            raise ValueError("Provider identifiers must be unique")
        self.providers = providers

    def collect(self) -> Snapshot:
        observations: list[Observation] = []
        for provider in self.providers:
            try:
                observations.append(provider.collect())
            except Exception as exc:  # Provider isolation is an availability boundary.
                observations.append(
                    Observation(
                        provider.provider_id,
                        provider.provider_id.title(),
                        Health.UNKNOWN,
                        "PROVIDER ERROR",
                        observed_at=datetime.now(UTC),
                        ttl=timedelta(seconds=5),
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )
        return Snapshot(tuple(observations))


class PollingStatusService:
    """Collects slow status outside the input/rendering thread."""

    def __init__(self, registry: ProviderRegistry, interval: float = 5.0) -> None:
        self.registry = registry
        self.interval = interval
        self._snapshot = Snapshot(())
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._refresh = threading.Event()
        self._thread = threading.Thread(target=self._run, name="status-poller", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            snapshot = self.registry.collect()
            with self._lock:
                self._snapshot = snapshot
            self._refresh.wait(self.interval)
            self._refresh.clear()

    def latest(self) -> Snapshot:
        with self._lock:
            return self._snapshot

    def refresh(self) -> None:
        self._refresh.set()

    def close(self) -> None:
        self._stop.set()
        self._refresh.set()
        if self._thread.is_alive():
            self._thread.join(timeout=5.0)
