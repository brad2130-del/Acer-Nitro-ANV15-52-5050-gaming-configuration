# Microlab V1 custom trays

Custom trays for the [CB4D Microlab](https://makerworld.com/en/models/1062225-microlab-mini-modular-home-server-rack)
**V1** (160 × 160 mm base). The rack interface was measured from the official V1
`Tray-1U-RPi5`, `Tray-0.5U-RPi4` and `Tray-1U-TLSG105` parts, so these trays bolt
into the columns exactly like the stock ones: M3 × 8 screws, same hole positions,
same 111.6 mm body between the columns.

| File | Height | What it holds |
|-|-|-|
| `stl/Tray-1U-RK3518.stl` | 1U | Bare RK3518 TV-box board (`3518_ZX_4X8_V01`). The DC/RJ45/HDMI/AV edge faces the front and the USB/microSD edge faces the right side. |
| `stl/FitCheck-RK3518.stl` | — | Optional ~10-minute print that checks the board's hole positions before you print the full tray. |
| `stl/Tray-1U-RPi3x2.stl` | 1U | Two Raspberry Pi 3B+ side by side. Read the notes below first. |
| `stl/Tray-0.5U-RPi3.stl` | 0.5U | One Pi 3B+. Print two to stack both Pis in 1U with flush, easy-to-reach ports. |

Your `Microlab.3mf` already has the other two parts you need:
- **TP-Link TL-SG105**: plate 1, `Tray-1U-TLSG105` + `TrayAcc-1-TLSG105`
- **Raspberry Pi 5**: plate 14, `Tray-1U-RPi5`

## Suggested 4U stack (top → bottom)

| U | Tray |
|-|-|
| 1 | TL-SG105 (stock) |
| 2 | Pi 5 (stock) |
| 3 | 2 × Pi 3B+ (`Tray-1U-RPi3x2`, or two `Tray-0.5U-RPi3`) |
| 4 | RK3518 (`Tray-1U-RK3518`) |

That fills a 4U column set exactly. Put the RK3518 on a side where its USB edge
faces a removable or passthrough side panel.

## Notes

### RK3518 tray
- The three mounting holes and the port positions were **estimated from photos**
  with a caliper in frame, so expect about ±1.5 mm error. Print `FitCheck-RK3518`
  first and lay the board on it. If all three pins go through the holes, print the
  tray. If they don't, measure each hole centre from the board edges, edit
  `RK_HOLES_UV` in `trays.py`, and regenerate.
- The standoffs are 4 mm tall with 1.8 mm pilot holes for the box's original
  M2/ST2.2 self-tapping screws.
- The front windows are oversized. The right side stays open behind the column so
  USB and microSD plugs can reach the board.

### Two Pi 3B+ side by side (`Tray-1U-RPi3x2`)
The columns are 112 mm apart, and two 56 mm Pi boards are also 112 mm, so the
boards can't sit flush at the front. This tray places them **just behind the
columns**, where the rack is wider. The trade-offs:
- The ports sit about 20 mm behind the face. RJ45 and USB plugs reach through,
  but the RJ45 latch is harder to press.
- The Pis overhang the tray body slightly, so they can't slide in with the tray.
  **Bolt the empty tray in first, then drop each Pi onto its four locating pegs
  through a side-panel opening.** Gravity and the side panels hold them in place.
- The right Pi's micro-USB power and HDMI face the left Pi, with only a 4 mm gap.
  Power it through the GPIO header (5 V on pin 2 or 4, GND on pin 6), or power both
  Pis that way so the cabling matches. The left Pi can use its micro-USB normally,
  out through the left side.

If that's too fiddly, print **two `Tray-0.5U-RPi3`** instead. It's the same 1U of
space, the ports are flush at the front, and the Pis screw down normally with
M2.5 self-tappers.

## Printing
- Print face down on the build plate, like the stock trays.
- Settings: PLA or PETG, 0.2 mm layers, 3 walls, 15–20 % infill. No supports needed.
- The floor has vent slots for the rack's vertical airflow (top 120 mm fan).

## Regenerating
`trays.py` is a [CadQuery](https://cadquery.readthedocs.io/) script. All board
positions and dimensions are parameters at the top of each section.

```sh
python3 -m venv .venv && .venv/bin/pip install cadquery
.venv/bin/python trays.py        # writes stl/ and step/
```

`step/` has editable STEP versions for Fusion, FreeCAD, Onshape and similar tools.

## Credit
Microlab is by Can Berk Durmus (CB4D) under the MIT license. These trays are new
geometry that only reuses the measured rack interface.
