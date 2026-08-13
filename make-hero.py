#!/usr/bin/env python3
"""
make-hero.py — build the homepage hero: the four apps cascaded, one behind the
other, MutationStation in front.

WHY THIS EXISTS AND WHY IT IS NOT JUST A SCREENSHOT
---------------------------------------------------
The hero used to be a single Spectrl window. That was the wrong first thing to
show: Spectrl is the most abstract of the four and reads as a spectrum analyser,
so a visitor's first impression of a company selling four instruments-adjacent
tools was one meter. The cascade shows there is a range, and the depth ordering
does the ranking for us -- whatever sits in front is what the site is arguing
you should care about first.

ORDER IS BACK TO FRONT, AND IT IS DELIBERATE
    midimirror, spectrl, chordinator, mutationstation
MutationStation ends up fully visible on top and Chordinator immediately behind
it, per the brief. The other two are present as evidence of a range rather than
as things you are meant to read at this size; their detail is on their own pages.

The source captures are inconsistent -- two are RGB with the rounded corners
already flattened to black, one is RGBA with real transparent corners, one is
full retina resolution and square-cornered. Rather than special-case each, every
window is scaled to one width and re-masked with the same corner radius, which
makes the stack look like four windows on one desktop instead of four
screenshots taken on four different days.

Output has a transparent background on purpose: it sits inside the site's dark
`.screen` recess, and a baked-in background colour would show as a rectangle the
moment that recess changes.

Run from site/:  ./make-hero.py
"""

from PIL import Image, ImageDraw, ImageFilter

SHOTS = "assets/shots"
OUT = f"{SHOTS}/hero-stack.png"

# Back to front. The last entry is the one in front.
ORDER = ["midimirror", "spectrl", "chordinator", "mutationstation"]

WIN_W = 1500          # every window scaled to this width
STEP_X, STEP_Y = 126, 98   # cascade offset per window
RADIUS = 12           # corner radius at WIN_W
PAD = 46              # room for the drop shadow to fall outside the stack

SHADOW_BLUR = 20
SHADOW_OFFSET = (0, 12)
SHADOW_ALPHA = 105


def rounded(im, radius):
    """Scale to WIN_W and give it clean rounded corners regardless of how the
    source capture handled them."""
    w, h = im.size
    im = im.convert("RGBA").resize((WIN_W, round(h * WIN_W / w)), Image.LANCZOS)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1],
                                           radius=radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


windows = [rounded(Image.open(f"{SHOTS}/{name}.png"), RADIUS) for name in ORDER]

span_x = STEP_X * (len(windows) - 1)
span_y = STEP_Y * (len(windows) - 1)
canvas_w = WIN_W + span_x + PAD * 2
canvas_h = max(w.size[1] for w in windows) + span_y + PAD * 2
canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

for i, win in enumerate(windows):
    x = PAD + STEP_X * i
    y = PAD + STEP_Y * i

    # Shadow first, from the window's own alpha, so it follows the rounded
    # corners rather than being a rectangle behind them.
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    solid = Image.new("RGBA", win.size, (0, 0, 0, SHADOW_ALPHA))
    shadow.paste(solid, (x + SHADOW_OFFSET[0], y + SHADOW_OFFSET[1]), win.split()[3])
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR)))

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(win, (x, y), win)
    canvas = Image.alpha_composite(canvas, layer)

# ---- Crop the cascade into the frame ---------------------------------------
# BLEED used to be 0.62, on the theory that cropping into the back of the
# stack would make the front window bigger once the page's 620px height cap
# scaled it down. That theory was wrong: the height cap scales from the
# canvas's own height, which barely moves as BLEED changes (the crop trims
# width, not height), so the front window rendered at the same size either
# way and the only visible effect was cost. At 0.62 it cropped MidiMirror out
# of the frame entirely and sliced through the middle of Spectrl's toolbar
# instead of along its rounded corner, which reads as a broken image rather
# than a window lying at an angle. BLEED=0 shows the full cascade — all four
# windows, each ending on its own rounded corner and drop shadow rather than
# a straight crop line through its content.
BLEED = 0.0
canvas = canvas.crop((round(span_x * BLEED), round(span_y * BLEED),
                      canvas_w, canvas_h))

canvas.save(OUT)
print(f"wrote {OUT} {canvas.size}")
