from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pitft_oob.models import ButtonAction, Health


@dataclass(frozen=True, slots=True)
class RowView:
    label: str
    value: str
    health: Health
    route: str | None = None


@dataclass(frozen=True, slots=True)
class RailLabelView:
    action: ButtonAction
    label: str
    center_y: int


@dataclass(frozen=True, slots=True)
class PanelView:
    title: str
    screen: str
    now: datetime
    rows: tuple[RowView, ...]
    selected: int
    rail_labels: tuple[RailLabelView, ...]
    pressed_action: ButtonAction | None = None
