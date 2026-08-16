import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image

from pitft_oob.adapters.clock import SystemClock
from pitft_oob.adapters.linux.evdev_input import EvdevInput
from pitft_oob.adapters.linux.framebuffer import FramebufferDisplay
from pitft_oob.adapters.linux.runner import SubprocessRunner
from pitft_oob.adapters.simulation.input import QueueInput
from pitft_oob.hardware_profiles import PITFT_28R_ROTATION_270
from pitft_oob.models import ButtonAction, InputEvent, InputKind


class FakeDevice:
    def __init__(self, name: str, events: tuple[object, ...] = ()) -> None:
        self.name = name
        self.events = events
        self.closed = False

    def read(self) -> tuple[object, ...]:
        return self.events

    def close(self) -> None:
        self.closed = True


class AdapterTests(unittest.TestCase):
    def test_clock_and_queue_input_lifecycle(self) -> None:
        clock = SystemClock()
        self.assertIsNotNone(clock.now().tzinfo)
        self.assertGreaterEqual(clock.monotonic(), 0)

        event = InputEvent(InputKind.BUTTON, action=ButtonAction.SELECT)
        inputs = QueueInput((event,))
        self.assertEqual((event,), inputs.poll(0))
        with patch("pitft_oob.adapters.simulation.input.time.sleep") as sleep:
            self.assertEqual((), inputs.poll(0.25))
        sleep.assert_called_once_with(0.25)
        inputs.push(event)
        inputs.close()
        self.assertEqual((), inputs.poll(0))

    def test_subprocess_runner_covers_success_timeout_and_missing_binary(self) -> None:
        completed = subprocess.CompletedProcess(("ok",), 0, " output \n", "")
        with patch("pitft_oob.adapters.linux.runner.subprocess.run", return_value=completed):
            result = SubprocessRunner().run(("ok",), 1)
        self.assertEqual(("ok",), result.argv)
        self.assertEqual("output", result.stdout)

        timeout = subprocess.TimeoutExpired(("slow",), 1, output="partial")
        with patch("pitft_oob.adapters.linux.runner.subprocess.run", side_effect=timeout):
            result = SubprocessRunner().run(("slow",), 1)
        self.assertTrue(result.timed_out)
        self.assertEqual(124, result.returncode)

        with patch(
            "pitft_oob.adapters.linux.runner.subprocess.run",
            side_effect=FileNotFoundError("missing"),
        ):
            result = SubprocessRunner().run(("missing",), 1)
        self.assertEqual(127, result.returncode)
        self.assertIn("missing", result.stderr)

    def test_framebuffer_packs_rgb565_and_honors_stride(self) -> None:
        image = Image.new("RGB", (2, 2), (255, 0, 0))
        display = object.__new__(FramebufferDisplay)
        display.width = 2
        display.height = 2
        display.stride = 6
        display._map = Mock()
        display._fd = 7

        display.present(image)
        self.assertEqual(2, display._map.write.call_count)
        self.assertEqual(
            [unittest.mock.call(0), unittest.mock.call(6)],
            display._map.seek.call_args_list,
        )

        with patch("pitft_oob.adapters.linux.framebuffer.os.close") as close_fd:
            display.close()
        display._map.close.assert_called_once_with()
        close_fd.assert_called_once_with(7)

    def test_evdev_maps_buttons_and_touch_and_closes_devices(self) -> None:
        ecodes = SimpleNamespace(
            KEY_ENTER=1,
            KEY_DOWN=2,
            KEY_UP=3,
            KEY_HOME=4,
            KEY_ESC=5,
            EV_ABS=6,
            ABS_X=7,
            ABS_Y=8,
            EV_KEY=9,
            BTN_TOUCH=10,
        )
        button = FakeDevice("button@11", (SimpleNamespace(type=9, code=1, value=1),))
        touch = FakeDevice(
            "stmpe-ts",
            (
                SimpleNamespace(type=6, code=7, value=10),
                SimpleNamespace(type=6, code=8, value=20),
                SimpleNamespace(type=9, code=10, value=1),
                SimpleNamespace(type=9, code=10, value=0),
            ),
        )
        unknown = FakeDevice("unrelated")

        with tempfile.TemporaryDirectory() as directory:
            touch_path = Path(directory) / "touchscreen"
            touch_path.touch()
            pointercal = Path(directory) / "pointercal"
            pointercal.write_text("65536 0 0 0 65536 0 65536", encoding="utf-8")
            devices = {
                "/dev/input/button": button,
                str(touch_path.resolve()): touch,
                "/dev/input/unknown": unknown,
            }

            def factory(path: str) -> FakeDevice:
                return devices[path]

            evdev_api = (factory, ecodes, lambda: tuple(devices))
            with (
                patch.object(EvdevInput, "_evdev", return_value=evdev_api),
                patch("pitft_oob.adapters.linux.evdev_input.time.monotonic", return_value=100.0),
            ):
                inputs = EvdevInput(
                    PITFT_28R_ROTATION_270,
                    touch_path=touch_path,
                    pointercal_path=pointercal,
                )

            with (
                patch.object(EvdevInput, "_evdev", return_value=evdev_api),
                patch(
                    "pitft_oob.adapters.linux.evdev_input.select.select",
                    return_value=([button, touch], [], []),
                ),
                patch(
                    "pitft_oob.adapters.linux.evdev_input.time.monotonic",
                    side_effect=(100.1, 101.0),
                ),
            ):
                events = inputs.poll(0)

        self.assertEqual(InputKind.BUTTON, events[0].kind)
        self.assertEqual(ButtonAction.SELECT, events[0].action)
        self.assertEqual(InputEvent(InputKind.TOUCH, point=(10, 20)), events[1])
        self.assertTrue(unknown.closed)
        inputs.close()
        self.assertTrue(button.closed)
        self.assertTrue(touch.closed)


if __name__ == "__main__":
    unittest.main()
