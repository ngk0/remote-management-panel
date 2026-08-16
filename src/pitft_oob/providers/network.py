from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

from pitft_oob.models import Fact, Health, Observation
from pitft_oob.ports.runner import CommandRunner


class NetworkProvider:
    provider_id = "network"

    def __init__(self, runner: CommandRunner) -> None:
        self.runner = runner

    def collect(self) -> Observation:
        observed_at = datetime.now(UTC)
        address_result = self.runner.run(("ip", "-j", "-4", "address", "show"), timeout=2)
        route_result = self.runner.run(("ip", "-j", "route", "show", "default"), timeout=2)
        if address_result.returncode != 0 or route_result.returncode != 0:
            error = address_result.stderr or route_result.stderr or "network query failed"
            return Observation(
                self.provider_id,
                "Network",
                Health.UNKNOWN,
                "UNKNOWN",
                observed_at=observed_at,
                ttl=timedelta(seconds=10),
                error=error,
            )
        try:
            interfaces: list[dict[str, Any]] = json.loads(address_result.stdout)
            routes: list[dict[str, Any]] = json.loads(route_result.stdout)
        except (json.JSONDecodeError, TypeError) as exc:
            return Observation(
                self.provider_id,
                "Network",
                Health.UNKNOWN,
                "INVALID DATA",
                observed_at=observed_at,
                ttl=timedelta(seconds=10),
                error=str(exc),
            )

        addresses: dict[str, str] = {}
        for interface in interfaces:
            name = str(interface.get("ifname", ""))
            global_address = next(
                (
                    str(item.get("local"))
                    for item in interface.get("addr_info", [])
                    if item.get("scope") == "global" and item.get("local")
                ),
                None,
            )
            if name and global_address:
                addresses[name] = global_address
        routes.sort(key=lambda route: int(route.get("metric", 0)))
        primary = str(routes[0].get("dev", "none")) if routes else "none"
        metric = routes[0].get("metric", "—") if routes else "—"
        health = Health.OK if primary in addresses else Health.CRITICAL
        facts = (
            *(
                Fact(name, address, Health.OK if name == primary else Health.WARNING)
                for name, address in sorted(addresses.items())[:3]
            ),
            Fact("Default route", f"{primary} · metric {metric}", health),
        )
        return Observation(
            self.provider_id,
            "Network",
            health,
            f"{primary.upper()} primary" if primary != "none" else "NO DEFAULT ROUTE",
            facts,
            observed_at,
            timedelta(seconds=15),
        )
