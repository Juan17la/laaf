"""Characters B: Owen (The Woodsman), Nora (The Teacher), Julian (The Medic), Silas (bar regular).

Built on tools/rig.py; geometry is joint-local, faces +Z, left = +X. Smooth-shaded SA-era bodies:
sculpted head grid with a 128px painted face planar-projected on the front half, lofted torsos,
capsule limbs with joint spheres, shells for open jackets/coats/hair.
"""
import math

import build_assets as B
import rig

mix, mul = B.mix, B.mul
TAU = 2 * math.pi


def _g(x, y):
    return math.exp(-(x * x + y * y))


def _clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def _smooth(e0, e1, v):
    t = _clamp((v - e0) / (e1 - e0))
    return t * t * (3 - 2 * t)


# ============================================================== head geometry (head-local, pre-offset)
# y: chin 0.03 .. crown 0.268. Face features: mouth 0.083, nose tip 0.115, eyes 0.153, brows 0.172.
FACE_W, FACE_TOP, FACE_H = 0.16, 0.27, 0.25   # planar projection of the painted face
HEAD_DROP = -0.045                              # whole head shifted down inside the Head joint

# y, rx (half width), rzf (front depth), rzb (back depth)
HEAD_ROWS = [
    (0.028, 0.0, 0.05, 0.0), (0.032, 0.024, 0.082, 0.012), (0.04, 0.04, 0.09, 0.02), (0.05, 0.052, 0.094, 0.03),
    (0.06, 0.058, 0.097, 0.045), (0.07, 0.062, 0.099, 0.06), (0.078, 0.065, 0.1, 0.07), (0.086, 0.067, 0.101, 0.08),
    (0.095, 0.07, 0.101, 0.088), (0.105, 0.072, 0.101, 0.095), (0.117, 0.0745, 0.101, 0.1),
    (0.13, 0.0765, 0.101, 0.105), (0.143, 0.078, 0.101, 0.109), (0.153, 0.079, 0.1, 0.11), (0.163, 0.079, 0.099, 0.11),
    (0.176, 0.0785, 0.097, 0.11), (0.192, 0.076, 0.093, 0.107), (0.21, 0.071, 0.086, 0.101),
    (0.23, 0.061, 0.072, 0.088), (0.248, 0.046, 0.054, 0.068), (0.261, 0.026, 0.03, 0.038), (0.268, 0.0, 0.0, 0.0),
]


def _row(y):
    R = HEAD_ROWS
    if y <= R[0][0]:
        return R[0][1:]
    for (y0, *a), (y1, *b) in zip(R, R[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            return tuple(p + (q - p) * t for p, q in zip(a, b))
    return R[-1][1:]


def _features(x, y):
    """Front displacement (m) sculpting sockets, brow, cheekbones, lips and chin."""
    ax = abs(x)
    return (-0.0075 * _g((ax - 0.032) / 0.014, (y - 0.152) / 0.011)
            + 0.0035 * _g(x / 0.045, (y - 0.173) / 0.008)
            + 0.004 * _g((ax - 0.048) / 0.018, (y - 0.13) / 0.013)
            + 0.004 * _g(x / 0.028, (y - 0.083) / 0.017)
            + 0.0022 * _g(x / 0.019, (y - 0.088) / 0.004) + 0.0028 * _g(x / 0.017, (y - 0.077) / 0.0045)
            - 0.002 * _g(x / 0.02, (y - 0.066) / 0.005)
            + 0.0045 * _g(x / 0.02, (y - 0.047) / 0.012)
            - 0.003 * _g((ax - 0.07) / 0.012, (y - 0.17) / 0.02))


def head_pt(a, y, off=0.0, sculpt=True, jaw=1.0):
    """Point on the head at loft angle a (0=+X, -pi/2=-Z, -pi=-X, -3pi/2=+Z) and height y."""
    rx, rzf, rzb = _row(y)
    c, s = math.cos(a), math.sin(a)
    if rx < 1e-6:
        return (0.0, y + off * 0.8, 0.01 if y < 0.1 else -0.01)
    if y < 0.1:
        rx *= 1 + (jaw - 1) * (0.1 - y) / 0.07
    x, z = rx * c, (rzf if s > 0 else rzb) * s
    d = off
    if sculpt and s > 0:
        d += _features(x, y) * s * s
    r = math.hypot(x, z)
    k = (r + d) / r
    return (x * k, y, z * k)


def face_uv(p):
    return (_clamp(0.5 + p[0] / FACE_W, 0.004, 0.996), _clamp((FACE_TOP - p[1]) / FACE_H, 0.004, 0.996))


def _angles(a0, a1, n):
    return [a0 + (a1 - a0) * j / n for j in range(n + 1)]


def head(m, who, jaw=1.0, ears=True, neck_r=0.052):
    """Neck + sculpted skull (face texture on the front half) + nose + ears on the Head joint."""
    skin, face = "cb_skin_" + who, "cb_face_" + who
    m.use("Head")
    ys = [r[0] for r in HEAD_ROWS]
    with m.push((0, HEAD_DROP, 0)):
        front = [[head_pt(a, y, jaw=jaw) for a in _angles(-math.pi, -TAU, 14)] for y in ys]
        back = [[head_pt(a, y, jaw=jaw) for a in _angles(0, -math.pi, 8)] for y in ys]
        m.surface(face, front, uv=face_uv)
        m.surface(skin, back)
        # nose (same projection, so the painted shading lands on it)
        m.loft(face, [(0.103, 0, 0, 0, 0.097), (0.106, 0.011, 0.008, 0, 0.1), (0.11, 0.0155, 0.012, 0, 0.103),
                      (0.117, 0.013, 0.013, 0, 0.105), (0.127, 0.009, 0.012, 0, 0.103), (0.14, 0.0075, 0.01, 0, 0.1),
                      (0.155, 0.007, 0.008, 0, 0.098), (0.164, 0, 0, 0, 0.095)], seg=10, uv=face_uv)
        if ears:
            for s in (-1, 1):
                m.ellipsoid(skin, (0.011, 0.03, 0.019), (s * 0.077, 0.143, -0.008), (0, s * 15, s * 8), seg=7, rings=5)
    # neck, leaning slightly forward, rooted inside the collar
    m.lathe(skin, [(neck_r * 1.25, -0.08), (neck_r * 1.05, -0.03), (neck_r, 0.02), (neck_r * 0.95, 0.07),
                   (neck_r * 0.85, 0.1)], (0, 0, -0.012), (8, 0, 0), (1.0, 1, 0.95), seg=10)


def scalp(m, mat, front_y, back_y, off=0.01, crown_lift=0.0, seg=16, rows=5, side_y=None, bulk=None):
    """Hair/hat shell following the skull: rim at front_y over the forehead, back_y at the nape,
    side_y at the temples (default: in between). bulk(a, t) adds extra thickness (t=0 rim..1 crown)."""
    side_y = (front_y + back_y) / 2 if side_y is None else side_y
    grid = []
    angs = _angles(0, -TAU, seg)[:-1]
    for k in range(rows + 1):
        t = k / rows
        row = []
        for a in angs:
            s = math.sin(a)
            rim = side_y + (front_y - side_y) * s if s > 0 else side_y + (back_y - side_y) * -s
            y = rim + (0.268 - rim) * (1 - (1 - t) ** 1.6)
            extra = bulk(a, t) if bulk else 0.0
            p = head_pt(a, y, off + extra, sculpt=False)
            row.append((p[0], p[1] + crown_lift * t * t, p[2]))
        grid.append(row)
    grid[-1] = [(0.0, 0.268 + off + crown_lift, -0.01)] * len(angs)
    with m.push((0, HEAD_DROP, 0)):
        m.surface(mat, grid, wrap=True)


def with_head(m):
    return m.push((0, HEAD_DROP, 0))


# ============================================================== generic shells

def shell(m, mat, secs, a0, a1, n, power=2.0, pos=(0, 0, 0), rot=(0, 0, 0), lining=None, uv=None):
    """Partial loft: superellipse arcs from angle a0 down to a1 (loft convention, see head_pt).
    secs: (y, rx, rz[, ox, oz]). lining: material for the inside so open garments aren't see-through."""
    grid = []
    for sec in secs:
        y, rx, rz = sec[:3]
        ox, oz = sec[3:5] if len(sec) > 3 else (0.0, 0.0)
        row = []
        for a in _angles(a0, a1, n):
            c, s = math.cos(a), math.sin(a)
            row.append((ox + rx * math.copysign(abs(c) ** (2 / power), c), y,
                        oz + rz * math.copysign(abs(s) ** (2 / power), s)))
        grid.append(row)
    with m.push(pos, rot):
        m.surface(mat, grid, uv=uv)
        if lining:
            m.surface(lining, [row[::-1] for row in grid])


FRONT = -1.5 * math.pi  # loft angle pointing +Z


def open_front(gap):
    """(a0, a1) covering everything except a gap (radians) centred on the front."""
    return FRONT - gap / 2, FRONT - TAU + gap / 2


def grow(secs, d, dz=None):
    dz = d if dz is None else dz
    return [(s[0], s[1] + d, s[2] + dz) + tuple(s[3:]) for s in secs]


# ============================================================== body

def torso_secs(sex, belly=0.0, bust=0.0):
    if sex == "f":
        return [(-0.1, 0.15, 0.1), (0.0, 0.135, 0.09), (0.1, 0.118, 0.085), (0.2, 0.13, 0.092 + bust * 0.3, 0, bust * 0.2),
                (0.28, 0.145, 0.1 + bust, 0, bust * 0.6), (0.36, 0.158, 0.098 + bust * 0.5, 0, bust * 0.4),
                (0.43, 0.182, 0.09), (0.48, 0.175, 0.078), (0.52, 0.11, 0.068), (0.55, 0.05, 0.048), (0.56, 0, 0)]
    return [(-0.1, 0.155 + belly * 0.3, 0.1 + belly * 0.4, 0, belly * 0.4), (0.0, 0.15 + belly * 0.4, 0.1 + belly, 0, belly),
            (0.12, 0.152 + belly * 0.4, 0.105 + belly, 0, belly * 0.9),
            (0.24, 0.165 + belly * 0.2, 0.11 + belly * 0.5, 0, belly * 0.4), (0.34, 0.18, 0.115, 0, 0.005),
            (0.42, 0.198, 0.11), (0.48, 0.19, 0.095), (0.52, 0.125, 0.08), (0.555, 0.058, 0.055), (0.565, 0, 0)]


def pelvis_secs(sex, belly=0.0):
    w = 1.1 if sex == "f" else 1.0
    return [(-0.2, 0.0, 0.0), (-0.19, 0.08 * w, 0.07), (-0.14, 0.16 * w, 0.1), (-0.06, 0.17 * w, 0.108 + belly * 0.3, 0, belly * 0.3),
            (0.02, 0.155 * w, 0.1 + belly * 0.6, 0, belly * 0.6), (0.1, 0.15 * w - (0.03 if sex == "f" else 0), 0.098 + belly, 0, belly)]


def torso(m, mat, sex, belly=0.0, bust=0.0, power=2.4):
    m.use("Spine")
    secs = torso_secs(sex, belly, bust)
    m.loft(mat, secs, seg=16, power=power)
    return secs


def pelvis(m, mat, sex, belly=0.0, belt=None, buckle="cb_steel"):
    m.use("Hips")
    secs = pelvis_secs(sex, belly)
    m.loft(mat, secs, seg=16, power=2.4)
    if belt:
        w = 1.1 if sex == "f" else 1.0
        m.loft(belt, [(0.03, 0.158 * w + 0.004, 0.103 + belly * 0.6, 0, belly * 0.6),
                      (0.075, 0.153 * w + 0.004, 0.101 + belly * 0.85, 0, belly * 0.85)], seg=16, power=2.4)
        z = 0.103 + belly * 1.3 + 0.002
        m.box(buckle, (0.05, 0.038, 0.012), (0, 0.052, z))
        m.box(belt, (0.032, 0.02, 0.014), (0, 0.052, z + 0.002))
    return secs


def arms(m, who, sleeve, forearm=None, hand=None, cuff=None, rolled=None, r=1.0, cuff_y=-0.23):
    """Capsule arms with deltoid + elbow spheres. forearm defaults to the sleeve; rolled: material of a
    rolled-up sleeve ring at the elbow (bare forearm)."""
    skin = "cb_skin_" + who
    hand = hand or skin
    forearm = forearm or sleeve

    def side(k, s):
        m.use("UpperArm" + k)
        m.ellipsoid(sleeve, (0.054 * r, 0.058 * r, 0.056 * r), (-0.01 * s, -0.05, 0), seg=8, rings=5)  # deltoid
        m.capsule(sleeve, 0.054 * r, 0.044 * r, 0.24, (0, -0.05, 0), seg=8, squash=(1.0, 1.08))
        m.use("Forearm" + k)
        m.ellipsoid(forearm if not rolled else sleeve, (0.046 * r, 0.046 * r, 0.048 * r), (0, 0, 0), seg=8, rings=5)
        if rolled:
            m.lathe(rolled, [(0.048 * r, -0.07), (0.056 * r, -0.06), (0.058 * r, -0.03), (0.056 * r, 0.0), (0.05 * r, 0.01)],
                    seg=10)
        m.capsule(forearm, 0.046 * r, 0.03, 0.24, (0, 0.0, 0), seg=8, squash=(0.9, 1.1))
        if cuff:
            m.lathe(cuff, [(0.034, cuff_y - 0.012), (0.042, cuff_y - 0.008), (0.043, cuff_y + 0.03), (0.036, cuff_y + 0.036)],
                    seg=10)
        m.use("Hand" + k)
        m.ellipsoid(hand, (0.019, 0.045, 0.043), (0, -0.047, 0.004), (0, 0, s * 4), seg=8, rings=5)  # palm
        m.capsule(hand, 0.017, 0.013, 0.055, (-0.003 * s, -0.085, 0.002), (0, 0, s * 12), seg=6, squash=(1.0, 2.3))  # fingers
        m.capsule(hand, 0.012, 0.009, 0.045, (-0.004 * s, -0.035, 0.036), (-30, 0, s * 18), seg=5)  # thumb
    rig.mirror(side)


def legs(m, pants, knee_mat=None, shin=None, r=1.0, cuff=None):
    shin = shin or pants

    def side(k, s):
        m.use("Thigh" + k)
        m.capsule(pants, 0.088 * r, 0.06 * r, 0.41, (0.005 * s, 0.0, 0), seg=10, squash=(0.95, 1.05))
        m.use("Shin" + k)
        m.ellipsoid(knee_mat or pants, (0.058 * r, 0.06, 0.062 * r), (0, 0.0, 0.004), seg=8, rings=5)
        m.capsule(shin, 0.058 * r, 0.038, 0.38, (0, 0.0, -0.004), seg=8, squash=(0.95, 1.08))
        if cuff:
            m.lathe(cuff, [(0.05, -0.42), (0.058, -0.41), (0.058, -0.36), (0.05, -0.345)], seg=10)
    rig.mirror(side)


def shoes(m, upper, sole="cb_sole", boot=None, boot_h=0.16, heel=0.0, toe=0.19, width=1.0, lace=None):
    """Lofted shoe on each Foot joint (ankle pivot, ground at y=-0.05); boot adds a shaft on the shin."""
    w = width

    def side(k, s):
        m.use("Foot" + k)
        # loft along +Z (rot 90 on X): section (z, half-width, half-height, 0, -centre_y)
        m.loft(upper, [(-0.075, 0.0, 0.0, 0, 0.012), (-0.07, 0.03 * w, 0.03, 0, 0.01), (-0.055, 0.042 * w, 0.042, 0, 0.004),
                       (-0.02, 0.046 * w, 0.048, 0, 0.0), (0.03, 0.046 * w, 0.042, 0, 0.008), (0.08, 0.051 * w, 0.032, 0, 0.016),
                       (toe - 0.045, 0.047 * w, 0.025, 0, 0.022), (toe - 0.015, 0.035 * w, 0.02, 0, 0.026),
                       (toe, 0.0, 0.0, 0, 0.028)], rot=(90, 0, 0), seg=10, power=2.6)
        m.loft(sole, [(-0.08, 0.0, 0.0, 0, 0.044), (-0.077, 0.036 * w, 0.01, 0, 0.044), (-0.06, 0.047 * w, 0.011, 0, 0.044),
                      (0.08, 0.055 * w, 0.01, 0, 0.044), (toe - 0.02, 0.042 * w, 0.009, 0, 0.044),
                      (toe + 0.006, 0.0, 0.0, 0, 0.044)], rot=(90, 0, 0), seg=10, power=3.5)
        if heel:
            m.lathe(sole, [(0.0, -0.05 + 0.0), (0.02, -0.05), (0.022, -0.05 + heel), (0.0, -0.05 + heel)],
                    (0, 0, -0.055), scale=(1.1, 1, 1), seg=8)
        if lace:
            for i in range(4):
                m.box(lace, (0.05, 0.006, 0.01), (0, 0.022 - i * 0.006, 0.02 + i * 0.022), (-35, 0, 0))
        if boot:
            m.use("Shin" + k)
            y0 = -0.43
            m.lathe(boot, [(0.05, y0), (0.056, y0 + 0.04), (0.054, y0 + boot_h * 0.6), (0.058, y0 + boot_h),
                           (0.062, y0 + boot_h + 0.015), (0.05, y0 + boot_h + 0.02)], (0, 0, 0.002), scale=(1, 1, 1.12), seg=10)
    rig.mirror(side)


def collar(m, mat, y=0.5, r=(0.075, 0.07), h=0.05, flare=0.02, gap=0.9, lining=None, tilt=-8, z=0.0):
    """Shirt/jacket collar ring around the neck base, open at the front."""
    m.use("Spine")
    a0, a1 = open_front(gap)
    shell(m, mat, [(0, r[0], r[1]), (h * 0.5, r[0] + flare * 0.4, r[1] + flare * 0.3), (h, r[0] + flare, r[1] + flare * 0.8, 0, -0.005)],
          a0, a1, 10, pos=(0, y, z), rot=(tilt, 0, 0), lining=lining or mat)


def pocket(m, mat, w, h, pos, rot=(0, 0, 0), flap=None):
    m.loft(mat, [(0, 0, 0), (0.002, w / 2, 0.006), (h, w / 2, 0.006), (h + 0.002, 0, 0)], pos, rot, seg=8, power=5)
    if flap:
        m.loft(flap, [(h - 0.018, 0, 0), (h - 0.016, w / 2 + 0.004, 0.009), (h + 0.004, w / 2 + 0.004, 0.009),
                      (h + 0.006, 0, 0)], pos, rot, seg=8, power=5)


def tube(m, mat, pts, r, seg=5):
    """Smooth swept tube through pts (cords, straps, bow limbs); r may be a list per point."""
    rs = r if isinstance(r, (list, tuple)) else [r] * len(pts)
    grid = []
    for i, p in enumerate(pts):
        t = B.v_norm(B.v_sub(pts[min(i + 1, len(pts) - 1)], pts[max(i - 1, 0)]))
        ref = (0, 1, 0) if abs(t[1]) < 0.9 else (1, 0, 0)
        u = B.v_norm(B.v_cross(ref, t))
        v = B.v_cross(t, u)
        grid.append([tuple(p[k] + rs[i] * (math.cos(TAU * j / seg) * u[k] + math.sin(TAU * j / seg) * v[k])
                           for k in range(3)) for j in range(seg)])
    m.surface(mat, grid, wrap=True)


# ============================================================== textures

def face_fn(skin, hair, iris, lips, hairline=0.212, stubble=0.0, beard=None, glasses=False,
            bags=0.35, wrinkles=0.0, grief=1.0, red_nose=0.0, lashes=False, brow_w=1.0, blush=0.0):
    """128px face painted in head metres: x=(u-.5)*FACE_W, y=FACE_TOP-v*FACE_H (see HEAD_ROWS)."""
    lip_dark = mul(lips, 0.45)

    def fn(px, py, a, b, r):
        x, y = (px + 0.5) / 128 * FACE_W - FACE_W / 2, FACE_TOP - (py + 0.5) / 128 * FACE_H
        ax = abs(x)
        c = mul(skin, 0.9 + 0.1 * a + 0.025 * (r - 0.5))
        # broad form shading: sockets, under-brow, sides of the nose, under the chin
        sh = 1.0
        sh -= 0.13 * _g((ax - 0.031) / 0.019, (y - 0.156) / 0.013)
        sh -= 0.08 * _g((ax - 0.045) / 0.02, (y - 0.108) / 0.012) * 0.6
        sh -= 0.09 * _g((ax - 0.011) / 0.004, (y - 0.13) / 0.022)
        sh += 0.06 * _g(x / 0.006, (y - 0.13) / 0.02)  # bridge highlight
        sh += 0.05 * _g(x / 0.03, (y - 0.19) / 0.015)   # forehead
        sh -= 0.12 * _smooth(0.058, 0.03, y) * _smooth(0.0, 0.012, ax)
        sh -= 0.06 * _smooth(0.055, 0.078, ax)
        c = mul(c, sh)
        if blush or True:
            k = (0.18 + blush) * _g((ax - 0.045) / 0.017, (y - 0.115) / 0.014)
            c = mix(c, (c[0] * 1.12, c[1] * 0.86, c[2] * 0.84), k)
        if red_nose:
            c = mix(c, (0.72, 0.3, 0.27), red_nose * _g(x / 0.015, (y - 0.115) / 0.015))
        # tired under-eyes
        c = mix(c, (c[0] * 0.78, c[1] * 0.72, c[2] * 0.78), bags * _g((ax - 0.033) / 0.014, (y - 0.141) / 0.0045))
        if wrinkles:
            for yy in (0.19, 0.198, 0.206):
                if abs(y - yy - 0.002 * math.sin(x * 90)) < 0.0012 and ax < 0.04 and r < 0.85:
                    c = mul(c, 1 - 0.22 * wrinkles)
            if abs(ax - 0.052) < 0.0014 and 0.137 < y < 0.16 and r < 0.8:  # crow's feet
                c = mul(c, 1 - 0.15 * wrinkles)
        # nasolabial folds
        fx = 0.019 + (0.115 - y) * 0.45
        if 0.075 < y < 0.113:
            c = mul(c, 1 - (0.1 + 0.2 * wrinkles) * _g((ax - fx) / 0.0018, 0) * (1 - 0.5 * a))
        # nostrils and nose tip
        c = mul(c, 1 - 0.65 * _g((ax - 0.0085) / 0.0042, (y - 0.106) / 0.0022))
        c = mul(c, 1 + 0.08 * _g(x / 0.006, (y - 0.116) / 0.006))
        c = mul(c, 1 - 0.15 * _g((ax - 0.0145) / 0.0025, (y - 0.109) / 0.005))
        # stubble / beard shadow
        mouth_y = 0.0835 - 0.0025 * grief * (x / 0.024) ** 2
        jaw_zone = (y < 0.1 and ax > 0.02 + (y - 0.06) * 0.2) or y < 0.068 or (ax < 0.03 and 0.087 < y < 0.101)
        if stubble and jaw_zone and y < 0.132 - 0.0 and not (ax < 0.026 and abs(y - mouth_y) < 0.007):
            fade = _smooth(0.128, 0.105, y) if ax > 0.05 else 1.0
            if r < stubble * fade + 0.1:
                c = mul(c, 0.8 - 0.2 * r)
            c = mix(c, mul(hair, 0.8), 0.15 * fade * stubble)
        if beard and not (ax < 0.022 and abs(y - mouth_y) < 0.006):
            if (y < 0.074) or (ax > 0.035 and y < 0.128 - 0.25 * (0.07 - min(ax, 0.07))) or (0.086 < y < 0.1 and ax < 0.03):
                c = mul(beard, 0.6 + 0.45 * a + 0.3 * (r - 0.5) + 0.12 * math.sin(px * 2.1 + py * 0.7))
        # lips
        if ax < 0.026:
            t = ax / 0.026
            up = mouth_y + 0.0065 * (1 - t ** 2) - 0.0014 * _g(x / 0.004, 0)   # cupid's bow notch
            lo = mouth_y - 0.008 * (1 - t ** 1.6)
            if mouth_y < y < up:
                c = mix(c, mul(lips, 0.78 + 0.1 * a), 0.8 * _smooth(1.0, 0.8, t) + 0.1)
            elif lo < y <= mouth_y:
                k = 0.95 + 0.1 * a + 0.18 * _g(x / 0.01, (y - mouth_y + 0.0035) / 0.0016)
                c = mix(c, mul(lips, k), 0.85 * _smooth(1.0, 0.8, t) + 0.1)
            if abs(y - mouth_y) < 0.0011 + 0.0006 * (1 - t):
                c = mix(c, lip_dark, 0.9)
            if abs(y - mouth_y) < 0.0022 and t > 0.85:
                c = mul(c, 0.7)  # corners
        c = mul(c, 1 - 0.1 * _g(x / 0.016, (y - 0.068) / 0.0035))  # under the lower lip
        # eyes
        for sg in (-1, 1):
            ex = sg * 0.0315
            dx = (x - ex) * sg  # + towards the outer corner
            t = dx / 0.0155
            if abs(t) < 1.0:
                ey = 0.153 + 0.0012 * t
                upper = ey + 0.0056 * (1 - t * t) ** 0.8 + 0.0007 * t
                lower = ey - 0.0042 * (1 - t * t) ** 0.9
                if lower < y < upper:
                    d = math.hypot(x - ex, (y - ey) * 1.0)
                    c = mul((0.84, 0.8, 0.74), 0.72 + 0.28 * (1 - t * t) + 0.05 * a)
                    if abs(t) > 0.82 and t < 0:
                        c = mix(c, (0.75, 0.45, 0.42), 0.6)  # tear duct
                    if d < 0.0058:
                        k = d / 0.0058
                        c = mul(iris, 0.55 + 0.7 * (1 - k) * (0.7 + 0.3 * a) + 0.2 * math.sin(math.atan2(y - ey, x - ex) * 9) * 0.3)
                        if k > 0.82:
                            c = mul(c, 0.5)  # limbal ring
                        if d < 0.0024:
                            c = (0.02, 0.02, 0.025)
                    if y > upper - 0.0022:
                        c = mul(c, 0.55)  # lid shadow on the eyeball
                    if math.hypot(x - ex - 0.0016, y - ey - 0.0017) < 0.0011:
                        c = (0.95, 0.95, 0.92)  # catchlight
                elif upper <= y < upper + 0.0016 + 0.0012 * max(0.0, t) * (2.0 if lashes else 1.0):
                    c = (0.06, 0.045, 0.04)  # lash line
                    if lashes and t > 0.55 and y > upper + 0.001:
                        c = (0.02, 0.02, 0.02)
                elif upper + 0.0016 < y < upper + 0.0065:
                    c = mul(c, 0.86 + 0.05 * a)  # upper lid
                    if abs(y - (upper + 0.0055)) < 0.0008:
                        c = mul(c, 0.8)  # crease
                elif lower - 0.0013 < y <= lower:
                    c = mix(c, (0.7, 0.45, 0.42), 0.4)  # lower lid rim
            # brows: thick inner head tapering outward; grief lifts the inner end
            tb = dx / 0.022
            if -0.85 < tb < 1.05:
                by = 0.1715 + 0.0035 * (1 - (tb - 0.25) ** 2) + 0.004 * grief * _clamp(-tb, 0, 1) - 0.002 * max(0.0, tb - 0.6)
                th = (0.0028 - 0.0014 * max(0.0, tb)) * brow_w
                if abs(y - by) < th:
                    k = 0.55 + 0.35 * r + 0.2 * math.sin(px * 3.1 + py)
                    c = mix(c, mul(hair, k), 0.85)
        # hair: hairline with temple recession, sideburns down to the ear
        hl = hairline - 0.006 * (1 - math.cos(x * 60)) + 0.01 * _g((ax - 0.05) / 0.012, 0)
        side = ax > 0.066 and y > 0.125 + (0.08 - ax) * 2
        if y > hl or side:
            c = mul(hair, 0.55 + 0.5 * a + 0.2 * math.sin(px * 1.9 + a * 7) * (0.6 + 0.4 * r))
        elif y > hl - 0.004:
            c = mix(c, mul(hair, 0.8), 0.45)
        if glasses:
            for sg in (-1, 1):
                ex = sg * 0.032
                e = ((x - ex) / 0.021) ** 4 + ((y - 0.152) / 0.012) ** 4
                if 0.75 < e < 1.0:
                    c = (0.05, 0.05, 0.06)
                elif e <= 0.75:
                    c = mix(c, (0.7, 0.75, 0.78), 0.12)  # lens sheen
            if ax < 0.012 and abs(y - 0.156) < 0.0012:
                c = (0.05, 0.05, 0.06)
        return c
    return fn


def t_flannel(x, y, a, b, r):
    dark = (x % 16 < 5) + (y % 16 < 5)
    c = [(0.55, 0.1, 0.08), (0.28, 0.06, 0.05), (0.06, 0.04, 0.04)][dark]
    if x % 16 == 10 or y % 16 == 10:
        c = mix(c, (0.5, 0.45, 0.3), 0.4)
    return mul(c, 0.7 + 0.4 * a + 0.05 * r)


def t_knit(x, y, a, b, r):
    rib = 0.75 + 0.25 * abs(math.sin(x * math.pi / 4))
    cable = abs(((x % 16) - 8) - abs(((y % 16) - 8))) < 1.5 and 4 < x % 32 < 28
    return mul((0.62, 0.46, 0.14), rib * (0.75 + 0.3 * a) * (1.12 if cable else 1) * (0.7 if b > 0.68 else 1))


def t_quilt(x, y, a, b, r):
    c = mul((0.17, 0.22, 0.14), 0.7 + 0.4 * a + 0.05 * r)
    if y % 10 == 0:
        c = mul(c, 0.5)
    elif y % 10 in (1, 9):
        c = mul(c, 0.8)
    return mul(c, 0.75) if b > 0.62 else c


def t_denim(x, y, a, b, r):
    tw = 0.9 + 0.1 * ((x + y) % 3 == 0)
    return mul(mix((0.14, 0.18, 0.27), (0.3, 0.34, 0.42), a * 0.8), tw * (0.8 + 0.2 * r) * (0.75 if b > 0.66 else 1))


def t_scrubs(x, y, a, b, r):
    c = mul((0.2, 0.42, 0.42), 0.75 + 0.3 * a + 0.05 * r)
    if x % 32 == 0:
        c = mul(c, 0.7)  # seam
    return mix(c, (0.3, 0.12, 0.08), 0.5) if b > 0.7 else c


def t_labcoat(x, y, a, b, r):
    c = mul((0.78, 0.78, 0.74), 0.8 + 0.2 * a + 0.03 * r)
    if b > 0.66:
        c = mix(c, (0.42, 0.12, 0.08), min(1.0, (b - 0.66) * 6))  # old blood
    elif b < 0.25:
        c = mul(c, 0.82)  # grime
    return c


def t_wool(x, y, a, b, r):
    herring = ((x + (y if (x // 4) % 2 else -y)) % 4) < 2
    return mul((0.3, 0.22, 0.14), (0.7 + 0.35 * a) * (1.08 if herring else 0.92) * (0.75 if b > 0.64 else 1))


def t_plum(x, y, a, b, r):
    return mul((0.26, 0.15, 0.2), (0.75 + 0.35 * a + 0.05 * r) * (1.1 if x % 8 == 0 else 1))


def t_cloth(x, y, a, b, r):
    return mul((0.8, 0.78, 0.74), 0.8 + 0.2 * a + 0.05 * r - (0.15 if b > 0.7 else 0))


def t_leather(x, y, a, b, r):
    c = mul((0.2, 0.13, 0.08), 0.65 + 0.5 * a + 0.05 * r)
    return mul(c, 1.3) if abs(b - 0.5) < 0.02 else c  # creases


def t_strands(x, y, a, b, r):
    v = 0.66 + 0.14 * math.sin(x * 1.7 + a * 8) + 0.08 * r + 0.08 * math.sin(x * 0.45 + y * 0.1) + 0.12 * (a - 0.5)
    return (v, v, v)


def t_beard(x, y, a, b, r):
    v = 0.5 + 0.35 * a + 0.2 * b + 0.25 * (r - 0.5)
    return (v, v, v)


def t_skin(x, y, a, b, r):
    v = 0.84 + 0.08 * a + 0.02 * (r - 0.5)
    return (v, v, v)


B.TEXTURES.update({
    "cb_flannel": t_flannel, "cb_knit": t_knit, "cb_quilt": t_quilt, "cb_denim": t_denim,
    "cb_scrubs": t_scrubs, "cb_labcoat": t_labcoat, "cb_wool": t_wool, "cb_plum": t_plum,
    "cb_cloth": t_cloth, "cb_leather": t_leather, "cb_strands": t_strands, "cb_skin": t_skin, "cb_beard": t_beard,
    "cb_face_owen": face_fn((0.72, 0.55, 0.44), (0.35, 0.22, 0.12), (0.25, 0.35, 0.2), (0.6, 0.38, 0.35),
                            hairline=0.215, stubble=0.45, bags=0.45, grief=1.2, brow_w=1.2),
    "cb_face_nora": face_fn((0.8, 0.64, 0.55), (0.3, 0.19, 0.11), (0.3, 0.32, 0.48), (0.66, 0.34, 0.36),
                            hairline=0.208, bags=0.6, grief=1.6, lashes=True, brow_w=0.8, blush=0.08),
    "cb_face_julian": face_fn((0.74, 0.6, 0.45), (0.06, 0.05, 0.05), (0.18, 0.12, 0.08), (0.58, 0.38, 0.35),
                              hairline=0.212, glasses=True, bags=0.3, grief=0.2, brow_w=1.1),
    "cb_face_silas": face_fn((0.7, 0.52, 0.44), (0.55, 0.53, 0.5), (0.3, 0.35, 0.4), (0.52, 0.32, 0.31),
                             hairline=0.2, beard=(0.55, 0.54, 0.5), bags=0.8, wrinkles=1.0, grief=1.0,
                             red_nose=0.55, brow_w=1.3),
})
for _f in ("owen", "nora", "julian", "silas"):
    B.TEX_SIZE["cb_face_" + _f] = 128

def lin(c):
    """glTF colour factors are linear; convert an sRGB colour so tints match the baked face textures."""
    return tuple(v ** 2.2 for v in c)


B.MATS.update({
    "cb_flannel": B.M("cb_flannel", scale=0.35), "cb_knit": B.M("cb_knit", scale=0.3),
    "cb_vest": B.M("cb_quilt", scale=0.4), "cb_denim": B.M("cb_denim", scale=0.4),
    "cb_scrubs": B.M("cb_scrubs", scale=0.5), "cb_labcoat": B.M("cb_labcoat", scale=0.6),
    "cb_coat": B.M("cb_wool", scale=0.4), "cb_skirt": B.M("cb_plum", scale=0.4),
    "cb_blouse": B.M("cb_cloth", scale=0.4), "cb_trousers": B.M("cb_cloth", lin((0.36, 0.34, 0.34)), 0.4),
    "cb_tights": B.M("cb_skin", lin((0.2, 0.16, 0.17)), 0.4), "cb_boot": B.M("cb_leather", scale=0.3),
    "cb_sole": B.M("plain", (0.07, 0.06, 0.05), 1), "cb_sneaker": B.M("cb_cloth", (0.9, 0.9, 0.9), 0.3),
    "cb_beanie": B.M("cb_knit", (0.3, 0.45, 0.35), 0.25), "cb_scarf": B.M("cb_knit", (0.7, 0.25, 0.25), 0.25),
    "cb_cap": B.M("cb_wool", (0.8, 0.9, 1.0), 0.3), "cb_bottle": B.M("plain", (0.12, 0.25, 0.1), 1, rough=0.2),
    "cb_wood": B.M("planks", (0.8, 0.7, 0.6), 0.5), "cb_steel": B.M("metal", (1.1, 1.1, 1.15), 0.3, rough=0.4),
    "cb_mask": B.M("plain", (0.2, 0.22, 0.2), 1), "cb_lens": B.M("plain", (0.25, 0.3, 0.3), 1, rough=0.1),
    "cb_badge": B.M("cb_cloth", (1.0, 1.0, 0.95), 0.1, fit=True),
    "cb_glove": B.M("cb_skin", lin((0.62, 0.75, 0.88)), 0.2, rough=0.4),
    "cb_raincoat": B.M("cb_cloth", (1.1, 0.9, 0.2), 0.3, rough=0.4),
    "cb_undershirt": B.M("cb_cloth", (0.72, 0.66, 0.52), 0.4),
    "cb_beard_silas": B.M("cb_beard", lin((0.8, 0.78, 0.74)), 0.15),
    "cb_lining": B.M("plain", (0.09, 0.08, 0.08), 1),
    "cb_string": B.M("plain", (0.6, 0.58, 0.5), 1),
})
for _f, _skin, _hair in (("owen", (0.72, 0.55, 0.44), (0.35, 0.22, 0.12)),
                         ("nora", (0.8, 0.64, 0.55), (0.3, 0.19, 0.11)),
                         ("julian", (0.74, 0.6, 0.45), (0.06, 0.05, 0.05)),
                         ("silas", (0.7, 0.52, 0.44), (0.55, 0.53, 0.5))):
    B.MATS["cb_face_" + _f] = B.M("cb_face_" + _f, fit=True)
    B.MATS["cb_skin_" + _f] = B.M("cb_skin", lin(_skin), 0.3)
    B.MATS["cb_hair_" + _f] = B.M("cb_strands", lin(mul(_hair, 1.25)), 0.12)


# ============================================================== characters

def m_owen():
    """The Woodsman: flannel, quilted vest, jeans, work boots, beanie, hunting bow, hatchet on the belt."""
    m = rig.skeleton("char_owen", 1.02)
    with m.push(scale=(1.02, 1.02, 1.02)):
        pelvis(m, "cb_denim", "m", belt="cb_boot")
        m.use("Hips")
        for s in (-1, 1):
            pocket(m, "cb_denim", 0.1, 0.1, (s * 0.085, -0.1, -0.105), (0, 180, 0))
        tors = torso(m, "cb_flannel", "m")
        collar(m, "cb_flannel", y=0.5, r=(0.068, 0.063), gap=1.1, h=0.035)
        # quilted vest: open shell over the shirt, zipper edge, pockets
        vest = grow([s for s in tors if 0.02 <= s[0] <= 0.5], 0.014)
        vest = [(-0.03, 0.16, 0.112)] + vest + [(0.52, 0.12, 0.085)]
        m.use("Spine")
        shell(m, "cb_vest", vest, *open_front(0.35), 16, power=2.4, lining="cb_lining")
        for s in (-1, 1):
            pocket(m, "cb_vest", 0.09, 0.07, (s * 0.1, 0.1, 0.122), (0, 0, 0), flap="cb_vest")
            m.box("iron", (0.005, 0.47, 0.006), (s * 0.028, 0.25, 0.108))
        m.use("Spine")
        tube(m, "cb_string", [(-0.05, 0.53, 0.04), (-0.04, 0.42, 0.11), (0.0, 0.33, 0.125), (0.04, 0.42, 0.11),
                              (0.05, 0.53, 0.04)], 0.003, seg=4)
        m.cyl("cb_steel", 0.009, 0.009, 0.045, (0, 0.3, 0.13), (0, 0, 90), seg=6)  # signal whistle
        # quiver with arrows across the back (strap diagonal)
        m.lathe("cb_boot", [(0.0, -0.2), (0.042, -0.2), (0.046, 0.0), (0.05, 0.2), (0.046, 0.21)], (0.06, 0.26, -0.15),
                (0, 0, -22), seg=8)
        for i, (dx, dz) in enumerate(((-0.01, 0.0), (0.012, 0.01), (0.0, -0.015), (0.02, -0.008))):
            with m.push((0.06, 0.26, -0.15), (0, 0, -22)):
                m.cyl("cb_wood", 0.004, 0.004, 0.14, (dx, 0.18, dz), seg=4)
                m.box("cb_sole" if i % 2 else "red", (0.002, 0.05, 0.016), (dx, 0.3, dz))
        tube(m, "cb_boot", [(0.19, 0.44, -0.04), (0.12, 0.3, 0.12), (-0.05, 0.08, 0.12), (-0.15, -0.02, 0.0),
                            (-0.1, 0.1, -0.12), (0.19, 0.44, -0.04)], 0.009, seg=4)

        def hair_hat(m):
            m.use("Head")
            scalp(m, "cb_hair_owen", 0.2, 0.075, off=0.006, side_y=0.13,
                  bulk=lambda a, t: 0.006 * (1 - t) if math.sin(a) < 0 else 0.0)
            scalp(m, "cb_beanie", 0.207, 0.135, off=0.016, crown_lift=0.006, side_y=0.175, rows=6,
                  bulk=lambda a, t: 0.004 * math.sin(t * math.pi))
            scalp(m, "cb_beanie", 0.2, 0.128, off=0.022, side_y=0.168, rows=1,
                  bulk=lambda a, t: 0.0)  # folded brim
            with with_head(m):
                m.box("cb_boot", (0.04, 0.025, 0.006), (0.0, 0.228, 0.101), (-20, 0, 0))  # patch
        hair_hat(m)
        head(m, "owen", jaw=1.05, neck_r=0.055)
        arms(m, "owen", "cb_flannel", forearm="cb_skin_owen", rolled="cb_flannel")
        # (his hunting bow is item_bow, held by the game with arm IK: scripts/enemy.gd _bow_arms)
        legs(m, "cb_denim", cuff=None)
        for k in ("L", "R"):
            m.use("Thigh" + k)
            m.ellipsoid("cb_denim", (0.05, 0.045, 0.012), (0, -0.37, 0.058), seg=8, rings=4)  # worn knee
        shoes(m, "cb_boot", boot="cb_boot", boot_h=0.15, lace="cb_sole", width=1.05)
        m.use("Hips")  # hatchet hanging on the right hip
        m.lathe("cb_wood", [(0, -0.36), (0.015, -0.355), (0.013, 0.0), (0.016, 0.02), (0, 0.025)], (-0.18, 0.02, 0.04),
                (0, 0, -6), seg=6)
        m.loft("cb_steel", [(0, 0.0, 0.0), (0.005, 0.012, 0.02), (0.06, 0.008, 0.02), (0.065, 0, 0)],
               (-0.14, -0.3, 0.11), (0, 90, 90), seg=6, power=4)
    return m


def m_nora():
    """The Teacher: long hair and bun, mustard cardigan over a blouse, long skirt, scissors, Lily's raincoat."""
    m = rig.skeleton("char_nora", 0.93)
    with m.push(scale=(0.93, 0.93, 0.93)):
        pelvis(m, "cb_skirt", "f")
        tors = torso(m, "cb_blouse", "f", bust=0.03)
        collar(m, "cb_blouse", y=0.5, r=(0.056, 0.05), gap=1.1, flare=0.012, h=0.028, tilt=-10)
        m.use("Spine")
        card = grow([s for s in tors if -0.05 <= s[0] <= 0.5], 0.012)
        card = [(-0.12, 0.16, 0.112)] + card + [(0.515, 0.115, 0.08)]
        a0, a1 = open_front(0.55)
        shell(m, "cb_knit", card, a0, a1, 16, power=2.4, lining="cb_lining")
        for i in range(5):
            y = 0.02 + i * 0.075
            z = [s for s in card if s[0] >= y][0][2] + 0.004
            m.ellipsoid("cb_boot", (0.009, 0.009, 0.004), (-0.07, y, z - 0.01), seg=6, rings=4)
        pocket(m, "cb_knit", 0.1, 0.09, (0.12, -0.06, 0.1))
        m.cyl("white", 0.006, 0.006, 0.1, (0.13, -0.02, 0.105), seg=4)  # syringe in the pocket
        tube(m, "cb_steel", [(-0.045, 0.53, 0.04), (-0.03, 0.44, 0.1), (0.0, 0.4, 0.118), (0.03, 0.44, 0.1),
                             (0.045, 0.53, 0.04)], 0.0022, seg=3)
        m.cyl("cb_steel", 0.014, 0.014, 0.007, (0, 0.388, 0.122), (90, 0, 0), seg=8)  # Lily's locket
        # long A-line skirt from the waist to mid-shin, with pleat ridges
        m.use("Hips")
        m.lathe("cb_skirt", [(0.27, -0.7), (0.27, -0.68), (0.24, -0.45), (0.2, -0.2), (0.175, -0.05), (0.16, 0.06),
                             (0.14, 0.1)], scale=(1.0, 1, 0.78), seg=16)
        m.lathe("cb_lining", [(0.14, 0.09), (0.16, 0.05), (0.2, -0.2), (0.24, -0.45), (0.27, -0.69)], scale=(1.0, 1, 0.78),
                seg=18)
        for i in range(5):
            ang = FRONT + (i - 2) * 0.45
            px, pz = math.cos(ang), math.sin(ang)
            m.loft("cb_skirt", [(-0.7, 0, 0, 0.275 * px, 0.275 * 0.78 * pz), (-0.69, 0.012, 0.012, 0.275 * px, 0.275 * 0.78 * pz),
                                (-0.25, 0.006, 0.006, 0.205 * px, 0.205 * 0.78 * pz), (-0.12, 0, 0, 0.19 * px, 0.19 * 0.78 * pz)],
                   seg=4)

        def hair(m):
            m.use("Head")
            bulk = lambda a, t: 0.012 * (1 - t) * (1 if math.sin(a) < 0.3 else 0.3)
            scalp(m, "cb_hair_nora", 0.207, 0.06, off=0.008, side_y=0.12, bulk=bulk)
            with with_head(m):
                # long hair falling behind the shoulders, open at the face
                a0, a1 = FRONT - 1.35, FRONT - TAU + 1.35
                shell(m, "cb_hair_nora", [(-0.14, 0.08, 0.05, 0, -0.07), (-0.05, 0.088, 0.075, 0, -0.045),
                                          (0.05, 0.088, 0.1, 0, -0.02), (0.14, 0.09, 0.112, 0, -0.01),
                                          (0.2, 0.087, 0.11, 0, -0.005)], a0, a1, 10, lining="cb_hair_nora")
                m.ellipsoid("cb_hair_nora", (0.042, 0.036, 0.034), (0, 0.2, -0.12), (-30, 0, 0), seg=8, rings=5)  # bun
                # side-swept fringe and a loose strand by the cheek
                m.ellipsoid("cb_hair_nora", (0.05, 0.01, 0.028), (0.02, 0.222, 0.078), (-28, 0, -12), seg=8, rings=4)
                m.capsule("cb_hair_nora", 0.009, 0.005, 0.14, (0.074, 0.19, 0.045), (0, 0, 3), seg=5)
                m.ellipsoid("cb_scarf", (0.016, 0.005, 0.008), (-0.045, 0.228, 0.083), (0, 0, 15), seg=6, rings=4)  # clip
        hair(m)
        head(m, "nora", jaw=0.93, neck_r=0.045)
        arms(m, "nora", "cb_knit", r=0.88, cuff="cb_knit")
        m.use("HandL")  # Lily's little yellow raincoat, clutched in her left hand
        m.loft("cb_raincoat", [(-0.36, 0.1, 0.03, 0.02, 0.02), (-0.3, 0.1, 0.035, 0.02, 0.02), (-0.18, 0.07, 0.035, 0.01, 0.02),
                               (-0.09, 0.03, 0.03, 0, 0.01), (-0.06, 0, 0, 0, 0.01)], seg=8, power=2.5)
        m.capsule("cb_raincoat", 0.02, 0.016, 0.2, (0.0, -0.1, 0.07), (0, 0, 8), seg=6)  # dangling sleeve
        m.use("HandR")  # scissors, blades down
        for s in (-1, 1):
            m.lathe("iron", [(0.012, -0.004), (0.02, 0.0), (0.012, 0.004)], (0, -0.05, 0.02 + s * 0.02), (0, 0, 90), seg=8)
            m.loft("cb_steel", [(-0.21, 0, 0), (-0.2, 0.002, 0.004), (-0.08, 0.004, 0.009), (-0.07, 0, 0)],
                   (0, 0, 0.022 + s * 0.004), (0, 0, s * 2), seg=4)
        legs(m, "cb_tights", r=0.85)
        shoes(m, "cb_boot", boot="cb_boot", boot_h=0.09, heel=0.03, width=0.85, toe=0.17)
    return m


def m_julian():
    """The Medic: scrubs, blood-stained lab coat, glasses, stethoscope, gas mask on the chest, scalpel."""
    m = rig.skeleton("char_julian", 1.0)
    pelvis(m, "cb_scrubs", "m")
    tors = torso(m, "cb_scrubs", "m")
    m.use("Spine")
    m.loft("cb_skin_julian", [(0.43, 0, 0, 0, 0.1), (0.44, 0.012, 0.004, 0, 0.1), (0.52, 0.045, 0.01, 0, 0.075),
                              (0.53, 0, 0, 0, 0.07)], seg=6, power=1.3)  # V-neck skin
    coat = grow([s for s in tors if -0.1 <= s[0] <= 0.5], 0.016)
    coat = coat + [(0.515, 0.14, 0.098), (0.535, 0.1, 0.075)]
    shell(m, "cb_labcoat", coat, *open_front(0.5), 18, power=2.4, lining="cb_lining")
    collar(m, "cb_labcoat", y=0.47, r=(0.085, 0.078), gap=1.4, flare=0.03, h=0.06)
    pocket(m, "cb_labcoat", 0.085, 0.07, (0.115, 0.24, 0.13))
    for i in range(2):
        m.cyl("red" if i else "iron", 0.005, 0.005, 0.07, (0.1 + i * 0.02, 0.3, 0.118), seg=4)
    m.box("cb_badge", (0.06, 0.08, 0.005), (-0.125, 0.27, 0.116))
    tube(m, "rubber", [(-0.07, 0.53, 0.02), (-0.08, 0.46, 0.1), (-0.05, 0.36, 0.13), (-0.04, 0.3, 0.13)], 0.006)
    tube(m, "rubber", [(0.07, 0.53, 0.02), (0.08, 0.46, 0.1), (0.05, 0.36, 0.13), (0.03, 0.28, 0.135)], 0.006)
    m.cyl("cb_steel", 0.018, 0.018, 0.01, (0.03, 0.27, 0.132), (90, 0, 0), seg=8)
    # gas mask hanging at the chest from a strap
    m.ellipsoid("cb_mask", (0.07, 0.075, 0.045), (0, 0.15, 0.14), (15, 0, 0), seg=10, rings=6)
    for s in (-1, 1):
        m.cyl("cb_lens", 0.024, 0.024, 0.01, (s * 0.032, 0.175, 0.175), (78, 0, 0), seg=8)
    m.lathe("cb_mask", [(0.0, 0.0), (0.028, 0.0), (0.028, 0.035), (0.0, 0.035)], (0, 0.1, 0.17), (60, 0, 0), seg=8)
    tube(m, "rubber", [(-0.06, 0.18, 0.14), (-0.08, 0.35, 0.1), (-0.06, 0.52, 0.03)], 0.005, seg=4)
    tube(m, "rubber", [(0.06, 0.18, 0.14), (0.08, 0.35, 0.1), (0.06, 0.52, 0.03)], 0.005, seg=4)
    # coat skirt from the hips, open at the front
    m.use("Hips")
    tails = [(-0.56, 0.2, 0.15), (-0.3, 0.19, 0.135), (-0.1, 0.182, 0.125), (0.03, 0.172, 0.118)]
    shell(m, "cb_labcoat", tails, *open_front(0.45), 16, power=2.4, lining="cb_lining")
    for s in (-1, 1):
        pocket(m, "cb_labcoat", 0.1, 0.1, (s * 0.15, -0.3, 0.13), (0, s * 25, 0), flap="cb_labcoat")
    m.cyl("cb_lens", 0.007, 0.007, 0.09, (0.14, -0.2, 0.115), seg=4)  # syringe in the pocket

    def hair(m):
        m.use("Head")
        bulk = lambda a, t: 0.012 * math.sin(t * math.pi) + (0.008 * t if math.cos(a) > 0 else 0.0)
        scalp(m, "cb_hair_julian", 0.212, 0.085, off=0.006, side_y=0.155, crown_lift=0.008, bulk=bulk)
        with with_head(m):
            m.ellipsoid("cb_hair_julian", (0.05, 0.016, 0.03), (0.018, 0.232, 0.07), (-20, 0, -10), seg=10, rings=5)  # quiff
            for s in (-1, 1):  # glasses temples, ear to frame corner
                tube(m, "iron", [head_pt(FRONT + s * a, 0.156, off=0.004, sculpt=False) for a in (1.62, 1.2, 0.75, 0.55)],
                     0.0018, seg=3)
    hair(m)
    head(m, "julian", jaw=0.97)
    arms(m, "julian", "cb_labcoat", hand="cb_glove", cuff="cb_labcoat", r=1.08)
    m.use("HandR")  # scalpel
    m.cyl("cb_steel", 0.005, 0.005, 0.09, (0, -0.17, 0.03), seg=5)
    m.loft("cb_steel", [(-0.21, 0, 0), (-0.2, 0.001, 0.006), (-0.17, 0.001, 0.004), (-0.168, 0, 0)], (0, 0, 0.03), seg=4)
    m.use("HandL")  # clipboard
    m.box("cb_boot", (0.012, 0.3, 0.22), (0.028, -0.12, 0.05))
    m.box("white", (0.004, 0.26, 0.19), (0.036, -0.13, 0.05))
    m.box("cb_steel", (0.012, 0.02, 0.06), (0.036, 0.02, 0.05))
    legs(m, "cb_scrubs", cuff="cb_scrubs")
    shoes(m, "cb_sneaker", sole="white", lace="white")
    return m


def m_silas():
    """Bar regular: grey beard, flat cap, old wool overcoat, scarf, beer belly, bottle in hand."""
    m = rig.skeleton("char_silas", 0.96, {"Head": (0, 0.54, 0.04)})
    with m.push(scale=(0.96, 0.96, 0.96)):
        belly = 0.045
        pelvis(m, "cb_trousers", "m", belly=0.02, belt="cb_boot")
        tors = torso(m, "cb_undershirt", "m", belly=belly)
        m.use("Spine")
        for i in range(4):
            m.ellipsoid("iron", (0.006, 0.006, 0.003), (0, 0.08 + i * 0.09, [s for s in tors if s[0] >= 0.08 + i * 0.09][0][2]
                                                        + ([s for s in tors if s[0] >= 0.08 + i * 0.09][0][4]
                                                           if len([s for s in tors if s[0] >= 0.08 + i * 0.09][0]) > 3 else 0)),
                        seg=5, rings=3)
        coat = grow([s for s in tors if -0.1 <= s[0] <= 0.5], 0.02, 0.022)
        coat = coat + [(0.52, 0.13, 0.09)]
        shell(m, "cb_coat", coat, *open_front(0.6), 18, power=2.4, lining="cb_lining")
        collar(m, "cb_coat", y=0.44, r=(0.1, 0.09), gap=1.0, flare=0.04, h=0.09, tilt=-4)
        for i in range(3):
            m.ellipsoid("iron", (0.011, 0.011, 0.005), (-0.13, 0.33 - i * 0.12, 0.13), seg=6, rings=4)
        # scarf: thick ring round the neck with one end hanging down the front
        m.lathe("cb_scarf", [(0.075, 0.44), (0.095, 0.46), (0.098, 0.5), (0.085, 0.53), (0.065, 0.54)], (0, 0, 0.01),
                scale=(1, 1, 0.9), seg=12)
        m.loft("cb_scarf", [(0.14, 0, 0, 0.05, 0.155), (0.15, 0.034, 0.008, 0.05, 0.155), (0.44, 0.03, 0.01, 0.055, 0.13),
                            (0.47, 0, 0, 0.055, 0.12)], seg=8, power=4)
        for i in range(3):
            m.box("cb_scarf", (0.01, 0.035, 0.006), (0.032 + i * 0.018, 0.13, 0.158))
        m.use("Hips")
        tails = [(-0.6, 0.23, 0.18), (-0.35, 0.215, 0.165), (-0.12, 0.2, 0.15), (0.05, 0.19, 0.145)]
        shell(m, "cb_coat", tails, *open_front(0.55), 16, power=2.4, lining="cb_lining")
        for s in (-1, 1):
            pocket(m, "cb_coat", 0.12, 0.11, (s * 0.17, -0.34, 0.15), (0, s * 28, 0), flap="cb_coat")

        def cap(m):
            m.use("Head")
            scalp(m, "cb_beard_silas", 0.18, 0.07, off=0.006, side_y=0.12,
                  bulk=lambda a, t: 0.008 * (1 - t) if math.sin(a) < 0 else 0.0)
            scalp(m, "cb_cap", 0.21, 0.165, off=0.014, side_y=0.19, crown_lift=-0.004, rows=4,
                  bulk=lambda a, t: 0.02 * t * (1 if math.sin(a) > 0 else 0.3))
            with with_head(m):
                m.loft("cb_cap", [(0, 0, 0), (0.002, 0.068, 0.034), (0.007, 0.064, 0.032), (0.009, 0, 0)],
                       (0, 0.197, 0.098), (-12, 0, 0), seg=12, power=2.2)  # brim
                # beard volume over the jaw and chin, moustache over the lip
                grid = []
                for y in (0.02, 0.04, 0.06, 0.075, 0.09, 0.105, 0.12, 0.135):
                    row = []
                    for a in _angles(-math.pi + 0.15, -TAU - 0.15, 10):
                        x = math.cos(a)
                        th = 0.011 * (1 - _smooth(0.09, 0.12, y)) if abs(x) > 0.75 else 0.012 * (1 - _smooth(0.06, 0.075, y))
                        row.append(head_pt(a, y, off=th + 0.001))
                    grid.append(row)
                grid[0] = [(p[0] * 0.6, 0.012, p[2] * 0.6 + 0.02) for p in grid[1]]
                m.surface("cb_beard_silas", grid)
                m.loft("cb_beard_silas", [(0.086, 0, 0, 0, 0.104), (0.087, 0.022, 0.007, 0, 0.106), (0.095, 0.026, 0.009, 0, 0.108),
                                         (0.1, 0.012, 0.006, 0, 0.108), (0.102, 0, 0, 0, 0.106)], seg=10)
        cap(m)
        head(m, "silas", jaw=1.05, neck_r=0.057)
        arms(m, "silas", "cb_coat", cuff="cb_coat", r=1.12, cuff_y=-0.22)
        m.use("HandL")  # bottle held by the neck, body hanging below the fist
        m.lathe("cb_bottle", [(0, -0.34), (0.034, -0.34), (0.036, -0.2), (0.03, -0.17), (0.013, -0.12), (0.012, -0.02),
                              (0.015, -0.015), (0, -0.01)], (0, 0, 0.03), seg=10)
        m.lathe("cb_blouse", [(0.037, -0.3), (0.037, -0.23)], (0, 0, 0.03), seg=10)  # label
        legs(m, "cb_trousers", cuff="cb_trousers")
        shoes(m, "cb_boot", boot="cb_boot", boot_h=0.07, width=1.05)
    return m


MODELS = [m_owen, m_nora, m_julian, m_silas]
