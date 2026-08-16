from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from urllib.request import ProxyHandler, build_opener

from pitft_oob.models import Fact, Health, Observation
from pitft_oob.ports.runner import CommandRunner

MAX_METRICS_BYTES = 256 * 1024


class CloudflaredProvider:
    provider_id = "cloudflared"

    def __init__(
        self,
        runner: CommandRunner,
        service_name: str = "cloudflared.service",
        metrics_url: str = "http://127.0.0.1:20241/metrics",
    ) -> None:
        self.runner = runner
        self.service_name = service_name
        self.metrics_url = metrics_url

    def _connections(self) -> int | None:
        try:
            with build_opener(ProxyHandler({})).open(self.metrics_url, timeout=1.5) as response:
                payload = response.read(MAX_METRICS_BYTES + 1)
        except OSError:
            return None
        if len(payload) > MAX_METRICS_BYTES:
            return None
        metrics = payload.decode("utf-8", "replace")
        match = re.search(
            r"^cloudflared_tunnel_ha_connections(?:\{[^}]*\})?\s+([0-9.]+)$",
            metrics,
            re.MULTILINE,
        )
        return int(float(match.group(1))) if match else None

    def collect(self) -> Observation:
        observed_at = datetime.now(UTC)
        active_result = self.runner.run(("systemctl", "is-active", self.service_name), timeout=2)
        enabled_result = self.runner.run(("systemctl", "is-enabled", self.service_name), timeout=2)
        active = active_result.returncode == 0 and active_result.stdout == "active"
        enabled = enabled_result.returncode == 0 and enabled_result.stdout == "enabled"
        connections = self._connections() if active else 0
        if not active:
            health = Health.CRITICAL
        elif connections:
            health = Health.OK
        else:
            health = Health.WARNING
        connection_text = "UNKNOWN" if connections is None else str(connections)
        return Observation(
            self.provider_id,
            "Cloudflare",
            health,
            f"{'ACTIVE' if active else 'DOWN'} · {connection_text}",
            (
                Fact(
                    "Service",
                    "ACTIVE" if active else "DOWN",
                    Health.OK if active else Health.CRITICAL,
                ),
                Fact(
                    "Enabled",
                    "YES" if enabled else "NO",
                    Health.OK if enabled else Health.WARNING,
                ),
                Fact("Connections", connection_text, health),
            ),
            observed_at,
            timedelta(seconds=15),
            None if active_result.returncode in {0, 3} else active_result.stderr,
        )
