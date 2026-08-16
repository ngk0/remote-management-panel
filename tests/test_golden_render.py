import importlib.util
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from pitft_oob.adapters.simulation.display import FileDisplay
from pitft_oob.hardware_profiles import PITFT_28R_ROTATION_270
from pitft_oob.models import Snapshot
from pitft_oob.providers.synthetic import synthetic_observations
from pitft_oob.ui.controller import PanelController
from pitft_oob.ui.layout import PanelLayout
from pitft_oob.ui.render import PillowRenderer
from pitft_oob.ui.theme import BLACK_THEME

PILLOW_AVAILABLE = importlib.util.find_spec("PIL") is not None


@unittest.skipUnless(PILLOW_AVAILABLE, "Pillow render dependency is not installed")
class GoldenRenderTests(unittest.TestCase):
    def test_clipping_uses_safe_ascii_marker_and_respects_width(self) -> None:
        from PIL import Image, ImageDraw

        renderer = PillowRenderer(PanelLayout.from_profile(PITFT_28R_ROTATION_270))
        draw = ImageDraw.Draw(Image.new("RGB", (320, 240)))
        font = renderer._font(14)
        clipped = renderer._fit(draw, "A deliberately overlong status value", font, 64)
        self.assertTrue(clipped.endswith("..."))
        self.assertNotIn(chr(0xE2), clipped)
        self.assertLessEqual(draw.textbbox((0, 0), clipped, font=font)[2], 64)

    def test_synthetic_home_render_has_black_rail_and_cad_ticks(self) -> None:
        fixed = datetime(2026, 1, 1, 12, 34, tzinfo=UTC)
        profile = PITFT_28R_ROTATION_270
        layout = PanelLayout.from_profile(profile)
        controller = PanelController(profile)
        controller.set_snapshot(Snapshot(synthetic_observations(fixed), fixed))
        image = PillowRenderer(layout).render(controller.view(fixed))

        self.assertEqual((320, 240), image.size)
        self.assertEqual(BLACK_THEME.background, image.getpixel((0, 239)))
        self.assertEqual(BLACK_THEME.accent, image.getpixel((60, 8)))
        self.assertEqual(BLACK_THEME.selected, image.getpixel((80, 40)))
        self.assertEqual(BLACK_THEME.header, image.getpixel((315, 30)))

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "synthetic.png"
            display = FileDisplay(output)
            display.present(image)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
