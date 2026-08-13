#!/usr/bin/env python3
"""
make-cutouts.py — cut the full-window screenshots out of their backgrounds so
they sit directly on the site's faceplate instead of inside a dark frame.

WHY THIS EXISTS
---------------
Every screenshot on the site used to sit in a `.screen` recess: a dark, inset
panel borrowed from the apps themselves, where a real analyser or piano roll is
a dark screen sunk into a cream plate. That framing is right for a piece of UI
inside an app and wrong for a picture of the whole app. It put a black rectangle
around a cream window, so the page read as a stack of cards on a plate rather
than as windows lying on it.

Take the frame away and a second problem surfaces immediately, which is what
this script is for: the captures do not have transparent corners. macOS draws a
window with rounded corners, but a screenshot flattens whatever was behind them
into the file. Two of the four captures baked pure black there and one baked a
grey desktop. On the old dark recess nobody could see it. On cream, every window
grows four small dark nubs.

So each full-window capture is re-masked with a rounded rectangle and everything
outside it becomes transparent. The page background then shows through the
corners, the CSS drop-shadow follows the real silhouette rather than a box, and
the window looks cut out instead of pasted on.

ONLY THE FULL-WINDOW SHOTS
--------------------------
The per-feature crops in assets/shots (chordinator-keybed, spectrl-notes and the
rest) are interiors cut out of these same captures. Their corners are square
because they are slices from the middle of a window, and rounding them would
invent a curve the app does not have. They are left alone deliberately; do not
"finish the job" by adding them to WINDOWS.

RADIUS
------
Proportional to width, because these were captured at different scale factors:
the same 10pt macOS corner is 20px in a 2x capture and 12px in a 1.25x one. The
mask is built at 4x and downsampled, which is the cheap way to get an antialiased
edge out of PIL — a mask drawn at final size leaves visible stair-steps on a
1:1 hero image.

IDEMPOTENT. Running it twice re-masks corners that are already transparent,
which changes nothing. Safe to re-run after re-capturing any of these windows.

Run from site/:  ./make-cutouts.py   then ./make-hero.py to rebuild the hero.
"""

from PIL import Image, ImageDraw

SHOTS = "assets/shots"

# Full-window captures only. See the note above before adding to this list.
WINDOWS = [
    "mutationstation.png",
    "chordinator.png",
    "spectrl.png",
    "midimirror.png",
]

RADIUS_RATIO = 0.008   # of image width: 16px at 2000px wide, 28px at 3456px
SS = 4                 # mask supersampling factor


def cut_out(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    r = max(8, round(w * RADIUS_RATIO))

    mask = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, w * SS - 1, h * SS - 1], radius=r * SS, fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    out.save(path)
    return w, h, r


if __name__ == "__main__":
    for name in WINDOWS:
        p = f"{SHOTS}/{name}"
        w, h, r = cut_out(p)
        print(f"cut out {p} ({w}x{h}, radius {r})")
