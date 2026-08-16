# Remote Management Panel

[![Continuous integration](https://github.com/ngk0/remote-management-panel/actions/workflows/ci.yml/badge.svg)](https://github.com/ngk0/remote-management-panel/actions/workflows/ci.yml)
[![Security analysis](https://github.com/ngk0/remote-management-panel/actions/workflows/codeql.yml/badge.svg)](https://github.com/ngk0/remote-management-panel/actions/workflows/codeql.yml)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](CHANGELOG.md)

Turn a Raspberry Pi and an Adafruit PiTFT into an always-visible dashboard for
remote infrastructure. Check the network, Cloudflare Tunnel, system health, and
local services at a glance, then navigate with the touchscreen or four physical
buttons.

![Remote Management Panel simulator preview](docs/assets/simulator-home.svg)

Remote management is also known as **out-of-band** or **lights-out management**:
it gives operators an independent way to understand and recover equipment when
the primary servers are unavailable. This project focuses on the local display
and its security boundaries. It does not store tunnel credentials or configure
remote access.

> [!IMPORTANT]
> This is alpha software. The simulator and status-only interface are ready for
> development and evaluation; the Raspberry Pi service package and privileged
> controls are not yet production-supported.

## What you get

- A readable 320x240 black theme designed for the Adafruit PiTFT Plus 2.8-inch
  resistive touchscreen.
- A left-side menu aligned with the display board's four physical buttons.
- Pages for Cloudflare Tunnel, wired and wireless networking, Raspberry Pi
  health, and local services.
- Safe, honest status: failed or stale checks display `UNKNOWN` instead of
  looking healthy.
- A desktop simulator with synthetic data, so contributors do not need the
  display hardware.
- Separate modules for hardware input, status collection, navigation, rendering,
  and guarded administrative actions.
- Privileged controls disabled by default, with no support for configured shell
  commands or plug-in supplied root commands.

The first hardware profile supports the Adafruit PiTFT Plus 2.8-inch resistive
display in landscape orientation. The architecture is ready for additional
displays and status sources without coupling them to the screen renderer.

## Try it without a Raspberry Pi

Python 3.11 or newer is required.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
pitft-oob-panel simulate --output panel.png
```

On Windows, activate the environment with `.venv\Scripts\activate`. The output
contains synthetic addresses and identifiers only.

The public project name changed for clarity; the Python distribution and command
remain `pitft-oob-panel` during the alpha series for compatibility.

## Check a configuration

```bash
pitft-oob-panel validate-config config/default.toml
pitft-oob-panel show-profile
```

Configuration can select reviewed actions, but it cannot contain shell scripts.
Hardware button positions and logical actions live in versioned
[hardware profiles](docs/hardware-profiles.md).

## Network safety

The panel observes `cloudflared`; it does not create or authorize a Cloudflare
Tunnel. An outbound tunnel is still a remote entry point because an authorized
remote shell can connect from the Raspberry Pi to its attached network.

Keep the tunnel stopped while the device is on a home, repair, staging, or other
temporary network. Before enabling it at the destination, audit every published
application, private network route, Cloudflare Access policy, and Secure Shell
key. Follow the [bench network procedure](docs/operations.md#bench-network-safety).

## Documentation

- [Architecture](docs/architecture.md) explains the modular design.
- [Operations guide](docs/operations.md) covers safe setup and troubleshooting.
- [Hardware profiles](docs/hardware-profiles.md) document physical button mapping.
- [Threat model](docs/threat-model.md) records trust boundaries and safeguards.
- [Pre-publication review](docs/pre-publication-review.md) records current evidence
  and the remaining production gates.

## Contributing and support

Bug reports and feature proposals are welcome in
[GitHub Issues](https://github.com/ngk0/remote-management-panel/issues).
Read [CONTRIBUTING.md](CONTRIBUTING.md) before sending a change and report security
problems through the private process in [SECURITY.md](SECURITY.md).

Local development checks:

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
mypy src
python -m build
pip-audit --strict .
```

## Hardware acknowledgement

Raspberry Pi is a trademark of Raspberry Pi Ltd. Adafruit and PiTFT are
trademarks of their respective owners. Remote Management Panel is an independent
project and is not affiliated with or endorsed by Raspberry Pi Ltd, Adafruit
Industries, or Cloudflare. The bundled button coordinates are derived from
Adafruit's public PiTFT Plus 2.8-inch circuit-board design; those design files
are not redistributed here.

## License

Apache License 2.0. See [LICENSE](LICENSE).
