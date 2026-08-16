# Contributing

Thank you for helping improve PiTFT OOB Panel.

## Before opening a change

1. Search existing issues.
2. For hardware changes, identify the exact board, display rotation, OS release,
   framebuffer dimensions, and input-device names.
3. Never attach live tunnel tokens, SSH keys, SSIDs, public hostnames, internal
   addresses, journals, or unsanitized framebuffer captures.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
mypy src
```

Windows users can run the simulator and unit tests, but Linux hardware adapters
require a Raspberry Pi or equivalent test host.

## Design rules

- Core models must remain immutable and independent of Linux.
- Rendering must consume view models, never invoke subprocesses.
- Providers must have bounded I/O and report `UNKNOWN` plus an error on failure.
- Configuration may select known actions but must never contain arbitrary commands.
- Privileged action identifiers are reviewed as security-sensitive API changes.
- New hardware profiles require a primary-source reference and observed-device test.
- Tunnel provisioning, credentials, private routes, and real site identifiers do
  not belong in fixtures, examples, screenshots, or tests.

Add tests for behavior changes and update the changelog. By contributing, you
agree that your contribution is licensed under Apache-2.0.
