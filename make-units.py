#!/usr/bin/env python3
"""
make-units.py — render each app screenshot as a photographed hardware unit.

WHY THIS EXISTS AND WHY IT IS NOT CSS
-------------------------------------
The website already puts every screenshot inside a chassis: the .unit component
in styles.css, which builds the faceplate, the extruded edge, the screws and the
ground shadow out of gradients and box-shadows. That is the right answer for the
site and it stays.

It is no answer at all for anywhere we cannot ship a stylesheet, which is most
of the places the product is actually sold: Gumroad covers and thumbnails,
social cards, anything embedded in a forum post. Those take a PNG and nothing
else. So this script produces the same object as a flat image, deliberately
matching styles.css layer for layer — same palette out of :root, same light
direction, same screw geometry — because two different-looking chassis is worse
than one plain screenshot.

Output: assets/units/<app>-unit.png at 2x, transparent background.

WHAT IS BEING FAKED, IN ORDER OF HOW MUCH IT MATTERS
----------------------------------------------------
1. THE EDGE. A ladder of solid 1px steps down the bottom and right, each one a
   shade darker. This is the whole illusion. Stacked, they read as one extruded
   side wall falling away from the light. A single soft drop shadow instead
   reads as a card lifted off a page, which is a completely different object,
   and it is the mistake that makes most "3D" product art look like a sticker.

2. THE PERSPECTIVE. A mild four-point warp (PIL's Image.PERSPECTIVE), applied
   AFTER the chassis is fully drawn, so the edge ladder and the screws warp with
   the body the way they would if the whole unit were turned. Warping the
   screenshot alone and pasting a flat frame around it is the other common tell.

3. THE GROUND SHADOW. Blurred, offset down, and drawn NARROWER than the body.
   Narrower is the part people get wrong: a shadow the same width as the object
   reads as a glow around it. Real contact shadows tuck underneath.

4. THE CHAMFER. One bright pixel line along the top inner lip, one dark along
   the bottom. Cheap, and without it the face is a printed rectangle.

Light source is above and slightly front, everywhere, in every layer. Get the
direction wrong on any single one of these and all four stop working at once.

USAGE
    python3 make-units.py            # every app
    python3 make-units.py spectrl    # just one

Re-run it after replacing anything in assets/shots/. It is pure derivation from
files already in the repo, so the output is disposable and regenerable.
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "assets", "shots")
OUT = os.path.join(HERE, "assets", "units")

# 2x, so the result survives a retina Gumroad cover without resampling mush.
S = 2

# ---- palette, lifted from styles.css :root so the two chassis cannot drift --
FACE_HI = (243, 241, 237)   # --face-hi
FACE_MID = (227, 225, 219)  # --ui-bg
FACE_LO = (198, 195, 188)   # --face-lo
INK = (42, 38, 33)          # --ink

APPS = {
    "mutationstation": ("MutationStation", (0xD1, 0x3A, 0x2C), "macOS app"),
    "chordinator":     ("Chordinator",     (0xE0, 0x86, 0x2C), "macOS app"),
    "spectrl":         ("Spectrl",         (0x4A, 0x86, 0xC5), "macOS app"),
    "midimirror":      ("MidiMirror",      (0xE0, 0x5A, 0x2C), "Remote Script + app"),
}

PAD_X, PAD_BOT = 20 * S, 20 * S
PLATE_H = 40 * S
RADIUS = 10 * S
# How thick the slab is, in ladder rungs. Deeper than the CSS uses, and on
# purpose: the site's 7px sits against a ~1000px-wide face, but these renders go
# out at 2000px+ and get downscaled by whatever is embedding them, so an edge
# tuned to the CSS ratio disappears entirely by the time Gumroad has finished
# with it. Scaled to the face instead of fixed, below.
EDGE_MIN = 14 * S
SCREW_INSET = 20 * S
SCREW_R = 5 * S


def vgrad(size, top, mid, bot, mid_at=0.46):
    """The faceplate light-fall, plus the 1px brushed grain the site uses."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        if t <= mid_at:
            k = t / mid_at
            a, b = top, mid
        else:
            k = (t - mid_at) / (1 - mid_at)
            a, b = mid, bot
        px[0, y] = tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
    img = img.resize((w, h))
    # brushed grain: alternate rows lifted and dropped a hair
    d = ImageDraw.Draw(img)
    for y in range(0, h, 2 * S):
        d.line([(0, y), (w, y)], fill=(255, 255, 255), width=1)
    return Image.blend(img, vflat(size, mid), 0.0) if False else img


def vflat(size, c):
    return Image.new("RGB", size, c)


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255)
    return m


def draw_screw(base, cx, cy):
    """Four rings out from the middle: slot, lit head, countersink wall, lower
    lip. Two rings is not enough — it comes out as an outline of a hole rather
    than a screw sitting in one, which is exactly what the CSS did first."""
    d = ImageDraw.Draw(base)
    rings = [
        (SCREW_R * 1.00, (255, 255, 255, 235), True),   # bright lower lip
        (SCREW_R * 0.80, (110, 106, 99, 255), False),   # countersink wall
        (SCREW_R * 0.58, (214, 211, 203, 255), False),  # the head, catching light
        (SCREW_R * 0.20, (128, 124, 116, 255), False),  # the slot
    ]
    for r, col, lip in rings:
        box = [cx - r, cy - r, cx + r, cy + r]
        if lip:
            # the lip is only the bottom half; a full bright ring reads as a bead
            d.ellipse([box[0], box[1] + r * 0.35, box[2], box[3] + r * 0.35], fill=col)
        else:
            d.ellipse(box, fill=col)


def perspective(img, yaw=0.055, pitch=0.022):
    """Turn the finished unit slightly, as if it were on a table in front of you.

    Applied to the WHOLE composited chassis, never to the screenshot alone: the
    edge ladder and the screws have to turn with the body, and warping the
    screen and pasting a flat frame round it is the usual tell that a product
    render was assembled rather than photographed.

    yaw shortens the right edge and lifts its corners toward the centre line;
    pitch tucks the bottom in. Both stay small. Past roughly 0.08 the far side
    of the screenshot stops being readable, and a product shot whose UI cannot
    be read has traded away the only thing it was for.
    """
    w, h = img.size
    dx, dy = yaw * w, pitch * h
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = [(0, 0), (w - dx, dy), (w - dx, h - dy), (0, h)]

    # PIL's PERSPECTIVE wants the INVERSE map (destination -> source), so solve
    # with dst as the input side. Eight unknowns, eight equations, one per
    # coordinate of the four corners.
    A, B = [], []
    for (u, v), (x, y) in zip(dst, src):
        A.append([u, v, 1, 0, 0, 0, -x * u, -x * v]); B.append(x)
        A.append([0, 0, 0, u, v, 1, -y * u, -y * v]); B.append(y)
    coeffs = np.linalg.solve(np.array(A, dtype=float), np.array(B, dtype=float))
    return img.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)


def build(slug, name, accent, model, tilt=True):
    shot = Image.open(os.path.join(SHOTS, slug + ".png")).convert("RGB")

    # cap the screenshot so no unit comes out absurdly large
    maxw = 1400 * S
    if shot.width > maxw:
        shot = shot.resize((maxw, round(shot.height * maxw / shot.width)),
                           Image.LANCZOS)

    inner_w, inner_h = shot.size
    bw = inner_w + PAD_X * 2
    bh = inner_h + PLATE_H + PAD_BOT

    # ---- 1. the extruded side wall -----------------------------------------
    # Solid steps, darkening downward. Drawn first and largest so the face lands
    # on top of it. This is the layer doing the actual work.
    edge = max(EDGE_MIN, round(bw * 0.010))
    canvas = Image.new("RGBA", (bw + edge + 60 * S, bh + edge + 110 * S),
                       (0, 0, 0, 0))
    ox, oy = 30 * S, 14 * S

    for i in range(edge, 0, -1):
        k = i / edge
        shade = tuple(int(FACE_LO[c] * (1 - 0.42 * k)) for c in range(3))
        layer = Image.new("RGBA", (bw, bh), shade + (255,))
        layer.putalpha(rounded_mask((bw, bh), RADIUS))
        canvas.alpha_composite(layer, (ox, oy + i))

    # ---- 2. the face --------------------------------------------------------
    face = vgrad((bw, bh), FACE_HI, FACE_MID, FACE_LO).convert("RGBA")
    d = ImageDraw.Draw(face)

    # chamfer: bright top inner lip, dark bottom inner lip
    d.line([(RADIUS, 0), (bw - RADIUS, 0)], fill=(255, 255, 255, 255), width=S)
    d.line([(RADIUS, bh - S), (bw - RADIUS, bh - S)], fill=(150, 146, 138, 255), width=S)

    # the accent rail down the left edge
    d.rounded_rectangle([0, 10 * S, 3 * S, bh - 10 * S], 2 * S, fill=accent + (255,))

    for sx in (SCREW_INSET, bw - SCREW_INSET):
        for sy in (SCREW_INSET, bh - SCREW_INSET):
            draw_screw(face, sx, sy)

    # the engraved nameplate: dark glyph with a bright lower lip, same two-layer
    # trick the CSS uses, done by drawing the text twice offset by one pixel
    font = None
    for cand in ("/System/Library/Fonts/Supplemental/Futura.ttc",
                 "/System/Library/Fonts/HelveticaNeue.ttc",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
        if os.path.exists(cand):
            from PIL import ImageFont
            try:
                font = ImageFont.truetype(cand, 15 * S)
                break
            except Exception:
                pass
    if font is not None:
        label = " ".join(name.upper())          # tracked out, like the CSS
        tx, ty = PAD_X + 12 * S, PLATE_H // 2 - 9 * S
        d.text((tx, ty + S), label, font=font, fill=(255, 255, 255, 210))
        d.text((tx, ty), label, font=font, fill=(74, 70, 63, 255))

        small = None
        from PIL import ImageFont as IF
        try:
            small = IF.truetype(cand, 10 * S)
        except Exception:
            small = font
        right = " ".join(("JAMWARE AUDIO · " + model).upper())
        rw = d.textlength(right, font=small)
        rx = bw - PAD_X - 12 * S - rw
        d.text((rx, ty + 4 * S + S), right, font=small, fill=(255, 255, 255, 200))
        d.text((rx, ty + 4 * S), right, font=small, fill=(96, 92, 85, 255))
        # the pilot lamp, lit
        d.ellipse([rx - 14 * S, ty + 7 * S, rx - 8 * S, ty + 13 * S], fill=accent + (255,))

    # the screenshot, sunk into a dark recess
    rec = [PAD_X - 2 * S, PLATE_H - 2 * S, PAD_X + inner_w + 2 * S, PLATE_H + inner_h + 2 * S]
    d.rounded_rectangle(rec, 3 * S, fill=(24, 22, 20, 255))
    face.paste(shot, (PAD_X, PLATE_H))

    face.putalpha(rounded_mask((bw, bh), RADIUS))
    canvas.alpha_composite(face, (ox, oy))

    # ---- 3. the ground shadow ----------------------------------------------
    # Narrower than the body on purpose. Same width reads as a glow.
    if tilt:
        canvas = perspective(canvas)

    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        [ox + bw * 0.07, oy + bh + edge - 6 * S,
         ox + bw * 0.93, oy + bh + edge + 30 * S],
        fill=(0, 0, 0, 105))
    sh = sh.filter(ImageFilter.GaussianBlur(13 * S))
    out = Image.alpha_composite(sh, canvas)
    out = out.crop(out.getbbox())

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, slug + "-unit.png")
    out.save(path)
    return path, out.size


if __name__ == "__main__":
    argv = sys.argv[1:]
    tilt = "--flat" not in argv
    want = [a for a in argv if not a.startswith("-")] or list(APPS)
    for slug in want:
        if slug not in APPS:
            sys.exit("unknown app: %s (have %s)" % (slug, ", ".join(APPS)))
        p, size = build(slug, *APPS[slug], tilt=tilt)
        print("%-16s %s  %dx%d" % (slug, os.path.relpath(p, HERE), *size))
