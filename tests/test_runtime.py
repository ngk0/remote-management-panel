import tempfile
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from pitft_oob.app import Application
from pitft_oob.cli import main
from pitft_oob.hardware_profiles import PITFT_28R_ROTATION_270
from pitft_oob.models import ButtonAction, Health, InputEvent, InputKind, Observation, Snapshot
from pitft_oob.registry import PollingStatusService, ProviderRegistry
from pitft_oob.ui.controller import PanelController


class FakeProvider:
    provider_id = "fake"

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def collect(self) -> Observation:
        if self.error is not None:
            raise self.error
        return Observation("fake", "Fake", Health.OK, "READY")


class RuntimeTests(unittest.TestCase):
    def test_registry_isolates_provider_errors_and_rejects_duplicates(self) -> None:
        with self.assertRaisesRegex(ValueError, "unique"):
            ProviderRegistry((FakeProvider(), FakeProvider()))
        registry = ProviderRegistry((FakeProvider(RuntimeError("boom")),))
        observation = registry.collect().observations[0]
        self.assertEqual(Health.UNKNOWN, observation.health)
        self.assertIn("RuntimeError: boom", observation.error or "")

    def test_polling_service_collects_refreshes_and_closes(self) -> None:
        service = PollingStatusService(ProviderRegistry((FakeProvider(),)), interval=60)
        service.start()
        deadline = time.monotonic() + 2
        while not service.latest().observations and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertEqual("fake", service.latest().observations[0].provider_id)
        service.refresh()
        service.close()
        self.assertFalse(service._thread.is_alive())

    def test_application_loop_renders_input_and_closes_every_port(self) -> None:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        status = Mock()
        status.latest.return_value = Snapshot((FakeProvider().collect(),), now)
        display = Mock()
        renderer = Mock()
        renderer.render.return_value = object()
        clock = Mock()
        clock.monotonic.side_effect = (0.0, 0.2, 0.2)
        clock.now.return_value = now

        class Inputs:
            def __init__(self) -> None:
                self.calls = 0
                self.application: Application | None = None
                self.closed = False

            def poll(self, _timeout: float) -> tuple[InputEvent, ...]:
                self.calls += 1
                if self.calls == 1:
                    return (InputEvent(InputKind.BUTTON, action=ButtonAction.DOWN),)
                assert self.application is not None
                self.application.stop()
                return ()

            def close(self) -> None:
                self.closed = True

        inputs = Inputs()
        application = Application(
            display,
            inputs,
            status,
            PanelController(PITFT_28R_ROTATION_270),
            renderer,
            clock,
        )
        inputs.application = application
        application.run()
        status.start.assert_called_once_with()
        status.close.assert_called_once_with()
        display.present.assert_called()
        display.close.assert_called_once_with()
        self.assertTrue(inputs.closed)

    def test_cli_simulation_validation_profile_and_error_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "panel.png"
            self.assertEqual(0, main(("simulate", "--output", str(output), "--extra-large")))
            self.assertTrue(output.is_file())
        self.assertEqual(0, main(("validate-config", "config/default.toml")))
        self.assertEqual(0, main(("show-profile",)))
        self.assertEqual(2, main(("show-profile", "missing-profile")))
        with patch("pitft_oob.cli._run_linux", side_effect=OSError("unavailable")):
            self.assertEqual(2, main(("run-linux", "--config", "config/default.toml")))


if __name__ == "__main__":
    unittest.main()
