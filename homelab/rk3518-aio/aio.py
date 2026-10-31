"""RK3518 all-in-one: a standalone mini PC case that mounts the bare RK3518
TV-box board (3518_ZX_4X8_V01) behind an iPistBit 7" 1024x600 HDMI touch screen.

Parts (all print without supports):
  AIO-Front     bezel + chin; holds the screen. Print face down.
  AIO-Rear      housing for the RK3518; faceted back. Print back face down.
  AIO-Stand     wedge foot, ~15 deg recline, 2x M3. Print on its side.
  AIO-FitCheck  2 mm slice of the front bezel to test the screen fit (~20 min).

Coordinates: X right, Y up, Z toward the viewer. Screen glass front at Z = 0,
screen board bottom edge (without chin) at Y = 0, centred on X = 0.

Run:  python aio.py   (needs cadquery)  -> writes stl/, step/
"""

import math
import os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- iPistBit 7" screen module (user measured) -------------------------------
SCR_W = 164.9          # board width
SCR_H = 115.0          # board height incl. the two top mounting tabs
SCR_T = 6.0            # total thickness, glass front to back parts
SCR_CLR = 0.4          # clearance around the module
ACTIVE_W, ACTIVE_H = 154.2, 85.9   # 7" 1024x600 active area
GLASS_H = 94.0
GLASS_Y0 = 15.0        # glass bottom above board bottom: glass sits ~2 mm below
                       # the top edge (photo); edit after the fit check
WIN_CY = GLASS_Y0 + GLASS_H / 2   # window centre height
WIN_MARGIN = 0.6       # window slightly larger than active area
# HDMI, 2x micro-USB and the backlight switch are on the right edge (seen from
# the front), soldered to the back of the board: from the board top they sit at
# HDMI 3-19 mm, USB 25-34 and 38-46 mm, switch 49-60 mm (from the photos)
SCR_PORT_Y = (46.0, 110.5)         # open band on the right edge for those plugs
SCR_PORT_Z = (-15.0, -1.0)         # plugs sit behind the glass, on the board back

# ---- case shape ---------------------------------------------------------------
WALL = 6.0             # bezel width around the screen (sides/top)
CHIN = 18.0            # bezel below the screen
FRONT_T = 2.0          # front lip thickness over the glass
CORNER_R = 7.0
REAR_DEPTH = 25.0      # inside depth of the rear housing
REAR_WALL = 2.5
BACK_CHAMFER = 6.0     # faceted back edge
LEDGE_OVERLAP = 3.0      # how far the rear ring overlaps the screen board edge
LEDGE_T = 2.0

X0 = -(SCR_W / 2 + SCR_CLR + WALL)
X1 = -X0
Y0 = -(SCR_CLR + CHIN)
Y1 = SCR_H + SCR_CLR + WALL
Z_FRONT = FRONT_T
Z_SPLIT = -SCR_T                       # front / rear part joint
Z_BACK = Z_SPLIT - REAR_DEPTH - REAR_WALL
OUT_W, OUT_H = X1 - X0, Y1 - Y0
CX, CY = 0.0, (Y0 + Y1) / 2

# ---- RK3518 board (same estimates as the Microlab tray; see FitCheck-RK3518)
RK_PCB_U = 85.4        # depth from back edge to the DC/RJ45/HDMI/AV port edge
RK_PCB_V = 83.5        # width from DC-jack corner to the USB/microSD edge
RK_HOLES_UV = [(61.9, 8.0), (3.3, 52.7), (47.4, 81.0)]
RK_STANDOFF_H = 6.0
RK_PILOT = 1.8
RK_PORTS_V = [(2.0, 43.0), (46.0, 68.0), (71.0, 86.0)]     # DC+RJ45, HDMI, AV
RK_USB_U = [(1.0, 21.0), (26.0, 45.0), (50.0, 69.0)]       # microSD, USB2, USB3
# board lies flat, parts facing the screen, port edge -> right wall,
# USB/microSD edge -> bottom wall
RK_XR = X1 - REAR_WALL - 1.5           # X of the port edge of the PCB
RK_YT = Y0 + REAR_WALL + 3.0 + RK_PCB_V  # Y of the DC-jack edge (top of board)
RK_Z0 = Z_BACK + REAR_WALL + RK_STANDOFF_H   # underside of PCB


def rk_xy(u, v):
    return RK_XR - (RK_PCB_U - u), RK_YT - v


# ---- joining screws (M3 self-tapping into the front part) ----------------------
SCREWS = [(-70.0, SCR_H + SCR_CLR + WALL / 2), (70.0, SCR_H + SCR_CLR + WALL / 2),
          (-75.0, Y0 + CHIN / 2), (-20.0, Y0 + CHIN / 2)]
PILOT = 2.5
CLEAR = 3.4
HEAD_D = 6.5

# ---- stand ------------------------------------------------------------------------
STAND_ANGLE = 15.0
STAND_W = 70.0
STAND_FOOT = 60.0
STAND_TOP_Y = 55.0
STAND_BOT_Y = Y0 + BACK_CHAMFER + 6
STAND_SCREWS = [(-22.0, 20.0), (22.0, 20.0)]


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def zcyl(x, y, z0, h, d):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def outline(z0, z1, inset=0.0):
    r = max(CORNER_R - inset, 0.5)
    return (cq.Workplane("XY").center(CX, CY)
            .rect(OUT_W - 2 * inset, OUT_H - 2 * inset).extrude(z1 - z0)
            .edges("|Z").fillet(r).translate((0, 0, z0)))


def front():
    f = outline(Z_SPLIT, Z_FRONT).faces(">Z").edges().fillet(1.2)
    # pocket for the screen module
    f = f.cut(box(-SCR_W / 2 - SCR_CLR, SCR_W / 2 + SCR_CLR, -SCR_CLR, SCR_H + SCR_CLR,
                  Z_SPLIT - 1, 0))
    # display window with a chamfered edge
    ww, wh = ACTIVE_W + WIN_MARGIN, ACTIVE_H + WIN_MARGIN
    win = (cq.Workplane("XY").center(0, WIN_CY).rect(ww, wh).extrude(FRONT_T + 2)
           .translate((0, 0, -1)).edges("|Z").fillet(1.5))
    f = f.cut(win)
    cham = (cq.Workplane("XY").workplane(offset=Z_FRONT - 1.0).center(0, WIN_CY)
            .rect(ww, wh).workplane(offset=1.01).rect(ww + 2.0, wh + 2.0).loft())
    f = f.cut(cham)
    # right edge: open band so the screen's HDMI / micro-USB plugs reach it
    f = f.cut(box(SCR_W / 2, X1 + 1, SCR_PORT_Y[0], SCR_PORT_Y[1], Z_SPLIT - 1, SCR_PORT_Z[1]))
    # chin detail: three fine grooves
    for i in range(3):
        y = Y0 + CHIN / 2 - 3 + 3 * i
        f = f.cut(box(-40, 40, y - 0.4, y + 0.4, Z_FRONT - 0.5, Z_FRONT + 1))
    for x, y in SCREWS:
        f = f.cut(zcyl(x, y, Z_SPLIT - 1, 8.5, PILOT))
    return f


def rear():
    hull = outline(Z_BACK, Z_SPLIT).faces("<Z").edges().chamfer(BACK_CHAMFER)
    r = hull.cut(outline(Z_BACK + REAR_WALL, Z_SPLIT + 1, inset=REAR_WALL))
    # ledge ring: overlaps the screen board edge by LEDGE_OVERLAP and presses it
    # against the bezel lip
    ring = outline(Z_SPLIT - LEDGE_T, Z_SPLIT).cut(
        box(-SCR_W / 2 + LEDGE_OVERLAP, SCR_W / 2 - LEDGE_OVERLAP,
            LEDGE_OVERLAP, SCR_H - LEDGE_OVERLAP, Z_SPLIT - 5, Z_SPLIT + 1))
    r = r.union(ring)
    # screen plugs pass through the right wall (and the ledge) behind the glass
    r = r.cut(box(SCR_W / 2 - LEDGE_OVERLAP - 1, X1 + 1, SCR_PORT_Y[0], SCR_PORT_Y[1],
                  SCR_PORT_Z[0], Z_SPLIT + 1))
    # screw bosses (trimmed to the outer shape) with counterbores from the back
    for x, y in SCREWS:
        r = r.union(zcyl(x, y, Z_BACK + 1, Z_SPLIT - Z_BACK - 1, 9.0).intersect(hull))
    for x, y in SCREWS:
        r = r.cut(zcyl(x, y, Z_BACK - 1, Z_SPLIT - Z_BACK + 2, CLEAR))
        r = r.cut(zcyl(x, y, Z_BACK - 1, (Z_SPLIT - 8) - (Z_BACK - 1), HEAD_D))
    # RK3518 standoffs
    for u, v in RK_HOLES_UV:
        x, y = rk_xy(u, v)
        r = r.union(zcyl(x, y, Z_BACK + 1, RK_Z0 - Z_BACK - 1, 7.0))
        r = r.cut(zcyl(x, y, RK_Z0 - 6, 6.5, RK_PILOT))
    # port windows: right wall
    for v0, v1 in RK_PORTS_V:
        ya, yb = RK_YT - v1, RK_YT - v0
        r = r.cut(box(X1 - REAR_WALL - 1, X1 + 1, ya, yb, RK_Z0 - 1.0, Z_SPLIT - LEDGE_T - 0.5))
    # port windows: bottom wall (microSD, USB2, USB3)
    for u0, u1 in RK_USB_U:
        xa, xb = RK_XR - (RK_PCB_U - u0), RK_XR - (RK_PCB_U - u1)
        r = r.cut(box(xa, xb, Y0 - 1, Y0 + REAR_WALL + 1, RK_Z0 - 1.0, RK_Z0 + 11.0))
    # vents: rear face upper band, top wall, bottom-left intake
    for i in range(6):
        y = 80 + i * 6
        r = r.cut(box(-62, 62, y, y + 2.5, Z_BACK - 1, Z_BACK + REAR_WALL + 1))
    for i in range(12):
        x = -60 + i * 10.5
        r = r.cut(box(x, x + 3, Y1 - REAR_WALL - 1, Y1 + 1, Z_BACK + 6, Z_SPLIT - 4))
    for i in range(6):
        x = X0 + 14 + i * 10.5
        r = r.cut(box(x, x + 3, Y0 - 1, Y0 + REAR_WALL + 1, Z_BACK + 6, Z_SPLIT - 4))
    # stand screw pads
    for x, y in STAND_SCREWS:
        r = r.union(zcyl(x, y, Z_BACK + 1, REAR_WALL + 2, 9.0))
        r = r.cut(zcyl(x, y, Z_BACK - 1, REAR_WALL + 4, PILOT))
    return r


def stand():
    t = math.radians(STAND_ANGLE)
    up = (math.cos(t), math.sin(t))                  # world-up in (Y, Z)
    dirn = (math.sin(t), -math.cos(t))               # along the desk, backwards
    f = lambda p: p[0] * up[0] + p[1] * up[1]
    d0 = f((Y0, Z_BACK))                             # case rests on its back-bottom edge
    T = (STAND_TOP_Y, Z_BACK)
    Q = (STAND_BOT_Y, Z_BACK)
    h = f(Q) - d0
    Pa = (Q[0] - h * up[0], Q[1] - h * up[1])
    Pb = (Pa[0] + STAND_FOOT * dirn[0], Pa[1] + STAND_FOOT * dirn[1])
    s = (cq.Workplane("YZ").polyline([T, Pb, Pa, Q]).close()
         .extrude(STAND_W).translate((-STAND_W / 2, 0, 0)))
    s = s.edges("|X").fillet(2.0)
    for x, y in STAND_SCREWS:
        s = s.cut(zcyl(x, y, Z_BACK - 200, 201, CLEAR))
        s = s.cut(zcyl(x, y, Z_BACK - 200, 200 - 6, HEAD_D))
    return s


def fitcheck():
    return front().intersect(box(X0 - 1, X1 + 1, Y0 - 1, Y1 + 1, -2.0, Z_FRONT + 1))


PARTS = {"AIO-Front": front, "AIO-Rear": rear, "AIO-Stand": stand, "AIO-FitCheck": fitcheck}

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "step"), exist_ok=True)
    for name, fn in PARTS.items():
        p = fn()
        cq.exporters.export(p, os.path.join(HERE, "stl", name + ".stl"),
                            tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(HERE, "step", name + ".step"))
        bb = p.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, valid={p.val().isValid()}")
