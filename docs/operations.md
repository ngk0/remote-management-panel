# Operations

## Preflight

- Confirm the display reports 320x240 and 16 bits per pixel.
- Confirm the touchscreen and all four button event devices are present.
- Validate configuration before restarting the panel.
- Keep tunnel provisioning and credentials outside this project.

```bash
pitft-oob-panel validate-config /etc/pitft-oob-panel/config.toml
pitft-oob-panel show-profile
```

## Bench network safety

An outbound tunnel does not automatically bridge two local networks, but it is
still a remote entry point. An authorized SSH user can originate traffic from
the Pi to the currently attached network even if
`/proc/sys/net/ipv4/ip_forward` is `0`.
Therefore the safe default on a home, staging, repair, or other temporary network
is a stopped and disabled tunnel:

```bash
sudo systemctl disable --now cloudflared.service
systemctl is-active cloudflared.service || true
```

Before enabling the tunnel at its destination:

1. Confirm every published application targets only the intended service; an
   SSH route should normally target loopback, not a subnet address.
2. Confirm the final unmatched ingress rule rejects traffic.
3. Confirm Cloudflare WARP and private-network routing are disabled unless
   explicitly designed, and audit every attached network range in the provider
   control plane.
4. Confirm Cloudflare Access policy, device posture where applicable, and SSH
   authorized keys grant only the intended operators.
5. If sites reuse the same private address range, use distinct routing domains
   or virtual networks, or renumber them. Never let route selection depend on
   which physical network happens to be connected.

Only after that review should an operator run:

```bash
sudo systemctl enable --now cloudflared.service
```

Cloudflare distinguishes a published service such as `ssh://localhost:22` from
[private network routing](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/connect-cidr/),
and documents [virtual networks](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/private-net/cloudflared/tunnel-virtual-networks/)
for overlapping address space. This repository configures neither feature.

## Service behavior

The sample unit runs as the locked `pitft-oob` identity and starts only when
`/dev/fb0` exists. Udev grants that identity only the named PiTFT framebuffer,
STMPE touchscreen, and `pitft-*` buttons—not the broad `video` or `input` groups.

The unit is enabled through `con2fbmap.service.wants` and ordered after that
service. It is deliberately not wanted by `multi-user.target`, which avoids the
ordering cycle present when `con2fbmap` itself is after that target. The panel is
not ordered before or required by the management tunnel; losing the display must
not take the remote management path down.

The alpha service exposes status only. Privileged controls require the future
broker and are not enabled by the packaging scaffold.

## Troubleshooting

- White display: verify the PiTFT overlay and SPI setup before debugging this app.
- Console cursor only: verify the panel service and framebuffer permissions.
- Wrong touch coordinates: confirm rotation and `/etc/pointercal`.
- Wrong button label: run `evtest`; do not guess based on GPIO list order.
- `UNKNOWN` status: inspect the observation error and its timestamp before retrying.

## Recovery

Stop the panel service to return framebuffer ownership to the console mapping.
The panel must never modify network configuration during startup. Roll back the
package independently of Cloudflare, SSH, NetworkManager, or PiTFT overlays.
