"""Pillow renderer; imports Pillow lazily so non-visual core tests stay portable."""

from __future__ import annotations

from typing import Any

from pitft_oob.models import Health
from pitft_oob.ui.layout import PanelLayout
from pitft_oob.ui.theme import BLACK_THEME, Theme
from pitft_oob.ui.viewmodels import PanelView


class PillowRenderer:
    def __init__(self, layout: PanelLayout, theme: Theme = BLACK_THEME, extra_large: bool = False):
        self.layout = layout
        self.theme = theme
        self.extra_large = extra_large

    @staticmethod
    def _font(size: int, bold: bool = False) -> Any:
        from PIL import ImageFont

        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            return ImageFont.load_default()

    def _health_color(self, health: Health) -> tuple[int, int, int]:
        return {
            Health.OK: self.theme.ok,
            Health.WARNING: self.theme.warning,
            Health.CRITICAL: self.theme.critical,
            Health.UNKNOWN: self.theme.unknown,
        }[health]

    @staticmethod
    def _fit(draw: Any, text: str, font: Any, max_width: int) -> str:
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return text
        marker = "..."
        value = text
        while value and draw.textbbox((0, 0), value + marker, font=font)[2] > max_width:
            value = value[:-1]
        if value:
            return value + marker
        marker_width = draw.textbbox((0, 0), marker, font=font)[2]
        return marker if marker_width <= max_width else ""

    def render(self, view: PanelView) -> Any:
        from PIL import Image, ImageDraw

        image = Image.new("RGB", (self.layout.width, self.layout.height), self.theme.background)
        draw = ImageDraw.Draw(image)
        title_font = self._font(21 if not self.extra_large else 23, bold=True)
        row_font = self._font(17 if not self.extra_large else 19, bold=True)
        value_font = self._font(14 if not self.extra_large else 16)
        rail_font = self._font(12 if not self.extra_large else 13, bold=True)
        small_font = self._font(11)

        # Permanent rail: labels and cyan ticks align with the physical switch centers.
        draw.rectangle(
            (self.layout.rail.left, 0, self.layout.rail.right, self.layout.height - 1),
            fill=self.theme.rail,
        )
        draw.line(
            (self.layout.rail.right, 0, self.layout.rail.right, self.layout.height - 1),
            fill=self.theme.divider,
        )
        slots_by_action = {slot.action: slot for slot in self.layout.rail_slots}
        for item in view.rail_labels:
            slot = slots_by_action[item.action]
            if item.action is view.pressed_action:
                draw.rectangle(
                    (slot.hitbox.left, slot.hitbox.top, slot.hitbox.right, slot.hitbox.bottom),
                    fill=self.theme.selected,
                )
            draw.line(
                (
                    self.layout.rail.right - 6,
                    item.center_y,
                    self.layout.rail.right,
                    item.center_y,
                ),
                fill=self.theme.accent,
                width=2,
            )
            text = self._fit(draw, item.label, rail_font, self.layout.rail.right - 7)
            box = draw.textbbox((0, 0), text, font=rail_font)
            text_width = box[2] - box[0]
            text_height = box[3] - box[1]
            text_y = max(
                0,
                min(self.layout.height - text_height, item.center_y - text_height // 2),
            )
            draw.text(
                ((self.layout.rail.right - text_width) // 2, text_y),
                text,
                font=rail_font,
                fill=self.theme.text,
            )

        # Content header and rows never overlap the physical-control rail.
        draw.rectangle(
            (
                self.layout.header.left,
                self.layout.header.top,
                self.layout.header.right,
                self.layout.header.bottom,
            ),
            fill=self.theme.header,
        )
        draw.text(
            (self.layout.content.left + 8, 4),
            self._fit(draw, view.title, title_font, 165),
            font=title_font,
            fill=self.theme.text,
        )
        clock = view.now.strftime("%H:%M")
        clock_width = draw.textbbox((0, 0), clock, font=value_font)[2]
        draw.text(
            (self.layout.width - clock_width - 8, 8),
            clock,
            font=value_font,
            fill=self.theme.muted,
        )

        rows = view.rows[:4]
        body_top = self.layout.header.bottom + 1
        row_height = (self.layout.height - body_top) // max(1, len(rows))
        for index, row in enumerate(rows):
            top = body_top + index * row_height
            bottom = self.layout.height - 1 if index == len(rows) - 1 else top + row_height
            if index == view.selected:
                draw.rectangle(
                    (self.layout.content.left, top, self.layout.width - 1, bottom),
                    fill=self.theme.selected,
                )
                draw.rectangle(
                    (self.layout.content.left, top, self.layout.content.left + 4, bottom),
                    fill=self.theme.accent,
                )
            draw.line(
                (self.layout.content.left, bottom, self.layout.width - 1, bottom),
                fill=self.theme.divider,
            )
            draw.text(
                (self.layout.content.left + 9, top + 10),
                self._fit(draw, row.label, row_font, 112),
                font=row_font,
                fill=self.theme.text,
            )
            value = self._fit(draw, row.value, value_font, 118)
            value_width = draw.textbbox((0, 0), value, font=value_font)[2]
            color = self.theme.text if index == view.selected else self._health_color(row.health)
            draw.text(
                (self.layout.width - value_width - 8, top + 12),
                value,
                font=value_font,
                fill=color,
            )

        if not rows:
            draw.text(
                (self.layout.content.left + 9, 54),
                "No status observations",
                font=small_font,
                fill=self.theme.unknown,
            )
        return image
