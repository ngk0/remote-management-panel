# Hardware profiles

Hardware geometry is reviewed data, not an assortment of conditionals in the renderer.

## Adafruit PiTFT Plus 2.8-inch resistive, rotation 270

Profile ID: `adafruit-pitft-plus-28r-rotation-270`

- Framebuffer: 320x240, RGB565 expected by the Linux adapter.
- Physical switch edge: left side of the landscape display.
- Permanent label rail: 62 pixels wide.
- Current action mapping is preserved rather than silently remapped.

| Top-to-bottom | GPIO | Screen Y | Current action |
|---:|---:|---:|---|
| 1 | 27 | 8 | Select |
| 2 | 23 | 71 | Down |
| 3 | 22 | 131 | Up |
| 4 | 17 | 194 | Back |

Adafruit's Eagle board places the switch centers at native X coordinates
10.795, 22.225, 33.020, and 44.450 mm. The TFT active native-X range is
9.515–52.715 mm. Projecting that 43.2 mm active range into 240 pixels gives
approximately 7, 71, 131, and 194 pixels. The first value is rounded to 8 to
keep a visible alignment tick inside the framebuffer.

Primary sources:

- [Adafruit product guide](https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/overview)
- [Adafruit PiTFT Plus 2.8-inch PCB repository](https://github.com/adafruit/Adafruit-PiTFT-Plus-2.8-PCB)
- [Eagle board file](https://raw.githubusercontent.com/adafruit/Adafruit-PiTFT-Plus-2.8-PCB/master/Adafruit%20PiTFT%2B%202.8in.brd)

## Field verification

CAD establishes order, but enclosure position and driver offsets can move visual
alignment a few pixels. Before changing a profile:

1. Run `pitft-oob-panel show-profile`.
2. Observe each button with `evtest` from top to bottom.
3. Use the touch-test screen or a simulator overlay to confirm the alignment ticks.
4. Record the PiTFT product/revision, rotation, framebuffer dimensions, and delta.

Do not change only the labels. A logical remap requires an atomic profile and
device-tree keycode migration plus a rollback procedure.
