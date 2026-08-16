from __future__ import annotations

from typing import Protocol, runtime_checkable

from pitft_oob.models import Observation


@runtime_checkable
class StatusProvider(Protocol):
    provider_id: str

    def collect(self) -> Observation: ...
