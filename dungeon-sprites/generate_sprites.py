#!/usr/bin/env python3
"""Dungeon pixel-art sprites based on a kid's drawing.

Characters from the drawing:
  * Skull Knight - horned skull head, blue tunic with a green skull gem,
    red arms/boots with yellow stripes, brown pants, spidery side legs.
  * Horned Dungeon Door - purple stone frame, black door, red/yellow eye,
    white peephole, yellow keyhole.
  * Skull Key - black key with a green skull in the bow.

Plus dungeon tiles (floor, wall, torch) and a composed scene.

Usage:  python3 generate_sprites.py [output_dir]
Requires Pillow.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

T = (0, 0, 0, 0)


def C(r, g, b, a=255):
    return (r, g, b, a)


OL = C(22, 17, 28)
BONE, BONE_S, SOCK = C(238, 232, 214), C(184, 174, 156), C(32, 24, 38)
HORN, HORN_S = C(222, 212, 190), C(150, 138, 120)
BLUE, BLUE_L, BLUE_D = C(44, 66, 196), C(84, 114, 236), C(26, 36, 124)
RED, RED_D = C(206, 32, 84), C(140, 18, 60)
YEL, YEL_D = C(252, 204, 48), C(196, 140, 20)
BRN, BRN_L, BRN_D = C(86, 54, 36), C(118, 80, 56), C(56, 34, 24)
GRN, GRN_D = C(66, 180, 76), C(30, 112, 48)
PUR, PUR_L, PUR_D = C(136, 104, 206), C(176, 150, 232), C(88, 64, 150)
PAD, PAD_L = C(112, 112, 148), C(156, 156, 192)
DOOR, DOOR_L, DOOR_D = C(44, 38, 52), C(64, 58, 74), C(26, 22, 32)
IRON = C(84, 78, 96)
KEY, KEY_L = C(48, 44, 58), C(100, 94, 118)
SPARK = C(255, 250, 220)


# ---------------------------------------------------------------- helpers
def outline(img, color=OL):
    """Add a 1px dark outline around every opaque shape."""
    w, h = img.size
    src = img.copy().load()
    px = img.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] and src[nx, ny] != color:
                    px[x, y] = color
                    break
    return img


def capsule(img, x0, y0, x1, y1, r, colfn):
    """Fill a thick line segment; colfn(t, below) picks the colour."""
    w, h = img.size
    px = img.load()
    vx, vy = x1 - x0, y1 - y0
    L2 = vx * vx + vy * vy or 1
    for y in range(h):
        for x in range(w):
            t = max(0.0, min(1.0, ((x - x0) * vx + (y - y0) * vy) / L2))
            cx, cy = x0 + t * vx, y0 + t * vy
            if math.hypot(x - cx, y - cy) <= r:
                c = colfn(t, y - cy)
                if c:
                    px[x, y] = c


def mirror_x(pts, w):
    return [(w - 1 - x, y) for x, y in pts]


def scale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


# ---------------------------------------------------------------- hero
HORN_L = [(9, 11), (10, 11), (8, 10), (9, 10), (7, 9), (8, 9), (6, 8), (7, 8),
          (6, 7), (7, 7), (6, 6), (7, 6), (6, 5), (7, 5), (7, 4), (7, 3), (8, 2)]


def hero(b=0):
    """Skull Knight, 32x48. b = 1 bobs the upper body down a pixel."""
    im = Image.new("RGBA", (32, 48), T)
    d = ImageDraw.Draw(im)
    p = im.load()

    # spidery side legs (thin, drawn behind the body)
    for seg in [(11, 27, 5, 30), (5, 30, 4, 34), (20, 27, 26, 30), (26, 30, 27, 34)]:
        d.line((seg[0], seg[1] + b, seg[2], seg[3] + b), fill=OL)

    # pants
    d.rectangle((11, 32, 20, 39), fill=BRN)
    d.rectangle((19, 32, 20, 39), fill=BRN_D)
    for y in range(33, 36):
        p[12, y] = BRN_L
        p[17, y] = BRN_L
    d.rectangle((15, 36, 16, 39), fill=T)

    # boots with yellow lightning stripes
    for x0, toe, sgn in ((10, 8, 1), (17, 22, -1)):
        d.rectangle((x0, 40, x0 + 4, 45), fill=RED)
        d.rectangle((min(toe, toe + 1), 43, max(toe, toe + 1), 45), fill=RED)
        d.line((min(toe, x0), 45, max(toe + 1, x0 + 4), 45), fill=RED_D)
        for i in range(5):
            x = (x0 + i) if sgn > 0 else (x0 + 4 - i)
            p[x, 44 - i] = YEL
            if 0 < 44 - i:
                xx = x + sgn
                if x0 <= xx <= x0 + 4:
                    p[xx, 44 - i] = YEL

    # arms: red with a yellow band, darker underside
    def arm(t, below):
        if 0.42 < t < 0.6:
            return YEL_D if below > 0.6 else YEL
        return RED_D if below > 0.6 else RED

    capsule(im, 9, 19 + b, 2, 27 + b, 1.6, arm)
    capsule(im, 22, 19 + b, 29, 27 + b, 1.6, arm)

    # tunic
    d.polygon([(9, 17 + b), (22, 17 + b), (21, 31 + b), (10, 31 + b)], fill=BLUE)
    d.line((10, 18 + b, 10, 30 + b), fill=BLUE_L)
    d.line((21, 18 + b, 20, 31 + b), fill=BLUE_D)
    for y in (18, 20):
        p[15, y + b] = BLUE_D

    # green gem with a tiny skull
    gem = {22: (15, 16), 23: (14, 17), 24: (13, 18), 25: (12, 19),
           26: (12, 19), 27: (13, 18), 28: (14, 17), 29: (15, 16)}
    for y, (a, z) in gem.items():
        for x in range(a, z + 1):
            p[x, y + b] = GRN_D if (x in (a, z) or y >= 28) else GRN
    for x in range(14, 18):
        p[x, 24 + b] = BONE
    for x, c in zip(range(13, 19), (BONE, SOCK, BONE, BONE, SOCK, BONE)):
        p[x, 25 + b] = c
    for x in range(14, 18):
        p[x, 26 + b] = BONE
    p[14, 27 + b] = BONE
    p[16, 27 + b] = BONE

    # shoulder pad (the grey blob on his right shoulder)
    d.ellipse((20, 14 + b, 25, 19 + b), fill=PAD)
    p[21, 15 + b] = PAD_L
    p[22, 15 + b] = PAD_L

    # hair spikes
    for seg in [(13, 1, 14, 5), (16, 0, 16, 4), (18, 1, 17, 5)]:
        d.line((seg[0], seg[1] + b, seg[2], seg[3] + b), fill=OL)

    # horns
    for i, (x, y) in enumerate(HORN_L):
        c = HORN_S if (y % 3 == 0) else HORN
        p[x, y + b] = c
    for x, y in mirror_x(HORN_L, 32):
        p[x, y + b] = HORN_S if (y % 3 == 0) else HORN

    # skull head + jagged jaw
    d.ellipse((10, 5 + b, 21, 16 + b), fill=BONE_S)
    d.ellipse((10, 5 + b, 20, 15 + b), fill=BONE)
    d.rectangle((12, 15 + b, 19, 17 + b), fill=BONE)
    for x in (13, 15, 16, 18):
        p[x, 17 + b] = SOCK
    for x, y in ((12, 18), (14, 18), (17, 18), (19, 18), (14, 19), (17, 19)):
        p[x, y + b] = BONE
    # big eyes with pupils, little nose
    for ex in (12, 17):
        d.rectangle((ex, 9 + b, ex + 2, 12 + b), fill=SOCK)
        p[ex + 1, 10 + b] = BONE
    p[15, 13 + b] = SOCK
    p[16, 13 + b] = SOCK

    return outline(im)


# ---------------------------------------------------------------- door
def door(open_=False):
    """Horned Dungeon Door, 32x48."""
    im = Image.new("RGBA", (32, 48), T)
    d = ImageDraw.Draw(im)
    p = im.load()

    def horn(t, below):
        return HORN_S if int(t * 7) % 2 else HORN

    capsule(im, 8, 9, 5, 4, 1.3, horn)
    capsule(im, 5, 4, 7, 0.6, 1.0, horn)
    capsule(im, 23, 9, 26, 4, 1.3, horn)
    capsule(im, 26, 4, 24, 0.6, 1.0, horn)

    # lumpy purple stone frame
    d.ellipse((3, 5, 28, 22), fill=PUR)
    d.rectangle((3, 13, 28, 47), fill=PUR)
    d.rectangle((26, 13, 28, 47), fill=PUR_D)
    for y in range(13, 45, 6):
        d.ellipse((2, y, 5, y + 4), fill=PUR_L)
        d.ellipse((26, y + 3, 29, y + 7), fill=PUR_D)
    for x in (9, 15, 21):
        p[x, 7] = PUR_L
        p[x + 1, 7] = PUR_L

    if not open_:
        d.ellipse((8, 9, 23, 22), fill=DOOR)
        d.rectangle((8, 15, 23, 47), fill=DOOR)
        for x in (12, 16, 20):
            d.line((x, 14, x, 47), fill=DOOR_D)
        d.line((9, 14, 9, 47), fill=DOOR_L)
        for y in (29, 43):
            d.line((8, y, 23, y), fill=IRON)
        # red eye with yellow centre
        d.ellipse((12, 11, 19, 18), fill=RED_D)
        d.ellipse((12, 11, 18, 17), fill=RED)
        d.ellipse((14, 13, 17, 16), fill=YEL)
        p[14, 13] = SPARK
        # white peephole
        d.ellipse((13, 20, 18, 25), fill=BONE)
        d.line((14, 25, 17, 25), fill=BONE_S)
        # yellow keyhole plate
        d.rectangle((12, 31, 19, 40), fill=YEL)
        d.line((19, 31, 19, 40), fill=YEL_D)
        d.line((12, 40, 19, 40), fill=YEL_D)
        d.rectangle((15, 32, 16, 34), fill=SOCK)
        p[14, 33] = SOCK
        p[17, 33] = SOCK
        d.rectangle((15, 35, 16, 38), fill=SOCK)
    else:
        # dark doorway with steps leading down
        d.ellipse((8, 9, 23, 22), fill=C(10, 8, 14))
        d.rectangle((8, 15, 23, 47), fill=C(10, 8, 14))
        for i, y in enumerate(range(36, 48, 3)):
            shade = 22 + i * 8
            d.rectangle((10 - i, y, 22 + i, y + 1), fill=C(shade, shade - 6, shade + 10))
        # swung-open door panel
        d.rectangle((8, 15, 10, 47), fill=DOOR)
        d.line((8, 15, 8, 47), fill=DOOR_L)
        d.rectangle((9, 34, 10, 37), fill=YEL)
        # glowing eyes in the dark
        p[14, 24] = RED
        p[17, 24] = RED

    return outline(im)


# ---------------------------------------------------------------- key
def key(sparkle=False):
    """Skull Key, 16x32."""
    im = Image.new("RGBA", (16, 32), T)
    d = ImageDraw.Draw(im)
    p = im.load()
    d.ellipse((1, 1, 14, 14), fill=KEY)
    for x, y in ((4, 2), (3, 3), (2, 4), (2, 5), (5, 2)):
        p[x, y] = KEY_L
    d.ellipse((4, 4, 11, 11), fill=GRN)
    d.line((5, 11, 10, 11), fill=GRN_D)
    d.ellipse((5, 5, 10, 9), fill=BONE)
    for x in (6, 9):
        p[x, 6] = SOCK
        p[x, 7] = SOCK
    p[6, 10] = BONE
    p[7, 10] = BONE_S
    p[8, 10] = BONE
    p[9, 10] = BONE_S
    # shaft and teeth
    d.rectangle((6, 14, 9, 29), fill=KEY)
    d.line((6, 14, 6, 29), fill=KEY_L)
    d.rectangle((10, 21, 12, 23), fill=KEY)
    d.rectangle((10, 26, 13, 29), fill=KEY)
    p[10, 21] = KEY_L
    p[10, 26] = KEY_L
    outline(im)
    if sparkle:
        for cx, cy in ((13, 2), (2, 20)):
            p[cx, cy] = SPARK
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p[cx + dx, cy + dy] = YEL
    return im


# ---------------------------------------------------------------- tiles
def floor_tile(seed):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (16, 16), C(58, 54, 66))
    d = ImageDraw.Draw(im)
    p = im.load()
    for (x0, y0, x1, y1) in ((0, 0, 7, 7), (8, 0, 15, 7), (0, 8, 5, 15),
                             (6, 8, 15, 15)):
        d.rectangle((x0, y0, x1, y1), outline=C(38, 34, 44))
        d.line((x0 + 1, y0 + 1, x1 - 1, y0 + 1), fill=C(76, 72, 86))
    for _ in range(10):
        x, y = rnd.randrange(16), rnd.randrange(16)
        p[x, y] = rnd.choice([C(48, 44, 56), C(70, 66, 80)])
    if seed % 3 == 2:  # crack
        x, y = rnd.randrange(3, 12), rnd.randrange(3, 12)
        for _ in range(5):
            p[x, y] = C(30, 26, 36)
            x += rnd.choice([0, 1])
            y += 1
            if y > 15 or x > 15:
                break
    return im


def wall_tile(seed):
    rnd = random.Random(seed + 100)
    im = Image.new("RGBA", (16, 16), C(36, 30, 44))
    d = ImageDraw.Draw(im)
    for row in range(4):
        y = row * 4
        off = 0 if row % 2 == 0 else -4
        for bx in range(off, 16, 8):
            base = rnd.choice([C(74, 66, 88), C(68, 60, 82), C(80, 72, 94)])
            d.rectangle((bx, y, bx + 6, y + 2), fill=base)
            d.line((bx, y, bx + 6, y), fill=C(98, 90, 114))
    p = im.load()
    for _ in range(rnd.randrange(0, 4)):  # moss
        p[rnd.randrange(16), rnd.randrange(16)] = C(60, 110, 60)
    return im


def torch(frame):
    im = Image.new("RGBA", (16, 16), T)
    d = ImageDraw.Draw(im)
    d.rectangle((7, 10, 8, 15), fill=BRN)
    d.rectangle((5, 9, 10, 10), fill=IRON)
    flames = [
        [(7, 3), (6, 4), (7, 4), (8, 4), (6, 5), (7, 5), (8, 5), (9, 5),
         (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (6, 7), (7, 7), (8, 7), (9, 7), (6, 8), (7, 8), (8, 8)],
        [(8, 2), (8, 3), (7, 4), (8, 4), (6, 5), (7, 5), (8, 5), (9, 5),
         (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (6, 7), (7, 7), (8, 7), (9, 7), (6, 8), (7, 8), (8, 8), (9, 8)],
    ][frame]
    p = im.load()
    for x, y in flames:
        p[x, y] = C(240, 110, 30)
    for x, y in flames:
        if 6 <= x <= 8 and y >= 5:
            p[x, y] = YEL
    p[7, 7] = SPARK
    return outline(im, C(120, 30, 20))


# ---------------------------------------------------------------- scene
def scene(frame):
    W, H = 14, 9
    im = Image.new("RGBA", (W * 16, H * 16), C(0, 0, 0))
    for ty in range(H):
        for tx in range(W):
            t = wall_tile(tx * 7 + ty * 3) if ty < 4 else floor_tile(tx * 5 + ty * 11)
            im.paste(t, (tx * 16, ty * 16))
    # shadow under the wall
    sh = Image.new("RGBA", im.size, T)
    ImageDraw.Draw(sh).rectangle((0, 64, W * 16, 67), fill=C(0, 0, 0, 110))
    im.alpha_composite(sh)

    im.alpha_composite(door(open_=False), (96, 16))
    torches = [(64, 28), (144, 28)]
    for x, y in torches:
        im.alpha_composite(torch(frame % 2), (x, y))

    def shadow(cx, cy, rx):
        s = Image.new("RGBA", im.size, T)
        ImageDraw.Draw(s).ellipse((cx - rx, cy - 2, cx + rx, cy + 2), fill=C(0, 0, 0, 120))
        im.alpha_composite(s)

    shadow(56, 126, 10)
    im.alpha_composite(hero(frame % 2), (40, 80))
    shadow(178, 126, 5)
    im.alpha_composite(key(sparkle=frame % 2 == 0), (170, 96 - (frame % 2)))

    # torch lighting
    px = im.load()
    lights = [(x + 8, y + 6) for x, y in torches]
    flick = 1.0 + (0.04 if frame % 2 else 0)
    for y in range(im.height):
        for x in range(im.width):
            lit = 0.6
            for lx, ly in lights:
                dist = math.hypot(x - lx, (y - ly) * 1.1)
                lit = max(lit, min(1.15, 1.25 * flick - dist / 110))
            r, g, b, a = px[x, y]
            warm = max(0.0, lit - 0.6)
            px[x, y] = (min(255, int(r * lit + 30 * warm)),
                        min(255, int(g * lit + 14 * warm)),
                        min(255, int(b * lit)), 255)
    return im


# ---------------------------------------------------------------- output
def main(out):
    raw = os.path.join(out, "sprites")
    big = os.path.join(out, "sprites_4x")
    os.makedirs(raw, exist_ok=True)
    os.makedirs(big, exist_ok=True)

    sprites = {
        "skull_knight_idle_0": hero(0),
        "skull_knight_idle_1": hero(1),
        "horned_door_closed": door(False),
        "horned_door_open": door(True),
        "skull_key": key(False),
        "skull_key_sparkle": key(True),
        "torch_0": torch(0),
        "torch_1": torch(1),
        "floor_tile_0": floor_tile(0),
        "floor_tile_1": floor_tile(1),
        "floor_tile_cracked": floor_tile(2),
        "wall_tile_0": wall_tile(0),
        "wall_tile_1": wall_tile(1),
    }
    for name, img in sprites.items():
        img.save(os.path.join(raw, name + ".png"))
        scale(img, 4).save(os.path.join(big, name + ".png"))

    # horizontal sprite strips (handy for game engines)
    def strip(names, fname):
        imgs = [sprites[n] for n in names]
        s = Image.new("RGBA", (sum(i.width for i in imgs), max(i.height for i in imgs)), T)
        x = 0
        for i in imgs:
            s.alpha_composite(i, (x, 0))
            x += i.width
        s.save(os.path.join(raw, fname))
        scale(s, 4).save(os.path.join(big, fname))

    strip(["skull_knight_idle_0", "skull_knight_idle_1"], "strip_skull_knight_idle.png")
    strip(["horned_door_closed", "horned_door_open"], "strip_horned_door.png")
    strip(["skull_key", "skull_key_sparkle"], "strip_skull_key.png")
    strip(["torch_0", "torch_1"], "strip_torch.png")

    # preview sheet
    K = 6
    try:
        font = ImageFont.load_default(size=22)
    except TypeError:
        font = ImageFont.load_default()
    show = [("Skull Knight", "skull_knight_idle_0"), ("Horned Door", "horned_door_closed"),
            ("Door (open)", "horned_door_open"), ("Skull Key", "skull_key"),
            ("Torch", "torch_0"), ("Floor", "floor_tile_0"), ("Wall", "wall_tile_0")]
    pad = 28
    width = sum(sprites[n].width * K + pad for _, n in show) + pad
    height = 48 * K + 2 * pad + 40
    sheet = Image.new("RGBA", (width, height), C(24, 20, 30))
    d = ImageDraw.Draw(sheet)
    x = pad
    for label, n in show:
        img = scale(sprites[n], K)
        y = pad + (48 * K - img.height)
        sheet.alpha_composite(img, (x, y))
        d.text((x, pad + 48 * K + 10), label, fill=C(220, 210, 240), font=font)
        x += img.width + pad
    sheet.save(os.path.join(out, "sprite_sheet_preview.png"))

    # scene: still + animated gif
    frames = [scale(scene(f), 4).convert("RGB") for f in range(2)]
    frames[0].save(os.path.join(out, "dungeon_scene.png"))
    frames[0].save(os.path.join(out, "dungeon_scene.gif"), save_all=True,
                   append_images=frames[1:], duration=450, loop=0)
    print("wrote sprites to", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
