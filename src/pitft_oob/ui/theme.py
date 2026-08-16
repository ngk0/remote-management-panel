from __future__ import annotations

from dataclasses import dataclass

RGB = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class Theme:
    background: RGB = (0, 0, 0)
    header: RGB = (8, 16, 20)
    rail: RGB = (0, 0, 0)
    selected: RGB = (22, 62, 71)
    accent: RGB = (98, 210, 227)
    ok: RGB = (99, 229, 162)
    warning: RGB = (246, 199, 91)
    critical: RGB = (255, 107, 107)
    unknown: RGB = (151, 174, 181)
    text: RGB = (239, 247, 248)
    muted: RGB = (151, 174, 181)
    divider: RGB = (41, 55, 58)


BLACK_THEME = Theme()
