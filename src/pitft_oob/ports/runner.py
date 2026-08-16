from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class CommandResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


@runtime_checkable
class CommandRunner(Protocol):
    def run(self, argv: Sequence[str], timeout: float) -> CommandResult: ...
