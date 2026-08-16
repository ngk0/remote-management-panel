"""Immutable domain models shared by hardware and simulation adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum


class Health(StrEnum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


HEALTH_RANK: dict[Health, int] = {
    Health.OK: 0,
    Health.UNKNOWN: 1,
    Health.WARNING: 2,
    Health.CRITICAL: 3,
}


class ButtonAction(StrEnum):
    SELECT = "select"
    DOWN = "down"
    UP = "up"
    BACK = "back"


class InputKind(StrEnum):
    BUTTON = "button"
    TOUCH = "touch"


class ActionRisk(StrEnum):
    SAFE = "safe"
    DISRUPTIVE = "disruptive"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True, slots=True)
class Fact:
    label: str
    value: str
    health: Health = Health.OK


@dataclass(frozen=True, slots=True)
class Observation:
    provider_id: str
    title: str
    health: Health
    summary: str
    facts: tuple[Fact, ...] = ()
    observed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ttl: timedelta = timedelta(seconds=15)
    error: str | None = None

    def is_stale(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return current > self.observed_at + self.ttl

    def effective_health(self, now: datetime | None = None) -> Health:
        return Health.UNKNOWN if self.is_stale(now) else self.health


@dataclass(frozen=True, slots=True)
class Snapshot:
    observations: tuple[Observation, ...]
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get(self, provider_id: str) -> Observation | None:
        return next((item for item in self.observations if item.provider_id == provider_id), None)

    @property
    def health(self) -> Health:
        if not self.observations:
            return Health.UNKNOWN
        return max(
            (item.effective_health(self.captured_at) for item in self.observations),
            key=HEALTH_RANK.__getitem__,
        )


@dataclass(frozen=True, slots=True)
class ButtonSlot:
    gpio: int
    center_y: int
    action: ButtonAction
    label: str


@dataclass(frozen=True, slots=True)
class HardwareProfile:
    profile_id: str
    display_width: int
    display_height: int
    rotation: int
    rail_width: int
    buttons: tuple[ButtonSlot, ...]
    source_url: str


@dataclass(frozen=True, slots=True)
class InputEvent:
    kind: InputKind
    action: ButtonAction | None = None
    point: tuple[int, int] | None = None


@dataclass(frozen=True, slots=True)
class ActionSpec:
    action_id: str
    label: str
    risk: ActionRisk
    capability: str


@dataclass(frozen=True, slots=True)
class ActionResult:
    action_id: str
    accepted: bool
    message: str
