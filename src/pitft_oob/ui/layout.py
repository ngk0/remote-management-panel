from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

from pitft_oob.models import ButtonAction, HardwareProfile


@dataclass(frozen=True, slots=True)
class Rect:
    left: int
    top: int
    right: int
    bottom: int

    def contains(self, point: tuple[int, int]) -> bool:
        x, y = point
        return self.left <= x <= self.right and self.top <= y <= self.bottom


@dataclass(frozen=True, slots=True)
class RailSlotGeometry:
    action: ButtonAction
    label: str
    gpio: int
    center_y: int
    hitbox: Rect


@dataclass(frozen=True, slots=True)
class PanelLayout:
    width: int
    height: int
    rail: Rect
    content: Rect
    header: Rect
    rail_slots: tuple[RailSlotGeometry, ...]

    @classmethod
    def from_profile(cls, profile: HardwareProfile) -> PanelLayout:
        centers = tuple(button.center_y for button in profile.buttons)
        tops = (0, *((left + right + 1) // 2 for left, right in pairwise(centers)))
        bottoms = (*(top - 1 for top in tops[1:]), profile.display_height - 1)
        slots = tuple(
            RailSlotGeometry(
                action=button.action,
                label=button.label,
                gpio=button.gpio,
                center_y=button.center_y,
                hitbox=Rect(0, top, profile.rail_width - 1, bottom),
            )
            for button, top, bottom in zip(profile.buttons, tops, bottoms, strict=True)
        )
        content_left = profile.rail_width + 2
        return cls(
            width=profile.display_width,
            height=profile.display_height,
            rail=Rect(0, 0, profile.rail_width - 1, profile.display_height - 1),
            content=Rect(
                content_left,
                0,
                profile.display_width - 1,
                profile.display_height - 1,
            ),
            header=Rect(content_left, 0, profile.display_width - 1, 32),
            rail_slots=slots,
        )

    def rail_action_at(self, point: tuple[int, int]) -> ButtonAction | None:
        if not self.rail.contains(point):
            return None
        slot = next((item for item in self.rail_slots if item.hitbox.contains(point)), None)
        return slot.action if slot else None
