"""Front panels for a 6U Microlab V1: a 5U flush 7" screen panel + a 1U vent.

Panel-5U-Screen7   iPistBit 7" LCD Display-C, portrait, glass behind a 1.5 mm
                   bezel lip. Hidden plug bay under the screen (HDMI, Touch,
                   micro-USB, backlight switch) with a front intake grille.
Strip-Screen7      x2, retainer strips that sit between the panel and the
                   columns and are clamped by the panel's own M3 screws.
Panel-1U-Vent      matching 10 mm vent panel for the remaining 1U (intake).
FitCheck-Screen7   a 3 mm slice of the screen panel to test the screen fit.

Panel interface measured from the V1 Panel-1U/2U/4U-Solid parts:
  width 148, height n*44.5 - 0.05, M3 holes (3.2) at x = 10.5 / 137.5,
  z = 11.12 + 22.25 k. The columns sit behind x = -2..18 and 130..150 and are
  112 mm apart, so the 115 mm wide screen must sit in front of them: the screen
  panel is 10 mm thick (about 8 mm prouder than the stock 2 mm panels).

Coordinates: X across the panel (front view, left -> right), Y up from the
panel bottom, Z = 0 at the front face, negative toward the rack.

Run:  python panels.py   (needs cadquery)  -> writes stl/, step/
"""

import os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Microlab V1 panel interface (measured) ----------------------------------
W = 148.0
HOLE_X = (10.5, 137.5)
HOLE_D = 3.2
HOLE_Z0, PITCH = 11.12, 22.25


def panel_h(units):
    return units * 44.5 - 0.05


def hole_ys(units):
    return [HOLE_Z0 + PITCH * k for k in range(units * 2)]


# ---- thick panel build-up -------------------------------------------------------
T = 10.0               # panel thickness
LIP = 1.5              # bezel lip in front of the glass
STRIP_T = 2.0          # retainer strip thickness (recessed into the back)
CB_D = 6.5             # counterbore for M3 heads (front)
CB_LEFT = 5.0          # material left under the head (panel + strip): M3 x 12
EDGE_CHAMFER = 2.5

# ---- iPistBit 7" LCD Display-C (landscape measurements, see ../rk3518-aio) ----
SCR_W, SCR_H, SCR_T, SCR_CLR = 164.9, 115.0, 6.0, 0.4
SCR_MAIN_H = 111.0                     # board height without the two tabs
ACTIVE_W, ACTIVE_H = 154.2, 85.9
GLASS_Y0, GLASS_H = 15.0, 94.0         # same estimate as the all-in-one case
# ports on the landscape right edge, measured down from the board top
PORTS_FROM_TOP = (3.0, 60.0)

# Portrait, rotated clockwise: landscape right edge (ports) -> bottom,
# landscape top (tabs) -> right side. Rotate the display 90 deg in the OS.
UNITS = 5
H = panel_h(UNITS)
TOP_MARGIN = 8.0
PK_X0 = W / 2 - SCR_H / 2 - SCR_CLR          # pocket (portrait: width = SCR_H)
PK_X1 = W / 2 + SCR_H / 2 + SCR_CLR
PK_Y1 = H - TOP_MARGIN
PK_Y0 = PK_Y1 - SCR_W - 2 * SCR_CLR
PK_Z = -(LIP + SCR_T + SCR_CLR)              # pocket floor (screen back)
SCR_X0 = PK_X0 + SCR_CLR                     # screen envelope left edge
SCR_Y0 = PK_Y0 + SCR_CLR                     # screen envelope bottom edge


def land_to_panel(lx, ly):
    """landscape (from bottom-left of the board) -> panel X, Y."""
    return SCR_X0 + ly, SCR_Y0 + (SCR_W - lx)


WIN_CX, WIN_CY = land_to_panel(SCR_W / 2, GLASS_Y0 + GLASS_H / 2)
WIN_W, WIN_H = ACTIVE_H + 0.6, ACTIVE_W + 0.6      # portrait window
PORT_X0 = SCR_X0 + SCR_MAIN_H - PORTS_FROM_TOP[1] - 4
PORT_X1 = SCR_X0 + SCR_MAIN_H - PORTS_FROM_TOP[0] + 4

# plug bay under the screen, open toward the rack (between the columns)
BAY_X0, BAY_X1 = 20.0, 128.0
BAY_Y0 = 6.0
FRONT_SKIN = 2.5

# retainer strips (left / right), clamped by the panel screws
STRIP_X = [(3.0, SCR_X0 + 5.5), (SCR_X0 + SCR_MAIN_H - 4.5, W - 3.0)]
STRIP_Y = (PK_Y0 - 4.0, PK_Y1 + 4.0)


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def zcyl(x, y, z0, h, d):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def thick_plate(units):
    h = panel_h(units)
    p = box(0, W, 0, h, -T, 0).faces(">Z").edges().chamfer(EDGE_CHAMFER)
    for x in HOLE_X:
        for y in hole_ys(units):
            p = p.cut(zcyl(x, y, -T - 1, T + 2, HOLE_D))
            p = p.cut(zcyl(x, y, -T + CB_LEFT, T, CB_D))
    return p


def screen_panel():
    p = thick_plate(UNITS)
    # pocket for the screen, open at the back
    p = p.cut(box(PK_X0, PK_X1, PK_Y0, PK_Y1, -T - 1, -LIP))
    # display window with chamfered edge
    win = (cq.Workplane("XY").center(WIN_CX, WIN_CY).rect(WIN_W, WIN_H)
           .extrude(LIP + 2).translate((0, 0, -LIP - 1)).edges("|Z").fillet(1.5))
    p = p.cut(win)
    cham = (cq.Workplane("XY").workplane(offset=-0.8).center(WIN_CX, WIN_CY)
            .rect(WIN_W, WIN_H).workplane(offset=0.81).rect(WIN_W + 1.6, WIN_H + 1.6).loft())
    p = p.cut(cham)
    # plug bay below the screen, joined to the pocket where the ports are
    p = p.cut(box(BAY_X0, BAY_X1, BAY_Y0, PK_Y0 + 1, -T - 1, -FRONT_SKIN))
    p = p.cut(box(PORT_X0, PORT_X1, BAY_Y0, PK_Y0 + 6, -T - 1, -LIP - 1.0))
    # intake grille into the bay
    for i in range(7):
        y = BAY_Y0 + 6 + i * 5.0
        if y + 2.2 > PK_Y0 - 4:
            break
        p = p.cut(box(30, 118, y, y + 2.2, -FRONT_SKIN - 1, 1))
    # recesses for the retainer strips
    for x0, x1 in STRIP_X:
        p = p.cut(box(x0 - 0.2, x1 + 0.2, STRIP_Y[0] - 0.2, STRIP_Y[1] + 0.2,
                      -T - 1, -T + STRIP_T))
    return p


def strip(side):
    x0, x1 = STRIP_X[side]
    s = box(x0, x1, STRIP_Y[0], STRIP_Y[1], -T, -T + STRIP_T)
    s = s.edges("|Z").fillet(1.0)
    for x in HOLE_X:
        for y in hole_ys(UNITS):
            if x0 < x < x1 and STRIP_Y[0] + 3 < y < STRIP_Y[1] - 3:
                s = s.cut(zcyl(x, y, -T - 1, STRIP_T + 2, 3.4))
    return s.translate((0, 0, T))     # print flat at z = 0


def vent_panel():
    p = thick_plate(1)
    h = panel_h(1)
    for i in range(14):
        x = 22 + i * 7.6
        if x + 3.6 > 126:
            break
        p = p.cut(box(x, x + 3.6, 7, h - 7, -T - 1, 1))
    # hollow the back so it weighs about the same as a stock panel
    p = p.cut(box(19, 129, 4, h - 4, -T - 1, -FRONT_SKIN))
    return p


def fitcheck():
    return screen_panel().intersect(box(-1, W + 1, PK_Y0 - 8, PK_Y1 + 8, -3.0, 1))


PARTS = {
    "Panel-5U-Screen7": screen_panel,
    "Strip-Screen7-L": lambda: strip(0),
    "Strip-Screen7-R": lambda: strip(1),
    "Panel-1U-Vent": vent_panel,
    "FitCheck-Screen7": fitcheck,
}

if __name__ == "__main__":
    for name, fn in PARTS.items():
        p = fn()
        cq.exporters.export(p, os.path.join(HERE, "stl", name + ".stl"),
                            tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(HERE, "step", name + ".step"))
        bb = p.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, valid={p.val().isValid()}")
