from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pitft_oob.models import Fact, Health, Observation


def synthetic_observations(now: datetime | None = None) -> tuple[Observation, ...]:
    observed_at = now or datetime.now(UTC)
    ttl = timedelta(minutes=5)
    return (
        Observation(
            "cloudflared",
            "Cloudflare",
            Health.OK,
            "ACTIVE · 4",
            (
                Fact("Service", "ACTIVE"),
                Fact("Connections", "4 · QUIC"),
                Fact("Edge", "SYNTHETIC"),
            ),
            observed_at,
            ttl,
        ),
        Observation(
            "network",
            "Network",
            Health.OK,
            "WIRED primary",
            (
                Fact("Wired", "198.51.100.24"),
                Fact("Wi-Fi backup", "192.0.2.18"),
                Fact("Default route", "wired · metric 100"),
            ),
            observed_at,
            ttl,
        ),
        Observation(
            "system",
            "System",
            Health.OK,
            "42.0°C · disk 67%",
            (
                Fact("Temperature", "42.0°C"),
                Fact("Memory", "38%"),
                Fact("Disk", "67%"),
            ),
            observed_at,
            ttl,
        ),
        Observation(
            "services",
            "Services",
            Health.OK,
            "4 active",
            (Fact("Synthetic service", "ACTIVE"),),
            observed_at,
            ttl,
        ),
    )
