import unittest

from pitft_oob.hardware_profiles import PITFT_28R_ROTATION_270
from pitft_oob.models import ButtonAction
from pitft_oob.ui.layout import PanelLayout


class LayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = PanelLayout.from_profile(PITFT_28R_ROTATION_270)

    def test_cad_button_order_and_centers(self) -> None:
        self.assertEqual((27, 23, 22, 17), tuple(slot.gpio for slot in self.layout.rail_slots))
        self.assertEqual((8, 71, 131, 194), tuple(slot.center_y for slot in self.layout.rail_slots))
        self.assertEqual(
            (ButtonAction.SELECT, ButtonAction.DOWN, ButtonAction.UP, ButtonAction.BACK),
            tuple(slot.action for slot in self.layout.rail_slots),
        )

    def test_touch_bands_are_contiguous_and_cover_entire_rail(self) -> None:
        bounds = tuple((slot.hitbox.top, slot.hitbox.bottom) for slot in self.layout.rail_slots)
        self.assertEqual(((0, 39), (40, 100), (101, 162), (163, 239)), bounds)
        for y, expected in (
            (8, ButtonAction.SELECT),
            (71, ButtonAction.DOWN),
            (131, ButtonAction.UP),
            (194, ButtonAction.BACK),
        ):
            self.assertEqual(expected, self.layout.rail_action_at((10, y)))
        self.assertIsNone(self.layout.rail_action_at((64, 71)))

    def test_content_starts_after_rail_and_divider(self) -> None:
        self.assertEqual(61, self.layout.rail.right)
        self.assertEqual(64, self.layout.content.left)


if __name__ == "__main__":
    unittest.main()
