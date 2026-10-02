# Alex_PS2_Base.py: PS2-style blockout of "Alex" (bald, 8 heads tall), exports a Godot-ready GLB.
import bpy, bmesh, os
from mathutils import Matrix

H = 0.25                      # 1 head = 0.25 m, so total height = 8H = 2.0 m
SEG = 8

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bm = bmesh.new()

def box(cx, cy, cz, sx, sy, sz):
    m = Matrix.LocRotScale((cx, cy, cz), None, (sx, sy, sz))
    return bmesh.ops.create_cube(bm, size=1.0, matrix=m)["verts"]

def cyl(x, y, z0, z1, r0, r1, seg=SEG):
    m = Matrix.Translation((x, y, (z0 + z1) / 2))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r0, radius2=r1, depth=z1 - z0, matrix=m)

TOP, CHIN, SHOULD, CROTCH, HAND_Z = 8*H, 7*H, 6.5*H, 4*H, 3*H

box(0, 0, (SHOULD + 1.22) / 2, 0.32, 0.22, SHOULD - 1.22)
box(0, 0, (1.22 + 0.93) / 2,   0.35, 0.25, 1.22 - 0.93)
cyl(0, 0, CHIN - 0.03, SHOULD, 0.05, 0.05, 6)

ARM_X = 0.20
for s in (-1, 1):
    cyl(s * ARM_X, 0, 1.20, SHOULD - 0.02, 0.055, 0.05)
    cyl(s * ARM_X, 0, 0.86, 1.20, 0.06, 0.055)
    box(s * ARM_X, 0, (0.86 + HAND_Z) / 2, 0.07, 0.05, 0.86 - HAND_Z)

LEG_X = 0.09
for s in (-1, 1):
    cyl(s * LEG_X, 0, 0.55, CROTCH, 0.09, 0.085)
    cyl(s * LEG_X, 0, 0.10, 0.55, 0.095, 0.09)
    box(s * LEG_X, -0.03, 0.05, 0.14, 0.27, 0.10)

# Head: blocky cube, tapered + beveled at the bottom for the jaw. No face detail, no hair.
hv = box(0, 0, CHIN + H / 2, 0.19, 0.21, H)
for v in hv:
    if v.co.z < CHIN + H / 2:
        v.co.x *= 0.9
bm.edges.ensure_lookup_table()
jaw = [e for e in bm.edges
       if all(v in hv for v in e.verts) and all(abs(v.co.z - CHIN) < 1e-5 for v in e.verts)]
bmesh.ops.bevel(bm, geom=jaw, offset=0.03, segments=1, affect='EDGES')

mesh = bpy.data.meshes.new("Alex_PS2_Base")
bm.to_mesh(mesh)
tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
bm.free()
assert tris < 2000, f"Too many tris: {tris}"
print(f"Alex: {len(mesh.polygons)} faces, {tris} tris, height {8*H} m")

obj = bpy.data.objects.new("Alex_PS2_Base", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_flat()

d = bpy.path.abspath("//") if bpy.data.filepath else "/home/jud1714/Projects/diseno_interfaces/laaf"
out = os.path.join(d, "Alex_PS2_Base.glb")
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True,
                          export_apply=True, export_yup=True)
print("Exported:", out)
