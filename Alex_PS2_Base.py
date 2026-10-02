# Alex_PS2_Base.py: Alex Moreno, rounded low-poly character (late-PS2 / GTA-SA era), textured, with 3D hair.
# Look matches the old Alex: ash-blonde swept hair, blue eyes, clean-shaven, grimy white tee, baggy black jeans, worn sneakers.
# 8 heads tall (2.0 m), shoulders 2 heads wide (arms outer edge x=+-0.25), fingertips at mid-thigh (z=0.75).
# Body = lofted rounded cross-sections. Face/skin/cloth/hair textures are painted procedurally (numpy) and embedded in the GLB.
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector

H = 0.25
OUT_DIR = bpy.path.abspath("//") if bpy.data.filepath else os.path.dirname(os.path.abspath(__file__))
MAX_TRIS = 6000

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bm = bmesh.new()
UV = bm.loops.layers.uv.verify()
MATS = ["face", "skin", "tee", "jeans", "sneaker", "sole", "hair", "hair_dark"]
MI = {m: i for i, m in enumerate(MATS)}

# ------------------------------------------------------------------ geometry helpers
def ring_pts(z, rx, ry, cx=0.0, cy=0.0, n=12):
    k = 1 / math.cos(math.pi / n)   # flat sides land on the nominal radius
    return [Vector((cx + rx * k * math.cos((i + .5) * 2 * math.pi / n),
                    cy + ry * k * math.sin((i + .5) * 2 * math.pi / n), z)) for i in range(n)]

def loft_pts(rows, mat, tile=(1, 1), cap_bottom=True, cap_top=True):
    """rows: list of rings (lists of Vector), bottom to top. Quads between rings + caps. UVs: u around, v along (0..1)."""
    n = len(rows[0])
    vr = [[bm.verts.new(p) for p in r] for r in rows]
    cum = [0.0]
    for a, b in zip(rows, rows[1:]):
        cum.append(cum[-1] + (sum(b, Vector()) / n - sum(a, Vector()) / n).length)
    tot = cum[-1] or 1.0
    new = []
    for j in range(len(vr) - 1):
        for k in range(n):
            f = bm.faces.new((vr[j][k], vr[j][(k + 1) % n], vr[j + 1][(k + 1) % n], vr[j + 1][k]))
            u0, u1 = k / n * tile[0], (k + 1) / n * tile[0]
            v0, v1 = cum[j] / tot * tile[1], cum[j + 1] / tot * tile[1]
            for l, uv in zip(f.loops, ((u0, v0), (u1, v0), (u1, v1), (u0, v1))):
                l[UV].uv = uv
            new.append(f)
    for ok, ring, rev in ((cap_bottom, vr[0], True), (cap_top, vr[-1], False)):
        if ok:
            f = bm.faces.new(ring[::-1] if rev else ring)
            for i, l in enumerate(f.loops):
                a = i / n * 2 * math.pi
                l[UV].uv = (0.5 + 0.4 * math.cos(a), 0.5 + 0.4 * math.sin(a))
            new.append(f)
    for f in new:
        f.material_index = MI[mat]
    return new

def loft(rings, mat, x=0.0, y=0.0, n=12, tile=(1, 1)):
    """rings: (z, rx, ry[, cy]) bottom to top, centred at (x, y)."""
    return loft_pts([ring_pts(r[0], r[1], r[2], x, y + (r[3] if len(r) > 3 else 0), n) for r in rings], mat, tile)

def tube(path, radii, mat, n=6, flat=1.0, tile=(1, 1)):
    """Tapered round tube along a polyline of (x,y,z) points (used for hair locks)."""
    pts = [Vector(p) for p in path]
    rows = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        helper = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        side = t.cross(helper).normalized()
        up = t.cross(side)                                   # side x up = t -> outward normals
        r = radii[i]
        rows.append([p + side * (r * math.cos(a)) + up * (r * flat * math.sin(a))
                     for a in (j * 2 * math.pi / n for j in range(n))])
    return loft_pts(rows, mat, tile)

# ------------------------------------------------------------------ the body (z up, faces -y)
CHIN = 7 * H; SHOULD = 6.5 * H; HAND_Z = 3 * H

# Torso: white tee, baggy hem, rounded chest, sloped shoulders
loft([(0.90, .188, .127), (0.95, .184, .126), (1.06, .170, .118), (1.18, .160, .112), (1.30, .170, .118),
      (1.40, .186, .126), (1.50, .200, .124), (1.59, .222, .116), (1.63, .190, .100), (1.66, .100, .075),
      (1.675, .070, .062)], "tee", n=14, tile=(2, 2))
loft([(1.64, .082, .070), (1.665, .086, .073), (1.685, .076, .065)], "tee", n=14, tile=(2, 0.3))   # crew collar
loft([(1.61, .064, .064), (1.69, .057, .058), (1.77, .056, .060)], "skin", n=10)                 # neck

AX = 0.185                                                       # arm centre; outer edge = 0.25 (2 heads wide in total)
for s in (-1, 1):
    loft([(0.90, .032, .026), (0.98, .040, .034), (1.10, .045, .045, -.006), (1.20, .048, .048, -.010),
          (1.32, .054, .054, -.004), (1.47, .058, .058), (1.61, .060, .060)], "skin", x=s * AX, n=10)
    loft([(0.75, .012, .010), (0.78, .026, .020), (0.83, .034, .024), (0.93, .031, .025)], "skin", x=s * AX, n=10)  # hand
    loft([(1.30, .066, .066), (1.40, .068, .068), (1.50, .068, .067), (1.60, .066, .064), (1.64, .056, .054), (1.665, .030, .030)], "tee", x=s * AX, n=12)    # short sleeve

# Hips + legs: baggy black jeans pooling over sneakers
loft([(0.78, .120, .095), (0.83, .160, .110), (0.88, .176, .120), (0.95, .174, .116), (0.99, .150, .106)], "jeans", n=14)
LX = 0.09
for s in (-1, 1):
    loft([(0.12, .098, .105), (0.20, .088, .092), (0.32, .084, .090), (0.46, .082, .088), (0.58, .088, .094),
          (0.72, .094, .100), (0.84, .098, .104), (0.93, .098, .106)], "jeans", x=s * LX, n=12)
    loft([(0.0, .066, .130, -.045), (0.03, .066, .130, -.045)], "sole", x=s * LX, n=12)
    loft([(0.03, .060, .126, -.045), (0.07, .063, .124, -.044), (0.11, .057, .100, -.030), (0.15, .052, .075, -.006)],
         "sneaker", x=s * LX, n=12)

# Head: rounded skull, jaw, brow, flat-ish face for the texture. n=16 for a smoother silhouette.
HP = [(1.750, .028, .038, -.030), (1.765, .055, .062, -.020), (1.790, .076, .082, -.010), (1.830, .088, .092, -.004),
      (1.875, .094, .098, -.002), (1.905, .096, .101, -.006), (1.945, .093, .098, -.002), (1.980, .074, .082, .003),
      (2.000, .036, .046, .005)]
HN = 16
def headp(z):
    zs = [h[0] for h in HP]
    return tuple(float(np.interp(z, zs, [h[i] for h in HP])) for i in (1, 2, 3))
head_faces = loft(HP, "face", n=HN)
# nose (wedge) + ears
yf = -0.094
t, bl, br, tip = (bm.verts.new(c) for c in ((0, yf, 1.88), (-.015, yf, 1.822), (.015, yf, 1.822), (0, yf - .030, 1.828)))
nose = [bm.faces.new(f) for f in ((tip, bl, br), (t, bl, tip), (t, tip, br), (t, br, bl))]
for f in nose: f.material_index = MI["face"]
bmesh.ops.recalc_face_normals(bm, faces=nose)
NOSE = set(f.index for f in nose)
for s in (-1, 1):
    loft([(1.84, .006, .016), (1.865, .009, .022), (1.90, .008, .020), (1.915, .004, .012)], "face", x=s * .098, y=.006, n=8)

# Face UVs: planar front projection (face painted on the texture); everything behind the face uses a plain skin patch.
FX, FZ0, FZS = 0.24, 1.72, 0.30
for f in bm.faces:
    if f.material_index == MI["face"]:
        behind = f.index in NOSE or sum(v.co.y for v in f.verts) / len(f.verts) > 0.0
        for l in f.loops:
            c = l.vert.co
            l[UV].uv = ((0.5, 0.97) if f.index in NOSE else (0.02, 0.5)) if behind else (0.5 + c.x / FX, (c.z - FZ0) / FZS)

# ------------------------------------------------------------------ hair: volumetric shell + 3D locks (no cards)
def hairline(a):                                          # height of the hairline by angle (270 deg = straight ahead)
    d = abs((math.degrees(a) - 270 + 180) % 360 - 180)
    return float(np.interp(d, [0, 35, 60, 90, 130, 180], [1.960, 1.950, 1.935, 1.915, 1.870, 1.800]))
TOPZ = 2.05
import random
rnd = random.Random(7)
rows = []
T = [0, .12, .28, .45, .62, .76, .86, .93, .975, 1.0]
for tj in T:
    row = []
    for i in range(HN):
        a = (i + .5) * 2 * math.pi / HN
        hl = hairline(a); z = hl + tj * (TOPZ - hl)
        rx, ry, cy = headp(z)
        k = 1 / math.cos(math.pi / HN)
        sc = float(np.interp(tj, [0, .76, .86, .93, .975, 1.0], [1, 1, .93, .8, .6, .3]))   # rows close into a rounded dome
        jit = 1 + (rnd.random() - .5) * (.06 if 0 < tj < 1 else 0)
        row.append(Vector(((rx * 1.10 * jit + .008) * k * sc * math.cos(a), cy + (ry * 1.10 * jit + .008) * k * sc * math.sin(a), z)))
    rows.append(row)
loft_pts(rows, "hair_dark", tile=(3, 1), cap_bottom=False)   # darker undercoat; lighter locks go on top

def smooth_path(path, sub=3):
    """Catmull-Rom resample so locks bend smoothly instead of kinking."""
    P = [Vector(p) for p in path]; P = [P[0]] + P + [P[-1]]; out = []
    for i in range(1, len(P) - 2):
        for t in (j / sub for j in range(sub)):
            out.append(0.5 * ((2 * P[i]) + (-P[i-1] + P[i+1]) * t + (2*P[i-1] - 5*P[i] + 4*P[i+1] - P[i+2]) * t*t
                              + (-P[i-1] + 3*P[i] - 3*P[i+1] + P[i+2]) * t**3))
    out.append(P[-2])
    return out

hr = random.Random(11)
def lock(path, r0, r1=0.007, n=6, flat=0.7, mat="hair", wob=0.004):
    """A clump of hair: tapered, slightly wobbly tube with its own streak offset in the texture."""
    pts = smooth_path([(x + hr.uniform(-wob, wob), y + hr.uniform(-wob, wob), z) for x, y, z in path], 2)
    radii = [r0 * (1 - (i / (len(pts) - 1)) ** 1.1) + r1 for i in range(len(pts))]
    uo = hr.random()
    for f in tube(pts, radii, mat, n=n, flat=flat):
        for l in f.loops: l[UV].uv = (l[UV].uv[0] + uo, l[UV].uv[1])

# crown: clumps that sweep over the top and flow down the back as one continuous curtain
for x in (-.075, -.05, -.025, 0.0, .025, .05, .075):
    lock([(x, -.075, 2.03), (x * 1.05, -.01, 2.065), (x * 1.15, .06, 2.05), (x * 1.2, .108, 1.975), (x * 1.15, .122, 1.89),
          (x * 1.1, .126, 1.82)], .042, flat=.9)
# swept fringe: clumps fall over the forehead and sweep toward the viewer's left, tips at different heights
for i, (x, tipz) in enumerate(((.075, 1.955), (.045, 1.935), (.015, 1.915), (-.015, 1.925), (-.045, 1.90), (-.075, 1.935))):
    lock([(x * .7, -.04, 2.04), (x, -.095, 2.03), (x * 1.0 - .014, -.128, 1.985), (x - .028 - .004 * i, -.134, tipz)], .034, flat=.7)
# side locks over the ears (front ones shorter), curved in at the tips
for s_ in (-1, 1):
    for y, endz in ((-.06, 1.905), (-.025, 1.855), (.015, 1.825), (.055, 1.80)):
        lock([(s_ * .090, y, 1.995), (s_ * .106, y, 1.945), (s_ * .108, y + .004, endz + .05), (s_ * .099, y + .012, endz)],
             .022, flat=.75)
# nape: shorter layer on top of the curtain that flicks out at the ends
for x, endz in ((-.07, 1.80), (-.04, 1.77), (-.01, 1.785), (.02, 1.765), (.05, 1.79), (.075, 1.80)):
    lock([(x, .10, 1.92), (x * 1.1, .124, 1.86), (x * 1.1, .132, 1.81), (x * 1.08, .139, endz)], .030, flat=.7)

# ------------------------------------------------------------------ mesh object
mesh = bpy.data.meshes.new("Alex_PS2_Base")
bm.to_mesh(mesh)
tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
bm.free()
assert tris < MAX_TRIS, f"Too many tris: {tris}"
print(f"Alex: {len(mesh.polygons)} faces, {tris} tris")

# ------------------------------------------------------------------ procedural textures (numpy)
def vnoise(w, h, cx, cy, seed):
    g = np.random.default_rng(seed).random((cy + 2, cx + 2))
    xs, ys = np.linspace(0, cx, w, endpoint=False), np.linspace(0, cy, h, endpoint=False)
    x0, y0 = xs.astype(int), ys.astype(int)
    fx, fy = xs - x0, ys - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0][:, x0] * (1 - fx) + g[y0][:, x0 + 1] * fx
    b = g[y0 + 1][:, x0] * (1 - fx) + g[y0 + 1][:, x0 + 1] * fx
    return a * (1 - fy)[:, None] + b * fy[:, None]

def uvgrid(w, h):
    return np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))   # row 0 = v 0 = image bottom (Blender)

def blend(img, mask, col, a=1.0):
    return img * (1 - (mask * a)[..., None]) + np.array(col) * (mask * a)[..., None]

def blob(X, Z, cx, cz, rx, rz, soft=0.35, rot=0.0):
    dx, dz = X - cx, Z - cz
    if rot:
        dx, dz = dx * math.cos(rot) + dz * math.sin(rot), -dx * math.sin(rot) + dz * math.cos(rot)
    return np.clip((1 - np.sqrt((dx / rx) ** 2 + (dz / rz) ** 2)) / soft, 0, 1)

SKIN = (0.80, 0.62, 0.52)
def tex_face():
    w = h = 512
    U, V = uvgrid(w, h)
    X, Z = (U - .5) * FX, FZ0 + V * FZS
    n1, n2 = vnoise(w, h, 24, 24, 1), vnoise(w, h, 96, 96, 2)
    img = np.ones((h, w, 3)) * np.array(SKIN) * (0.94 + 0.08 * n1 + 0.03 * n2)[..., None]
    img = blend(img, np.clip((np.abs(X) - .06) / .04, 0, 1), (.58, .43, .35), .8)       # sides fall into shade
    img = blend(img, np.clip((1.80 - Z) / .06, 0, 1), (.60, .45, .38), .7)              # under the jaw
    img = blend(img, np.clip((Z - 1.93) / .05, 0, 1), (.86, .68, .57), .5)              # forehead light
    for s in (-1, 1):
        img = blend(img, blob(X, Z, s * .052, 1.835, .03, .02, .8), (.78, .45, .42), .35)           # cheeks
        img = blend(img, blob(X, Z, s * .036, 1.875, .036, .022, .7), (.55, .38, .34), .35)          # eye socket
        img = blend(img, blob(X, Z, s * .036, 1.857, .030, .009, .7), (.48, .36, .42), .30)          # under-eye shadow
        e = blob(X, Z, s * .036, 1.875, .0215, .0105, .12)                                           # eye white
        img = blend(img, e, (.92, .92, .90))
        ex = s * .036 + (-s * .0015)
        img = blend(img, blob(X, Z, ex, 1.875, .0102, .0102, .15), (.25, .44, .68))                  # blue iris
        img = blend(img, blob(X, Z, ex, 1.875, .0102, .0102, .15) * (1 - blob(X, Z, ex, 1.875, .0078, .0078, .2)), (.12, .2, .32), .8)
        img = blend(img, blob(X, Z, ex, 1.875, .0045, .0045, .25), (.02, .02, .03))                  # pupil
        img = blend(img, blob(X, Z, ex + s * .003, 1.8795, .0022, .0022, .5), (1, 1, 1), .9)         # catchlight
        lid = np.clip(blob(X, Z, s * .036, 1.8785, .0235, .0125, .2) - blob(X, Z, s * .036, 1.8715, .0235, .0125, .2), 0, 1)
        img = blend(img, lid, (.16, .10, .09), .85)                                                  # upper lid line
        brow = blob(X, Z, s * .038, 1.908 + (abs(X) - .038) * .12, .032, .0055, .5, rot=-s * .12)
        img = blend(img, brow, (.40, .32, .20), .9)                                                  # brows (dark blond)
        img = blend(img, blob(X, Z, s * .010, 1.829, .0042, .0032, .5), (.22, .1, .09), .9)          # nostrils
        img = blend(img, blob(X, Z, s * .019, 1.852, .008, .03, .8), (.5, .36, .3), .25)             # nose side shade
    img = blend(img, blob(X, Z, 0, 1.826, .014, .007, .6), (.9, .72, .62), .25)                      # nose tip light
    img = blend(img, blob(X, Z, 0, 1.783, .028, .0075, .5), (.62, .36, .34), .9)                     # upper lip
    img = blend(img, blob(X, Z, 0, 1.771, .024, .0065, .5), (.68, .42, .39), .9)                     # lower lip
    img = blend(img, blob(X, Z, 0, 1.7775, .027, .0014, .6), (.22, .1, .1), .95)                     # mouth line
    img = blend(img, blob(X, Z, 0, 1.759, .028, .007, .8), (.62, .46, .4), .35)                      # under-lip shade
    img = blend(img, np.clip((n2 - .72) * 4, 0, 1), (.7, .52, .44), .25)                             # pores
    return np.clip(img, 0, 1)

def tex_skin():
    n = vnoise(256, 256, 16, 16, 3)
    return np.ones((256, 256, 3)) * np.array(SKIN) * (0.93 + 0.1 * n)[..., None]

def tex_tee():
    w = h = 256
    U, V = uvgrid(w, h)
    n1, n2, n3 = vnoise(w, h, 8, 8, 4), vnoise(w, h, 32, 32, 5), vnoise(w, h, 6, 6, 6)
    img = np.ones((h, w, 3)) * np.array((.74, .72, .67)) * (0.86 + 0.14 * n1)[..., None]
    img = blend(img, np.clip((n3 - .6) * 3, 0, 1), (.62, .55, .36), .55)                  # sweat blooms
    img = blend(img, np.clip((.25 - n1) * 3, 0, 1) + np.clip((.12 - V) * 4, 0, 1) * .6, (.3, .26, .2), .55)  # dirt, dirty hem
    img = img * (0.96 + 0.04 * np.sin(V * 70 + n2 * 6))[..., None]                         # wrinkles
    return np.clip(img, 0, 1)

def tex_jeans():
    w = h = 256
    U, V = uvgrid(w, h)
    xi, yi = np.arange(w)[None, :] * np.ones((h, 1)), np.arange(h)[:, None] * np.ones((1, w))
    n1, n2 = vnoise(w, h, 8, 8, 7), vnoise(w, h, 5, 5, 8)
    img = np.ones((h, w, 3)) * np.array((.085, .085, .095)) * (0.8 + 0.3 * n1 + .12 * ((xi + yi) % 4 < 2))[..., None]
    img = blend(img, np.clip((n2 - .6) * 3, 0, 1), (.36, .36, .37), .30)                  # fade
    img = blend(img, blob(U, V, .5, .43, .6, .1, .8), (.36, .36, .37), .35)               # knee wear
    img = blend(img, np.clip((.1 - V) * 10, 0, 1) * (0.5 + n1), (.2, .15, .1), .7)        # muddy hem
    return np.clip(img, 0, 1)

def tex_sneaker():
    n = vnoise(128, 128, 8, 8, 9)
    img = np.ones((128, 128, 3)) * np.array((.5, .49, .46)) * (0.75 + 0.35 * n)[..., None]
    U, V = uvgrid(128, 128)
    return np.clip(blend(img, np.clip((.4 - V) * 3, 0, 1), (.24, .19, .13), .55), 0, 1)

def tex_hair(base=(.66, .55, .36), dark=False):
    w, h = 256, 128
    U, V = uvgrid(w, h)
    s = vnoise(w, h, 48, 3, 10)
    img = np.ones((h, w, 3)) * np.array(base) * (0.62 + 0.62 * s)[..., None]          # fine strands run along v
    if not dark:
        img = blend(img, np.clip((s - .75) * 5, 0, 1), (.85, .72, .45), .6)                    # blond highlights
    img = blend(img, np.clip((.3 - V) * 3, 0, 1), (.3, .22, .12), .55)                         # darker roots
    return np.clip(img, 0, 1)

TEX = {"face": tex_face, "skin": tex_skin, "tee": tex_tee, "jeans": tex_jeans, "sneaker": tex_sneaker, "hair": tex_hair, "hair_dark": lambda: tex_hair((.40, .31, .17), True)}
tex_dir = os.path.join(OUT_DIR, "alex_textures"); os.makedirs(tex_dir, exist_ok=True)
for name in MATS:
    m = bpy.data.materials.new("Alex_" + name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 1.0
    try: b.inputs["Specular IOR Level"].default_value = 0.0
    except KeyError: pass
    if name in TEX:
        a = TEX[name]()
        img = bpy.data.images.new("Alex_" + name, a.shape[1], a.shape[0], alpha=False)
        img.pixels.foreach_set(np.dstack([a, np.ones(a.shape[:2])]).astype(np.float32).ravel())
        img.filepath_raw = os.path.join(tex_dir, f"alex_{name}.png"); img.file_format = 'PNG'; img.save(); img.pack()
        tx = m.node_tree.nodes.new("ShaderNodeTexImage"); tx.image = img
        m.node_tree.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    else:
        b.inputs["Base Color"].default_value = (0.32, 0.30, 0.27, 1)                          # sole
    mesh.materials.append(m)

obj = bpy.data.objects.new("Alex_PS2_Base", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
try:
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(65))
except Exception:
    bpy.ops.object.shade_smooth()

out = os.path.join(OUT_DIR, "Alex_PS2_Base.glb")
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True, export_yup=True)
print("Exported:", out)
