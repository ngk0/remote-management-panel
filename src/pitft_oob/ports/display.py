from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class DisplayPort(Protocol):
    width: int
    height: int

    def present(self, image: object) -> None: ...

    def close(self) -> None: ...
