from __future__ import annotations

from pitft_oob.models import Health, Snapshot
from pitft_oob.ui.viewmodels import RowView


def _provider_row(snapshot: Snapshot, provider_id: str, label: str) -> RowView:
    observation = snapshot.get(provider_id)
    if observation is None:
        return RowView(label, "UNKNOWN", Health.UNKNOWN, provider_id)
    return RowView(
        label,
        observation.summary,
        observation.effective_health(snapshot.captured_at),
        provider_id,
    )


def build_home_rows(snapshot: Snapshot) -> tuple[RowView, ...]:
    return (
        _provider_row(snapshot, "cloudflared", "Cloudflare"),
        _provider_row(snapshot, "network", "Network"),
        _provider_row(snapshot, "system", "System"),
        RowView("Open menu", ">", Health.OK, "menu"),
    )
