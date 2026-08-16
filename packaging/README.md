# Packaging scaffold

These files document the intended service identity and filesystem layout. They
are not yet a supported installer.

- Configuration: `/etc/pitft-oob-panel/config.toml`, root-owned and not secret-bearing.
- Mutable state: `/var/lib/pitft-oob-panel`, owned by the locked service account.
- Service identity: `pitft-oob`, with udev access only to the named PiTFT
  framebuffer, STMPE touchscreen, and reviewed `pitft-*`/`button@*` gpio-key
  event devices. The supported legacy names are enumerated rather than matched
  with a broad `button@*` rule.
- Privileged broker: deliberately absent from alpha packaging.

The service uses a dependency-only console pattern: enabling it creates
`con2fbmap.service.wants/pitft-oob-panel.service`. It must not be wanted by
`multi-user.target`, because deployed `con2fbmap.service` units can themselves be
ordered after that target and would form an ordering cycle. The panel remains
`After=con2fbmap.service` so framebuffer console mapping completes first.

An eventual package must install atomically, validate before restart, retain the
previous configuration, and uninstall without touching PiTFT, networking, SSH,
or tunnel configuration.

The sample service adds a closed device policy, an empty capability set,
read-only system paths, bounded memory/CPU, and syscall/address-family filters.
These directives remain a scaffold until `systemd-analyze verify` and hardware
smoke tests pass on each supported Raspberry Pi OS/systemd combination.
