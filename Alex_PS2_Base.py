# Alex_PS2_Base.py: PS2-era (Silent Hill style) low-poly Alex. Bald, 8 heads tall, shoulders 2 heads wide,
# fingertips at mid-thigh. Body = lofted octagonal cross-sections (shaped, not boxes), flat-shaded, 4 materials.
import bpy, bmesh, math, os
from mathutils import Matrix

H = 0.25                                  # 1 head = 0.25 m -> 8H = 2.0 m
N = 8                                     # verts per ring (octagon, rotated so faces are flat front/back/sides)
K = 1 / math.cos(math.pi / N)             # makes the flat sides land exactly on the nominal radius
MATS = {"skin": (0.62, 0.45, 0.36), "sweater": (0.16, 0.17, 0.15),
        "pants": (0.08, 0.08, 0.10), "boots": (0.05, 0.04, 0.035)}
IDX = {k: i for i, k in enumerate(MATS)}

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bm = bmesh.new()

def ring(z, rx, ry, cx=0.0, cy=0.0):
    return [bm.verts.new((cx + rx * K * math.cos((k + .5) * 2 * math.pi / N),
                          cy + ry * K * math.sin((k + .5) * 2 * math.pi / N), z)) for k in range(N)]

def loft(rings, mat, x=0.0, y=0.0):
    """rings: (z, rx, ry[, cy]) bottom to top, capped both ends. x,y offset the whole tube."""
    start = len(bm.faces)
    rs = [ring(r[0], r[1], r[2], x, y + (r[3] if len(r) > 3 else 0)) for r in rings]
    for a, b in zip(rs, rs[1:]):
        for k in range(N):
            bm.faces.new((a[k], a[(k + 1) % N], b[(k + 1) % N], b[k]))
    bm.faces.new(rs[0][::-1]); bm.faces.new(rs[-1])
    bm.faces.ensure_lookup_table()
    for f in bm.faces[start:]:
        f.material_index = IDX[mat]

def block(cx, cy, cz, sx, sy, sz, mat):
    start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.LocRotScale((cx, cy, cz), None, (sx, sy, sz)))
    bm.faces.ensure_lookup_table()
    for f in bm.faces[start:]:
        f.material_index = IDX[mat]

CHIN, SHOULD, CROTCH, HAND_Z = 7 * H, 6.5 * H, 4 * H, 3 * H

# ---- Torso: baggy sweater, hem flare, broad sloped shoulders ----
loft([(0.90, .190, .130), (1.00, .175, .120), (1.15, .160, .110), (1.38, .185, .125),
      (1.54, .215, .120), (1.61, .120, .085)], "sweater")
loft([(CHIN - .02, .047, .047), (SHOULD - .01, .055, .055)], "skin")               # neck

# ---- Arms: baggy sleeves, bare hands. Outer edge at x=0.25 (= shoulders 2 heads wide) ----
AX = 0.195
for s in (-1, 1):
    loft([(0.86, .062, .060), (1.00, .052, .050), (1.20, .054, .052), (1.42, .058, .058),
          (1.58, .062, .060)], "sweater", x=s * AX)
    loft([(HAND_Z, .020, .016), (0.79, .036, .020), (0.84, .040, .024), (0.87, .030, .020)], "skin", x=s * AX)

# ---- Legs: baggy pants bunching over boots ----
LX = 0.09
for s in (-1, 1):
    loft([(0.13, .105, .105), (0.30, .092, .095), (0.52, .088, .092), (0.75, .092, .098),
          (CROTCH - .04, .092, .105)], "pants", x=s * LX)
    loft([(0.0, .062, .125, -.045), (0.05, .062, .125, -.045), (0.11, .060, .090, -.01),
          (0.15, .060, .085, 0)], "boots", x=s * LX)

# ---- Head: egg-shaped, tapered jaw, brow ridge. Flat front face for painted texture. NO HAIR. ----
loft([(CHIN,        .040, .050),            # chin
      (CHIN + .04,  .075, .080),            # jaw
      (CHIN + .10,  .092, .092),            # cheeks
      (CHIN + .17,  .096, .100, -.006),     # brow (juts forward)
      (CHIN + .22,  .085, .092),            # forehead
      (CHIN + .25,  .050, .060)],           # crown (flat top, bald)
     "skin")
# nose wedge on the flat face + ears (tiny, skin coloured)
yf = -0.093
t, bl, br, tip = (bm.verts.new(c) for c in ((0, yf, 1.87), (-.014, yf, 1.83), (.014, yf, 1.83), (0, yf - .028, 1.835)))
start = len(bm.faces)
for tri in ((tip, bl, br), (t, bl, tip), (t, tip, br), (t, br, bl)):
    bm.faces.new(tri)
bm.faces.ensure_lookup_table()
for f in bm.faces[start:]:
    f.material_index = IDX["skin"]
for s in (-1, 1):
    block(s * .098, 0.005, 1.86, .018, .030, .050, "skin")

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

# ---- Mesh object + materials ----
mesh = bpy.data.meshes.new("Alex_PS2_Base")
bm.to_mesh(mesh)
tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
bm.free()
assert tris < 2000, f"Too many tris: {tris}"
print(f"Alex: {len(mesh.polygons)} faces, {tris} tris, height {8*H} m")
for name, col in MATS.items():
    m = bpy.data.materials.new("Alex_" + name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = 1.0
    mesh.materials.append(m)

obj = bpy.data.objects.new("Alex_PS2_Base", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_flat()

d = bpy.path.abspath("//") if bpy.data.filepath else os.path.dirname(os.path.abspath(__file__))
out = os.path.join(d, "Alex_PS2_Base.glb")
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True,
                          export_apply=True, export_yup=True)
print("Exported:", out)
