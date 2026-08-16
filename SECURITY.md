# Security policy

## Supported versions

No version is currently production-supported. Security fixes target the latest
pre-release until the project reaches 1.0.

## Reporting a vulnerability

Use the repository's private security-advisory feature. Do not open a public
issue containing credentials, internal topology, or a working exploit.

Include the affected version, deployment model, impact, reproduction steps, and
whether the issue crosses the unprivileged-panel/privileged-action boundary.

## Credential boundary

This project does not provision tunnels or store their enrollment tokens. Never
commit tunnel tokens, SSH material, Wi-Fi credentials, access policies, real
captures, or service logs. Rotate any credential that has entered a public issue,
build log, screenshot, or Git history; deleting the visible text is insufficient.

## Privileged actions

Privileged action support is not production-ready in this alpha. Deployments
must not grant the interactive SSH account passwordless access to reboot,
poweroff, or network-control helpers. The intended design uses a locked service
account and a broker that accepts only reviewed action identifiers.

## Tunnel and attached-network boundary

An SSH-only tunnel is not a layer-2 bridge, but it still places a remotely
reachable shell on the LAN to which the appliance is attached. Disabling IP
forwarding does not prevent an authenticated shell from initiating connections
to that LAN.

Keep tunnels disabled on bench and temporary networks. Before site activation,
verify that only intended loopback services are published, private-network/WARP
routing is disabled unless explicitly required, no unintended CIDR route points
at the appliance, and Access plus SSH authorization follows least privilege.
Overlapping private address ranges require deliberate routing isolation; never
assume identical RFC 1918 addresses refer to the intended site.
