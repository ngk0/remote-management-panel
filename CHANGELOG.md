# Changelog

All notable changes are documented here. The project follows Semantic Versioning.

## Unreleased

### Added

- Clear public name, search-friendly project summary, and plain-language
  documentation for Raspberry Pi remote management users.

- Clean-room modular scaffold.
- PiTFT Plus 2.8-inch rotation-270 hardware profile and left-side button rail.
- Typed observations, simulator, Linux adapters, provider interfaces, and tests.
- Bench-network tunnel safety guidance and expanded threat model.
- Device-specific PiTFT permissions and hardened systemd packaging scaffold.
- Disabled-by-default privileged actions with strict identifier validation.
- Bounded cloudflared metrics reads and current SHA-pinned CI actions.
- Real paged status menu with page-consistent touch selection.
- Truthful `UNKNOWN` reporting for failed service/sensor probes and periodic
  input-device recovery when only part of the PiTFT input stack is present.
- Linux adapter, runtime-loop, provider-isolation, and CLI regression tests,
  bringing the local statement coverage baseline to 88 percent.
- Compatibility with Pillow's replacement for the deprecated pixel-data API,
  while retaining support for the project's older Pillow floor.
- PiTFT device-specific udev permissions ordered after Raspberry Pi OS's
  generic `99-com.rules`, preventing clean boots from restoring the broad
  `input` group and locking the panel service out of its physical buttons.

## 0.1.0-alpha.1 - 2026-08-16

- Initial public-development baseline. Not yet recommended for production deployment.
