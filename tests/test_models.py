import unittest
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

from pitft_oob.models import Fact, Health, Observation, Snapshot


class ModelTests(unittest.TestCase):
    def test_observation_is_immutable_and_becomes_unknown_when_stale(self) -> None:
        observed = datetime(2026, 1, 1, tzinfo=UTC)
        observation = Observation(
            "network",
            "Network",
            Health.OK,
            "WIRED primary",
            (Fact("Link", "up"),),
            observed,
            timedelta(seconds=5),
        )
        self.assertFalse(observation.is_stale(observed + timedelta(seconds=5)))
        self.assertTrue(observation.is_stale(observed + timedelta(seconds=6)))
        self.assertEqual(
            Health.UNKNOWN,
            observation.effective_health(observed + timedelta(seconds=6)),
        )
        with self.assertRaises(FrozenInstanceError):
            observation.summary = "changed"  # type: ignore[misc]

    def test_snapshot_reports_worst_effective_health(self) -> None:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        snapshot = Snapshot(
            (
                Observation("one", "One", Health.OK, "OK", observed_at=now),
                Observation("two", "Two", Health.WARNING, "WARN", observed_at=now),
            ),
            now,
        )
        self.assertEqual(Health.WARNING, snapshot.health)
        self.assertEqual("WARN", snapshot.get("two").summary)  # type: ignore[union-attr]


if __name__ == "__main__":
    unittest.main()
