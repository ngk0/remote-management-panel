from __future__ import annotations

import select
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from pitft_oob.models import ButtonAction, HardwareProfile, InputEvent, InputKind


class EvdevInput:
    """Hotplug-tolerant evdev buttons and calibrated STMPE touch input."""

    DISCOVERY_INTERVAL = 5.0
    EXPECTED_DEVICE_COUNT = 5

    def __init__(
        self,
        profile: HardwareProfile,
        touch_path: str | Path = "/dev/input/touchscreen",
        pointercal_path: str | Path = "/etc/pointercal",
    ) -> None:
        self.profile = profile
        self.touch_path = Path(touch_path)
        self.pointercal_path = Path(pointercal_path)
        self._devices: list[Any] = []
        self._touch: Any | None = None
        self._raw_x = 0
        self._raw_y = 0
        self._touching = False
        self._last_tap = 0.0
        self._last_discovery = 0.0
        self._pointercal = self._load_pointercal()
        self._discover()

    @staticmethod
    def _evdev() -> tuple[Any, Any, Any]:
        from evdev import InputDevice, ecodes, list_devices

        return InputDevice, ecodes, list_devices

    def _load_pointercal(self) -> tuple[int, int, int, int, int, int, int]:
        try:
            values = tuple(int(item) for item in self.pointercal_path.read_text().split())
        except (OSError, ValueError):
            values = ()
        if len(values) == 7:
            return values
        return (0, 5120, 0, 3840, 0, 0, 65536)

    def _discover(self) -> None:
        InputDevice, _, list_devices = self._evdev()
        self.close()
        paths = set(list_devices())
        if self.touch_path.exists():
            paths.add(str(self.touch_path.resolve()))
        for path in sorted(paths):
            try:
                device = InputDevice(path)
            except OSError:
                continue
            if device.name == "stmpe-ts":
                self._touch = device
                self._devices.append(device)
            elif device.name.startswith(("pitft-", "button@")) or device.name == "gpio_keys":
                self._devices.append(device)
            else:
                device.close()
        self._last_discovery = time.monotonic()

    def _mapped_touch(self) -> tuple[int, int]:
        a, b, c, d, e, f, scale = self._pointercal
        x = int((a * self._raw_x + b * self._raw_y + c) / scale)
        y = int((d * self._raw_x + e * self._raw_y + f) / scale)
        return (
            max(0, min(self.profile.display_width - 1, x)),
            max(0, min(self.profile.display_height - 1, y)),
        )

    def poll(self, timeout: float) -> tuple[InputEvent, ...]:
        _, ecodes, _ = self._evdev()
        discovery_due = time.monotonic() - self._last_discovery >= self.DISCOVERY_INTERVAL
        if discovery_due and (
            self._touch is None or len(self._devices) < self.EXPECTED_DEVICE_COUNT
        ):
            self._discover()
        if not self._devices:
            time.sleep(timeout)
            return ()
        try:
            ready, _, _ = select.select(self._devices, [], [], timeout)
        except (OSError, ValueError):
            self._discover()
            return ()
        actions: list[InputEvent] = []
        key_map = {
            ecodes.KEY_ENTER: ButtonAction.SELECT,
            ecodes.KEY_DOWN: ButtonAction.DOWN,
            ecodes.KEY_UP: ButtonAction.UP,
            ecodes.KEY_HOME: ButtonAction.BACK,
            ecodes.KEY_ESC: ButtonAction.BACK,
        }
        for device in ready:
            try:
                events = device.read()
            except OSError:
                self._discover()
                break
            for event in events:
                if device is self._touch:
                    if event.type == ecodes.EV_ABS:
                        if event.code == ecodes.ABS_X:
                            self._raw_x = event.value
                        elif event.code == ecodes.ABS_Y:
                            self._raw_y = event.value
                    elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                        if event.value == 1:
                            self._touching = True
                        elif event.value == 0 and self._touching:
                            self._touching = False
                            now = time.monotonic()
                            if now - self._last_tap > 0.18:
                                self._last_tap = now
                                actions.append(
                                    InputEvent(InputKind.TOUCH, point=self._mapped_touch())
                                )
                elif event.type == ecodes.EV_KEY and event.value == 1:
                    action = key_map.get(event.code)
                    if action is not None:
                        actions.append(InputEvent(InputKind.BUTTON, action=action))
        return tuple(actions)

    def close(self) -> None:
        for device in self._devices:
            with suppress(OSError):
                device.close()
        self._devices.clear()
        self._touch = None
        self._touching = False
