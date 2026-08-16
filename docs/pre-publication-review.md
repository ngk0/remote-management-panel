# Pre-publication review

Review date: 2026-08-16

## Decision

The curated tree is suitable for publication as **alpha source code** after it
is placed in a new repository and the first CI run passes. It is not suitable
for a production package, appliance image, or signed release yet.

No deployment token, SSH key, real hostname, site address, SSID, journal,
framebuffer capture, or provider configuration belongs in this repository.
Provisioning and live-appliance hardening remain separate projects.

## Publication status

The alpha source was pushed to the public canonical repository on 2026-08-16.
Its Python 3.11 and 3.14 continuous-integration runs, CodeQL security analysis,
and full-history secret scans passed. Main-branch protection requires those
checks, private vulnerability reporting and push protection are enabled, and
the initial source is subject to the same protected pull-request workflow.

## Reviewed in this tree

- Core, user-interface, Linux, and simulation boundaries plus background status
  collection.
- Black 320x240 layout and left rail aligned to the four physical buttons.
- Unknown provider/action rejection and disabled-by-default privileged actions.
- Bounded command and cloudflared-metrics reads.
- Locked service identity, named-device udev rules, and systemd sandbox scaffold.
- Bench-network tunnel/pivot/overlapping-subnet guidance.
- Apache-2.0 metadata, contribution/security policy, CI, CodeQL, dependency audit,
  and full-history secret-scan workflow.
- Removal of repository-owner placeholders and deployment identifiers.

## Latest validation evidence

The 2026-08-16 clean-tree validation completed with:

- Ruff lint and formatting, strict mypy, 32 unit/regression tests, and 88 percent
  statement coverage passing on Python 3.14;
- wheel and source-distribution builds, dependency audit, and dependency
  consistency checks passing;
- a wheel install plus profile, configuration, and 320x240 simulator smoke test
  passing on 32-bit Raspberry Pi OS with Python 3.11; and
- independent Gitleaks and TruffleHog scans of the 84-file curated publication
  tree reporting no secrets.

This is partial release evidence, not a production qualification. The live
32-bit smoke test could not exercise the service-owned framebuffer, and no
64-bit hardware target was available.

## Required before a production release

- Smoke-test the public package on supported 32-bit and 64-bit Raspberry Pi OS
  images, including the display framebuffer, all four buttons, touch hotplug,
  and clean boot.
- Validate systemd sandbox directives on every supported systemd version.
- Implement and separately review the privileged broker and destructive-action
  confirmation protocol; keep controls disabled until then.
- Prove install, upgrade, rollback, uninstall, and power-loss recovery.
- Complete sustained soak, network failover, SD-card recovery, and hardware
  watchdog testing.
- Produce signed artifacts, checksums, SBOM/provenance, and a reproducible release.

## Repository-owner activation checklist

1. [x] Create a new empty public repository; do not import provisioning history.
2. [x] Enable private vulnerability reporting, secret scanning/push protection,
   Dependabot, CodeQL, and branch protection with required CI checks.
3. [x] Push this curated tree and require the first CI/secret-scan run to pass.
4. [x] Add canonical project URLs to package metadata only after the repository
   URL is final.
5. [x] Do not upload the local `dist/`, virtual environment, caches, captures,
   or any file from a live appliance.
