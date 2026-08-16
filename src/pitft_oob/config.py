"""Versioned configuration loading with a deliberately narrow schema."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pitft_oob.actions.catalog import ACTIONS
from pitft_oob.hardware_profiles import get_profile
from pitft_oob.models import HardwareProfile

KNOWN_PROVIDERS = frozenset({"network", "cloudflared", "system", "services"})


def _reject_unknown(data: dict[str, Any], allowed: set[str], scope: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"Unknown {scope} keys: {', '.join(sorted(unknown))}")


@dataclass(frozen=True, slots=True)
class UIConfig:
    theme: str
    font_size: str
    refresh_seconds: float
    clock_redraw_seconds: float


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    enabled: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ActionConfig:
    enabled: tuple[str, ...]
    destructive_hold_seconds: float


@dataclass(frozen=True, slots=True)
class PanelConfig:
    schema_version: int
    hardware: HardwareProfile
    ui: UIConfig
    providers: ProviderConfig
    actions: ActionConfig


def _table(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key!r} must be a TOML table")
    return value


def _string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be an array of strings")
    result = tuple(value)
    if len(set(result)) != len(result):
        raise ValueError(f"{field_name} must not contain duplicates")
    return result


def _bounded_number(value: Any, field_name: str, lower: float, upper: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    result = float(value)
    if not lower <= result <= upper:
        raise ValueError(f"{field_name} must be between {lower:g} and {upper:g}")
    return result


def load_config(path: str | Path) -> PanelConfig:
    with Path(path).open("rb") as stream:
        data: dict[str, Any] = tomllib.load(stream)

    _reject_unknown(
        data,
        {"schema_version", "hardware_profile", "ui", "providers", "actions"},
        "top-level",
    )
    if data.get("schema_version") != 1:
        raise ValueError("Only schema_version = 1 is supported")
    profile_id = data.get("hardware_profile")
    if not isinstance(profile_id, str):
        raise ValueError("hardware_profile must be a string")

    ui = _table(data, "ui")
    _reject_unknown(
        ui,
        {"theme", "font_size", "refresh_seconds", "clock_redraw_seconds"},
        "ui",
    )
    theme = ui.get("theme")
    if theme != "black":
        raise ValueError("The supported theme is 'black'")
    font_size = ui.get("font_size")
    if font_size not in {"large", "extra-large"}:
        raise ValueError("ui.font_size must be 'large' or 'extra-large'")

    providers = _table(data, "providers")
    actions = _table(data, "actions")
    _reject_unknown(providers, {"enabled"}, "providers")
    _reject_unknown(actions, {"enabled", "destructive_hold_seconds"}, "actions")
    enabled_providers = _string_tuple(providers.get("enabled"), "providers.enabled")
    unknown_providers = set(enabled_providers) - KNOWN_PROVIDERS
    if unknown_providers:
        raise ValueError(f"Unknown providers: {', '.join(sorted(unknown_providers))}")
    enabled_actions = _string_tuple(actions.get("enabled"), "actions.enabled")
    unknown_actions = set(enabled_actions) - ACTIONS.keys()
    if unknown_actions:
        raise ValueError(f"Unknown actions: {', '.join(sorted(unknown_actions))}")
    return PanelConfig(
        schema_version=1,
        hardware=get_profile(profile_id),
        ui=UIConfig(
            theme=theme,
            font_size=font_size,
            refresh_seconds=_bounded_number(
                ui.get("refresh_seconds"), "ui.refresh_seconds", 1, 300
            ),
            clock_redraw_seconds=_bounded_number(
                ui.get("clock_redraw_seconds"), "ui.clock_redraw_seconds", 1, 60
            ),
        ),
        providers=ProviderConfig(enabled_providers),
        actions=ActionConfig(
            enabled=enabled_actions,
            destructive_hold_seconds=_bounded_number(
                actions.get("destructive_hold_seconds"),
                "actions.destructive_hold_seconds",
                1,
                10,
            ),
        ),
    )
