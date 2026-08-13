"""
Turn an app window capture into a relief height map for the Blender rig.

WHY THIS IS POSSIBLE AT ALL, and why it is not guesswork: these apps draw every
control as a closed shape with a dark outline around a flat fill. That is a
hardware-panel drawing convention and the app followed it for its own reasons,
but it happens to be exactly the structure a segmenter wants. Cut the dark
outlines out of the image and every remaining connected blob IS a control face,
already separated from its neighbours by the outline that surrounds it.

So the rule is: find the outlines, label what is left, and give each label a
height by what it evidently is. No edge detection heuristics, no rectangle
fitting, no hand-listing hundreds of buttons.

Assigning the heights is where the judgement is, and it is made on FILL COLOUR
rather than on luminance-versus-surroundings, which was the first idea and is
wrong. A button here is a light grey face on a lighter cream panel, so it is
DARKER than what surrounds it while being physically PROUD of it. Anything
keyed off local contrast raises the panel and sinks the buttons, which is the
relief inside out. Fill colour does not have that problem: grey means moulded
key cap, cream means panel, near-black means a recessed well, orange means a
lit indicator.

The outlines themselves are deliberately left at panel height while the fill
they enclose is raised. That is not a compromise, it is the point: it leaves a
dark seam running around every raised face, which is exactly what the gap
around a real key cap looks like.

Output is a 16-bit greyscale PNG, 0.5 = panel surface, above = proud, below =
recessed. 16-bit because 8 gives 256 steps across the whole relief and the
banding shows up as terracing on any surface the key light rakes across.

Run: python3 heightmap.py <shot.png> <out.png> [--debug]
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

SHOT, OUT = sys.argv[1], sys.argv[2]
DEBUG = "--debug" in sys.argv
APP = os.path.basename(SHOT).rsplit(".", 1)[0]

# Knob centres in source pixels, duplicated from the Blender rig's SPEC. The
# knobs are modelled as real cones there, so the map must be FLAT under them --
# otherwise each modelled knob stands on a raised disc of its own painted body
# and the two silhouettes fight. Radius is padded past the drawn one so the
# knob's cast shadow lands on plate, not on the lip of a disc.
KNOBS = {
    "mutationstation": [(1073, 695, 46), (1427, 305, 37),
                        (1427, 523, 37), (1427, 707, 37)],
    "chordinator": [(65, 700, 28), (162, 700, 28), (258, 699, 28)],
}
KNOB_PAD = 1.30

img = Image.open(SHOT).convert("RGB")
a = np.asarray(img).astype(np.float32) / 255.0
h, w, _ = a.shape
# Explicit weighted sum rather than `a @ weights`. The matmul form is the
# obvious one and on this machine it drops into a BLAS path that warns about
# divide-by-zero and overflow on a (h, w, 3) x (3,) contraction, then returns
# NaNs in the corners. Three multiplies cost nothing and are simply correct.
lum = (0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2])

# --- 1. classify every pixel by what it is made of --------------------------
# The first version of this labelled only the NON-outline pixels, treating
# everything dark as outline. That silently threw away the recessed wells: the
# piano roll is dark, so it was classed as outline, never got a label, and came
# out at panel height. The relief had buttons and no holes, which is half a
# relief.
#
# So classify first, then label WITHIN each class. Dark is a class of its own,
# not the absence of one. The outline band between dark and mid stays its own
# class and stays at panel height, which is what leaves the seam around every
# raised face.
DARK, OUTLINE, MID, LIGHT, PALE, ACCENT = 0, 1, 2, 3, 4, 5
cls = np.full(lum.shape, PALE, dtype=np.uint8)
cls[lum < 0.90] = LIGHT
cls[lum < 0.72] = MID
cls[lum < 0.42] = OUTLINE
cls[lum < 0.30] = DARK

# Warmth separates the orange/red indicators from grey of the same brightness.
# They are their own class because an indicator is a lit lens sitting proud,
# and by luminance alone a mid-orange is indistinguishable from a grey cap.
warm_px = (a[:, :, 0] - a[:, :, 2]) > 0.10
cls[warm_px & (lum > 0.30)] = ACCENT

# --- 2. label every face ---------------------------------------------------
# 4-connectivity, not 8. With 8-connectivity a single anti-aliased pixel where
# two outlines cross lets a button leak into its neighbour, and once two
# controls share a label they share a height and the seam between them closes
# up. 4-connectivity keeps them apart at the cost of a few extra labels.
CONN = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

BASE_H = {DARK: -0.85,     # a well: piano roll, dark readout
          OUTLINE: 0.0,    # the seam, left at panel height on purpose
          MID: 0.75,       # moulded key cap
          LIGHT: 0.0,      # an inset field: a readout, flush with the panel
          PALE: 0.0,       # panel field
          ACCENT: 0.55}    # lit indicator, proud like a lens

# LIGHT was 0.45 -- a low cap -- until it was looked at on a raked render. The
# regions that land in it are not caps at all: they are the value readouts and
# the drop-down fields, and standing them proud made every label on the panel
# look like a button. On real gear a readout is printed on the plate or set
# flush into it behind a window; only a thing you press is proud. So LIGHT is
# flush now, and the only proud classes left are MID (key caps) and ACCENT (lit
# indicators). The outline seam around each field still reads it as a distinct
# area without any relief at all.

# Colour gets a region most of the way. Three cases it cannot decide alone,
# each of which showed up the moment a map was actually looked at:
#
# DARK IS AMBIGUOUS. Near-black is a recessed well (the piano roll, a readout)
# AND it is a dark moulded key cap with light legend on it (the Apply-to-all
# row, the black keys of the trigger keybed). Colour cannot separate those, and
# the first map recessed every one of them, so the black keys sank into the
# keybed and the buttons became holes. Size separates them cleanly: measured on
# Chordinator, the well is 470,000px, the caps are ~4,000, and there is nothing
# in between.
#
# GLYPHS ARE NOT CONTROLS. Dark text on a light panel is dark and small, so the
# cap rule above grabs every letter and stands "Apply to all:" up as tall as
# the buttons under it -- which is what the second map did. A glyph is smaller
# again than a cap by an order of magnitude (median dark region on Chordinator
# is 2px), and it wants to go the other way anyway: legend text on real gear is
# engraved or silkscreened, i.e. flush to slightly sunk, never proud.
#
# FULL-WIDTH BANDS ARE STRUCTURE, NOT CONTROLS. The piano roll is drawn as
# alternating light and dark lanes running the whole width of the roll. Judged
# individually, one lane raises and the next recesses, and the roll came out
# corrugated.
TEXT_MAX_PX = 320
WELL_MIN_PX = 60_000
STRUCT_SPAN = 0.35
WELL_FLOOR = -0.85

hm = np.zeros(lum.shape, dtype=np.float32)
well_seed = np.zeros(lum.shape, dtype=bool)
total = 0
plate_px = w * h
for k, base in BASE_H.items():
    mask = cls == k
    if not mask.any():
        continue
    lab, n = ndimage.label(mask, structure=CONN)
    total += n
    if n == 0:
        continue
    idx = np.arange(1, n + 1)
    area = ndimage.sum(mask, lab, idx)
    boxes = ndimage.find_objects(lab)
    mlum = ndimage.mean(lum, lab, idx)

    hgt = np.zeros(n + 1, dtype=np.float32)
    hgt[1:] = base

    span = np.zeros(n, dtype=bool)
    for i, sl in enumerate(boxes):
        if sl is None:
            continue
        bh = sl[0].stop - sl[0].start
        bw = sl[1].stop - sl[1].start
        span[i] = (bw > STRUCT_SPAN * w) or (bh > STRUCT_SPAN * h)

    if k == DARK:
        cap = (area < WELL_MIN_PX) & ~span
        hgt[1:][cap] = 0.75
        hgt[1:][area < TEXT_MAX_PX] = -0.05      # engraved legend
        # Anything genuinely big and dark seeds a well, and the seed is grown
        # into a solid region below.
        big = (area >= WELL_MIN_PX) | span
        if big.any():
            well_seed |= np.isin(lab, idx[big])

    # One height per structural feature, decided by its own darkness, so a
    # banded region cannot corrugate.
    hgt[1:][span] = np.where(mlum[span] < 0.55, WELL_FLOOR, 0.0)

    hgt[1:][area < 6] = 0.0            # anti-aliasing crumbs

    # A big pale region is a panel subdivision, not a giant button, and raising
    # it would step the whole face plate.
    hgt[1:][(area > 0.030 * plate_px) & (hgt[1:] > 0)] = 0.0

    hm += hgt[lab]

print(f"{total} regions")

# --- 3. wells are one hole, not a stack of lanes ----------------------------
# The per-region pass gets the dark lanes of the piano roll down but leaves the
# light lanes between them at panel height, so the roll reads as a stack of
# ribs rather than one recessed window. A well is a single machined pocket: its
# whole footprint drops to the floor, and only then does anything sit inside it.
#
# The footprint is the seed's bounding box rather than the seed itself, because
# the seed is exactly the dark lanes and its own outline stops at each light
# one. Filling holes afterwards would not help -- the light lanes reach the
# edge of the roll, so they are not enclosed and are not holes.
#
# The seed is closed before it is measured, and that is not cosmetic. On
# Chordinator the roll's dark background survives as one 470,000px blob and any
# threshold finds it. On MutationStation the same roll is drawn as dark lanes
# with light lanes between them, so the largest connected dark piece is a
# single 16,000px stripe -- under any threshold that keeps buttons out, and the
# roll came out as a stack of ribs. Closing across the light lanes first turns
# the stripes back into the one region they visually are.
if well_seed.any():
    GAP = 20
    closed = ndimage.binary_dilation(well_seed, iterations=GAP)
    closed = ndimage.binary_erosion(closed, iterations=GAP, border_value=1)
    lab, n = ndimage.label(closed, structure=CONN)
    well_seed = closed
    idx = np.arange(1, n + 1)
    area = ndimage.sum(well_seed, lab, idx)
    boxes = [(sl[0].start, sl[0].stop, sl[1].start, sl[1].stop)
             for i, sl in enumerate(ndimage.find_objects(lab))
             if sl is not None and area[i] >= WELL_MIN_PX]

    # Then merge the surviving boxes pairwise until nothing moves. Closing
    # alone is not enough: MutationStation's roll has a band across its middle
    # where every lane is light, roughly 240px of it, and no dilation radius
    # that bridges a 240px gap can still be trusted not to swallow the panel
    # around the pocket. Merging boxes is the safer half of the same idea --
    # two pieces of pocket separated by a stretch of pocket-coloured nothing
    # are one pocket, and their union is the rectangle both sit in.
    MERGE_GAP = 320
    changed = True
    while changed and boxes:
        changed = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                y0, y1, x0, x1 = boxes[i]
                z0, z1, u0, u1 = boxes[j]
                near = (min(y1, z1) + MERGE_GAP > max(y0, z0) and
                        min(x1, u1) + MERGE_GAP > max(x0, u0))
                if not near:
                    continue
                boxes[i] = (min(y0, z0), max(y1, z1), min(x0, u0), max(x1, u1))
                boxes.pop(j)
                changed = True
                break
            if changed:
                break

    footprint = np.zeros(lum.shape, dtype=bool)
    for y0, y1, x0, x1 in boxes:
        footprint[y0:y1, x0:x1] = True
    # The pocket floor is FLAT, and everything drawn inside it stays flat with
    # it. This is the one place the panel is not a panel: the sequencer roll is
    # a screen, and what is on a screen is emitted light, not moulded plastic.
    # An earlier version re-raised the notes to floor + 0.30 so they sat proud
    # of the pocket bottom, which is a perfectly good description of a machined
    # part and completely wrong for this part -- a note with a lit edge and a
    # cast shadow stops reading as a note and starts reading as a tile someone
    # laid in the recess. Same argument retires the relief inside every dark
    # readout: they are displays, and a display is flat behind its window.
    hm[footprint] = WELL_FLOOR
    print(f"well footprint {footprint.mean() * 100:.1f}% of plate")

# --- 4. flat under the modelled knobs --------------------------------------
if APP in KNOBS:
    yy, xx = np.ogrid[:h, :w]
    for px, py, pr in KNOBS[APP]:
        r = pr * KNOB_PAD
        hm[(xx - px) ** 2 + (yy - py) ** 2 <= r * r] = 0.0

# --- 5. borders ------------------------------------------------------------
# Force the outer margin flat. The plate is solidified from this surface in
# Blender, so its side walls are extruded from the border ring; if the border
# is not flat the walls come out ragged and the unit loses its straight edge.
#
# Wide, and with a ramp inside it, because 8px was not enough. Solidify offsets
# each vertex along its own normal, so a border vertex whose normal is tilted
# by nearby relief throws its wall out at an angle -- and Chordinator's trigger
# keybed runs right to the bottom edge of the window. The result was a plate
# with a frayed rim, clearly visible in the first v3 test. 30px of genuinely
# flat margin puts every boundary normal straight up; the 26px ramp inside it
# stops that flat margin from being a cliff of its own.
#
# It also happens to be what real gear looks like: a plain bezel around the
# graphics, not artwork running off the edge of the plate.
M, RAMP = 30, 26
yy, xx = np.mgrid[0:h, 0:w]
edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
hm *= np.clip((edge - M) / RAMP, 0, 1)

# --- 6. chamfer ------------------------------------------------------------
# The map is piecewise constant, so every face currently has a vertical cliff
# at its edge. A real moulded cap has a small chamfer, and more practically a
# vertical cliff aliases badly against the render's sampling. A 1.2px gaussian
# turns each cliff into a chamfer a few tenths of a millimetre wide, which is
# what a moulding tool would leave anyway.
#
# 2.0px, not the 1.2 it started at, because the displacement grid in Blender is
# coarser than the image: a chamfer narrower than one grid cell is sampled back
# into a vertical cliff and the softening is thrown away before it is used.
hm = ndimage.gaussian_filter(hm, 2.0)

out = np.clip(hm * 0.5 + 0.5, 0, 1)
Image.fromarray((out * 65535).astype(np.uint16), mode="I;16").save(OUT)
print("WROTE", OUT, f"range {hm.min():.2f}..{hm.max():.2f}")

if DEBUG:
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(
        OUT.replace(".png", "-debug8.png"))
