import unittest
from datetime import UTC, datetime

from pitft_oob.hardware_profiles import PITFT_28R_ROTATION_270
from pitft_oob.models import ButtonAction, InputEvent, InputKind, Snapshot
from pitft_oob.providers.synthetic import synthetic_observations
from pitft_oob.ui.controller import PanelController


class ControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        self.controller = PanelController(PITFT_28R_ROTATION_270)
        self.controller.set_snapshot(Snapshot(synthetic_observations(now), now))

    def test_buttons_navigate_without_rendering_or_hardware(self) -> None:
        self.assertEqual("Remote Panel", self.controller.view().title)
        self.controller.handle_action(ButtonAction.DOWN)
        self.assertEqual(1, self.controller.selected)
        self.controller.handle_action(ButtonAction.SELECT)
        self.assertEqual("network", self.controller.screen)
        self.controller.handle_action(ButtonAction.BACK)
        self.assertEqual("home", self.controller.screen)

    def test_touching_left_rail_invokes_adjacent_physical_action(self) -> None:
        self.controller.selected = 2
        self.controller.handle(InputEvent(InputKind.TOUCH, point=(12, 71)))
        self.assertEqual(3, self.controller.selected)
        self.assertEqual(ButtonAction.DOWN, self.controller.pressed_action)

    def test_menu_is_real_and_pages_all_status_routes(self) -> None:
        self.controller.selected = 3
        self.controller.handle_action(ButtonAction.SELECT)
        self.assertEqual("menu", self.controller.screen)
        self.assertEqual(5, len(self.controller._rows()))

        for _ in range(4):
            self.controller.handle_action(ButtonAction.DOWN)
        view = self.controller.view()
        self.assertEqual(0, view.selected)
        self.assertEqual(("Services",), tuple(row.label for row in view.rows))

        self.controller.handle(
            InputEvent(
                InputKind.TOUCH,
                point=(self.controller.layout.content.left + 10, 60),
            )
        )
        self.assertEqual("services", self.controller.screen)


if __name__ == "__main__":
    unittest.main()
