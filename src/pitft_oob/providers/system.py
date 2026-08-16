from __future__ import annotations

import os
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pitft_oob.models import Fact, Health, Observation
from pitft_oob.ports.runner import CommandRunner


class SystemProvider:
    provider_id = "system"

    def __init__(self, runner: CommandRunner, root: str | Path = "/") -> None:
        self.runner = runner
        self.root = Path(root)

    def _read(self, relative: str, default: str = "") -> str:
        try:
            return (self.root / relative.lstrip("/")).read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            return default

    def collect(self) -> Observation:
        observed_at = datetime.now(UTC)
        temperature_raw = self._read("sys/class/thermal/thermal_zone0/temp")
        try:
            temperature = int(temperature_raw) / 1000 if temperature_raw else None
        except ValueError:
            temperature = None
        meminfo: dict[str, int] = {}
        for line in self._read("proc/meminfo").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            try:
                meminfo[key] = int(value.strip().split()[0])
            except (ValueError, IndexError):
                continue
        total = meminfo.get("MemTotal", 0)
        memory_percent = (
            round((total - meminfo.get("MemAvailable", 0)) * 100 / total) if total else None
        )
        usage = shutil.disk_usage(self.root)
        disk_percent = round(usage.used * 100 / usage.total)
        throttled_result = self.runner.run(("vcgencmd", "get_throttled"), timeout=2)
        throttled = (
            throttled_result.stdout.split("=", 1)[1]
            if throttled_result.returncode == 0 and "=" in throttled_result.stdout
            else "unknown"
        )
        load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
        if (temperature is not None and temperature >= 80) or disk_percent >= 95:
            health = Health.CRITICAL
        elif (
            (temperature is not None and temperature >= 70)
            or disk_percent >= 85
            or throttled not in {"0x0", "unknown"}
        ):
            health = Health.WARNING
        elif temperature is None or memory_percent is None or throttled == "unknown":
            health = Health.UNKNOWN
        else:
            health = Health.OK
        temperature_text = "UNKNOWN" if temperature is None else f"{temperature:.1f}°C"
        memory_text = "UNKNOWN" if memory_percent is None else f"{memory_percent}%"
        errors = []
        if temperature is None:
            errors.append("temperature unavailable")
        if memory_percent is None:
            errors.append("memory data unavailable")
        if throttled == "unknown":
            errors.append("power flags unavailable")
        return Observation(
            self.provider_id,
            "System",
            health,
            f"{temperature_text} · disk {disk_percent}%",
            (
                Fact("Temperature / load", f"{temperature_text} · {load:.2f}", health),
                Fact("Memory / disk", f"{memory_text} · {disk_percent}%", health),
                Fact("Power flags", throttled, Health.OK if throttled == "0x0" else Health.UNKNOWN),
            ),
            observed_at,
            timedelta(seconds=15),
            "; ".join(errors) or None,
        )
