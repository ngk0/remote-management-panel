from __future__ import annotations

from typing import Protocol, runtime_checkable

from pitft_oob.models import InputEvent


@runtime_checkable
class InputPort(Protocol):
    def poll(self, timeout: float) -> tuple[InputEvent, ...]: ...

    def close(self) -> None: ...
