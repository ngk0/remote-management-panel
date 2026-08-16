from __future__ import annotations

from typing import Protocol, runtime_checkable

from pitft_oob.models import ActionResult


@runtime_checkable
class ActionPort(Protocol):
    def execute(self, action_id: str) -> ActionResult: ...
