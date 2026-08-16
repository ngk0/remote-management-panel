import json
import tempfile
import unittest
from collections.abc import Sequence
from unittest.mock import Mock, patch

from pitft_oob.models import Health
from pitft_oob.ports.runner import CommandResult
from pitft_oob.providers.cloudflare import MAX_METRICS_BYTES, CloudflaredProvider
from pitft_oob.providers.network import NetworkProvider
from pitft_oob.providers.services import ServicesProvider
from pitft_oob.providers.system import SystemProvider


class FakeRunner:
    def __init__(self, responses: dict[tuple[str, ...], CommandResult]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, ...]] = []

    def run(self, argv: Sequence[str], timeout: float) -> CommandResult:
        key = tuple(argv)
        self.calls.append(key)
        return self.responses[key]


class ProviderTests(unittest.TestCase):
    def test_network_provider_discovers_interfaces_instead_of_assuming_names(self) -> None:
        address_argv = ("ip", "-j", "-4", "address", "show")
        route_argv = ("ip", "-j", "route", "show", "default")
        addresses = [
            {
                "ifname": "wired-test0",
                "addr_info": [{"scope": "global", "local": "198.51.100.24"}],
            },
            {
                "ifname": "radio-test0",
                "addr_info": [{"scope": "global", "local": "192.0.2.18"}],
            },
        ]
        routes = [{"dev": "wired-test0", "metric": 100}]
        runner = FakeRunner(
            {
                address_argv: CommandResult(address_argv, 0, json.dumps(addresses), ""),
                route_argv: CommandResult(route_argv, 0, json.dumps(routes), ""),
            }
        )
        observation = NetworkProvider(runner).collect()
        self.assertEqual(Health.OK, observation.health)
        self.assertEqual("WIRED-TEST0 primary", observation.summary)
        facts = {fact.label: fact.value for fact in observation.facts}
        self.assertEqual("198.51.100.24", facts["wired-test0"])

    def test_metrics_read_bound(self) -> None:
        class OversizedResponse:
            requested = 0

            def __enter__(self) -> object:
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def read(self, amount: int) -> bytes:
                self.requested = amount
                return b"x" * amount

        response = OversizedResponse()
        opener = Mock()
        opener.open.return_value = response
        with patch("pitft_oob.providers.cloudflare.build_opener", return_value=opener):
            provider = CloudflaredProvider(FakeRunner({}))
            self.assertIsNone(provider._connections())
        self.assertEqual(MAX_METRICS_BYTES + 1, response.requested)

    def test_service_query_failure_is_unknown_not_down(self) -> None:
        argv = ("systemctl", "is-active", "missing.service")
        runner = FakeRunner({argv: CommandResult(argv, 127, "", "systemctl unavailable")})
        observation = ServicesProvider(runner, ("missing.service",)).collect()
        self.assertEqual(Health.UNKNOWN, observation.health)
        self.assertEqual("UNKNOWN", observation.facts[0].value)
        self.assertIn("systemctl unavailable", observation.error or "")

    def test_missing_system_sensors_are_reported_unknown(self) -> None:
        argv = ("vcgencmd", "get_throttled")
        runner = FakeRunner({argv: CommandResult(argv, 127, "", "not installed")})
        with tempfile.TemporaryDirectory() as directory:
            observation = SystemProvider(runner, root=directory).collect()
        self.assertEqual(Health.UNKNOWN, observation.health)
        self.assertIn("UNKNOWN", observation.summary)
        self.assertIn("temperature unavailable", observation.error or "")


if __name__ == "__main__":
    unittest.main()
