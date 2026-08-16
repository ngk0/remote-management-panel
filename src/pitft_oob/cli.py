from __future__ import annotations

import argparse
import json
import signal
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from pitft_oob.adapters.clock import SystemClock
from pitft_oob.adapters.linux.evdev_input import EvdevInput
from pitft_oob.adapters.linux.framebuffer import FramebufferDisplay
from pitft_oob.adapters.linux.runner import SubprocessRunner
from pitft_oob.adapters.simulation.display import FileDisplay
from pitft_oob.app import Application
from pitft_oob.config import load_config
from pitft_oob.hardware_profiles import PITFT_28R_ROTATION_270, get_profile
from pitft_oob.models import Snapshot
from pitft_oob.ports.status import StatusProvider
from pitft_oob.providers import (
    CloudflaredProvider,
    NetworkProvider,
    ServicesProvider,
    SystemProvider,
)
from pitft_oob.providers.synthetic import synthetic_observations
from pitft_oob.registry import PollingStatusService, ProviderRegistry
from pitft_oob.ui.controller import PanelController
from pitft_oob.ui.layout import PanelLayout
from pitft_oob.ui.render import PillowRenderer


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pitft-oob-panel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate = subparsers.add_parser("simulate", help="render a sanitized synthetic panel")
    simulate.add_argument("--output", type=Path, default=Path("panel.png"))
    simulate.add_argument("--profile", default=PITFT_28R_ROTATION_270.profile_id)
    simulate.add_argument("--extra-large", action="store_true")

    validate = subparsers.add_parser("validate-config", help="validate a versioned TOML file")
    validate.add_argument("path", type=Path)

    run_linux = subparsers.add_parser("run-linux", help="run with Linux framebuffer and evdev")
    run_linux.add_argument("--config", type=Path, required=True)
    run_linux.add_argument("--framebuffer", default="/dev/fb0")
    run_linux.add_argument("--touch", default="/dev/input/touchscreen")

    profile = subparsers.add_parser("show-profile", help="print reviewed hardware geometry")
    profile.add_argument("profile_id", nargs="?", default=PITFT_28R_ROTATION_270.profile_id)
    return parser


def _simulate(output: Path, profile_id: str, extra_large: bool) -> int:
    profile = get_profile(profile_id)
    layout = PanelLayout.from_profile(profile)
    fixed_time = datetime(2026, 1, 1, 12, 34, tzinfo=UTC)
    controller = PanelController(profile)
    controller.set_snapshot(Snapshot(synthetic_observations(fixed_time), fixed_time))
    renderer = PillowRenderer(layout, extra_large=extra_large)
    display = FileDisplay(output, profile.display_width, profile.display_height)
    display.present(renderer.render(controller.view(fixed_time)))
    print(f"Wrote sanitized synthetic panel to {output}")
    return 0


def _show_profile(profile_id: str) -> int:
    profile = get_profile(profile_id)
    payload = {
        "profile_id": profile.profile_id,
        "display": [profile.display_width, profile.display_height],
        "rotation": profile.rotation,
        "rail_width": profile.rail_width,
        "buttons_top_to_bottom": [
            {
                "gpio": button.gpio,
                "center_y": button.center_y,
                "action": button.action,
                "label": button.label,
            }
            for button in profile.buttons
        ],
        "source_url": profile.source_url,
    }
    print(json.dumps(payload, indent=2))
    return 0


def _run_linux(config_path: Path, framebuffer_path: str, touch_path: str) -> int:
    config = load_config(config_path)
    runner = SubprocessRunner()
    available: dict[str, StatusProvider] = {
        "network": NetworkProvider(runner),
        "cloudflared": CloudflaredProvider(runner),
        "system": SystemProvider(runner),
        "services": ServicesProvider(
            runner,
            ("cloudflared.service", "ssh.service", "NetworkManager.service"),
        ),
    }
    unknown = set(config.providers.enabled) - set(available)
    if unknown:
        raise ValueError(f"Unknown providers: {', '.join(sorted(unknown))}")
    registry = ProviderRegistry(tuple(available[item] for item in config.providers.enabled))
    status = PollingStatusService(registry, config.ui.refresh_seconds)
    display = FramebufferDisplay(framebuffer_path)
    if (display.width, display.height) != (
        config.hardware.display_width,
        config.hardware.display_height,
    ):
        display.close()
        raise ValueError(
            f"Framebuffer is {display.width}x{display.height}; profile expects "
            f"{config.hardware.display_width}x{config.hardware.display_height}"
        )
    inputs = EvdevInput(config.hardware, touch_path=touch_path)
    controller = PanelController(config.hardware)
    renderer = PillowRenderer(
        PanelLayout.from_profile(config.hardware),
        extra_large=config.ui.font_size == "extra-large",
    )
    application = Application(
        display,
        inputs,
        status,
        controller,
        renderer,
        SystemClock(),
        config.ui.clock_redraw_seconds,
    )
    signal.signal(signal.SIGTERM, lambda _signum, _frame: application.stop())
    signal.signal(signal.SIGINT, lambda _signum, _frame: application.stop())
    application.run()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "simulate":
            return _simulate(args.output, args.profile, args.extra_large)
        if args.command == "validate-config":
            config = load_config(args.path)
            print(
                f"Valid schema v{config.schema_version}: {config.hardware.profile_id}, "
                f"{len(config.providers.enabled)} providers"
            )
            return 0
        if args.command == "run-linux":
            return _run_linux(args.config, args.framebuffer, args.touch)
        if args.command == "show-profile":
            return _show_profile(args.profile_id)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
