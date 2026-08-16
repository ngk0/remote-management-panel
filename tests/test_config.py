import tempfile
import unittest
from pathlib import Path

from pitft_oob.config import load_config

REPOSITORY = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    def test_default_configuration_is_valid(self) -> None:
        config = load_config(REPOSITORY / "config" / "default.toml")
        self.assertEqual(1, config.schema_version)
        self.assertEqual("black", config.ui.theme)
        self.assertEqual((), config.actions.enabled)
        self.assertEqual((27, 23, 22, 17), tuple(item.gpio for item in config.hardware.buttons))

    def test_configuration_rejects_non_black_theme(self) -> None:
        source = (REPOSITORY / "config" / "default.toml").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.toml"
            path.write_text(source.replace('theme = "black"', 'theme = "white"'), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "supported theme"):
                load_config(path)

    def test_configuration_rejects_unknown_action_identifier(self) -> None:
        source = (REPOSITORY / "config" / "default.toml").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-action.toml"
            path.write_text(
                source.replace("enabled = []", 'enabled = ["run-supplied-command"]'),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Unknown actions"):
                load_config(path)

    def test_configuration_rejects_unknown_top_level_key(self) -> None:
        source = (REPOSITORY / "config" / "default.toml").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unknown-key.toml"
            path.write_text('command = "do-not-ignore-me"\n' + source, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unknown top-level keys"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
