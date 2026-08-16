import re
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]


class PublicationTests(unittest.TestCase):
    def test_packaging_uses_dependency_only_boot_order(self) -> None:
        unit = (REPOSITORY / "packaging/systemd/pitft-oob-panel.service").read_text(
            encoding="utf-8"
        )
        self.assertIn("WantedBy=con2fbmap.service", unit)
        self.assertNotIn("WantedBy=multi-user.target", unit)
        self.assertNotIn("SupplementaryGroups=video", unit)
        self.assertNotIn("SupplementaryGroups=input", unit)

    def test_udev_rules_cover_only_reviewed_legacy_buttons(self) -> None:
        self.assertFalse((REPOSITORY / "packaging/udev/70-pitft-oob-panel.rules").exists())
        rules = (REPOSITORY / "packaging/udev/99-pitft-oob-panel.rules").read_text(encoding="utf-8")
        self.assertIn("99-com.rules", rules)
        for name in ("button@11", "button@16", "button@17", "button@1b"):
            self.assertIn(f'ATTRS{{name}}=="{name}"', rules)
        self.assertNotIn('ATTRS{name}=="button@*"', rules)

    def test_workflow_actions_are_commit_pinned(self) -> None:
        uses_pattern = re.compile(r"^\s*- uses: [^@\s]+@([^\s#]+)", re.MULTILINE)
        workflows = tuple((REPOSITORY / ".github/workflows").glob("*.yml"))
        self.assertTrue(workflows)
        for workflow in workflows:
            body = workflow.read_text(encoding="utf-8")
            pins = uses_pattern.findall(body)
            self.assertTrue(pins, workflow)
            for pin in pins:
                self.assertRegex(pin, r"^[0-9a-f]{40}$", workflow)

    def test_no_fake_repository_owner_links_remain(self) -> None:
        paths = [
            *(path for path in REPOSITORY.iterdir() if path.is_file()),
            *(
                path
                for directory in (
                    ".github",
                    "config",
                    "docs",
                    "packaging",
                    "privileged",
                    "src",
                    "tests",
                )
                for path in (REPOSITORY / directory).rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            ),
        ]
        fake_owner = "github.com/" + "example/"
        for path in paths:
            try:
                body = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            self.assertNotIn(fake_owner, body, path)


if __name__ == "__main__":
    unittest.main()
