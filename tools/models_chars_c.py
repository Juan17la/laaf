"""Characters C: Marcus (the Deacon), The Shepherd, and two Marked townspeople.

Smooth SA-era bodies on the shared segmented rig (tools/rig.py): sculpted skull grids with
nose/brow/cheek relief, 128px painted faces planar-projected onto the head front, capsule
limbs with joint spheres (no gaps when bending), lofted cloth with folds.

Head geometry is built in a canonical space (metres, Head-local, chin ~y 0.035, crown ~y 0.27)
and the face painters work in the same metres, so painted eyes/mouth sit on the sculpted relief.
"""
import math

import build_assets as B
import rig

mix, mul = B.mix, B.mul


def g(t):
    return math.exp(-t * t)


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def lerp_rows(table, y):
    """Linear interpolation in a [(y, a, b, ...), ...] table sorted by y."""
    if y <= table[0][0]:
        return table[0][1:]
    for p, q in zip(table, table[1:]):
        if y <= q[0]:
            t = (y - p[0]) / (q[0] - p[0])
            return tuple(a + (b - a) * t for a, b in zip(p[1:], q[1:]))
    return table[-1][1:]


# ============================================================== face space

FX, FY0, FY1 = 0.08, 0.035, 0.235  # face texture covers x in [-FX, FX], y in [FY0, FY1] (Head-local metres)


def face_uv(p):
    return (clamp(0.5 + p[0] / (2 * FX), 0.004, 0.996), clamp((FY1 - p[1]) / (FY1 - FY0), 0.004, 0.996))


def px_to_face(x, y, size=128):
    return ((x + 0.5) / size - 0.5) * 2 * FX, FY1 - (y + 0.5) / size * (FY1 - FY0)


EYE_X, EYE_Y, BROW_Y, NOSE_Y, MOUTH_Y = 0.031, 0.158, 0.177, 0.118, 0.0845

SKULL = [  # (y, rx, rz, oz): canonical adult skull rings, chin to crown
    (0.03, 0.0, 0.0, 0.04),
    (0.034, 0.02, 0.02, 0.045),
    (0.045, 0.042, 0.05, 0.03),
    (0.06, 0.056, 0.072, 0.016),
    (0.08, 0.064, 0.086, 0.007),
    (0.105, 0.07, 0.094, 0.001),
    (0.135, 0.074, 0.098, -0.002),
    (0.16, 0.077, 0.1, -0.005),
    (0.185, 0.078, 0.102, -0.008),
    (0.21, 0.076, 0.1, -0.011),
    (0.235, 0.068, 0.09, -0.013),
    (0.252, 0.053, 0.071, -0.015),
    (0.264, 0.03, 0.042, -0.016),
    (0.268, 0.0, 0.0, -0.016),
]
HEAD_YS = [0.03, 0.034, 0.045, 0.056, 0.066, 0.076, 0.085, 0.094, 0.103, 0.111, 0.119, 0.128, 0.138, 0.148,
           0.157, 0.166, 0.176, 0.186, 0.198, 0.214, 0.232, 0.248, 0.26, 0.268]


def face_relief(x, y):
    """Forward (+z) displacement of the face front: nose, brow, sockets, cheekbones, lips, chin."""
    ax = abs(x)
    d = 0.0
    if 0.1 < y < 0.182:  # nose: bridge to tip, widening
        t = clamp((0.178 - y) / (0.178 - NOSE_Y))
        h = 0.005 + 0.019 * t ** 1.6 if y >= NOSE_Y else 0.024 * g((NOSE_Y - y) / 0.0075)
        d += h * g(x / (0.0065 + 0.006 * t))
    d += 0.007 * g((ax - 0.014) / 0.006) * g((y - 0.113) / 0.007)  # nose wings
    d += 0.007 * g((y - 0.18) / 0.01) * g(x / 0.06)  # brow ridge
    d -= 0.009 * g((ax - EYE_X) / 0.016) * g((y - EYE_Y) / 0.011)  # eye sockets
    d += 0.006 * g((ax - 0.047) / 0.014) * g((y - 0.135) / 0.014)  # cheekbones
    d += 0.005 * g(x / 0.02) * g((y - 0.086) / 0.009)  # lips
    d -= 0.003 * g(x / 0.018) * g((y - 0.071) / 0.004)  # under the lower lip
    d += 0.006 * g(x / 0.02) * g((y - 0.05) / 0.011)  # chin
    return d


def skull_pt(th, y, grow=0.0, relief=True, table=SKULL):
    rx, rz, oz = lerp_rows(table, y)
    if rx > 0:
        rx, rz = rx + grow, rz + grow
    p = [rx * math.sin(th), y, oz + rz * math.cos(th)]
    if relief and math.cos(th) > 0:
        p[2] += face_relief(p[0], y) * math.cos(th) ** 2
    return tuple(p)


def angles(a0, a1, n, bias=1.0):
    """n+1 angles (radians) from a0 to a1 degrees; bias>1 packs them toward the middle."""
    out = []
    for i in range(n + 1):
        t = 2 * i / n - 1
        t = math.copysign(abs(t) ** bias, t)
        out.append(math.radians((a0 + a1) / 2 + t * (a1 - a0) / 2))
    return out


def skull(m, face_mat, back_mat, relief=True, grow=0.0, table=SKULL):
    """Head: front grid (painted face, planar projection) + back grid (skin/cloth)."""
    front = [[skull_pt(th, y, grow, relief, table) for th in angles(-100, 100, 16, 1.25)] for y in HEAD_YS]
    back = [[skull_pt(th, y, grow, False, table) for th in angles(100, 260, 8)] for y in HEAD_YS]
    m.surface(face_mat, front, uv=face_uv)
    m.surface(back_mat, back)


def hair_cap(m, mat, line, thick=0.01, top=0.0, rows=6, seg=24, lift=None):
    """Hair volume over the skull above hairline y=line(theta_deg); thick(ness) may be a fn of theta."""
    grid = []
    for k in range(rows + 1):
        t = k / rows
        row = []
        for j in range(seg):
            th = 2 * math.pi * j / seg  # increases with j: counter-clockwise from above
            deg = math.degrees(th)
            deg = deg - 360 if deg > 180 else deg
            y0 = line(deg)
            y = y0 + (0.266 - y0) * (1 - (1 - t) ** 1.3)
            tk = thick(deg) if callable(thick) else thick
            grow = tk * (0.25 + 0.75 * min(1.0, t * 3))
            p = skull_pt(th, y, grow, relief=False)
            if k == rows:
                p = (0.0, 0.268 + tk + top, -0.016)
            if lift:
                p = lift(p, deg, t)
            row.append(p)
        grid.append(row)
    m.surface(mat, grid, wrap=True)


def hairline_short(deg):
    a = abs(deg)
    return lerp_rows([(0, 0.21), (40, 0.2), (75, 0.17), (95, 0.125), (120, 0.1), (180, 0.075)], a)[0]


def ears(m, mat, y=0.148, s=1.0):
    for sx in (1, -1):
        rx = lerp_rows(SKULL, y)[0]
        m.ellipsoid(mat, (0.011, 0.029, 0.019), (sx * (rx - 0.003), y, -0.012), (0, sx * -15, sx * -8), seg=8, rings=6)
        m.ellipsoid(mat, (0.006, 0.012, 0.009), (sx * (rx + 0.004), y + 0.004, -0.01), seg=6, rings=4)


def neck(m, mat, r=0.056):
    m.lathe(mat, [(r * 1.06, -0.07), (r, -0.02), (r * 0.92, 0.04), (r * 0.9, 0.1), (0, 0.11)], (0, 0, -0.012),
            scale=(1, 1, 0.94), seg=10)


def shell(m, mat, rows, a0, a1, n, inner=None, fold=None, grow_in=-0.004, bias=1.0):
    """Partial surface of revolution: rows [(y, rx, rz, ox, oz)], angles a0..a1 deg (0 = +Z front, 90 = +X).
    fold(deg, row_index) -> radius multiplier. inner: material for the back side (double-sided cloth)."""
    a0, a1 = min(a0, a1), max(a0, a1)
    ths = angles(a0, a1, n, bias)
    grid = []
    for i, (y, rx, rz, ox, oz) in enumerate(rows):
        row = []
        for th in ths:
            f = fold(math.degrees(th), i) if fold else 1.0
            row.append((ox + rx * f * math.sin(th), y, oz + rz * f * math.cos(th)))
        grid.append(row)
    m.surface(mat, grid[::-1] if rows[0][0] > rows[-1][0] else grid)  # rows must run upward
    if inner:
        gin = []
        for i, (y, rx, rz, ox, oz) in enumerate(rows):
            row = []
            for th in reversed(ths):
                f = (fold(math.degrees(th), i) if fold else 1.0)
                row.append((ox + (rx * f + grow_in) * math.sin(th), y, oz + (rz * f + grow_in) * math.cos(th)))
            gin.append(row)
        m.surface(inner, gin[::-1] if rows[0][0] > rows[-1][0] else gin)


# ============================================================== textures

def tex(name, size=64):
    def deco(fn):
        B.TEXTURES[name] = fn
        if size != 64:
            B.TEX_SIZE[name] = size
        return fn
    return deco


def veil_eye(u, v, cx, cy, w, h):
    """The Veil's Eye symbol: almond ring + pupil, in 0..1 texture space."""
    dx, dy = (u - cx) / w, (v - cy) / h
    lid = 1 - dx * dx
    if lid <= 0:
        return False
    ring = abs(dy) < lid and not (abs(dy) < lid - 0.35 and abs(dx) < 0.86)
    return ring or (u - cx) ** 2 + ((v - cy) * 1.0) ** 2 < (0.38 * h) ** 2


def face(X, Y, a, r, skin, iris, brow, lips, hairline=0.21, hair=None, stubble=0.0, age=0.0):
    """Realistic painted face in Head-local metres (see FX/FY): shading follows the sculpted relief."""
    c = mul(skin, 0.9 + 0.12 * a + 0.03 * r)
    ax = abs(X)
    c = mul(c, 1 - 0.25 * clamp((ax - 0.055) / 0.03))  # side planes
    warm = (skin[0] * 1.08, skin[1] * 0.8, skin[2] * 0.78)
    c = mix(c, warm, 0.35 * g((ax - 0.045) / 0.018) * g((Y - 0.12) / 0.018) + 0.3 * g(X / 0.01) * g((Y - 0.12) / 0.008))
    c = mul(c, 1 + 0.1 * g(X / 0.005) * (0.122 < Y < 0.172))  # nose bridge highlight
    c = mul(c, 1 - 0.18 * g((ax - 0.012) / 0.004) * (0.113 < Y < 0.165))  # nose sides
    c = mul(c, 1 - 0.25 * g(X / 0.013) * g((Y - 0.105) / 0.003))  # under the nose
    c = mul(c, 1 - 0.07 * (ax < 0.005 and 0.092 < Y < 0.104))  # philtrum
    c = mul(c, 1 - 0.2 * g(X / 0.014) * g((Y - 0.071) / 0.004))  # under the lip
    c = mul(c, 1 - 0.25 * clamp((0.05 - Y) / 0.015))  # jaw underside
    for sx in (1, -1):  # nasolabial folds
        d = B.seg_dist(X, Y, sx * 0.016, 0.112, sx * 0.03, 0.079)
        c = mul(c, 1 - (0.12 + 0.2 * age) * g(d / 0.0015))
    if stubble:
        zone = clamp((0.108 - Y) / 0.01) * (1 - 0.8 * g(X / 0.026) * g((Y - MOUTH_Y) / 0.006))
        zone = max(zone, clamp((ax - 0.062) / 0.006) * (Y < 0.14))
        c = mix(c, mul(hair, 1.4), zone * stubble * (0.35 + 0.35 * (r < 0.5)))
    if age:
        for ly in (0.198, 0.206, 0.214):
            if abs(Y - ly - 0.002 * math.sin(X * 90)) < 0.0009 and ax < 0.045:
                c = mul(c, 1 - 0.3 * age)
    # mouth
    t = X / 0.021
    if abs(t) < 1:
        y0 = MOUTH_Y - 0.0018 * t * t
        k = 1 - t ** 4
        if y0 < Y < y0 + 0.0042 * k:
            c = mix(c, mul(lips, 0.8), 0.75)
        elif y0 - 0.0058 * k < Y <= y0:
            c = mix(c, mul(lips, 1.05 + 0.2 * (Y > y0 - 0.002)), 0.7)
        if abs(Y - y0) < 0.0009:
            c = mul(lips, 0.35)
    for ex in (EYE_X, -EYE_X):  # sockets, eyes, brows
        dx, dy = X - ex, Y - EYE_Y
        c = mul(c, 1 - 0.3 * g(dx / 0.021) * g((dy - 0.002) / 0.012))
        if age:
            c = mul(c, 1 - 0.2 * age * g(dx / 0.012) * g((dy + 0.011) / 0.003))  # bags
        c = mul(c, 1 - 0.1 * g(dx / 0.012) * g((dy + 0.0075) / 0.0015))
        tt = dx / 0.0125
        if abs(tt) < 1:
            inner = tt * math.copysign(1, ex)  # -1 at the nose side
            top = 0.0055 * (1 - tt * tt) + 0.0008 * inner
            bot = -0.0035 * (1 - tt * tt)
            if bot < dy < top:
                d2 = dx * dx + (dy - 0.0005) ** 2
                if d2 < 0.0021 ** 2:
                    return (0.02, 0.02, 0.02)
                if d2 < 0.0054 ** 2:
                    return mul(iris, 0.75 + 0.4 * a) if dy < top - 0.0012 else mul(iris, 0.45)
                e = mul((0.72, 0.68, 0.62), 0.9 + 0.1 * r)
                return mul(e, 0.7) if dy > top - 0.0012 or abs(tt) > 0.8 else e
            if top <= dy < top + 0.0017:
                return mul(brow, 0.5)  # lash line
            if top + 0.0017 <= dy < top + 0.0048:
                c = mul(c, 0.82)  # lid crease
            if bot - 0.001 < dy <= bot:
                c = mul(c, 0.78)
        bt = dx / 0.02 * math.copysign(1, ex)  # -1 inner end .. 1 outer end
        if abs(bt) < 1:
            by = BROW_Y + 0.0045 * (1 - (bt - 0.15) ** 2) - 0.002 * bt
            th = 0.0034 * (1.15 - 0.55 * max(0.0, bt))
            if abs(Y - by) < th:
                c = mix(c, mul(brow, 0.8 + 0.4 * r), 0.9)
    for sx in (1, -1):  # nostrils
        if ((X - sx * 0.0075) / 0.0045) ** 2 + ((Y - 0.1115) / 0.0022) ** 2 < 1:
            c = mul(c, 0.35)
    if hair and Y > hairline + 0.003 * math.sin(X * 400 + a * 5):
        c = mul(hair, 0.75 + 0.4 * a)
    return c


def face_tex(name, **kw):
    @tex(name, 128)
    def _(x, y, a, b, r):
        X, Y = px_to_face(x, y)
        return face(X, Y, a, r, **kw)


face_tex("cc_marcus_face", skin=(0.6, 0.44, 0.35), iris=(0.2, 0.14, 0.09), brow=(0.09, 0.07, 0.05),
         lips=(0.48, 0.28, 0.25), hair=(0.09, 0.07, 0.05), hairline=0.205, stubble=0.55, age=0.35)


@tex("cc_shep_face", 128)
def _(x, y, a, b, r):
    """Old face lost in the hood: shadowed brow, two glints, white beard below."""
    X, Y = px_to_face(x, y)
    c = face(X, Y, a, r, (0.56, 0.47, 0.42), (0.5, 0.46, 0.36), (0.6, 0.58, 0.54), (0.36, 0.24, 0.23), age=1.0)
    for sx in (1, -1):  # sunken cheeks
        c = mul(c, 1 - 0.25 * g((X - sx * 0.052) / 0.012) * g((Y - 0.1) / 0.02))
    c = mix(c, (0.01, 0.01, 0.012), clamp((Y - 0.1) / 0.08) * 0.9 + 0.5 * clamp((abs(X) - 0.04) / 0.03))  # hood shadow
    for ex in (EYE_X, -EYE_X):
        if ((X - ex) / 0.004) ** 2 + ((Y - EYE_Y) / 0.0022) ** 2 < 1:
            return (0.8, 0.72, 0.5)
    return c


@tex("cc_mask_burlap", 128)
def _(x, y, a, b, r):
    X, Y = px_to_face(x, y)
    weave = 0.82 + 0.18 * ((x // 2 + y // 2) % 2)
    c = mul((0.46, 0.37, 0.24), weave * (0.7 + 0.4 * a) - (0.2 if b > 0.63 else 0))
    for ex, ey, w, h in ((EYE_X + 0.002, EYE_Y + 0.004, 0.015, 0.009), (-EYE_X, EYE_Y - 0.004, 0.012, 0.011)):
        d = ((X - ex) / w) ** 2 + ((Y - ey) / h) ** 2
        if d < 1:
            return (0.01, 0.008, 0.006)  # uneven cut eye holes
        if d < 1.8:
            c = mul(c, 0.55)
            if (x + y) % 3 == 0:
                return (0.12, 0.07, 0.04)  # crude stitching
    t = X / 0.03
    if abs(t) < 1:
        my = MOUTH_Y + 0.004 * t
        if abs(Y - my) < 0.0012:
            return (0.1, 0.06, 0.04)
        if abs(Y - my) < 0.007 and x % 5 == 0:
            return (0.14, 0.07, 0.04)  # sewn mouth
    u, v = x / 128, y / 128
    if veil_eye(u, v, 0.5, 0.13, 0.26, 0.08):
        return mul((0.5, 0.05, 0.04), 0.7 + 0.4 * a)
    if 0.17 < v and x % 11 == 5 and abs(u - 0.5) < 0.25 and v < 0.25 + 0.35 * b:
        return mul((0.4, 0.05, 0.04), 0.8)  # paint runs
    return c


@tex("cc_mask_porcelain", 128)
def _(x, y, a, b, r):
    X, Y = px_to_face(x, y)
    c = mul((0.84, 0.81, 0.75), 0.88 + 0.12 * a)
    c = mul(c, 1 - 0.3 * clamp((abs(X) - 0.05) / 0.03))
    crack = [(0.012, 0.24), (-0.004, 0.2), (0.014, 0.17), (0.006, 0.13), (0.02, 0.1)]
    if min(B.seg_dist(X, Y, *p, *q) for p, q in zip(crack, crack[1:])) < 0.0009 + 0.0006 * r:
        return (0.2, 0.17, 0.15)  # one long crack down the brow
    c = mix(c, (0.75, 0.35, 0.35), 0.35 * g((abs(X) - 0.045) / 0.012) * g((Y - 0.118) / 0.012))  # painted rouge
    for ex in (EYE_X, -EYE_X):
        dx, dy = X - ex, Y - EYE_Y
        tt = dx / 0.013
        if abs(tt) < 1 and -0.004 * (1 - tt * tt) < dy < 0.0045 * (1 - tt * tt):
            return (0.0, 0.0, 0.0)  # eye slits
        if abs(tt) < 1.15 and abs(dy - 0.006 * (1 - tt * tt)) < 0.0012:
            return (0.1, 0.08, 0.08)  # painted lashes
        by = BROW_Y + 0.008 - 0.004 * abs(tt)
        if abs(tt) < 1.2 and abs(Y - by) < 0.001:
            return (0.25, 0.2, 0.18)  # thin arched brows, too high
        if dy < -0.006 and abs(dx - 0.0015 * math.sin(Y * 500)) < 0.0012 and Y > 0.06:
            return (0.28, 0.24, 0.22)  # tear stains
    t = X / 0.012
    if abs(t) < 1 and abs(Y - MOUTH_Y - 0.0015 * t * t) < 0.0035 * (1 - t * t) + 0.0008:
        return (0.42, 0.06, 0.07)  # small painted lips, a smile that is not a smile
    if veil_eye(x / 128, y / 128, 0.5, 0.14, 0.14, 0.05):
        return (0.55, 0.04, 0.03)
    return c


@tex("cc_skin")
def _(x, y, a, b, r):
    return mul((1, 1, 1), 0.88 + 0.12 * a + 0.03 * r)


@tex("cc_hair")
def _(x, y, a, b, r):
    return mul((1, 1, 1), 0.7 + 0.3 * a + 0.12 * math.sin(x * 1.3 + a * 14) + 0.12 * r)


@tex("cc_wool")
def _(x, y, a, b, r):
    v = 0.75 + 0.15 * ((x + y) % 3 == 0) + 0.2 * a + 0.05 * r
    return mul((1, 1, 1), v * (1 - 0.3 * clamp((b - 0.6) * 8)))


@tex("cc_coat")
def _(x, y, a, b, r):
    return mul((1, 1, 1), (0.85 + 0.12 * ((x + y) % 4 < 2)) * (0.8 + 0.25 * a) + 0.04 * r)


@tex("cc_robe")
def _(x, y, a, b, r):
    v = (0.88 + 0.06 * (y % 2) + 0.05 * ((x * 3 + y) % 7 == 0)) * (0.65 + 0.45 * a)
    return mul((1, 1, 1), v * (1 - 0.25 * clamp((b - 0.6) * 6)))  # soft grime


@tex("cc_plaid")
def _(x, y, a, b, r):
    bx, by = (x // 8) % 2, (y // 8) % 2
    c = (0.45, 0.1, 0.08) if bx + by == 0 else (0.08, 0.07, 0.07) if bx + by == 2 else (0.26, 0.08, 0.07)
    if x % 16 == 3 or y % 16 == 3:
        c = (0.55, 0.45, 0.3)
    return mul(c, 0.7 + 0.4 * a - (0.2 if b > 0.64 else 0))


@tex("cc_denim")
def _(x, y, a, b, r):
    v = 0.8 + 0.2 * ((x + y) % 4 < 2)
    return mul((0.2, 0.25, 0.36), v * (0.7 + 0.4 * a) + (0.15 if b > 0.66 else 0))


@tex("cc_leather")
def _(x, y, a, b, r):
    return mul((0.2, 0.13, 0.08), 0.6 + 0.6 * a + 0.1 * r)


@tex("cc_knit")
def _(x, y, a, b, r):
    return mul((1, 1, 1), (0.9 + 0.1 * (x % 3 == 0)) * (0.78 + 0.3 * a))


@tex("cc_dress")
def _(x, y, a, b, r):
    c = mul((0.52, 0.5, 0.42), 0.75 + 0.3 * a)
    if (x % 12 - 6) ** 2 + (y % 12 - 6 + (x // 12) * 5 % 8 - 4) ** 2 < 3:
        c = mix(c, (0.42, 0.2, 0.22), 0.7)  # faded flowers
    return mul(c, 1 - 0.3 * clamp((b - 0.6) * 6))


@tex("cc_eyeband", 64)
def _(x, y, a, b, r):
    u, v = x / 64, y / 64
    if veil_eye(u, v, 0.5, 0.5, 0.36, 0.2):
        return (0.03, 0.03, 0.03)
    return mul((0.5, 0.06, 0.05), 0.7 + 0.4 * a)


@tex("cc_stole", 64)
def _(x, y, a, b, r):
    u, v = x / 64, y / 64
    if u < 0.12 or u > 0.88:
        return mul((0.55, 0.45, 0.2), 0.7 + 0.4 * a)  # tarnished gold trim
    if veil_eye(u, v, 0.5, 0.3, 0.3, 0.12):
        return mul((0.6, 0.5, 0.25), 0.8 + 0.2 * a)
    return mul((0.36, 0.05, 0.05), 0.65 + 0.45 * a)


@tex("cc_ledger", 64)
def _(x, y, a, b, r):
    if x < 6:
        return (0.1, 0.06, 0.04)
    if veil_eye(x / 64, y / 64, 0.55, 0.45, 0.25, 0.1):
        return (0.5, 0.42, 0.2)
    return mul((0.26, 0.1, 0.07), 0.6 + 0.5 * a)


def MAT(name, tex_, color=(1, 1, 1), scale=0.5, **kw):
    B.MATS[name] = B.M(tex_, color, scale, **kw)


MAT("cc_marcus_face", "cc_marcus_face")
MAT("cc_shep_face", "cc_shep_face")
MAT("cc_mask_burlap", "cc_mask_burlap")
MAT("cc_mask_porcelain", "cc_mask_porcelain", rough=0.5)
MAT("cc_eyeband", "cc_eyeband", fit=True)
MAT("cc_stole", "cc_stole", fit=True)
MAT("cc_ledger", "cc_ledger", fit=True)
MAT("cc_skin_marcus", "cc_skin", (0.6, 0.44, 0.35), 0.2)
MAT("cc_skin_old", "cc_skin", (0.56, 0.47, 0.42), 0.2)
MAT("cc_skin_pale", "cc_skin", (0.56, 0.45, 0.39), 0.2)
MAT("cc_hair_dark", "cc_hair", (0.09, 0.07, 0.05), 0.08)
MAT("cc_hair_brown", "cc_hair", (0.24, 0.16, 0.1), 0.1)
MAT("cc_hair_white", "cc_hair", (0.5, 0.48, 0.45), 0.2)
MAT("cc_coat_black", "cc_coat", (0.05, 0.047, 0.045), 0.3)
MAT("cc_shirt_black", "cc_wool", (0.025, 0.025, 0.03), 0.3)
MAT("cc_collar", "cc_skin", (0.85, 0.84, 0.8))
MAT("cc_trousers", "cc_wool", (0.13, 0.13, 0.14), 0.4)
MAT("cc_boot", "cc_leather", (0.6, 0.6, 0.6), 0.3)
MAT("cc_sole", "cc_leather", (0.25, 0.25, 0.25), 0.3)
MAT("cc_leather", "cc_leather", scale=0.3)
MAT("cc_robe", "cc_robe", (0.17, 0.15, 0.14), 0.5)
MAT("cc_robe_in", "cc_robe", (0.04, 0.035, 0.035), 0.5)
MAT("cc_rope", "cc_hair", (0.45, 0.38, 0.25), 0.2)
MAT("cc_plaid", "cc_plaid", scale=0.35)
MAT("cc_denim", "cc_denim", scale=0.4)
MAT("cc_burlap", "cc_wool", (0.34, 0.27, 0.17), 0.3)
MAT("cc_cardigan", "cc_knit", (0.35, 0.3, 0.24), 0.3)
MAT("cc_dress", "cc_dress", scale=0.45)
MAT("cc_stocking", "cc_skin", (0.08, 0.07, 0.07))
MAT("cc_apron", "cc_wool", (0.34, 0.32, 0.28), 0.4)
MAT("cc_wood", "planks" if "planks" in B.TEXTURES else "cc_leather", (0.8, 0.7, 0.6), 0.5)


# ============================================================== body parts

TORSO_M = [  # Spine-local (y, rx, rz, ox, oz): adult male, clothed
    (-0.1, 0.15, 0.105, 0, 0.0),
    (0.0, 0.148, 0.102, 0, 0.0),
    (0.12, 0.152, 0.105, 0, 0.004),
    (0.24, 0.166, 0.114, 0, 0.012),
    (0.34, 0.178, 0.118, 0, 0.012),
    (0.42, 0.188, 0.108, 0, 0.0),
    (0.47, 0.18, 0.095, 0, -0.006),
    (0.51, 0.135, 0.08, 0, -0.01),
    (0.545, 0.08, 0.064, 0, -0.012),
    (0.575, 0.06, 0.052, 0, -0.012),
]
PELVIS_M = [  # Hips-local
    (-0.2, 0.0, 0.0, 0, 0.0),
    (-0.19, 0.08, 0.06, 0, 0.0),
    (-0.15, 0.145, 0.1, 0, 0.0),
    (-0.08, 0.172, 0.113, 0, 0.0),
    (0.0, 0.168, 0.11, 0, 0.0),
    (0.08, 0.155, 0.104, 0, 0.0),
    (0.15, 0.15, 0.104, 0, 0.0),
]


def sized(rows, sx=1.0, sz=1.0, grow=0.0):
    return [(y, rx * sx + (grow if rx else 0), rz * sz + (grow if rz else 0), ox, oz) for y, rx, rz, ox, oz in rows]


def body(m, top, pelvis, torso=TORSO_M, hips=PELVIS_M, power=2.6):
    m.use("Hips")
    m.loft(pelvis, hips, seg=16, power=power)
    m.use("Spine")
    m.loft(top, torso, seg=18, power=power)


def arm(m, side, s, mat, skin, r=0.047, fore_mat=None, cuff=None, sleeve=1.0, grip=""):
    """Upper arm + forearm capsules, deltoid and elbow spheres over the pivots; hand."""
    m.use("UpperArm" + side)
    m.capsule(mat, r * 1.15 * sleeve, r * 0.88 * sleeve, 0.27, (0, -0.02, 0), seg=10, squash=(1, 1.08))
    m.use("Forearm" + side)
    fm = fore_mat or mat
    rr = r * 0.9 * sleeve
    m.ellipsoid(fm, (rr, rr, rr), seg=10, rings=6)
    m.lathe(fm, [(0, -0.25), (rr * 0.66, -0.245), (rr * 0.7, -0.2), (rr * 1.02, -0.07), (rr, -0.02), (0, 0.01)],
            seg=10, scale=(1, 1, 1.08))
    if cuff:
        m.lathe(cuff, [(rr * 0.7, -0.255), (rr * 0.78, -0.25), (rr * 0.8, -0.215), (rr * 0.7, -0.21)], seg=10)
    hand(m, side, s, skin, side in grip)


def hand(m, side, s, skin, grip=False):
    """Palm faces the thigh (-s X); fingers grouped in one curled block, thumb forward."""
    m.use("Hand" + side)
    m.ellipsoid(skin, (0.02, 0.05, 0.04), (-s * 0.002, -0.04, 0.002), seg=8, rings=5)  # palm
    curl = 35 if grip else 14
    m.capsule(skin, 0.017, 0.014, 0.04, (-s * 0.004, -0.082, 0.002), (0, 0, -s * curl), seg=6, squash=(0.8, 2.3))
    m.capsule(skin, 0.011, 0.01, 0.04, (-s * 0.008, -0.03, 0.03), (-45, 0, -s * 18), seg=5)  # thumb


def shoe(m, mat, sole, length=0.26, width=0.052, heel_h=0.0, boot=0.0):
    """Shoe on the Foot joint (ankle pivot, ground at y=-0.05): lofted upper along +Z, sole, ankle."""
    z0, z1 = -0.065, length - 0.065
    secs = [  # (z, rx, ry, ox, oy): ry spans height, oy centre height (Foot-local y)
        (z0, 0.0, 0.0, 0, -0.01),
        (z0 + 0.008, width * 0.72, 0.04, 0, -0.012),
        (z0 + 0.04, width * 0.86, 0.045, 0, -0.008),
        (z0 + 0.1, width * 0.9, 0.042, 0, -0.012),
        (z1 - 0.07, width, 0.032, 0, -0.022),
        (z1 - 0.03, width * 0.92, 0.026, 0, -0.026),
        (z1 - 0.008, width * 0.62, 0.02, 0, -0.03),
        (z1, 0.0, 0.0, 0, -0.03),
    ]
    m.loft(mat, [(z, rx, ry, ox, -oy) for z, rx, ry, ox, oy in secs], rot=(90, 0, 0), seg=12, power=2.4)
    m.loft(sole, [(z0 - 0.004, 0.0, 0.0, 0, 0.045), (z0 + 0.002, width * 0.8, 0.008, 0, 0.045),
                  (z0 + 0.1, width * 0.92, 0.008, 0, 0.045), (z1 - 0.04, width * 1.04, 0.007, 0, 0.045),
                  (z1 + 0.004, width * 0.6, 0.007, 0, 0.045), (z1 + 0.008, 0.0, 0.0, 0, 0.045)],
           rot=(90, 0, 0), seg=10, power=3)
    m.lathe(mat, [(0.042, -0.04), (0.046 + boot * 0.005, 0.0), (0.044 + boot * 0.006, 0.03 + boot),
                  (0.04 + boot * 0.006, 0.045 + boot)], (0, 0, -0.005), seg=10, scale=(1, 1, 1.1))


def leg(m, side, s, mat, shoe_mat, sole="cc_sole", r=0.084, shin_mat=None, boot=0.0):
    m.use("Thigh" + side)
    m.capsule(mat, r, r * 0.68, 0.38, (0, 0.01, 0), seg=10, squash=(0.95, 1.05))
    m.use("Shin" + side)
    sm = shin_mat or mat
    kr = r * 0.66
    m.ellipsoid(mat, (kr, kr, kr * 1.05), seg=10, rings=6)
    m.lathe(sm, [(0, -0.41), (kr * 0.6, -0.4), (kr * 0.68, -0.34), (kr * 0.95, -0.2), (kr * 1.06, -0.11),
                 (kr * 0.98, -0.03), (0, 0.02)], (0, 0, -0.004), seg=10, scale=(1, 1, 1.06))
    m.use("Foot" + side)
    shoe(m, shoe_mat, sole, boot=boot)


def half_skirts(m, mat, inner, rows, folds=4, amp=0.03, seg=10, cx=0.1):
    """Long coat/robe/skirt split in two halves, one per thigh, meeting at the centre line: legs still walk.
    rows: Thigh-local [(y, rx, rz)] centred on the body mid-line; folds deepen toward the hem."""
    n = len(rows) - 1
    for side, s in (("L", 1), ("R", -1)):
        m.use("Thigh" + side)
        a0, a1 = (0, 180) if s > 0 else (180, 360)
        fold = lambda deg, i: 1 + amp * (i / n) ** 1.2 * math.sin(math.radians(deg) * folds * 2 + s)
        shell(m, mat, [(y, rx, rz, -s * cx, 0.0) for y, rx, rz in rows], a0, a1, seg, inner=inner, fold=fold)


def eye_band(m, joint, y, r):
    m.use(joint)
    m.lathe("cc_eyeband", [(r, y - 0.045), (r * 1.02, y), (r, y + 0.045)], seg=10)


# ============================================================== characters

def char_marcus():
    """Marcus Hale, the Deacon: big, black long coat over clerical shirt, sledgehammer + lantern."""
    m = rig.skeleton("char_marcus", 1.04)
    with m.push(scale=(1.04,) * 3):
        m.use("Head")
        neck(m, "cc_skin_marcus", 0.062)
        with m.push((0, 0.004, 0), scale=(1.06, 1.02, 1.02)):
            skull(m, "cc_marcus_face", "cc_skin_marcus")
            ears(m, "cc_skin_marcus")
            hair_cap(m, "cc_hair_dark", hairline_short, lambda d: 0.006 + 0.006 * (abs(d) < 60))
        body(m, "cc_coat_black", "cc_coat_black", sized(TORSO_M, 1.1, 1.08), sized(PELVIS_M, 1.1, 1.1, 0.01))
        m.use("Spine")
        # shirt showing in the open coat front + lapels
        shell(m, "cc_shirt_black", [(y, rx * 1.1 + 0.002, rz * 1.08 + 0.002, 0, oz) for y, rx, rz, _, oz in TORSO_M[2:7]],
              -16, 16, 4)
        for sgn in (1, -1):
            rows = [(y, rx * 1.1 + 0.006, rz * 1.08 + 0.008, 0, oz) for y, rx, rz, _, oz in TORSO_M[2:7]]
            shell(m, "cc_coat_black", rows, sgn * 14, sgn * 30, 2)
            for y in (0.06, 0.18):
                m.ellipsoid("iron", (0.011, 0.011, 0.006), (sgn * 0.07, y, 0.116), seg=6, rings=4)
        m.lathe("cc_collar", [(0.07, 0.535), (0.068, 0.56), (0.063, 0.585), (0.06, 0.588)], (0, 0, -0.01), seg=12)
        m.box("cc_collar", (0.028, 0.026, 0.008), (0, 0.56, 0.057))  # the white tab
        shell(m, "cc_coat_black", [(0.49, 0.16, 0.1, 0, -0.012), (0.56, 0.1, 0.085, 0, -0.012),
                                   (0.61, 0.098, 0.085, 0, -0.016)], 60, 300, 10, inner="cc_robe_in")  # turned-up collar
        m.use("Hips")
        m.lathe("cc_leather", [(0.172, 0.05), (0.176, 0.07), (0.172, 0.09)], scale=(1.1, 1, 0.72), seg=16)  # belt
        m.box("metal", (0.05, 0.035, 0.012), (0, 0.07, 0.128))
        m.cyl("cc_leather", 0.006, 0.006, 0.08, (-0.19, -0.03, 0.04), seg=4, caps=False)  # the church hand bell
        m.lathe("metal", [(0.042, -0.1), (0.035, -0.085), (0.022, -0.05), (0.01, -0.04), (0, -0.038)],
                (-0.19, -0.0, 0.04), seg=10)
        half_skirts(m, "cc_coat_black", "cc_robe_in",
                    [(0.08, 0.19, 0.128), (-0.1, 0.2, 0.14), (-0.3, 0.215, 0.15), (-0.5, 0.23, 0.16), (-0.62, 0.235, 0.166)],
                    folds=3, amp=0.04)
        rig.mirror(lambda side, s: arm(m, side, s, "cc_coat_black", "cc_skin_marcus", 0.052, cuff="cc_shirt_black", grip="LR"))
        rig.mirror(lambda side, s: leg(m, side, s, "cc_trousers", "cc_boot", r=0.088, boot=0.03))
        # sledgehammer in the right hand, head down
        m.use("HandR")
        m.lathe("cc_wood", [(0.017, -0.8), (0.02, -0.4), (0.021, 0.05), (0.018, 0.07)], (0, 0, 0.012), seg=8)
        m.lathe("cc_leather", [(0.024, -0.16), (0.025, -0.02), (0.024, 0.0)], (0, 0, 0.012), seg=8)
        m.loft("rust", [(-0.13, 0.0, 0.0), (-0.128, 0.045, 0.052), (-0.11, 0.055, 0.062), (0.11, 0.055, 0.062),
                        (0.128, 0.045, 0.052), (0.13, 0.0, 0.0)], (0, -0.74, 0.012), (0, 0, 0), seg=10, power=4)
        m.use("HandL")
        m.lathe("cc_collar", [(0.02, -0.105), (0.02, -0.098)], (-0.004, 0, 0), (0, 0, 90), seg=8)  # wedding ring
        # storm lantern in the left hand
        m.cyl("iron", 0.004, 0.004, 0.11, (0, -0.2, 0.0), seg=3, caps=False)
        with m.push((0, -0.36, 0)):
            m.lathe("iron", [(0.075, -0.03), (0.075, 0.0), (0.06, 0.012), (0, 0.014)], seg=10)
            m.lathe("bulb", [(0.045, 0.0), (0.056, 0.05), (0.052, 0.1), (0.04, 0.12)], seg=10)
            m.lathe("iron", [(0.05, 0.12), (0.06, 0.135), (0.035, 0.16), (0.012, 0.17), (0, 0.172)], seg=10)
            for k in range(4):
                a = k * math.pi / 2 + 0.78
                m.cyl("iron", 0.005, 0.005, 0.13, (0.063 * math.cos(a), 0.0, 0.063 * math.sin(a)), seg=4, caps=False)
    return m


def char_shepherd():
    """The Shepherd: old, hunched, deep hood, ashen robe with the Veil's stole; ledger + brand iron."""
    m = rig.skeleton("char_shepherd", 0.96, {"Head": (0, 0.53, 0.05)})
    with m.push(scale=(0.96,) * 3):
        m.use("Head")
        neck(m, "cc_skin_old", 0.05)
        with m.push((0, 0, 0), (6, 0, 0), (0.96, 1.0, 0.98)):
            skull(m, "cc_shep_face", "cc_robe_in")
            # beard: a hanging wedge + a mustache over the mouth
            m.loft("cc_hair_white", [(-0.05, 0.0, 0.0, 0, 0.05), (-0.035, 0.016, 0.01, 0, 0.052),
                                      (0.01, 0.038, 0.026, 0, 0.05), (0.055, 0.056, 0.04, 0, 0.042),
                                      (0.1, 0.066, 0.048, 0, 0.028), (0.108, 0.02, 0.03, 0, 0.05)], seg=10)
            # hood: open oval at the face, peak drooping forward; dark lining
            rows = []
            for y, rx, rz, oz in ((-0.08, 0.17, 0.16, -0.03), (0.0, 0.125, 0.14, -0.01), (0.08, 0.112, 0.135, 0.012),
                                  (0.16, 0.112, 0.138, 0.022), (0.24, 0.106, 0.13, 0.026), (0.31, 0.08, 0.105, 0.022),
                                  (0.35, 0.03, 0.05, 0.03)):
                rows.append((y, rx, rz, 0.0, oz))
            ths = []
            for i, (y, rx, rz, ox, oz) in enumerate(rows):
                open_ = lerp_rows([(-0.08, 20), (0.0, 50), (0.2, 46), (0.3, 25), (0.35, 5)], y)[0]
                row = []
                for k in range(15):
                    th = math.radians(open_ + (360 - 2 * open_) * k / 14)
                    fz = 0.02 * g((math.degrees(th) - 180) / 70)
                    row.append((rx * math.sin(th), y, oz + rz * math.cos(th) - fz))
                ths.append(row)
            m.surface("cc_robe", ths)
            m.surface("cc_robe_in", [[(x * 0.96, y, (z + 0.0) * 0.96) for x, y, z in reversed(row)] for row in ths])
        m.use("Spine")
        body(m, "cc_robe", "cc_robe", sized(TORSO_M, 1.08, 1.12), sized(PELVIS_M, 1.12, 1.15, 0.01), power=2.3)
        m.use("Spine")
        m.ellipsoid("cc_robe", (0.15, 0.12, 0.09), (0, 0.4, -0.07), (-15, 0, 0), seg=12, rings=6)  # hump
        shell(m, "cc_robe", [(0.26, 0.25, 0.17, 0, 0.0), (0.4, 0.268, 0.17, 0, 0.0), (0.47, 0.24, 0.145, 0, -0.005),
                             (0.53, 0.15, 0.1, 0, -0.01), (0.58, 0.075, 0.07, 0, -0.01)], -180, 180, 20, inner="cc_robe_in",
              fold=lambda d, i: 1 + 0.035 * (i == 0) * math.sin(math.radians(d) * 9))  # capelet
        m.lathe("iron", [(0.025, -0.004), (0.028, 0.0), (0.025, 0.004)], (0, 0.5, 0.1), (90, 0, 0), seg=8)  # clasp
        for sgn in (1, -1):  # stole with the Veil's Eye, over the mantle down to the knees
            shell(m, "cc_stole", [(-0.1, 0.17, 0.13, 0, 0.012), (0.12, 0.172, 0.135, 0, 0.016),
                                   (0.3, 0.215, 0.165, 0, 0.004), (0.46, 0.2, 0.14, 0, -0.002)],
                  sgn * 12, sgn * 32, 2)
        shell(m, "cc_stole", [(0.18, 0.18, 0.15, 0, -0.02), (0.44, 0.2, 0.16, 0, -0.04)], 150, 210, 4)  # eye on back
        m.use("Hips")
        m.lathe("cc_rope", [(0.2, 0.04), (0.205, 0.055), (0.2, 0.07)], scale=(1, 1, 0.8), seg=16)
        m.cyl("cc_rope", 0.01, 0.01, 0.36, (0.12, -0.33, 0.145), seg=4, caps=False)
        for i in range(9):  # beads
            a = i / 8 * math.pi
            m.ellipsoid("cc_wood", (0.011, 0.011, 0.011), (0.12 + 0.04 * math.cos(a), -0.14 - 0.1 * math.sin(a), 0.16), seg=6, rings=4)
        m.loft("iron", [(-0.08, 0.05, 0.03), (0.08, 0.05, 0.03)], (-0.19, -0.05, 0.1), (0, 0, 0), seg=8, power=4)  # radio
        m.box("metal", (0.07, 0.05, 0.005), (-0.19, -0.02, 0.131))
        m.cyl("iron", 0.005, 0.003, 0.2, (-0.16, 0.03, 0.1), seg=4, caps=False)
        for sgn in (1, -1):
            shell(m, "cc_stole", [(-0.42, 0.25, 0.2, 0, 0.0), (-0.2, 0.24, 0.185, 0, 0.0), (0.05, 0.225, 0.17, 0, 0.0)],
                  sgn * 12, sgn * 32, 2)
        half_skirts(m, "cc_robe", "cc_robe_in",
                    [(0.1, 0.2, 0.135), (-0.1, 0.225, 0.16), (-0.35, 0.25, 0.19), (-0.6, 0.275, 0.22), (-0.8, 0.29, 0.23)],
                    folds=4, amp=0.05)
        for side, s in (("L", 1), ("R", -1)):
            m.use("UpperArm" + side)
            m.capsule("cc_robe", 0.058, 0.056, 0.27, (0, -0.02, 0), seg=10)
            m.use("Forearm" + side)
            m.ellipsoid("cc_robe", (0.055, 0.055, 0.055), seg=10, rings=6)
            m.lathe("cc_robe", [(0.1, -0.29), (0.095, -0.2), (0.07, -0.08), (0.06, 0.0), (0, 0.04)], seg=12)  # bell sleeve
            m.lathe("cc_robe_in", [(0.094, -0.29), (0.02, -0.26)], seg=12)
            m.lathe("cc_skin_old", [(0.024, -0.26), (0.026, -0.2)], seg=8)  # thin wrist inside the sleeve
            hand(m, side, s, "cc_skin_old", grip=True)
        rig.mirror(lambda side, s: leg(m, side, s, "cc_robe_in", "cc_leather", r=0.075))
        # the ledger in the left hand, the brand iron in the right
        m.use("HandL")
        m.loft("cc_ledger", [(-0.13, 0.024, 0.1), (0.13, 0.024, 0.1)], (-0.035, -0.12, 0.02), seg=8, power=6)
        m.box("sheet", (0.042, 0.25, 0.19), (-0.03, -0.12, 0.025))
        m.use("HandR")
        m.lathe("iron", [(0.01, -0.9), (0.011, 0.02)], (0, 0, 0.02), seg=6)
        m.lathe("cc_leather", [(0.018, -0.15), (0.02, -0.08), (0.018, 0.03)], (0, 0, 0.02), seg=8)
        with m.push((0, -0.93, 0.02)):  # eye-shaped brand head
            for sgn in (1, -1):
                m.lathe("rust", [(0.009, -0.07), (0.009, 0.07)], (0, 0, sgn * 0.025), (0, 0, 90), seg=6)
            m.ellipsoid("rust", (0.02, 0.018, 0.018), seg=8, rings=5)
    return m


def char_marked_man():
    """Marked townsman: flannel, jeans, work vest, burlap sack mask with the eye; lead pipe."""
    m = rig.skeleton("char_marked_man", 1.0)
    m.use("Head")
    neck(m, "cc_skin_pale", 0.058)
    with m.push((0, 0.0, 0), (0, 0, -9), (1.12, 1.06, 1.08)):  # sack sits crooked: something is wrong with him
        sack = [(y, rx * 1.05, rz * 1.02, oz) for y, rx, rz, oz in SKULL]
        skull(m, "cc_mask_burlap", "cc_burlap", relief=False, grow=0.006, table=sack)
        m.lathe("cc_burlap", [(0.062, -0.005), (0.058, 0.015), (0.066, 0.045), (0.078, 0.06)], (0, 0, 0.0), seg=12,
                scale=(1, 1, 1.2))  # gathered sack neck
        m.lathe("cc_rope", [(0.058, 0.004), (0.063, 0.013), (0.058, 0.022)], (0, 0, 0.002), seg=10, scale=(1, 1, 1.2))
        m.loft("cc_burlap", [(0.0, 0.03, 0.024), (0.02, 0.02, 0.014), (0.035, 0.0, 0.0)],
               (0.035, 0.245, -0.04), (-70, 0, -30), seg=8)  # knotted corner, flopped back
    body(m, "cc_plaid", "cc_denim")
    m.use("Spine")
    # denim work vest over the flannel: open at the front
    for sgn in (1, -1):
        rows = [(y, rx + 0.008, rz + 0.01, 0, oz) for y, rx, rz, _, oz in TORSO_M[:7]]
        shell(m, "cc_denim", rows, sgn * 14, sgn * 180, 10)
        m.box("cc_denim", (0.09, 0.07, 0.012), (sgn * 0.075, 0.12, 0.112), (0, sgn * 22, 0))  # pockets
    for sgn in (1, -1):
        m.loft("cc_plaid", [(0.0, 0.012, 0.018), (0.06, 0.006, 0.03), (0.07, 0.0, 0.0)], (sgn * 0.035, 0.5, 0.05),
               (0, 0, sgn * 60), seg=6)  # shirt collar points
    for y in (0.08, 0.2, 0.32):
        m.ellipsoid("white", (0.008, 0.008, 0.004), (0, y, 0.118), seg=6, rings=4)
    m.use("Hips")
    m.lathe("cc_leather", [(0.17, 0.04), (0.172, 0.06), (0.168, 0.075)], scale=(1, 1, 0.68), seg=16)
    m.box("metal", (0.05, 0.035, 0.01), (0, 0.058, 0.116))
    for sgn in (1, -1):
        m.box("cc_denim", (0.08, 0.1, 0.012), (sgn * 0.07, -0.08, -0.108))  # back pockets
    rig.mirror(lambda side, s: arm(m, side, s, "cc_plaid", "cc_skin_pale", 0.048, cuff="cc_plaid", grip="R"))
    eye_band(m, "UpperArmL", -0.17, 0.056)
    m.use("HandL")
    m.lathe("white", [(0.02, -0.075), (0.036, -0.06), (0.034, -0.02), (0.02, -0.008)], (0, 0, 0.0), seg=8,
            scale=(0.65, 1, 1.35))  # dirty bandage
    rig.mirror(lambda side, s: leg(m, side, s, "cc_denim", "cc_boot", r=0.09, boot=0.02))
    m.use("HandR")
    m.lathe("rust", [(0.018, -0.6), (0.02, -0.5), (0.019, 0.1)], (0, 0, 0.012), seg=8)
    m.lathe("rust", [(0.03, -0.62), (0.03, -0.54), (0.02, -0.53)], (0, 0, 0.012), seg=8)  # fitting
    return m


def char_marked_woman():
    """Marked townswoman: porcelain mask, bun and braid, cardigan over a faded dress; burnt festival lantern."""
    m = rig.skeleton("char_marked_woman", 0.94)
    with m.push(scale=(0.94,) * 3):
        m.use("Head")
        neck(m, "cc_skin_pale", 0.05)
        with m.push((0, 0.0, 0), (0, 0, 7), (0.93, 0.98, 0.95)):  # head cocked, listening
            skull(m, "cc_skin_pale", "cc_skin_pale")
            # the mask: the face front lifted off the head
            mask = [[skull_pt(th, y, 0.006) for th in angles(-78, 78, 12, 1.2)] for y in HEAD_YS[1:21]]
            m.surface("cc_mask_porcelain", mask, uv=face_uv)
            m.lathe("cc_leather", [(0.084, 0.16), (0.086, 0.17), (0.084, 0.18)], (0, 0, -0.008), seg=14,
                    scale=(1, 1, 1.23))  # strap
            hair_cap(m, "cc_hair_brown", lambda d: lerp_rows([(0, 0.228), (60, 0.2), (95, 0.11), (140, 0.08),
                                                                (180, 0.07)], abs(d))[0],
                     lambda d: 0.014 + 0.012 * (abs(d) > 60), top=0.01)
            m.ellipsoid("cc_hair_brown", (0.05, 0.045, 0.04), (0, 0.19, -0.115), (30, 0, 0), seg=10, rings=6)  # bun
            m.lathe("cc_hair_brown", [(0, -0.3), (0.012, -0.29), (0.018, -0.2), (0.024, -0.1), (0.03, 0.0), (0, 0.03)],
                    (0, 0.13, -0.1), (12, 0, 0), seg=6)  # braid down the back
        body(m, "cc_cardigan", "cc_dress",
             [(-0.1, 0.13, 0.095, 0, 0.0), (0.0, 0.125, 0.09, 0, 0.0), (0.12, 0.132, 0.094, 0, 0.004),
              (0.24, 0.15, 0.112, 0, 0.016), (0.32, 0.158, 0.118, 0, 0.018), (0.42, 0.172, 0.1, 0, 0.0),
              (0.47, 0.165, 0.088, 0, -0.006), (0.51, 0.12, 0.074, 0, -0.01), (0.545, 0.075, 0.058, 0, -0.012), (0.575, 0.055, 0.048, 0, -0.012)],
             [(-0.2, 0.0, 0.0, 0, 0.0), (-0.19, 0.08, 0.06, 0, 0.0), (-0.15, 0.16, 0.11, 0, 0.0),
              (-0.08, 0.182, 0.12, 0, 0.0), (0.0, 0.168, 0.11, 0, 0.0), (0.08, 0.14, 0.098, 0, 0.0),
              (0.15, 0.13, 0.095, 0, 0.0)])
        m.use("Spine")
        shell(m, "cc_dress", [(0.1, 0.136, 0.099, 0, 0.006), (0.24, 0.154, 0.117, 0, 0.018),
                              (0.36, 0.164, 0.117, 0, 0.012), (0.46, 0.15, 0.09, 0, -0.006)], -18, 18, 4)  # dress bodice
        for y in (0.1, 0.2, 0.3):
            m.ellipsoid("white", (0.008, 0.008, 0.004), (0.03, y, 0.108 if y < 0.2 else 0.128), seg=6, rings=4)
        m.lathe("cc_cardigan", [(0.1, 0.44), (0.19, 0.4), (0.2, 0.44), (0.15, 0.52), (0.08, 0.56), (0.065, 0.58)],
                (0, 0, -0.01), scale=(1, 1, 0.72), seg=16)  # knitted shawl
        m.use("Hips")
        shell(m, "cc_apron", [(-0.45, 0.25, 0.218, 0, 0.0), (-0.25, 0.236, 0.195, 0, 0.0), (-0.05, 0.2, 0.152, 0, 0.0),
                              (0.08, 0.146, 0.108, 0, 0.0)], -34, 34, 6)
        m.lathe("cc_apron", [(0.142, 0.06), (0.146, 0.07), (0.142, 0.08)], scale=(1, 1, 0.72), seg=16)  # apron band
        half_skirts(m, "cc_dress", "cc_robe_in",
                    [(0.08, 0.19, 0.13), (-0.1, 0.21, 0.155), (-0.3, 0.235, 0.18), (-0.5, 0.25, 0.2)], folds=4, amp=0.05)
        rig.mirror(lambda side, s: arm(m, side, s, "cc_cardigan", "cc_skin_pale", 0.042, cuff="cc_cardigan", grip="L"))
        eye_band(m, "UpperArmR", -0.17, 0.05)
        rig.mirror(lambda side, s: leg(m, side, s, "cc_stocking", "cc_leather", r=0.074))
        m.use("HandL")
        m.cyl("iron", 0.004, 0.004, 0.1, (0, -0.2, 0), seg=3, caps=False)
        m.lathe("lantern", [(0.0, -0.52), (0.05, -0.51), (0.1, -0.44), (0.1, -0.36), (0.06, -0.3), (0.0, -0.29)], seg=8)
        m.lathe("iron", [(0.03, -0.3), (0.03, -0.285)], seg=6)
    return m


MODELS = [char_marcus, char_shepherd, char_marked_man, char_marked_woman]
