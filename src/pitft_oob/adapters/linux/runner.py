from __future__ import annotations

import subprocess
from collections.abc import Sequence

from pitft_oob.ports.runner import CommandResult


class SubprocessRunner:
    def run(self, argv: Sequence[str], timeout: float) -> CommandResult:
        normalized = tuple(str(item) for item in argv)
        try:
            result = subprocess.run(
                normalized,
                capture_output=True,
                check=False,
                text=True,
                timeout=timeout,
            )
            return CommandResult(
                normalized,
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip(),
            )
        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                normalized,
                124,
                str(exc.stdout or "").strip(),
                str(exc.stderr or "command timed out").strip(),
                timed_out=True,
            )
        except OSError as exc:
            return CommandResult(normalized, 127, "", str(exc))
