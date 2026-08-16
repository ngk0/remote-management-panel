# Threat model

## Assets

- Availability of the out-of-band appliance and its outbound management tunnel.
- Integrity of local network and service controls.
- Tunnel enrollment material, SSH keys, Wi-Fi credentials, and site topology.
- Operator confidence in status freshness and action outcomes.
- Isolation of temporary, home, staging, and destination networks.

## Trust boundaries

1. Physical button and resistive-touch events enter the unprivileged UI.
2. Providers read operating-system state and local metrics.
3. The UI requests an enumerated action from a future privileged broker.
4. The SSH administration account is separate from the locked panel identity.
5. Public source, CI logs, screenshots, and issues are untrusted disclosure surfaces.

## Principal threats and controls

| Threat | Control |
|---|---|
| Credential disclosure | No provisioning secrets; secret scanning; sanitized fixtures and screenshots |
| SSH compromise invokes power/network control | Dedicated locked panel user; independent broker authorization |
| Ghost touch or key bounce powers off appliance | Release-before-confirm, hold timer, expiry, and visible destructive state |
| Slow/hung probe freezes controls | Background collection, per-command timeout, stale observations |
| Malicious provider gains root execution | Providers remain unprivileged; no plugin-defined broker commands |
| Misleading cached status | `observed_at`, TTL, `UNKNOWN`, and explicit stale rendering |
| Device disappearance crashes service | Input rediscovery and isolated adapter errors |
| Public artifact exposes topology | Documentation-range addresses and synthetic identifiers only |
| Tunnel starts on the wrong physical LAN | Tunnel lifecycle stays outside panel startup; bench procedure defaults it off |
| Authorized remote shell pivots into attached LAN | Least-privilege Access/SSH policy; site-only activation; operator route audit |
| Reused private subnet reaches the wrong site | No bench private routes; explicit virtual-network isolation or renumbering |

## Out of scope

- Protecting against an attacker with physical possession and storage access.
- Enforcement of Cloudflare account policy and tunnel enrollment. Operators must
  still audit them before activation.
- Network firewall configuration.
- Raw serial-console multiplexing; only future presence/status is contemplated.

Privileged actions are disabled in simulation and remain pre-production until the
broker design receives a separate security review.
