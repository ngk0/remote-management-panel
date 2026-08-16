from __future__ import annotations

from pathlib import Path
from typing import Any


class FileDisplay:
    def __init__(self, output: str | Path, width: int = 320, height: int = 240) -> None:
        self.output = Path(output)
        self.width = width
        self.height = height
        self.last_image: Any | None = None

    def present(self, image: object) -> None:
        candidate: Any = image
        self.last_image = candidate.copy()
        self.output.parent.mkdir(parents=True, exist_ok=True)
        candidate.save(self.output)

    def close(self) -> None:
        return
