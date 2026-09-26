"""Photoreal concept render with Blender (bpy) from a scene exported by scene_export.py.
Usage: python photoreal.py scene.npz out.png [--preview]
Materials come from part names (keywords) and the part's color, so any repo works without edits.
Optional per-repo overrides: a JSON file next to the npz named <stem>.materials.json mapping
part name -> material class (wood, fabric, clear, metal, painted, rubber, screen, paper, film,
plastic, clay)."""
import sys, json, math, colorsys, re
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]   # works under `blender -b -P photoreal.py -- ...` too
sys.argv = [sys.argv[0]] + ARGS
npz_path, out = Path(ARGS[0]), Path(ARGS[1])
preview = "--preview" in sys.argv
EXPO = 0.8
if "--product" in sys.argv: EXPO = 0.5
RES = None
FOCUS = None
PRODUCT = "--product" in sys.argv
az = el = None
for a in sys.argv:
    if a.startswith("--az="): az = float(a[5:])
    if a.startswith("--el="): el = float(a[5:])
    if a.startswith("--expo="): EXPO = float(a[7:])
    if a.startswith("--focus="): FOCUS = a[8:].lower().split(",")
    if a.startswith("--res="): RES = tuple(int(x) for x in a[6:].split("x"))
AZ = math.radians(az if az is not None else -58)
EL = math.radians(el if el is not None else 24)

data = np.load(npz_path)
meta = json.loads(npz_path.with_suffix(".json").read_text())
ovr_path = npz_path.with_name(npz_path.stem + ".materials.json")
overrides = json.loads(ovr_path.read_text()) if ovr_path.exists() else {}

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene


def hex_rgb(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]  # to linear


def classify(name, color, given=None):
    if given:
        return given
    if name in overrides:
        return overrides[name]
    n = name.lower()
    r, g, b = [int(color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    sat = colorsys.rgb_to_hsv(r, g, b)[1]
    rules = [
        (r"person|figure|hand|forearm|arm \(scale\)|scale\)", "clay"),
        (r"label|carton|paper|cardboard", "paper"),
        (r"bench|timber|wood|plywood|table|frame, pine|oak|bamboo", "wood"),
        (r"sack|strap|sleeve|textile|fabric|cloth|canvas|mesh bag|band", "fabric"),
        (r"bottle|glass|window|lens|acrylic|polycarbonate|glazing|cover, clear|clear", "clear"),
        (r"film|foil|membrane", "film"),
        (r"phone|screen|display|tablet", "screen"),
        (r"mat\b|rubber|tyre|tire|grip|foot|feet|gasket|seal", "rubber"),
        (r"alumin|stainless|can\b|copper|brass|galvan|chrome|rod|axle|shaft|bolt", "metal"),
        (r"steel|iron|sheet metal|enclosure", "painted" if sat > 0.25 else "metal"),
    ]
    for pat, cls in rules:
        if re.search(pat, n):
            return cls
    return "plastic"


def principled(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    return nt, nt.nodes["Principled BSDF"]


def make_material(name, color, cls):
    mat = bpy.data.materials.new(name)
    nt, p = principled(mat)
    base = hex_rgb(color) + [1]
    p.inputs["Base Color"].default_value = base
    I = p.inputs
    if cls == "wood":
        tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (0.15, 1, 1)
        wave = nt.nodes.new("ShaderNodeTexWave"); wave.wave_type = "BANDS"; wave.bands_direction = "Y"
        wave.inputs["Scale"].default_value = 40; wave.inputs["Distortion"].default_value = 3
        wave.inputs["Detail"].default_value = 4; wave.inputs["Detail Scale"].default_value = 1.5
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        dark = [c * 0.55 for c in base[:3]] + [1]
        ramp.color_ramp.elements[0].color = dark; ramp.color_ramp.elements[1].color = base
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
        nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], I["Base Color"])
        I["Roughness"].default_value = 0.55
    elif cls == "fabric":
        I["Roughness"].default_value = 0.95; I["Sheen Weight"].default_value = 0.6
        noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 400
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], I["Normal"])
    elif cls == "clear":
        I["Transmission Weight"].default_value = 1.0; I["Roughness"].default_value = 0.04
        I["IOR"].default_value = 1.57
        tint = [0.6 + 0.4 * c for c in base[:3]] + [1]
        I["Base Color"].default_value = tint
    elif cls == "metal":
        I["Metallic"].default_value = 1.0; I["Roughness"].default_value = 0.28
        I["Anisotropic"].default_value = 0.5
        I["Base Color"].default_value = [max(c, 0.35) for c in base[:3]] + [1]
    elif cls == "painted":
        I["Roughness"].default_value = 0.38; I["Coat Weight"].default_value = 0.35
        I["Coat Roughness"].default_value = 0.15
    elif cls == "rubber":
        I["Roughness"].default_value = 0.85
    elif cls == "screen":
        I["Roughness"].default_value = 0.08; I["Coat Weight"].default_value = 1.0
        I["Coat Roughness"].default_value = 0.02
    elif cls == "paper":
        I["Roughness"].default_value = 0.75
    elif cls == "film":
        I["Roughness"].default_value = 0.3; I["Transmission Weight"].default_value = 0.6
        I["Alpha"].default_value = 0.85
    elif cls == "emissive":
        I["Base Color"].default_value = (0.02, 0.02, 0.025, 1); I["Roughness"].default_value = 0.1
        I["Emission Color"].default_value = base; I["Emission Strength"].default_value = 2.5
        I["Coat Weight"].default_value = 1.0
    elif cls == "clay":
        I["Base Color"].default_value = (0.33, 0.33, 0.34, 1); I["Roughness"].default_value = 0.6
    else:  # plastic
        I["Roughness"].default_value = 0.42; I["Specular IOR Level"].default_value = 0.45
    return mat


objs = []
for i, m in enumerate(meta["parts"]):
    v, f = data[f"v{i}"], data[f"f{i}"]
    me = bpy.data.meshes.new(m["name"])
    me.from_pydata(v.tolist(), [], f.tolist())
    me.update()
    ob = bpy.data.objects.new(m["name"], me)
    scn.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.00005)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.select_set(False)
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(32))
    cls = classify(m["name"], m["color"], m.get("material"))
    if cls not in ("clear", "film"):
        bev = ob.modifiers.new("bevel", "BEVEL")
        bev.width = 0.0003 if PRODUCT else 0.0012; bev.segments = 3; bev.limit_method = "ANGLE"
        bev.angle_limit = math.radians(40); bev.harden_normals = False
        bev.use_clamp_overlap = True
        ob.modifiers.new("wn", "WEIGHTED_NORMAL").keep_sharp = True
    me.materials.append(make_material(m["name"], m["color"], cls))
    objs.append(ob)
    print(f"{m['name']}: {cls}")

# bounds
pts = [ob.matrix_world @ Vector(c) for ob in objs for c in ob.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ctr = (lo + hi) / 2
size = (hi - lo).length

# studio floor with a curved sweep far behind, so the horizon never shows
bpy.ops.mesh.primitive_plane_add(size=size * 12, location=(ctr.x, ctr.y, lo.z))
floor = bpy.context.active_object
fm = bpy.data.materials.new("floor"); nt, p = principled(fm)
p.inputs["Base Color"].default_value = (0.5, 0.49, 0.47, 1); p.inputs["Roughness"].default_value = 0.4
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 30; noise.inputs["Detail"].default_value = 8
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.44, 0.43, 0.41, 1); ramp.color_ramp.elements[1].color = (0.54, 0.53, 0.51, 1)
nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
if PRODUCT:   # seamless white product-studio floor
    ramp.color_ramp.elements[0].color = (0.52, 0.53, 0.55, 1); ramp.color_ramp.elements[1].color = (0.56, 0.57, 0.59, 1)
    p.inputs["Roughness"].default_value = 0.6
floor.data.materials.append(fm)

# world: soft neutral studio ambient
world = bpy.data.worlds.new("studio"); scn.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.78, 0.8, 0.83, 1); bg.inputs["Strength"].default_value = 0.9 if PRODUCT else 0.35

# lights (three-point softboxes), scaled to the scene
def area(name, direction_az, direction_el, dist, power, sz, color=(1, 1, 1)):
    a, e = math.radians(direction_az), math.radians(direction_el)
    d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    L = bpy.data.lights.new(name, "AREA"); L.shape = "DISK"; L.size = sz; L.energy = power; L.color = color
    ob = bpy.data.objects.new(name, L); scn.collection.objects.link(ob)
    ob.location = ctr + d * dist
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()

D = max(size, 1.0)
az_deg = math.degrees(AZ)
area("key", az_deg - 35, 50, D * 1.4, EXPO * 75 * D ** 2, D * 0.9, (1.0, 0.96, 0.9))
area("fill", az_deg + 70, 25, D * 1.6, EXPO * 22 * D ** 2, D * 1.2, (0.9, 0.95, 1.0))
area("rim", az_deg + 180, 40, D * 1.5, EXPO * 50 * D ** 2, D * 0.8)
area("top", 0, 89, D * 1.3, EXPO * 18 * D ** 2, D * 1.5)

# camera
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 55
cam = bpy.data.objects.new("cam", cam_data); scn.collection.objects.link(cam); scn.camera = cam
d = Vector((math.cos(EL) * math.cos(AZ), math.cos(EL) * math.sin(AZ), math.sin(EL)))
cam.location = ctr + d * size * 3
cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
W, H = RES or ((1280, 960) if preview else (2560, 1920))
scn.render.resolution_x, scn.render.resolution_y = W, H
bpy.context.view_layer.update()
fobjs = [o for o in objs if FOCUS is None or any(o.name.lower().startswith(k) for k in FOCUS)]
fpts = [ob.matrix_world @ Vector(c) for ob in fobjs for c in ob.bound_box]
if FOCUS:
    ctr = sum(fpts, Vector()) / len(fpts)
    cam.location = ctr + d * size * 3
    cam_data.lens = 85
coords = [c for p in fpts for c in p]
loc, _ = cam.camera_fit_coords(bpy.context.evaluated_depsgraph_get(), coords)
cam.location = ctr + (Vector(loc) - ctr) * (1.3 if PRODUCT else 1.07)
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = (cam.location - ctr).length
cam_data.dof.aperture_fstop = 16 if PRODUCT else 11

# render settings
scn.render.engine = "CYCLES"
c = scn.cycles
c.device = "CPU"
if "--gpu" in sys.argv:   # Apple Silicon (Metal) or other GPU when run in the Blender app
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("METAL", "OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = kind; prefs.get_devices()
            if any(d.type == kind for d in prefs.devices):
                for d in prefs.devices: d.use = True
                c.device = "GPU"; print("GPU:", kind); break
        except TypeError:
            continue
c.samples = 48 if preview else (96 if PRODUCT else 192); c.use_adaptive_sampling = True
c.adaptive_threshold = 0.02 if preview else 0.008
c.use_denoising = True; c.denoiser = "OPENIMAGEDENOISE"
c.max_bounces = 8; c.transmission_bounces = 8; c.glossy_bounces = 4
scn.view_settings.view_transform = "AgX"; scn.view_settings.look = "AgX - Medium High Contrast"
scn.render.threads_mode = "AUTO"
scn.render.image_settings.file_format = "PNG"
scn.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print("wrote", out)
