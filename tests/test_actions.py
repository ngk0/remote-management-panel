import unittest
from collections.abc import Sequence

from pitft_oob.actions.client import HelperActionClient
from pitft_oob.ports.runner import CommandResult


class RecordingRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    def run(self, argv: Sequence[str], timeout: float) -> CommandResult:
        normalized = tuple(argv)
        self.calls.append(normalized)
        return CommandResult(normalized, 0, "", "")


class ActionTests(unittest.TestCase):
    def test_unknown_action_blocked(self) -> None:
        runner = RecordingRunner()
        result = HelperActionClient(runner).execute("run-supplied-command")
        self.assertFalse(result.accepted)
        self.assertEqual([], runner.calls)

    def test_known_action_is_one_identifier_without_shell(self) -> None:
        runner = RecordingRunner()
        result = HelperActionClient(runner, "/reviewed/broker").execute("reboot")
        self.assertTrue(result.accepted)
        self.assertEqual([("/reviewed/broker", "reboot")], runner.calls)


if __name__ == "__main__":
    unittest.main()
