"""Custom trays for the CB4D Microlab V1 (160 x 160 mm base) mini rack.

Generates:
  Tray-1U-RK3518        - bare RK3518 TV-box board (3518_ZX_4X8_V01)
  Tray-1U-RPi3x2        - two Raspberry Pi 3B+ side by side
  Tray-0.5U-RPi3        - one Raspberry Pi 3B+ (print two for a stacked 1U pair)

The rack interface was measured from the official V1 trays (Tray-1U-RPi5,
Tray-0.5U-RPi4, Tray-1U-TLSG105) so these bolt in exactly like them:
  face plate 148 x 3 mm, 44.45 mm (1U) / 22.2 mm (0.5U) tall
  M3 clearance holes (3.2 mm) at x = 10.5 / 137.5, z = 11.12 (+ 33.37 for 1U)
  tray body between x = 18.2 .. 129.8 (columns are 112 mm apart)

Coordinates: x across the face (viewed from the front, left -> right),
y = depth into the rack (0 = front of the face plate), z = up (0 = bottom).

Run:  python trays.py   (needs cadquery)  -> writes stl/, step/
"""

import os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Microlab V1 rack interface (measured, do not change) -------------------
FACE_W = 148.0
FACE_T = 3.0
U1 = 44.45
U05 = 22.2
HOLE_D = 3.2
HOLE_X = (10.5, 137.5)
HOLE_Z_1U = (11.12, 33.37)
HOLE_Z_05U = (11.12,)
BODY_X0, BODY_X1 = 18.2, 129.8   # everything behind the face must stay inside this
COLUMN_DEPTH = 23.0              # columns occupy y = 3 .. ~23 behind the face
FLOOR_T = 2.0
CHAMFER = 1.0


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def cyl(x, y, z0, h, d):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def side_profile(x0, x1, pts):
    """Extrude a (y, z) polygon across x0..x1 (used for gussets/ribs)."""
    return (cq.Workplane("YZ").polyline(pts).close()
            .extrude(x1 - x0).translate((x0, 0, 0)))


def base_tray(height, depth, hole_z):
    face = box(0, FACE_W, 0, FACE_T, 0, height).edges("|Y").chamfer(CHAMFER)
    for hx in HOLE_X:
        for hz in hole_z:
            face = face.cut(cq.Workplane("XZ").center(hx, hz).circle(HOLE_D / 2)
                            .extrude(-10).translate((0, -1, 0)))
    floor = box(BODY_X0, BODY_X1, 0, depth, 0, FLOOR_T)
    # small fillet strip where floor meets face
    fillet = side_profile(BODY_X0, BODY_X1, [(FACE_T, FLOOR_T), (FACE_T, FLOOR_T + 3),
                                             (FACE_T + 3, FLOOR_T)])
    return face.union(floor).union(fillet)


def wall(x0, x1, y_end, z_front):
    """Sloped gusset like the stock V1 trays, from the face back to y_end."""
    return side_profile(x0, x1, [(FACE_T - 0.01, 0), (FACE_T - 0.01, z_front),
                                 (y_end, FLOOR_T), (y_end, 0)])


def window(t, x0, x1, z0, z1):
    return t.cut(box(x0, x1, -1, FACE_T + 1, z0, z1))


def vents(t, x0, x1, y0, y1, slot=3.0, pitch=6.0, end=4.0):
    """Floor slots running front-to-back for vertical airflow."""
    x = x0
    while x + slot <= x1:
        t = t.cut(box(x, x + slot, y0 + end, y1 - end, -1, FLOOR_T + 1))
        x += pitch
    return t


def clip_to_body(solid, depth, height):
    return solid.intersect(box(BODY_X0, BODY_X1, 0, depth + 1, 0, height))


def standoff(x, y, top, od, pilot=None, peg=None):
    s = cyl(x, y, 0, top, od)
    if pilot:
        s = s.cut(cyl(x, y, top - 5, 6, pilot))
    if peg:
        d, h = peg
        p = cyl(x, y, top, h, d).faces(">Z").edges().chamfer(0.5)
        s = s.union(p)
    return s


# ---- RK3518 board (3518_ZX_4X8_V01) -----------------------------------------
# Board is placed with its DC / RJ45 / HDMI / audio edge facing the front and
# its USB / microSD edge on the right-hand side (reachable through a side panel).
# Board coords: u = from the antenna-side edge toward the port edge (front),
#               v = from the DC-jack corner toward the USB edge (left -> right).
# Values estimated from photos with a caliper in frame; tolerance about +/-1.5 mm.
# Measure your board and edit these if the pilot holes don't line up.
RK_PCB_U = 85.4          # depth of PCB (front port edge -> back edge)
RK_PCB_V = 83.5          # width of PCB across the face
RK_HOLES_UV = [(61.9, 8.0),   # near DC jack
               (3.3, 52.7),   # back edge, middle
               (47.4, 81.0)]  # between USB2 and USB3
RK_X0 = 43.0             # x of the board's left (v = 0) edge
RK_Y0 = 5.0              # y of the board's front PCB edge (jacks overhang ~2 mm)
RK_STANDOFF_H = 4.0      # clearance under board for bottom-side parts
RK_PILOT = 1.8           # for M2 / ST2.2 self-tapping screws (the box's own screws)
# front cut-outs as (v0, v1) along the edge, in board coords
RK_PORTS_V = [(2.0, 43.0),    # DC jack + RJ45
              (46.0, 68.0),   # HDMI
              (71.0, 86.0)]   # 3.5 mm audio/AV
RK_WIN_Z = (4.0, 27.0)


def tray_rk3518():
    depth = RK_Y0 + RK_PCB_U + 4.0
    t = base_tray(U1, depth, HOLE_Z_1U)
    t = t.union(wall(BODY_X0, BODY_X0 + 2.4, 66, 26))
    # right side stays open behind the column so USB/microSD plugs can reach
    t = t.union(wall(BODY_X1 - 2.4, BODY_X1, COLUMN_DEPTH - 2, 26))
    for v0, v1 in RK_PORTS_V:
        t = window(t, RK_X0 + v0, min(RK_X0 + v1, BODY_X1 - 0.5), *RK_WIN_Z)
    t = vents(t, RK_X0 + 6, RK_X0 + RK_PCB_V - 6, RK_Y0 + 6, RK_Y0 + RK_PCB_U - 6)
    top = FLOOR_T + RK_STANDOFF_H
    for u, v in RK_HOLES_UV:
        x, y = RK_X0 + v, RK_Y0 + (RK_PCB_U - u)
        t = t.union(standoff(x, y, top, 7.0, pilot=RK_PILOT))
    return t


# ---- Raspberry Pi 3B+ -------------------------------------------------------
# 85 x 56 board, holes 58 x 49 mm, 3.5 mm from the edges, USB/RJ45 on a short
# edge (holes 23.5 / 81.5 mm from that edge). Seen from the front with the
# ports facing you, the RJ45 is always on the LEFT and the GPIO on the RIGHT.
PI_W, PI_L = 56.0, 85.0
PI_HOLES_FROM_PORT_EDGE = (23.5, 81.5)
PI_HOLES_ACROSS = (3.5, 52.5)


def pi_holes(x0, y_front):
    return [(x0 + a, y_front + b) for a in PI_HOLES_ACROSS for b in PI_HOLES_FROM_PORT_EDGE]


def tray_rpi3_05u():
    """Single Pi 3B+, same placement as the stock V1 0.5U Pi 4 tray."""
    depth = 91.1
    x0, yf = 46.0, 3.5
    t = base_tray(U05, depth, HOLE_Z_05U)
    for x in (BODY_X0, BODY_X1 - 2.4):
        t = t.union(wall(x, x + 2.4, 66, U05 - 0.01))
    t = window(t, x0 + 1.0, x0 + PI_W - 1.0, 5.0, U05 + 1)   # open to the top like V1
    t = vents(t, x0 + 8, x0 + PI_W - 8, yf + 8, yf + PI_L - 8)
    for x, y in pi_holes(x0, yf):
        t = t.union(standoff(x, y, FLOOR_T + 2.2, 6.6, pilot=2.2))  # M2.5 self-tap
    return t


def tray_rpi3x2_1u():
    """Two Pi 3B+ side by side.

    Two 56 mm boards need 112 mm, which is exactly the gap between the columns,
    so the boards sit just behind the columns (front edge at y = 25) where the
    rack is wider. Tray body itself still fits between the columns; the Pis are
    dropped onto locating pegs AFTER the tray is installed (through a side
    panel opening) and held by gravity + the side panels.
    """
    yf = COLUMN_DEPTH + 2.0
    depth = yf + PI_L + 3.0
    xa, xb = 16.0, 76.0      # left/right board edges (RJ45 plug clears column)
    t = base_tray(U1, depth, HOLE_Z_1U)
    # no side walls: plugs for the outer ports pass right next to the columns.
    # centre rib between the boards: tall in the column zone, low under the boards
    t = t.union(side_profile(73.0, 75.0, [(FACE_T - 0.01, 0), (FACE_T - 0.01, 30),
                                          (yf - 1, 14), (yf - 1, FLOOR_T + 2.5),
                                          (depth, FLOOR_T + 2.5), (depth, 0)]))
    t = window(t, BODY_X0 + 0.5, 73.0, 4.0, 28.0)
    t = window(t, 75.0, BODY_X1 - 0.5, 4.0, 28.0)
    for x0 in (xa, xb):
        t = vents(t, max(x0 + 8, BODY_X0 + 2), min(x0 + PI_W - 8, BODY_X1 - 2),
                  yf + 8, yf + PI_L - 8)
    top = FLOOR_T + 3.0
    for x0 in (xa, xb):
        for x, y in pi_holes(x0, yf):
            s = standoff(x, y, top, 6.0, peg=(2.4, 2.6))
            t = t.union(clip_to_body(s, depth, U1))
    return t


def fitcheck_rk3518():
    """1.2 mm plate with the board outline and a pin at each hole position.

    Prints in ~10 min. Lay the board on it: if all three pins go through the
    board's holes, the full tray will line up. If not, measure and edit
    RK_HOLES_UV above, then regenerate.
    """
    plate = box(0, RK_PCB_V, 0, RK_PCB_U, 0, 1.2)
    plate = plate.cut(box(8, RK_PCB_V - 8, 8, RK_PCB_U - 8, -1, 2))
    for u, v in RK_HOLES_UV:
        x, y = v, RK_PCB_U - u
        plate = plate.union(cyl(x, y, 0, 1.2, 8.0))
        pin = cyl(x, y, 1.2, 4.0, 1.7).faces(">Z").edges().chamfer(0.4)
        plate = plate.union(pin)
    # arrow toward the port edge (front)
    plate = plate.union(side_profile(RK_PCB_V / 2 - 1, RK_PCB_V / 2 + 1,
                                     [(RK_PCB_U - 8, 0), (RK_PCB_U - 8, 1.2),
                                      (RK_PCB_U, 1.2), (RK_PCB_U, 0)]))
    return plate


PARTS = {
    "Tray-1U-RK3518": tray_rk3518,
    "FitCheck-RK3518": fitcheck_rk3518,
    "Tray-1U-RPi3x2": tray_rpi3x2_1u,
    "Tray-0.5U-RPi3": tray_rpi3_05u,
}

if __name__ == "__main__":
    for name, fn in PARTS.items():
        part = fn()
        cq.exporters.export(part, os.path.join(HERE, "stl", name + ".stl"),
                            tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(part, os.path.join(HERE, "step", name + ".step"))
        bb = part.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.2f} mm, "
              f"valid={part.val().isValid()}")
