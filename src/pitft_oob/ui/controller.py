from __future__ import annotations

from datetime import UTC, datetime

from pitft_oob.models import ButtonAction, HardwareProfile, InputEvent, InputKind, Snapshot
from pitft_oob.ui.layout import PanelLayout
from pitft_oob.ui.screens.home import build_home_rows
from pitft_oob.ui.screens.menu import build_menu_rows
from pitft_oob.ui.viewmodels import PanelView, RailLabelView, RowView


class PanelController:
    """Navigation state only; rendering and I/O remain outside this class."""

    PAGE_SIZE = 4

    def __init__(self, profile: HardwareProfile) -> None:
        self.profile = profile
        self.layout = PanelLayout.from_profile(profile)
        self.screen = "home"
        self.selected = 0
        self.snapshot = Snapshot(())
        self.pressed_action: ButtonAction | None = None

    def set_snapshot(self, snapshot: Snapshot) -> None:
        self.snapshot = snapshot
        rows = self._rows()
        self.selected = min(self.selected, max(0, len(rows) - 1))

    def _rows(self) -> tuple[RowView, ...]:
        if self.screen == "home":
            return build_home_rows(self.snapshot)
        if self.screen == "menu":
            return build_menu_rows()
        observation = self.snapshot.get(self.screen)
        if observation is None:
            return (RowView("Status", "UNKNOWN", self.snapshot.health),)
        if observation.facts:
            return tuple(RowView(fact.label, fact.value, fact.health) for fact in observation.facts)
        return (RowView(observation.title, observation.summary, observation.health),)

    def handle_action(self, action: ButtonAction) -> None:
        self.pressed_action = action
        rows = self._rows()
        if not rows:
            self.selected = 0
            return
        if action is ButtonAction.UP:
            self.selected = (self.selected - 1) % len(rows)
        elif action is ButtonAction.DOWN:
            self.selected = (self.selected + 1) % len(rows)
        elif action is ButtonAction.BACK:
            self.screen = "menu" if self.screen == "home" else "home"
            self.selected = 0
        elif action is ButtonAction.SELECT:
            route = rows[self.selected].route if rows else None
            if route:
                self.screen = route
                self.selected = 0

    def handle(self, event: InputEvent) -> None:
        if event.kind is InputKind.BUTTON and event.action is not None:
            self.handle_action(event.action)
            return
        if event.kind is InputKind.TOUCH and event.point is not None:
            rail_action = self.layout.rail_action_at(event.point)
            if rail_action is not None:
                self.handle_action(rail_action)
                return
            x, y = event.point
            if x >= self.layout.content.left and y > self.layout.header.bottom:
                page_start, visible_rows = self._visible_rows()
                if visible_rows:
                    row_height = (self.profile.display_height - 33) / len(visible_rows)
                    visible_index = min(
                        len(visible_rows) - 1,
                        int((y - 33) / row_height),
                    )
                    self.selected = page_start + visible_index
                    self.handle_action(ButtonAction.SELECT)

    def _visible_rows(self) -> tuple[int, tuple[RowView, ...]]:
        rows = self._rows()
        if not rows:
            return 0, ()
        page_start = (self.selected // self.PAGE_SIZE) * self.PAGE_SIZE
        return page_start, rows[page_start : page_start + self.PAGE_SIZE]

    def view(self, now: datetime | None = None) -> PanelView:
        title = "RPi Tunnel" if self.screen == "home" else self.screen.title()
        labels = tuple(
            RailLabelView(slot.action, slot.label, slot.center_y) for slot in self.layout.rail_slots
        )
        page_start, visible_rows = self._visible_rows()
        return PanelView(
            title=title,
            screen=self.screen,
            now=now or datetime.now(UTC),
            rows=visible_rows,
            selected=self.selected - page_start,
            rail_labels=labels,
            pressed_action=self.pressed_action,
        )

    def clear_press_feedback(self) -> None:
        self.pressed_action = None
