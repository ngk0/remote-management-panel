from __future__ import annotations

import array
import mmap
import os
import sys
from pathlib import Path
from typing import Any


class FramebufferDisplay:
    """RGB565 framebuffer output with stride-aware row writes."""

    def __init__(self, path: str | Path = "/dev/fb0") -> None:
        self.path = Path(path)
        sysfs = Path("/sys/class/graphics") / self.path.name
        virtual_size = (sysfs / "virtual_size").read_text().strip()
        width, height = (int(item) for item in virtual_size.split(","))
        self.width = width
        self.height = height
        self.bits_per_pixel = int((sysfs / "bits_per_pixel").read_text().strip())
        self.stride = int((sysfs / "stride").read_text().strip())
        if self.bits_per_pixel != 16:
            raise RuntimeError(f"Expected a 16-bit framebuffer, got {self.bits_per_pixel}")
        self._fd = os.open(self.path, os.O_RDWR)
        self._map = mmap.mmap(self._fd, self.stride * self.height, access=mmap.ACCESS_WRITE)

    def present(self, image: object) -> None:
        candidate: Any = image
        if getattr(candidate, "size", None) != (self.width, self.height):
            candidate = candidate.resize((self.width, self.height))
        rgb = candidate.convert("RGB")
        flattened = getattr(rgb, "get_flattened_data", None)
        pixels = flattened() if flattened is not None else rgb.getdata()
        packed = array.array(
            "H",
            (
                ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)
                for red, green, blue in pixels
            ),
        )
        if sys.byteorder != "little":
            packed.byteswap()
        data = packed.tobytes()
        row_size = self.width * 2
        if self.stride == row_size:
            self._map.seek(0)
            self._map.write(data)
            return
        for row in range(self.height):
            self._map.seek(row * self.stride)
            self._map.write(data[row * row_size : (row + 1) * row_size])

    def close(self) -> None:
        self._map.close()
        os.close(self._fd)
