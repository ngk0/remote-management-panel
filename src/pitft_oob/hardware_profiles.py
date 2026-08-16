"""Reviewed physical profiles; values are data, not runtime autodetection."""

from pitft_oob.models import ButtonAction, ButtonSlot, HardwareProfile

PITFT_28R_ROTATION_270 = HardwareProfile(
    profile_id="adafruit-pitft-plus-28r-rotation-270",
    display_width=320,
    display_height=240,
    rotation=270,
    rail_width=62,
    # Top-to-bottom when the buttons are physically left of the display.
    # CAD-projected centers are approximately 7, 71, 131, and 194 pixels.
    # These logical actions preserve the deployed key mapping.
    buttons=(
        ButtonSlot(gpio=27, center_y=8, action=ButtonAction.SELECT, label="SELECT"),
        ButtonSlot(gpio=23, center_y=71, action=ButtonAction.DOWN, label="DOWN"),
        ButtonSlot(gpio=22, center_y=131, action=ButtonAction.UP, label="UP"),
        ButtonSlot(gpio=17, center_y=194, action=ButtonAction.BACK, label="BACK"),
    ),
    source_url="https://github.com/adafruit/Adafruit-PiTFT-Plus-2.8-PCB",
)


PROFILES: dict[str, HardwareProfile] = {
    PITFT_28R_ROTATION_270.profile_id: PITFT_28R_ROTATION_270,
}


def get_profile(profile_id: str) -> HardwareProfile:
    try:
        return PROFILES[profile_id]
    except KeyError as exc:
        choices = ", ".join(sorted(PROFILES))
        raise ValueError(
            f"Unknown hardware profile {profile_id!r}; choose one of: {choices}"
        ) from exc
