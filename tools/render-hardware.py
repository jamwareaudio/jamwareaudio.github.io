"""
JamWare hardware-render rig, v3 -- the whole panel is geometry.

v1 (render.py) put the flat screenshot on a lit slab and let a real camera
supply the realism. That got us most of the way, and it is still the base here.
What it could not do is give a control any actual height: every knob was a
picture of a knob lying flat on the panel, which is fine at the wide framing
and falls apart the moment the camera gets low.

v2 adds two things.

1. MODELLED KNOBS. Each knob in the screenshot gets a truncated cone standing
   on the panel at that exact spot. The trick that makes this cheap and keeps
   it honest: the cone's TOP CAP is UV-mapped from the same screenshot, using
   the same world-to-UV formula as the panel itself. So the cap shows whatever
   the shot already drew there -- pointer line, value arc, cap shading -- and
   we never have to reconstruct a knob face or guess where a pointer is aimed.
   Only the skirt is invented, and a skirt is just a grey cylinder.

   The cone tapers to 80% at the top because both apps draw conical knobs. A
   straight cylinder reads as a bottle cap.

2. STUDIO ENVIRONMENT. Named softbox planes that are actually visible in the
   panel's specular, and a floor with enough gloss to hold a soft reflection of
   the unit. A product shot reads as photographed largely because you can see
   the shape of the lights in the surface; a flat world colour gives a dead
   even sheen no real studio produces.

v3 replaces the flat face plate with a grid displaced by a height map derived
from the screenshot (heightmap.py), so buttons, key caps, indicators, recessed
windows and the plate's own thickness are all real geometry. See the face plate
section below for why Solidify rather than a sheet on a cube.

Needs hm-<app>.png next to this script; build it with heightmap.py first.

Run: blender -b -P render3.py -- <app> <out.png> <hero|macro|low> [samples] [resx]
"""
import bpy, sys, math, os
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
APP, OUT = argv[0], argv[1]
FRAMING = argv[2] if len(argv) > 2 else "hero"
SAMPLES = int(argv[3]) if len(argv) > 3 else 96
RESX = int(argv[4]) if len(argv) > 4 else 1500

SHOTS = "/Users/jonathansidenros/Documents/CompanionApps/site/assets/shots"
HMAPS = os.path.dirname(os.path.abspath(__file__))

# Knob centres and body radii in source-image pixels, located by overlaying
# candidate circles on the shot and checking the crop -- not by a circle
# detector, because there are only seven of them across the two apps and a
# Hough pass would need more tuning than the eyeball did.
#
# Radius is the DRAWN BODY, deliberately not the outer value arc: the cone has
# to cover the flat knob it replaces while leaving the red arc around it
# visible, since the arc is what shows the parameter value.
SPEC = {
    "mutationstation": {
        "shot": "mutationstation.png",
        "knobs": [(1073, 695, 46),    # PITCH MUTATION -- the big one
                  (1427, 305, 37),    # Octave
                  (1427, 523, 37),    # Accent
                  (1427, 707, 37)],   # Slide
    },
    "chordinator": {
        "shot": "chordinator.png",
        "knobs": [(65, 700, 28),      # Invert
                  (162, 700, 28),     # Octave
                  (258, 699, 28)],    # Humanize
    },
}
spec = SPEC[APP]
SHOT = os.path.join(SHOTS, spec["shot"])
HMAP = os.path.join(HMAPS, "hm-%s.png" % APP)

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

img = bpy.data.images.load(os.path.abspath(SHOT))
iw, ih = img.size
aspect = iw / ih

W = 1.0
H = W / aspect
# Thicker than v2's 0.030. Against a width of 1.0 -- call it a 480mm panel --
# this is a 20mm face plate over an 85mm body, which is the proportion of a
# desktop unit you could pick up. The v2 plate was 14mm and, now that the
# relief gives the eye something to judge scale against, read as sheet metal.
T = 0.042

# World units per unit of height map, where the map runs -0.85 (pocket floor)
# to +0.75 (key cap). At 0.0045 a cap stands 1.6mm proud and a pocket is 1.9mm
# deep on a 480mm panel: a little more than a real moulding, which is
# deliberate -- these are product shots and the relief has to survive being
# looked at 900px wide on a web page.
RELIEF = 0.0045


def px_to_world(px, py):
    """Source-image pixel -> world XY on the panel's top face.

    Image rows run downward from the top; the panel's +Y runs away from the
    camera, so the vertical term is flipped. Getting this backwards puts every
    knob in the mirror-image position, which looks almost right on
    Chordinator (its knobs are in a horizontal row) and obviously wrong on
    MutationStation.
    """
    return ((px / iw - 0.5) * W, (0.5 - py / ih) * H)


def px_to_world_r(r):
    return (r / iw) * W


# --- shared texture material for anything showing the screenshot -----------
def make_panel_material(name, bump_strength=0.18):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out_node = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Cubic'
    tex.extension = 'EXTEND'
    texco = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(texco.outputs['UV'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    if bump_strength > 0:
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.0020
        nt.links.new(tex.outputs['Color'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.42
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.34
    # A thin clear coat is what makes a moulded panel look moulded: it lets the
    # softboxes draw a soft sweep across the surface without washing the UI out,
    # because the coat highlight is additive over the base rather than replacing
    # its colour.
    # Kept low. At 0.25 the coat highlight sat on top of everything at grazing
    # angles and drained the warm cream out of both apps' panels -- the render
    # went grey-blue while the source shot is distinctly warm.
    for k in ('Coat Weight', 'Clearcoat'):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = 0.12
    for k in ('Coat Roughness', 'Clearcoat Roughness'):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = 0.20
    nt.links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat


# Bump down from v2's 0.18. The macro relief is geometry now, so the bump is
# only doing what it should have been doing all along -- microtexture on the
# printed legend. At the old strength it embossed the same edges the geometry
# already has and the two disagreed about which way the light was coming from.
panel_mat = make_panel_material("panel", bump_strength=0.09)

skirt_mat = bpy.data.materials.new("skirt")
skirt_mat.use_nodes = True
sb = skirt_mat.node_tree.nodes["Principled BSDF"]
sb.inputs['Base Color'].default_value = (0.62, 0.61, 0.59, 1)
sb.inputs['Roughness'].default_value = 0.34
if 'Metallic' in sb.inputs:
    sb.inputs['Metallic'].default_value = 0.0

# --- the face plate --------------------------------------------------------
# v3: the plate is no longer a cube with a picture on it. It is a dense grid
# displaced by a height map built from the screenshot itself (heightmap.py),
# so every button, key cap, indicator and recessed window in the UI is real
# geometry with a real silhouette and a real cast shadow.
#
# Why a grid + Solidify rather than the obvious "lay a displaced sheet on top
# of a cube": wells go BELOW the panel surface. A sheet sitting on a cube would
# have the piano roll's floor several millimetres inside the cube, z-fighting
# its top face along the whole pocket. Solidify extrudes downward from the
# displaced surface instead, so the pocket floor takes the plate with it and
# there is no second surface to fight. The height map is forced flat in an 8px
# border margin for exactly this reason -- it is what gives the solidified
# plate straight, vertical side walls.
edge_mat = bpy.data.materials.new("edge")
edge_mat.use_nodes = True
eb = edge_mat.node_tree.nodes["Principled BSDF"]
eb.inputs['Base Color'].default_value = (0.085, 0.082, 0.078, 1)
eb.inputs['Roughness'].default_value = 0.48

hmimg = bpy.data.images.load(os.path.abspath(HMAP))
hw, hh = hmimg.size
# Non-Color, or Blender applies an sRGB decode to what is a geometric quantity
# and every height in the map lands somewhere it was not put.
hmimg.colorspace_settings.name = 'Non-Color'
px = np.empty(hw * hh * 4, dtype=np.float32)
hmimg.pixels.foreach_get(px)
hmap = px.reshape(hh, hw, 4)[:, :, 0]        # row 0 is the BOTTOM row in Blender

# Grid vertex counts. Finer than this stops buying anything: the map's chamfers
# are ~2px wide at 2000px, so a grid at 1400 already resolves them, and the
# vertex count is squared in both memory and build time.
GRID_LONG = 1400
NX = min(GRID_LONG, hw)
NY = max(2, int(round(NX * (H / W))))
bpy.ops.mesh.primitive_grid_add(x_subdivisions=NX, y_subdivisions=NY, size=1)
slab = bpy.context.object
slab.scale = (W, H, 1.0)
bpy.ops.object.transform_apply(scale=True)
me = slab.data

# Displace by sampling each vertex's OWN xy rather than by trusting the grid's
# vertex ordering. primitive_grid_add's ordering is an implementation detail
# and has changed between Blender versions; xy is not going to.
nv = len(me.vertices)
co = np.empty(nv * 3, dtype=np.float32)
me.vertices.foreach_get("co", co)
co = co.reshape(nv, 3)
u = np.clip(co[:, 0] / W + 0.5, 0, 1)
v = np.clip(co[:, 1] / H + 0.5, 0, 1)
row = (v * (hh - 1)).astype(np.int32)
col = (u * (hw - 1)).astype(np.int32)
# The map stores 0.5 as the panel surface so that it can carry wells as well as
# proud faces in an unsigned image.
rel = hmap[row, col] * 2.0 - 1.0
co[:, 2] = T / 2 + rel * RELIEF
me.vertices.foreach_set("co", co.ravel())

# UV from xy as well, same formula as everywhere else in this rig, so the
# texture lands on the geometry it was used to build.
uvs = np.empty(len(me.loops) * 2, dtype=np.float32)
lv = np.empty(len(me.loops), dtype=np.int32)
me.loops.foreach_get("vertex_index", lv)
uvs[0::2] = co[lv, 0] / W + 0.5
uvs[1::2] = co[lv, 1] / H + 0.5
me.uv_layers.new(name="UVMap")
me.uv_layers.active.data.foreach_set("uv", uvs)

me.materials.append(panel_mat)    # slot 0 -- the displaced top surface
me.materials.append(edge_mat)     # slot 1 -- the walls Solidify builds
me.shade_smooth()

sol = slab.modifiers.new("solidify", 'SOLIDIFY')
sol.thickness = T
sol.offset = -1.0                 # extrude downward, top surface stays put
sol.use_even_offset = False       # even offset balloons the pocket walls
sol.material_offset = 1
sol.material_offset_rim = 1

# --- modelled knobs --------------------------------------------------------
KNOB_TAPER = 0.80
FLUTES = 44
FLUTE_DEPTH = 0.014

knob_world = []
for i, (px, py, pr) in enumerate(spec["knobs"]):
    cx, cy = px_to_world(px, py)
    knob_world.append((cx, cy))
    r = px_to_world_r(pr)
    h = r * 0.95                    # about as tall as it is wide, like real ones
    z0 = T / 2

    bpy.ops.mesh.primitive_cone_add(
        vertices=FLUTES * 2, radius1=r, radius2=r * KNOB_TAPER,
        depth=h, location=(cx, cy, z0 + h / 2))
    knob = bpy.context.object
    knob.name = "knob_%d" % i
    kme = knob.data

    # Knurl: push alternate vertex columns out and in. Real geometry rather
    # than a bump map, because the knurl is on the silhouette at these camera
    # angles and a bump map cannot break a silhouette.
    for v in kme.vertices:
        ang = math.atan2(v.co.y, v.co.x)
        k = 1.0 + FLUTE_DEPTH * (1 if math.sin(FLUTES * ang) > 0 else -1)
        v.co.x *= k
        v.co.y *= k

    kme.materials.append(panel_mat)   # slot 0 -- top cap
    kme.materials.append(skirt_mat)   # slot 1 -- skirt and underside

    kme.uv_layers.new(name="UVMap")
    kuv = kme.uv_layers.active.data
    for poly in kme.polygons:
        top = poly.normal.z > 0.9
        poly.material_index = 0 if top else 1
        poly.use_smooth = False
        for li in poly.loop_indices:
            if top:
                # Same world-to-UV formula as the panel, offset by the knob's
                # own centre. This is what makes the cap show the pointer and
                # cap shading the app already drew, instead of us inventing one.
                co = kme.vertices[kme.loops[li].vertex_index].co
                wx, wy = cx + co.x, cy + co.y
                kuv[li].uv = (wx / W + 0.5, wy / H + 0.5)
            else:
                kuv[li].uv = (0.0, 0.0)

    kb = knob.modifiers.new("bevel", 'BEVEL')
    kb.width = r * 0.06
    kb.segments = 3
    kb.limit_method = 'ANGLE'
    kb.angle_limit = math.radians(35)

# --- chassis body ----------------------------------------------------------
BODY_INSET = 0.014
BODY_D = 0.085
bpy.ops.mesh.primitive_cube_add(size=1)
body = bpy.context.object
body.scale = (W - BODY_INSET * 2, H - BODY_INSET * 2, BODY_D)
bpy.ops.object.transform_apply(scale=True)
body.location = (0, 0, -T / 2 - BODY_D / 2)
bm = bpy.data.materials.new("body")
bm.use_nodes = True
bbs = bm.node_tree.nodes["Principled BSDF"]
bbs.inputs['Base Color'].default_value = (0.048, 0.046, 0.043, 1)
bbs.inputs['Roughness'].default_value = 0.55
body.data.materials.append(bm)
bbev = body.modifiers.new("bevel", 'BEVEL')
bbev.width = 0.004
bbev.segments = 3

# --- floor -----------------------------------------------------------------
FLOOR_Z = -T / 2 - BODY_D
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, FLOOR_Z))
floor = bpy.context.object
fm = bpy.data.materials.new("floor")
fm.use_nodes = True
fb = fm.node_tree.nodes["Principled BSDF"]
fb.inputs['Base Color'].default_value = (0.035, 0.037, 0.042, 1)
# Glossy enough to hold a soft reflection of the unit. This is the single
# cheapest realism gain in the scene: a matte floor reads as a diagram
# background, a reflective one reads as a table in a studio.
fb.inputs['Roughness'].default_value = 0.22
floor.data.materials.append(fm)

# --- studio environment ----------------------------------------------------
world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.020, 0.022, 0.027, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def softbox(name, loc, rot, size, energy, color=(1, 1, 1)):
    """An area lamp that is also visible in reflections.

    Cycles area lamps do show up in specular, which is the point: the panel's
    clear coat picks up a soft rectangular sweep, and the eye reads a rectangle
    of light as a softbox and therefore as a photograph.
    """
    d = bpy.data.lights.new(name, 'AREA')
    d.shape = 'RECTANGLE'
    d.size = size[0]
    d.size_y = size[1]
    d.energy = energy
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = rot
    scene.collection.objects.link(o)
    return o


# Key is warm and rim is cool, the standard studio split. Both apps' panels are
# a warm cream; a neutral key plus a strongly blue rim read as grey plastic.
softbox("key",  (-2.4, -1.9, 3.2), (math.radians(30), math.radians(-24), 0), (5.0, 3.0), 105, (1.00, 0.965, 0.92))
softbox("fill", ( 3.0, -1.4, 2.0), (math.radians(46), math.radians(42), 0), (4.0, 4.0), 28)
softbox("rim",  ( 0.5,  3.2, 1.8), (math.radians(-58), 0, 0), (5.0, 2.0), 70, (0.80, 0.86, 1.0))
# A low, tight kicker from the front-left. It exists to put a bright line along
# the top edge of every knob skirt -- without it the modelled knobs are the same
# tone as the panel and all that geometry reads as nothing. Kept weak: it is
# nearly edge-on to the panel, so a little of it goes a very long way, and at
# 34W it blew out the whole near half of the plate.
softbox("kick", (-1.6, -2.2, 0.55), (math.radians(74), math.radians(-16), 0), (2.0, 0.6), 11)

# --- camera ----------------------------------------------------------------
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.dof.use_dof = True

if FRAMING == "top":
    # Straight down, no tilt, no DOF. Not a shipping framing -- it exists to
    # check that the displaced grid's UVs still land the texture exactly where
    # the flat slab did, which is the one thing a three-quarter view is bad at
    # showing.
    cam_data.lens = 50
    cam_data.dof.aperture_fstop = 22.0
    cam.location = (0, 0, 2.6)
    cam.rotation_euler = (0, 0, 0)
    focus_at = (0, 0, T / 2)
    ratio = H / W
elif FRAMING == "macro":
    cam_data.lens = 70
    cam_data.dof.aperture_fstop = 4.0
    cam.location = (-0.84, -1.24, 0.84)
    cam.rotation_euler = (math.radians(54), 0, math.radians(-30))
    focus_at = (0.02, 0.04, T / 2)
    ratio = 0.70
elif FRAMING == "low":
    # Low and close, so the knobs break the horizon of the panel. This framing
    # only became worth having once the knobs were real geometry.
    #
    # It is AIMED, not hand-placed, and that is the fix for the first attempt:
    # the camera numbers were tuned against MutationStation, whose knobs sit at
    # source x=1073..1427 (centre-right), and reusing them for Chordinator --
    # whose three knobs are at x=65..258, hard against the left edge -- put the
    # entire subject out of frame. Aiming at the knob cluster's own centroid
    # makes the shot correct for any app in SPEC without a second table of
    # magic numbers to keep in sync.
    tx = sum(c[0] for c in knob_world) / len(knob_world)
    ty = sum(c[1] for c in knob_world) / len(knob_world)
    cam_data.lens = 85
    # f/3.2 left almost the whole frame blurred. At this distance the knobs are
    # only a few cm deep, so the shallow end of the range buys nothing but mush.
    cam_data.dof.aperture_fstop = 6.3
    off = (-0.30, -0.62, 0.26)
    cam.location = (tx + off[0], ty + off[1], T / 2 + off[2])
    # Derive the aim from the offset rather than typing angles. Blender's camera
    # looks down -Z, so at rx=90,rz=0 it looks along +Y; rotating rz about Z
    # sends +Y to (-sin rz, cos rz), hence rz = -atan2(dx, dy).
    dx, dy, dz = -off[0], -off[1], -off[2]
    horiz = math.hypot(dx, dy)
    cam.rotation_euler = (math.radians(90) - math.atan2(-dz, horiz),
                          0,
                          -math.atan2(dx, dy))
    focus_at = (tx, ty, T / 2)
    ratio = 0.62
else:
    cam_data.lens = 55
    cam_data.dof.aperture_fstop = 14.0
    cam.location = (-0.86, -1.60, 1.10)
    cam.rotation_euler = (math.radians(56), 0, math.radians(-28))
    focus_at = (0.0, 0.0, T / 2)
    ratio = 0.62

focus = bpy.data.objects.new("focus", None)
focus.location = focus_at
scene.collection.objects.link(focus)
cam_data.dof.focus_object = focus

scene.render.resolution_x = RESX
scene.render.resolution_y = int(RESX * ratio)
# Standard, not Filmic/AgX: the texture is an already tone-mapped sRGB UI shot,
# and a second film curve lifts its blacks and chalks out the accent colours.
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.abspath(OUT)
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
