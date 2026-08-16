from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pitft_oob.models import Fact, Health, Observation
from pitft_oob.ports.runner import CommandRunner


class ServicesProvider:
    provider_id = "services"

    def __init__(self, runner: CommandRunner, services: tuple[str, ...]) -> None:
        self.runner = runner
        self.services = services

    def collect(self) -> Observation:
        facts: list[Fact] = []
        errors: list[str] = []
        for service in self.services:
            result = self.runner.run(("systemctl", "is-active", service), timeout=2)
            active = result.returncode == 0 and result.stdout == "active"
            if active:
                state = "ACTIVE"
                fact_health = Health.OK
            elif result.returncode == 3:
                state = "DOWN"
                fact_health = Health.CRITICAL
            else:
                state = "UNKNOWN"
                fact_health = Health.UNKNOWN
                errors.append(f"{service}: {result.stderr or 'status query failed'}")
            facts.append(
                Fact(
                    service,
                    state,
                    fact_health,
                )
            )
        active_count = sum(fact.health is Health.OK for fact in facts)
        if any(fact.health is Health.CRITICAL for fact in facts):
            health = Health.CRITICAL
        elif any(fact.health is Health.UNKNOWN for fact in facts):
            health = Health.UNKNOWN
        else:
            health = Health.OK
        return Observation(
            self.provider_id,
            "Services",
            health,
            f"{active_count}/{len(facts)} active",
            tuple(facts),
            datetime.now(UTC),
            timedelta(seconds=15),
            "; ".join(errors) or None,
        )
