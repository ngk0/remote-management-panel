from pitft_oob.models import ActionRisk, ActionSpec

ACTIONS: dict[str, ActionSpec] = {
    "cloudflared-restart": ActionSpec(
        "cloudflared-restart", "Restart cloudflared", ActionRisk.DISRUPTIVE, "service-control"
    ),
    "wifi-reconnect": ActionSpec(
        "wifi-reconnect", "Reconnect Wi-Fi", ActionRisk.DISRUPTIVE, "network-control"
    ),
    "dhcp-renew": ActionSpec(
        "dhcp-renew", "Renew wired DHCP", ActionRisk.DISRUPTIVE, "network-control"
    ),
    "reboot": ActionSpec("reboot", "Reboot appliance", ActionRisk.DESTRUCTIVE, "power-control"),
    "poweroff": ActionSpec(
        "poweroff", "Power off appliance", ActionRisk.DESTRUCTIVE, "power-control"
    ),
}
