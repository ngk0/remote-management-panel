# Architecture

The panel is split around explicit ports so an unavailable status command cannot
freeze local navigation and Linux details cannot leak into view logic.

```text
Linux providers ─┐
Synthetic data ──┼─> ProviderRegistry -> background poller -> immutable Snapshot
Future plugins ──┘                                      |
                                                        v
evdev -> InputPort -> PanelController -> PanelView -> PillowRenderer -> DisplayPort
                                                               |          |-- fb0
                                                               |          `-- PNG
                                                               `-- black theme/layout
```

## Boundaries

- `models.py` contains immutable observations, facts, actions, and hardware geometry.
- `ports/` defines the interfaces the application core consumes.
- `providers/` performs bounded, unprivileged observation only.
- `ui/` owns navigation, physical layout, view models, theme, and rendering.
- `adapters/linux/` owns subprocess, framebuffer, and evdev details.
- `adapters/simulation/` provides deterministic development output.
- `actions/` contains an enumerated catalog and broker client. It never accepts a
  configured shell command.

The status poller owns its own thread. Provider failures become `UNKNOWN`
observations and do not terminate the UI. Each provider is still responsible for
bounded I/O; a future worker-pool implementation may add independent provider
deadlines when external plugins are supported.

The controller owns one global selection index and exposes at most four visible
rows per page. Rendering and content-area touch handling consume that same page,
so an off-screen row cannot be selected accidentally.

## Provider extension model

Version 0.1 uses an internal registry. A provider exposes a stable identifier and
returns one `Observation`. Later entry-point discovery must be allowlisted by
configuration and run unprivileged. External providers may add facts and pages;
they may not add root commands.

Likely future providers include NUT/UPS state, USB serial-device presence, a
second Cloudflare connector, and local hardware sensors.

## Action model

`ActionSpec` declares risk and capability. UI confirmation policy is selected
from risk. The privileged side must independently validate the identifier and
caller; it must not trust labels, arguments, or UI state. Destructive actions
will remain disabled in packaged releases until hold-to-confirm and the broker
have hardware and security tests.
