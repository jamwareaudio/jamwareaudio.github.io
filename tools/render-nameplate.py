"""
The JamWare Audio nameplate, milled as real geometry.

WHY THIS ONE AND NOT THE OTHER RENDERS. The first attempt at 3D on this site
took each app's whole window capture and extruded it. It failed, and it failed
structurally rather than for want of tuning: a plugin GUI carries hundreds of
elements, so giving relief to all of them produces a uniform micro-relief no
tool could mould, and displaced legend text warps into mush at exactly the
raking angles that make an object look like an object. The reference shots
everyone points at -- Serum's 3dOsc, the Spire overview -- are not extruded
screenshots. They are purpose-built scenes of a FEW modelled objects, with the
GUI shown separately, flat and crisp.

A nameplate is that kind of subject. It is a dozen letterforms and a plate.
Every edge in it can be real geometry cut by a real boolean, so nothing is
approximated and nothing has to be smoothed into porridge to hide the sampling.

The build is the way these are actually made:

  - a dark anodised plate, chamfered on every edge,
  - the wordmark and the company mark cut THROUGH the anodising with an end
    mill, so the groove floor and its walls are bare bright aluminium,
  - the seven step dots infilled with the brand amber, the way a filled
    engraving is done.

That is why the cutter carries its own material: Blender's boolean assigns the
operand's material to the faces it creates, so the bright-metal material on the
cutter lands on precisely the surfaces a mill would have exposed and nowhere
else. Painting the letters bright instead would have been a texture, and a
texture has no wall.

Two deliberate restraints, both learned from the renders that got pulled:

  LEGIBILITY FIRST. The camera tilt is small and the aperture nearly closed.
  A product shot may give up almost anything before it gives up readable panel
  text, and a shallow depth of field over a wordmark is decoration eating the
  thing it is decorating.

  ONE POINT OF COLOUR. Everything is aluminium except the seven dots. The site
  already argues that each app owns exactly one accent; the company plate holds
  to the same rule.

Renders on a transparent background so the plate drops onto the site's own
brushed faceplate rather than carrying a background that has to match it.

Run: blender -b -P render-nameplate.py -- <out.png> [samples] [resx]
"""
import bpy
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 128
RESX = int(argv[2]) if len(argv) > 2 else 2000

FONT = "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf"

# From brand/brand.json. Do not invent values here -- the plate is another
# surface in the same family as the app icons and the site palette.
INK = (0.028, 0.025, 0.022, 1)        # #2A2621, near enough, in linear
AMBER = (0.72, 0.22, 0.030, 1)        # #E0862C
RED = (0.62, 0.045, 0.028, 1)         # #D13A2C

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
try:
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
except Exception as e:
    print("GPU setup skipped:", e)


def metal(name, base, rough, aniso=0.0, metallic=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = base
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    if 'Anisotropic' in b.inputs:
        b.inputs['Anisotropic'].default_value = aniso
    return m


# The plate is anodised, not painted: dark, but still a metal underneath, so it
# keeps a metal's specular behaviour and goes light at grazing angles. Painted
# black would read as plastic, which is the whole thing we are trying not to be.
anod = metal("anodised", (0.020, 0.019, 0.017, 1), 0.34, aniso=0.55)
# 0.38, not the 0.26 this started at. A near-polished floor inside a groove
# only 17 thousandths deep throws a hard specular that breaks the letterforms
# into glassy shards -- the letters stop reading as cut metal and start reading
# as chrome plastic. A milled floor is satin; the tool leaves it that way.
bare = metal("bare-alu", (0.62, 0.615, 0.60, 1), 0.38, aniso=0.30)
amber = metal("amber", AMBER, 0.38, metallic=0.0)
red = metal("red", RED, 0.38, metallic=0.0)

# --- the plate -------------------------------------------------------------
# primitive_cube_add(size=1) is already 1x1x1, so scale factors ARE final
# dimensions. Halving them is the obvious-looking mistake and it silently
# makes the plate half the size of every other number in the scene.
PW, PH, PT = 2.32, 0.62, 0.075
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -PT / 2))
plate = bpy.context.object
plate.scale = (PW, PH, PT)
bpy.ops.object.transform_apply(scale=True)
plate.data.materials.append(anod)
plate.data.materials.append(bare)
plate.data.materials.append(amber)
plate.data.materials.append(red)

# The perimeter chamfer is applied NOW, before any cutting, so that the boolean
# solver is handed a clean closed solid. The groove lips get their own, much
# smaller chamfer from a second bevel added after the booleans -- see the end of
# the cutting section for why the two cannot be one modifier.
bev = plate.modifiers.new("bevel", 'BEVEL')
bev.width = 0.014
bev.segments = 5
bev.limit_method = 'ANGLE'
bpy.context.view_layer.objects.active = plate
bpy.ops.object.modifier_apply(modifier=bev.name)

TOP = 0.0
CUT = 0.017          # groove depth; a real nameplate mill goes about this far


def cutter_z(extrude):
    """Sit a cutter so its underside lands CUT below the plate top.

    Blender extrudes text and curves symmetrically about their own plane, so
    the solid spans z +/- extrude. Placing the object at this height puts the
    bottom face exactly at TOP - CUT and leaves the rest poking out above the
    plate, where the boolean discards it. Getting this wrong does not error --
    it quietly cuts a groove of the wrong depth, or none at all.
    """
    return TOP - CUT + extrude


EXT = 0.09
cutters = []

# --- the wordmark ----------------------------------------------------------
# DIN, because it is the typeface actually used on machine nameplates -- it is
# the German industrial standard for lettering, which is why every panel that
# has ever been engraved looks like this. Tracked open: a mill cannot cut two
# letters closer than its own bit diameter, so real engraved lettering is
# always loose, and tight tracking is the fastest way to make this look drawn.
bpy.ops.object.text_add(location=(0.390, -0.005, cutter_z(EXT)))
txt = bpy.context.object
td = txt.data
td.body = "JAMWARE AUDIO"
td.font = bpy.data.fonts.load(FONT)
td.align_x = 'CENTER'
td.align_y = 'CENTER'
td.size = 0.20
td.space_character = 1.14
td.extrude = EXT
# ⚠ DO NOT put a bevel_depth on this text. The obvious way to get the mill's
# corner radius onto the groove lip is to round the cutter, and it renders an
# empty frame: a bevelled text object doubles its vertex count by folding
# geometry back through itself at every tight interior corner, and the EXACT
# boolean solver's response to a self-intersecting operand is to return an
# empty mesh -- no error, no warning, a plate with zero vertices and a fully
# transparent render. Measured here: bevel_depth 0 leaves the plate at 1923
# verts, bevel_depth 0.0016 leaves it at 0. The lip comes from the second
# bevel modifier below instead, which is the more honest model anyway: the
# radius belongs to the cut, not to the shape being cut.
bpy.ops.object.convert(target='MESH')
txt.data.materials.append(bare)
cutters.append(txt)

# --- the company mark ------------------------------------------------------
# The step run and the squelch tail, rebuilt from the canonical geometry in
# brand/company-logo.svg rather than imported from it. The SVG draws them as
# STROKED paths with no fill, and Blender's SVG importer only brings in fills,
# so an import lands a zero-area curve and nothing renders. A curve with a
# bevel depth is the same object the SVG describes -- a path of a given width
# with round caps -- so it is rebuilt here, at the same coordinates, and the
# stroke width becomes the bevel radius.
SVG_STEPS = [(76, 256), (76, 226), (112, 226), (112, 196), (148, 196),
             (148, 236), (184, 236), (184, 186), (220, 186), (220, 216),
             (256, 216), (256, 176), (292, 176)]
SVG_TAIL = [((292, 176), (316, 120), (340, 110), (364, 166)),
            ((364, 166), (388, 222), (396, 300), (424, 268)),
            ((424, 268), (440, 250), (448, 250), (456, 256))]
SVG_DOTS = [(76, 256), (112, 226), (148, 196), (184, 236),
            (220, 186), (256, 216), (292, 176)]

# Map SVG user units onto the plate. The mark occupies the left third; the
# wordmark above is offset right by the same amount to balance it.
# Sized and placed so the mark's left edge and the wordmark's right edge sit
# the same 0.16 in from their own ends of the plate. Eyeballing this is what
# produced the first pass, where the mark ran off the left chamfer entirely.
# Sized to 0.32 tall against a 0.62 plate -- most of the available height. The
# first pass gave the mark roughly the wordmark's cap height, which is what you
# would do on paper, and on the plate it disappeared: the camera looks along the
# plate at 20 degrees, so everything's vertical dimension is foreshortened to
# about a third, and a mark that merely matches the type flattens into a scratch
# while the type stays readable. Anything whose shape carries meaning in the
# y direction has to be drawn oversize to survive the rake.
MARK_S = 0.00170
MARK_X, MARK_Y = -1.01 - 76 * MARK_S, 205 * MARK_S


def m(p):
    return (MARK_X + p[0] * MARK_S, MARK_Y - p[1] * MARK_S)


def stadium(name, p0, p1, r, material):
    """One stroke segment, as an explicit convex prism.

    ⚠ This used to be a Blender curve with a bevel_depth, which is the obvious
    way to draw a stroked path and is wrong here in two separate ways.

    First, a multi-point poly spline swept at any useful width self-intersects
    on the inside of a right-angle corner, and a self-intersecting operand makes
    the EXACT boolean solver return an empty mesh with no error at all -- the
    render just comes out blank. Splitting to one spline per segment fixed that.

    Second, and this is the one that took a render to see: a 3D curve's `extrude`
    runs along the curve's own normal frame, NOT along global Z. Segments running
    across the plate therefore extruded sideways, so instead of a groove the
    boolean got a slab standing on edge, and the mark rendered as coloured fins
    sticking up out of the plate. There is no setting that pins the frame; the
    frame is the feature.

    So the outline is built by hand: a rectangle with a semicircular cap at each
    end -- exactly the shape a round-nosed cutter of radius r sweeps between two
    points, and exactly what an SVG round-capped stroke means -- extruded along
    global Z by explicit vertex coordinates, where nothing can reinterpret it.
    Every such prism is convex, so no single cutter can fold through itself, and
    separate booleans are free to overlap at the joints.
    """
    import bmesh
    x0, y0 = m(p0)
    x1, y1 = m(p1)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 1e-9:
        return None
    ux, uy = dx / L, dy / L
    a = math.atan2(uy, ux)
    K = 12
    ring = []
    # cap on p1, swinging from the left side of the direction round to the right
    for k in range(K + 1):
        t = a + math.pi / 2 - math.pi * k / K
        ring.append((x1 + r * math.cos(t), y1 + r * math.sin(t)))
    # cap on p0, continuing the same sweep
    for k in range(K + 1):
        t = a - math.pi / 2 - math.pi * k / K
        ring.append((x0 + r * math.cos(t), y0 + r * math.sin(t)))

    # Bottom at the groove floor, top well clear of the plate face. Stopping the
    # prism flush at TOP leaves it coplanar with the plate, which is the other
    # way to make the EXACT solver silently produce nothing.
    zb, zt = TOP - CUT, TOP + 0.10
    bm = bmesh.new()
    lower = [bm.verts.new((x, y, zb)) for x, y in ring]
    upper = [bm.verts.new((x, y, zt)) for x, y in ring]
    bm.faces.new(lower)
    bm.faces.new(list(reversed(upper)))
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lower[i], lower[j], upper[j], upper[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    me.materials.append(material)
    return ob


# strokeWidth 14 in the SVG's 420-unit design space, halved because this is a
# radius. Opened from 14 to 18: at 14 the groove came out narrower than it is
# deep, and a groove narrower than it is deep reads as a scratch rather than as
# engraving, because no light reaches its floor.
SW = 18 * MARK_S / 2

for i in range(len(SVG_STEPS) - 1):
    cutters.append(stadium("step%02d" % i, SVG_STEPS[i], SVG_STEPS[i + 1],
                           SW, bare))


def bez(p0, c1, c2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * p0[i] + 3 * u * u * t * c1[i]
                 + 3 * u * t * t * c2[i] + t ** 3 * p3[i] for i in range(2))


# The squelch tail is three cubic segments. It is flattened to a polyline here
# and cut as a chain of the same stadium prisms rather than as a bezier curve,
# for the reasons in stadium(): the curve route cannot be made to extrude along
# Z. Eight samples per cubic is enough that the joints disappear under a stroke
# this wide -- the chord error at that spacing is well under the stroke radius.
tail_pts = []
for seg in SVG_TAIL:
    for k in range(8):
        tail_pts.append(bez(*seg, k / 8.0))
tail_pts.append(SVG_TAIL[-1][3])
for i in range(len(tail_pts) - 1):
    cutters.append(stadium("tail%02d" % i, tail_pts[i], tail_pts[i + 1],
                           SW, red))

# The dots are filled amber rather than bare metal: a filled engraving, which
# is how a single colour gets onto a machined plate without printing it.
for i, d in enumerate(SVG_DOTS):
    x, y = m(d)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=SW * 0.78, depth=0.20, location=(x, y, cutter_z(0.10)))
    c = bpy.context.object
    c.data.materials.append(amber)
    cutters.append(c)

cutters = [c for c in cutters if c is not None]

# --- cut -------------------------------------------------------------------
# One boolean per cutter, all EXACT. A single joined cutter would be one
# modifier instead of twenty, but joining meshes that overlap each other --
# the dots sit inside the step run -- gives the solver self-intersecting input,
# and the EXACT solver's answer to that is to drop faces silently rather than
# fail. Separate booleans never see an overlap.
for c in cutters:
    mo = plate.modifiers.new("cut-" + c.name, 'BOOLEAN')
    mo.operation = 'DIFFERENCE'
    mo.solver = 'EXACT'
    mo.object = c
    c.hide_render = True
    # Checked after EVERY cut, because the only symptom of a failed EXACT
    # boolean is a plate with no vertices and a completely transparent render
    # -- no exception, no console warning, thirty seconds of GPU time and a
    # blank PNG that looks like a framing mistake. Two separate causes have
    # already produced it here. Failing loudly, naming the cutter, is worth
    # the depsgraph evaluation per modifier.
    dg = bpy.context.evaluated_depsgraph_get()
    if len(plate.evaluated_get(dg).to_mesh().vertices) == 0:
        raise SystemExit("boolean collapsed the plate at cutter: " + c.name)

# The groove lip. It runs AFTER the booleans so it catches the edges the cut
# just created; clamping keeps it from eating the narrow strokes of the company
# mark, which are only a couple of hundredths wide.
lip = plate.modifiers.new("lip", 'BEVEL')
# ⚠ Keep this small. At 0.0022 the bevel could not fit inside the dot holes and
# threw thin spikes straight up out of the plate, carrying the amber material
# with them -- two orange pins standing on the logo, which looks like a render
# bug and is one. Clamping alone does not save it; the width has to be under the
# smallest radius on the part.
lip.width = 0.0010
lip.segments = 2
lip.limit_method = 'ANGLE'
lip.angle_limit = math.radians(40)
lip.use_clamp_overlap = True

# --- world and lighting ----------------------------------------------------
# A metal is nothing but what it reflects, so the world is not merely fill
# here -- it is most of the material. A flat grey world makes anodising look
# like matte plastic no matter how the roughness is set.
world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
wn = world.node_tree
bg = wn.nodes["Background"]
grad = wn.nodes.new('ShaderNodeTexGradient')
grad.gradient_type = 'LINEAR'
mapn = wn.nodes.new('ShaderNodeMapping')
texco = wn.nodes.new('ShaderNodeTexCoord')
mapn.inputs['Rotation'].default_value = (0, math.radians(-90), 0)
ramp = wn.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.30
ramp.color_ramp.elements[0].color = (0.045, 0.048, 0.055, 1)
ramp.color_ramp.elements[1].position = 0.92
ramp.color_ramp.elements[1].color = (0.85, 0.87, 0.92, 1)
wn.links.new(texco.outputs['Generated'], mapn.inputs['Vector'])
wn.links.new(mapn.outputs['Vector'], grad.inputs['Vector'])
wn.links.new(grad.outputs['Fac'], ramp.inputs['Fac'])
wn.links.new(ramp.outputs['Color'], bg.inputs['Color'])
# Held well below 1: at full strength the sky is most of what the top face
# reflects and the anodising reads as light grey, which is the opposite of the
# material. The lights do the shaping; the world only keeps the metal from
# going dead black where nothing hits it.
bg.inputs['Strength'].default_value = 0.42


def area_light(name, loc, rot, size, energy, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'AREA')
    d.size = size
    d.energy = energy
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = rot
    scene.collection.objects.link(o)
    return o


# A long, narrow key running along the plate rather than a square softbox. The
# groove walls are what has to catch light, and they are 17 thousandths deep --
# a compact source lights the four or five letters nearest it and leaves the
# rest of the word flat. A strip the length of the plate reaches every wall.
area_light("key", (-1.1, -1.5, 2.0), (math.radians(34), math.radians(-16), 0), 4.0, 260)
area_light("fill", (1.6, -1.2, 1.3), (math.radians(50), math.radians(38), 0), 3.0, 60)
area_light("rim", (0.2, 1.9, 1.1), (math.radians(-62), 0, 0), 3.2, 110,
           (0.78, 0.84, 1.0))

# --- camera ----------------------------------------------------------------
# Shallow tilt and a long lens. The temptation is a dramatic 55-degree rake,
# and it is the same temptation that wrecked the app renders: past about 25
# degrees the letterforms foreshorten into each other and the wordmark stops
# being readable, which for a nameplate is the entire failure. f/16 keeps the
# far end as sharp as the near one for the same reason.
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
# Framed by arithmetic rather than by nudging: a 36mm sensor at focal length f
# covers sensor_w / f * distance across, so the distance that puts a chosen
# width across the frame is that solved for distance. The plate is 2.30 wide and
# FRAME_W leaves the margin around it.
TILT = 20.0          # degrees off the plate's own plane
FRAME_W = 2.60
cam_data.lens = 85
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 16.0
dist = FRAME_W * cam_data.lens / cam_data.sensor_width
cam.location = (0.06,
                -dist * math.cos(math.radians(TILT)),
                dist * math.sin(math.radians(TILT)))
cam.rotation_euler = (math.radians(90 - TILT), 0, math.radians(1.4))
focus = bpy.data.objects.new("focus", None)
focus.location = (0, 0, 0)
scene.collection.objects.link(focus)
cam_data.dof.focus_object = focus

# --- output ----------------------------------------------------------------
# Transparent film, so the plate lands on the site's own brushed faceplate
# instead of carrying a background that would have to be colour-matched to it
# and would drift the moment the palette moved.
scene.render.film_transparent = True
scene.render.resolution_x = RESX
scene.render.resolution_y = int(RESX * 0.26)
# Standard, not Filmic/AgX: the accent amber and red come straight from
# brand.json and a film curve desaturates them away from the values every other
# surface in the family uses.
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = os.path.abspath(OUT)
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
