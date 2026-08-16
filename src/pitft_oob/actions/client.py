from __future__ import annotations

from pitft_oob.actions.catalog import ACTIONS
from pitft_oob.models import ActionResult
from pitft_oob.ports.runner import CommandRunner


class HelperActionClient:
    """Calls a reviewed broker path with one enumerated identifier and no shell."""

    def __init__(
        self,
        runner: CommandRunner,
        helper: str = "/usr/libexec/pitft-oob-panel-action",
    ) -> None:
        self.runner = runner
        self.helper = helper

    def execute(self, action_id: str) -> ActionResult:
        if action_id not in ACTIONS:
            return ActionResult(action_id, False, "Unsupported action")
        result = self.runner.run((self.helper, action_id), timeout=15)
        if result.returncode == 0:
            return ActionResult(action_id, True, "Action accepted")
        message = result.stderr or "Action rejected"
        return ActionResult(action_id, False, message[:160])


class DisabledActionClient:
    def execute(self, action_id: str) -> ActionResult:
        return ActionResult(action_id, False, "Privileged actions are disabled in simulation")
