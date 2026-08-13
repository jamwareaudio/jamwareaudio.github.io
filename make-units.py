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

THE THIN-SLAB MISTAKE, AND WHY THIS FILE IS SHAPED AROUND AVOIDING IT
---------------------------------------------------------------------
The first version of this script produced four iPads. That is worth writing
down at length, because every individual decision in it was defensible and the
result was still wrong, and the same four decisions will look reasonable again
next time somebody edits this.

An iPad and a MIDI controller are distinguished by almost nothing in a still
image except proportion of body to screen. The first pass had a ~28px side wall
under a 2000px face — a body-to-screen ratio that no piece of studio hardware
has ever had — a bezel two pad-widths wide all round, and the screenshot sunk
into a black glass recess. Black recess plus thin slab plus even bezel IS a
tablet; it is not a near miss, it is the actual visual definition of one. Four
changes, and all four have to stay together or it slides straight back:

1. THE SLAB IS THICK. `edge` is now ~3.2% of the face width with a hard floor,
   against 1% before, and the wall steps down AND right (RX) instead of straight
   down, so a genuine side face is visible rather than a lip. Hardware is a box
   seen slightly from above; a tablet is a plane.

2. THE UI IS THE FACEPLATE, NOT A SCREEN — except on Spectrl. This is the one
   the user asked for directly and it is the biggest single lever. On the three
   instrument apps the screenshot is now flush with the panel and carries a
   relief pass (see `relief`) that lifts the edge of every knob, fader and
   button in the app's own interface, so the controls read as milled into the
   metal rather than drawn on glass behind it. Spectrl keeps the dark recess and
   the glass sheen, because Spectrl genuinely IS a screen — it is an analyser,
   and pretending its spectrum display is an engraved panel would be a lie about
   what the product is.

3. END CHEEKS. Dark wooden strips down both sides, the single most legible
   "this is an instrument" signal there is, borrowed from every desktop synth
   ever made. They also break the even all-round bezel that reads as tablet.

4. THE BEZEL IS ASYMMETRIC. Deeper below the panel than above it, because
   hardware puts its mass under the controls.

WHAT IS BEING FAKED, IN ORDER OF HOW MUCH IT MATTERS
----------------------------------------------------
1. THE EDGE. A ladder of solid steps down and to the right, each one a shade
   darker. This is the whole illusion. Stacked, they read as one extruded side
   wall falling away from the light. A single soft drop shadow instead reads as
   a card lifted off a page, which is a completely different object, and it is
   the mistake that makes most "3D" product art look like a sticker.

2. THE RELIEF PASS. An emboss convolution blended back over the screenshot as
   highlight-and-shadow rather than as grey, so it adds depth without draining
   colour. Lit from the top left, the same direction as every other layer.

3. THE PERSPECTIVE. A mild four-point warp (PIL's Image.PERSPECTIVE), applied
   AFTER the chassis is fully drawn, so the edge ladder and the screws warp with
   the body the way they would if the whole unit were turned. Warping the
   screenshot alone and pasting a flat frame around it is the other common tell.

4. THE GROUND SHADOW. Blurred, offset down, and drawn NARROWER than the body.
   Narrower is the part people get wrong: a shadow the same width as the object
   reads as a glow around it. Real contact shadows tuck underneath.

5. THE CHAMFER. One bright pixel line along the top inner lip, one dark along
   the bottom. Cheap, and without it the face is a printed rectangle.

Light source is above and slightly front, everywhere, in every layer. Get the
direction wrong on any single one of these and all of them stop working at once.

USAGE
    python3 make-units.py            # every app
    python3 make-units.py spectrl    # just one
    python3 make-units.py --flat     # square on, no perspective warp

Re-run it after replacing anything in assets/shots/. It is pure derivation from
files already in the repo, so the output is disposable and regenerable.
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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

# End-cheek walnut. Warm and dark enough to separate from the panel at thumbnail
# size, not so dark it becomes a black bar.
WOOD_HI = (122, 78, 46)
WOOD_LO = (58, 34, 20)

# slug -> (display name, accent, model line, is_screen)
# is_screen is the switch described at length in the header: True keeps the dark
# glass recess, False makes the screenshot the faceplate itself.
APPS = {
    "mutationstation": ("MutationStation", (0xD1, 0x3A, 0x2C), "macOS app",          False),
    "chordinator":     ("Chordinator",     (0xE0, 0x86, 0x2C), "macOS app",          False),
    "spectrl":         ("Spectrl",         (0x4A, 0x86, 0xC5), "macOS app",          True),
    "midimirror":      ("MidiMirror",      (0xE0, 0x5A, 0x2C), "Remote Script + app", False),
}

PAD_X = 20 * S          # panel margin inside the cheeks
PAD_BOT = 34 * S        # deeper than the top margin on purpose — see header (4)
PLATE_H = 46 * S        # the nameplate strip above the panel
RADIUS = 12 * S
CHEEK = 30 * S          # end-cheek width, instrument apps only

# How thick the slab is. ~3.2% of the face width against the first version's 1%,
# with a hard floor: these renders go out at 2000px+ and get downscaled by
# whatever is embedding them, so an edge tuned to the CSS ratio disappears
# entirely by the time Gumroad has finished with it.
EDGE_MIN = 40 * S
EDGE_RATIO = 0.032
RX = 0.5                # how far right the wall steps per step down

SCREW_INSET = 17 * S
SCREW_R = 5 * S


def vgrad(size, top, mid, bot, mid_at=0.46, grain=True):
    """The faceplate light-fall, plus the 1px brushed grain the site uses."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        if t <= mid_at:
            k, a, b = t / mid_at, top, mid
        else:
            k, a, b = (t - mid_at) / (1 - mid_at), mid, bot
        px[0, y] = tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
    img = img.resize((w, h))
    if grain:
        d = ImageDraw.Draw(img)
        for y in range(0, h, 2 * S):
            d.line([(0, y), (w, y)], fill=(255, 255, 255), width=1)
    return img


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255)
    return m


def relief(img, amount=0.30):
    """Give the app's own interface depth, control by control.

    This is what the user meant by "the design within the apps should stick out".
    We cannot model the individual widgets — we only have a flat screenshot — but
    an emboss convolution finds every edge in it, which for a UI screenshot is
    precisely the outline of every knob, fader, button and panel divider.

    The naive use of that is `ImageFilter.EMBOSS`, which returns a grey relief
    map and, blended in, drains the colour out of the whole shot. So instead the
    map is re-centred to zero and applied as a lighten-toward-white where it is
    positive and a darken-toward-black where it is negative, each scaled by the
    headroom actually available in the pixel. Saturated colour survives; edges
    gain a lit top lip and a shadowed bottom one.

    Kernel is lit from the TOP LEFT, matching every other layer in this file.
    Flip it and the panel reads as lit from below, which is the uncanny one.

    `amount` is the one number here worth being careful with. 0.55 was tried and
    is too much: a UI screenshot is nearly all edges, so at that strength the
    highlight term lands on most of the image at once and the whole panel washes
    out pale — MutationStation's and Chordinator's oranges went chalky. The
    embossing has to be felt rather than seen. If it is legible as an effect it
    is already too strong, and legibility of the UI is the only thing these
    renders exist to sell.
    """
    g = img.convert("L")
    emb = g.filter(ImageFilter.Kernel(
        (3, 3), [2, 1, 0,
                 1, 1, -1,
                 0, -1, -2], scale=1, offset=128))

    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    e = np.asarray(emb, dtype=np.float32) / 255.0
    e = np.clip((e - 0.5) * 2.0, -1.0, 1.0)[..., None] * amount

    up = np.where(e > 0, e, 0.0)
    dn = np.where(e < 0, -e, 0.0)
    out = a + up * (1.0 - a) - dn * a
    return Image.fromarray(np.clip(out * 255.0, 0, 255).astype(np.uint8), "RGB")


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


def draw_cheek(face, x0, x1, h, left):
    """A wooden end cheek, the desktop-synth signal. Lit edge on the side facing
    the light, dark on the other, so the two cheeks are not mirror images."""
    w = x1 - x0
    wood = vgrad((w, h), WOOD_HI, tuple((WOOD_HI[i] + WOOD_LO[i]) // 2 for i in range(3)),
                 WOOD_LO, mid_at=0.35, grain=False).convert("RGBA")
    d = ImageDraw.Draw(wood)
    # a few grain lines, irregular enough not to read as a stripe pattern
    for i, y in enumerate(range(0, h, 11 * S)):
        d.line([(0, y + (i % 3) * S), (w, y + ((i + 1) % 3) * S)],
               fill=(255, 255, 255, 16), width=S)
    d.line([(0, 0), (w, 0)], fill=(255, 226, 196, 120), width=S)
    if left:
        d.line([(w - S, 0), (w - S, h)], fill=(0, 0, 0, 130), width=S)
    else:
        d.line([(0, 0), (0, h)], fill=(255, 226, 196, 90), width=S)
    face.alpha_composite(wood, (x0, 0))


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


def _font(size):
    for cand in ("/System/Library/Fonts/Supplemental/Futura.ttc",
                 "/System/Library/Fonts/HelveticaNeue.ttc",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                pass
    return None


def build(slug, name, accent, model, is_screen, tilt=True):
    shot = Image.open(os.path.join(SHOTS, slug + ".png")).convert("RGB")

    # cap the screenshot so no unit comes out absurdly large
    maxw = 1400 * S
    if shot.width > maxw:
        shot = shot.resize((maxw, round(shot.height * maxw / shot.width)),
                           Image.LANCZOS)

    # The instrument apps ARE their faceplate, so their UI gets milled; Spectrl
    # is a display and stays flat behind glass. Header, point (2).
    if not is_screen:
        shot = relief(shot)

    cheek = 0 if is_screen else CHEEK
    inner_w, inner_h = shot.size
    px0 = cheek + PAD_X                      # panel left edge on the face
    bw = px0 * 2 + inner_w
    bh = inner_h + PLATE_H + PAD_BOT

    # ---- 1. the extruded side wall -----------------------------------------
    # Solid steps, darkening downward and rightward. Drawn first and largest so
    # the face lands on top. This is the layer doing the actual work.
    edge = max(EDGE_MIN, round(bw * EDGE_RATIO))
    ox, oy = 34 * S, 16 * S
    canvas = Image.new("RGBA",
                       (bw + round(edge * RX) + 70 * S, bh + edge + 120 * S),
                       (0, 0, 0, 0))

    for i in range(edge, 0, -1):
        k = i / edge
        f = 0.95 - 0.62 * k
        shade = tuple(int(FACE_LO[c] * f) for c in range(3))
        layer = Image.new("RGBA", (bw, bh), shade + (255,))
        layer.putalpha(rounded_mask((bw, bh), RADIUS))
        canvas.alpha_composite(layer, (ox + round(i * RX), oy + i))

    # ---- 2. the face --------------------------------------------------------
    face = vgrad((bw, bh), FACE_HI, FACE_MID, FACE_LO).convert("RGBA")
    if cheek:
        draw_cheek(face, 0, cheek, bh, left=True)
        draw_cheek(face, bw - cheek, bw, bh, left=False)
    d = ImageDraw.Draw(face)

    # chamfer: bright top inner lip, dark bottom inner lip
    d.line([(RADIUS, 0), (bw - RADIUS, 0)], fill=(255, 255, 255, 255), width=S)
    d.line([(RADIUS, bh - S), (bw - RADIUS, bh - S)], fill=(150, 146, 138, 255), width=S)

    if not cheek:
        # no wooden ends on the analyser, so the accent rail carries the brand
        d.rounded_rectangle([0, 10 * S, 3 * S, bh - 10 * S], 2 * S, fill=accent + (255,))

    for sx in (px0 + SCREW_INSET, bw - px0 - SCREW_INSET):
        for sy in (SCREW_INSET + 4 * S, bh - SCREW_INSET):
            draw_screw(face, sx, sy)

    # the engraved nameplate: dark glyph with a bright lower lip, same two-layer
    # trick the CSS uses, done by drawing the text twice offset by one pixel
    font, small = _font(16 * S), _font(10 * S)
    if font is not None:
        # The nameplate shares its band with the two top screws, so it starts
        # clear of them rather than at the panel margin. It did not, first pass,
        # and the right-hand model line ran straight under a screw head.
        plate_in = SCREW_INSET * 2 + SCREW_R
        label = " ".join(name.upper())          # tracked out, like the CSS
        tx, ty = px0 + plate_in, PLATE_H // 2 - 10 * S
        d.text((tx, ty + S), label, font=font, fill=(255, 255, 255, 210))
        d.text((tx, ty), label, font=font, fill=(74, 70, 63, 255))

        right = " ".join(("JAMWARE AUDIO · " + model).upper())
        rw = d.textlength(right, font=small)
        rx = bw - px0 - plate_in - rw
        d.text((rx, ty + 5 * S + S), right, font=small, fill=(255, 255, 255, 200))
        d.text((rx, ty + 5 * S), right, font=small, fill=(96, 92, 85, 255))
        # the pilot lamp, lit
        d.ellipse([rx - 15 * S, ty + 8 * S, rx - 9 * S, ty + 14 * S], fill=accent + (255,))

    if is_screen:
        # a display: sunk into a dark recess, with a glass sheen over it
        rec = [px0 - 3 * S, PLATE_H - 3 * S,
               px0 + inner_w + 3 * S, PLATE_H + inner_h + 3 * S]
        d.rounded_rectangle(rec, 3 * S, fill=(24, 22, 20, 255))
        face.paste(shot, (px0, PLATE_H))
        sheen = Image.new("RGBA", (inner_w, inner_h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sheen)
        for y in range(inner_h // 3):
            sd.line([(0, y), (inner_w, y)],
                    fill=(255, 255, 255, int(26 * (1 - y / (inner_h / 3)))))
        face.alpha_composite(sheen, (px0, PLATE_H))
    else:
        # a faceplate: flush with the panel, raised, with a milled lip round it
        face.paste(shot, (px0, PLATE_H))
        lip = [px0 - S, PLATE_H - S, px0 + inner_w, PLATE_H + inner_h]
        d.line([(lip[0], lip[1]), (lip[2], lip[1])], fill=(255, 255, 255, 210), width=S)
        d.line([(lip[0], lip[1]), (lip[0], lip[3])], fill=(255, 255, 255, 150), width=S)
        d.line([(lip[0], lip[3]), (lip[2], lip[3])], fill=(120, 116, 108, 220), width=S)
        d.line([(lip[2], lip[1]), (lip[2], lip[3])], fill=(140, 136, 128, 200), width=S)

    face.putalpha(rounded_mask((bw, bh), RADIUS))
    canvas.alpha_composite(face, (ox, oy))

    # ---- 3. the ground shadow ----------------------------------------------
    # Narrower than the body on purpose. Same width reads as a glow.
    if tilt:
        canvas = perspective(canvas)

    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        [ox + bw * 0.08, oy + bh + edge - 8 * S,
         ox + bw * 0.92, oy + bh + edge + 34 * S],
        fill=(0, 0, 0, 115))
    sh = sh.filter(ImageFilter.GaussianBlur(15 * S))
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
