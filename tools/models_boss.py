"""Boss: a 2.7 m pitch-black, heavily muscled humanoid with burning red eyes and a
two-handed sword built from fused skulls and vertebrae (held in the right hand).

Shared rig (tools/rig.py) at scale 1.5 with widened shoulders/hips; geometry lives in
joint-local space so scripts/humanoid_anim.gd animates it like any other character.
"""
import math
import random

import build_assets as B
import rig

mix, mul = B.mix, B.mul


# ============================================================== textures

def tex(name, size=64):
    def deco(fn):
        B.TEXTURES[name] = fn
        if size != 64:
            B.TEX_SIZE[name] = size
        return fn
    return deco


_PTS = [(random.Random(7 + i).random() * 64, random.Random(99 + i).random() * 64) for i in range(9)]


def _cell_edge(x, y):
    """Distance (px) to the nearest Voronoi border on a wrapping 64px tile -> cracked-skin plates."""
    d = sorted(min(abs(x - px), 64 - abs(x - px)) ** 2 + min(abs(y - py), 64 - abs(y - py)) ** 2 for px, py in _PTS)
    return math.sqrt(d[1]) - math.sqrt(d[0])


def _skin(x, y, a, b, r):
    """Muscle striations + mottling + raised veins, as a dark-grey sRGB value (~0.03-0.06 linear)."""
    fib = 0.5 + 0.5 * math.sin(y * 0.8 + a * 7 + 0.3 * math.sin(x * 0.35))
    v = 0.17 + 0.08 * a + 0.03 * fib + 0.01 * r
    if abs(b - 0.52) < 0.012:
        v += 0.06  # raised vein catching the light
    return v


@tex("bx_skin")
def _(x, y, a, b, r):
    v = _skin(x, y, a, b, r)
    return (v, v * 0.97, v * 1.03)


@tex("bx_crack")
def _(x, y, a, b, r):
    """Same skin, torn by cracks that smoulder dark red (emissive material; the skin itself stays ~black)."""
    e = _cell_edge(x, y)
    if e < 0.8 and b > 0.45:
        return (0.3 + 0.2 * a, 0.02, 0.0)
    v = _skin(x, y, a, b, r) * (0.3 if e < 2.0 and b > 0.45 else 0.5)
    return (v, v * 0.95, v)


@tex("bx_bone")
def _(x, y, a, b, r):
    c = mix((0.8, 0.74, 0.58), (0.5, 0.42, 0.28), a)  # yellowed bone to grime
    if b > 0.66:
        c = mul(c, 0.75)  # dirt in the pores
    if abs(a - 0.52) < 0.008:
        c = mul(c, 0.35)  # hairline cracks
    if b < 0.3:
        c = mix(c, (0.3, 0.08, 0.05), 0.3)  # old blood
    return mul(c, 0.9 + 0.12 * r)


@tex("bx_plain")
def _(x, y, a, b, r):
    return mul((1, 1, 1), 0.85 + 0.15 * a)


def MAT(name, tex_, color=(1, 1, 1), scale=0.5, **kw):
    B.MATS[name] = B.M(tex_, color, scale, **kw)


MAT("bx_skin", "bx_skin", scale=0.3, rough=0.5)  # matte charcoal with a wet sheen
MAT("bx_crack", "bx_crack", scale=0.35, emit=1.0, rough=0.5)  # ember seams
MAT("bx_claw", "bx_plain", (0.02, 0.018, 0.018), 1, rough=0.25)
MAT("bx_bone", "bx_bone", scale=0.25, rough=0.8)
MAT("bx_socket", "bx_plain", (0.03, 0.02, 0.015), 1)
MAT("bx_eye", "bx_plain", (1.0, 0.01, 0.0), 1, emit=4.0)
MAT("bx_ember", "bx_plain", (0.8, 0.03, 0.0), 1, emit=1.5)


# ============================================================== parts

S = "bx_skin"


def ell(m, r, pos, rot=(0, 0, 0), mat=S, seg=10, rings=6):
    m.ellipsoid(mat, r, pos, rot, seg=seg, rings=rings)


def spike(m, mat, r, length, pos, rot=(0, 0, 0), seg=5):
    """Tapered cone from pos along local -Y (claws, rib tips, jagged teeth)."""
    m.cyl(mat, r, 0.0, length, pos, (180 + rot[0], rot[1], rot[2]), seg=seg, caps=False)


def skull(m, s, seg=8):
    """Bone skull centred on the origin, face toward local +Z, s = cranium radius."""
    ell(m, (s, s * 0.95, s * 1.05), (0, 0.05 * s, -s * 0.05), mat="bx_bone", seg=seg, rings=5)
    ell(m, (s * 0.62, s * 0.4, s * 0.55), (0, -s * 0.72, s * 0.35), mat="bx_bone", seg=6, rings=4)  # jaw
    for sx in (1, -1):
        ell(m, (s * 0.28, s * 0.24, s * 0.14), (sx * s * 0.37, -s * 0.08, s * 0.86), mat="bx_socket", seg=5, rings=3)
    ell(m, (s * 0.1, s * 0.15, s * 0.08), (0, -s * 0.42, s * 0.93), mat="bx_socket", seg=4, rings=2)  # nose hole
    m.box("bx_socket", (s * 0.7, s * 0.05, s * 0.1), (0, -s * 0.66, s * 0.8))  # gap between the teeth rows


def vertebra(m, s):
    m.lathe("bx_bone", [(s * 0.55, -s * 0.3), (s, -s * 0.12), (s, s * 0.12), (s * 0.55, s * 0.3)], seg=7)
    for sx in (1, -1):  # transverse processes: jagged side teeth along the blade
        spike(m, "bx_bone", s * 0.28, s * 1.5, (sx * s * 0.7, 0, 0), (0, 0, sx * 100))


def sword(m):
    """Built along +Y from the grip centre; skulls face +Z (the flat). ~2.4 m overall, ~1.95 m blade."""
    m.lathe("bx_bone", [(0.03, -0.27), (0.034, -0.1), (0.032, 0.1), (0.036, 0.2)], seg=7)  # grip shaft
    for k in range(4):
        with m.push((0, -0.19 + k * 0.1, 0)):
            m.lathe("bx_bone", [(0.036, -0.02), (0.052, 0), (0.036, 0.022)], seg=7)  # vertebra rings
    with m.push((0, -0.35, 0), (180, 0, 0)):
        skull(m, 0.075)  # pommel skull, upside down
    # crossguard: ribcage splayed sideways from a central skull, rib tips hooking up the blade
    with m.push((0, 0.3, 0.02)):
        skull(m, 0.11)
    for sx in (1, -1):
        for w, dy in ((0.4, 0.0), (0.32, 0.09), (0.22, 0.17)):
            m.cyl("bx_bone", 0.024, 0.018, w * 0.6, (sx * 0.05, 0.22 + dy, 0), (0, 0, sx * -72), seg=5)
            with m.push((sx * (0.05 + w * 0.57), 0.22 + dy + w * 0.19, 0)):
                ell(m, (0.022, 0.022, 0.022), (0, 0, 0), mat="bx_bone", seg=5, rings=3)
                spike(m, "bx_bone", 0.02, w * 0.5, (0, 0, 0), (0, 0, sx * 150))
    # blade: jagged bone plate behind a spine of fused skulls shrinking to the point
    secs = []
    for i in range(11):
        t = i / 11
        w = 0.1 * (1 - t) ** 0.7 + (0.05 * (1 - t) if i % 2 else 0.0)
        secs.append((0.36 + i * 0.17, w, 0.03 * (1 - 0.6 * t)))
    secs += [(2.28, 0.012, 0.01), (2.3, 0.0, 0.0)]
    m.loft("bx_bone", secs, seg=8, power=1.3)
    sizes = (0.1, 0.088, 0.077, 0.067, 0.058, 0.05)
    y = 0.52
    for i, s in enumerate(sizes):
        with m.push((0, y, 0.015)):
            skull(m, s)
        if i < len(sizes) - 1:
            with m.push((0, y + s * 1.05 + 0.04, 0)):
                vertebra(m, s * 0.55)
        y += s * 2.1 + 0.08


def muscle_body(m):
    # ---- pelvis + glutes
    m.use("Hips")
    m.loft(S, [(-0.3, 0.14, 0.11), (-0.24, 0.25, 0.18), (-0.1, 0.28, 0.19), (0.04, 0.26, 0.19), (0.14, 0.25, 0.185)],
           seg=14, power=2.4)
    for sx in (1, -1):
        ell(m, (0.15, 0.16, 0.12), (sx * 0.12, -0.13, -0.09))  # glutes
        ell(m, (0.07, 0.14, 0.07), (sx * 0.2, 0.0, 0.08), (0, 0, sx * -28), seg=8)  # obliques over the hip
    # ---- torso: V-taper core with smouldering cracks
    m.use("Spine")
    m.loft("bx_crack", [(0.0, 0.25, 0.185), (0.14, 0.26, 0.19), (0.3, 0.33, 0.21), (0.46, 0.42, 0.23),
                        (0.6, 0.44, 0.22), (0.7, 0.36, 0.19), (0.78, 0.2, 0.15), (0.84, 0.12, 0.12)], seg=16, power=2.6)
    for sx in (1, -1):
        ell(m, (0.17, 0.12, 0.075), (sx * 0.135, 0.52, 0.155), (0, sx * 14, sx * -10))  # pecs
        ell(m, (0.1, 0.25, 0.12), (sx * 0.3, 0.4, -0.05), (0, 0, sx * 20))  # lats
        ell(m, (0.15, 0.21, 0.07), (sx * 0.13, 0.5, -0.155), (0, 0, sx * 12), seg=8)  # back slabs
        ell(m, (0.2, 0.1, 0.13), (sx * 0.17, 0.74, -0.03), (0, 0, sx * 20))  # traps
        ell(m, (0.06, 0.12, 0.05), (sx * 0.22, 0.24, 0.13), (0, sx * 30, sx * -12), seg=8)  # serratus
        for k in range(3):
            ell(m, (0.058, 0.05, 0.03), (sx * 0.06, 0.1 + k * 0.11, 0.178), seg=6, rings=4)  # abs
    # ---- neck + head (bald, elongated skull, heavy brow, no mouth: a faint ember slit)
    m.use("Head")
    m.lathe(S, [(0.16, -0.14), (0.135, -0.02), (0.11, 0.08), (0.1, 0.15)], scale=(1.1, 1, 1), seg=12)
    for sx in (1, -1):
        ell(m, (0.045, 0.14, 0.045), (sx * 0.065, 0.0, 0.05), (28, 0, sx * -18), seg=6)  # neck cords
    with m.push((0, 0.02, 0.0), (0, 0, 0), (1.15, 1.15, 1.15)):
        m.loft(S, [(0.02, 0.05, 0.05, 0, 0.08), (0.05, 0.085, 0.1, 0, 0.05), (0.12, 0.1, 0.12, 0, 0.03),
                   (0.19, 0.115, 0.135, 0, 0.01), (0.25, 0.12, 0.15, 0, -0.02), (0.31, 0.115, 0.16, 0, -0.05),
                   (0.37, 0.1, 0.15, 0, -0.085), (0.42, 0.07, 0.11, 0, -0.115), (0.45, 0.0, 0.0, 0, -0.125)],
               seg=14, power=2.2)  # bald skull swept back and up
        for sx in (1, -1):
            ell(m, (0.065, 0.022, 0.035), (sx * 0.048, 0.214, 0.126), (-8, 0, sx * 22), seg=8, rings=5)  # scowling brow
            ell(m, (0.04, 0.018, 0.03), (sx * 0.078, 0.15, 0.11), (0, 0, sx * 25), seg=6, rings=4)  # cheekbones
            ell(m, (0.032, 0.011, 0.016), (sx * 0.047, 0.194, 0.14), (0, 0, sx * 18), mat="bx_eye", seg=8, rings=4)
        ell(m, (0.016, 0.035, 0.018), (0, 0.16, 0.143), (12, 0, 0), seg=6, rings=4)  # nose ridge
        m.box("bx_ember", (0.06, 0.004, 0.01), (0, 0.085, 0.148))  # lipless slit


def limbs(m):
    def arm(side, sx):
        m.use("UpperArm" + side)
        ell(m, (0.14, 0.2, 0.135), (sx * 0.02, -0.08, 0), (0, 0, sx * -8), seg=12)  # deltoid
        m.capsule(S, 0.125, 0.1, 0.36, (0, -0.02, 0), seg=10)
        ell(m, (0.09, 0.14, 0.085), (sx * 0.01, -0.22, 0.06))  # biceps
        ell(m, (0.095, 0.16, 0.08), (0, -0.19, -0.06))  # triceps
        m.use("Forearm" + side)
        ell(m, (0.1, 0.1, 0.1), (0, 0, 0), seg=8, rings=5)  # elbow
        m.capsule("bx_crack", 0.11, 0.07, 0.34, (0, -0.02, 0), seg=10)
        ell(m, (0.115, 0.13, 0.1), (sx * 0.01, -0.09, 0.01))  # forearm bulk
        m.use("Hand" + side)
        ell(m, (0.062, 0.06, 0.06), (0, 0, 0), seg=6, rings=4)  # wrist
        m.loft(S, [(-0.16, 0.04, 0.075), (-0.08, 0.05, 0.085), (0.0, 0.05, 0.065)], seg=8, power=3)  # palm
        fist = side == "R"  # right fist wraps the sword grip
        for k in range(4):
            z = (k - 1.5) * 0.042
            with m.push((-sx * 0.01, -0.15, z), (0, 0, -sx * (100 if fist else 18))):
                m.cyl(S, 0.022, 0.018, 0.07, (0, -0.07, 0), seg=5)
                with m.push((0, -0.07, 0), (0, 0, -sx * (85 if fist else 30))):
                    m.cyl(S, 0.018, 0.013, 0.05, (0, -0.05, 0), seg=5)
                    spike(m, "bx_claw", 0.013, 0.06, (0, -0.05, 0))
        with m.push((-sx * 0.03, -0.06, 0.07), (-40, 0, -sx * 30)):  # thumb
            m.cyl(S, 0.026, 0.018, 0.09, (0, -0.09, 0), seg=5)
            spike(m, "bx_claw", 0.015, 0.06, (0, -0.09, 0))

    def leg(side, sx):
        m.use("Thigh" + side)
        m.capsule(S, 0.19, 0.12, 0.56, (0, 0.02, 0), seg=12)
        ell(m, (0.155, 0.27, 0.13), (sx * 0.02, -0.3, 0.06), (0, 0, sx * 6))  # quads
        ell(m, (0.075, 0.1, 0.065), (-sx * 0.06, -0.52, 0.065), seg=8)  # teardrop
        ell(m, (0.12, 0.24, 0.1), (0, -0.28, -0.06))  # hamstrings
        m.use("Shin" + side)
        ell(m, (0.12, 0.12, 0.12), (0, 0, 0), seg=10, rings=5)  # knee
        m.capsule(S, 0.12, 0.08, 0.55, (0, -0.02, 0), seg=10)
        ell(m, (0.11, 0.2, 0.1), (0, -0.19, -0.055))  # calves
        m.use("Foot" + side)
        ell(m, (0.085, 0.085, 0.085), (0, 0, 0), seg=8, rings=4)  # ankle
        m.loft(S, [(-0.11, 0.0, 0.0), (-0.08, 0.08, 0.04), (0.0, 0.1, 0.07), (0.18, 0.09, 0.065), (0.24, 0.0, 0.0)],
               (0, -0.005, 0.08), (90, 0, 0), seg=10, power=2.6)  # bare foot, lofted along +Z
        for k in range(4):
            spike(m, "bx_claw", 0.017, 0.07, ((k - 1.5) * 0.042, -0.035, 0.3), (-90, 0, 0))

    rig.mirror(arm)
    rig.mirror(leg)


def char_boss():
    m = rig.skeleton("char_boss", 1.42, {  # ~2.8 m; broad shoulders and hips
        "UpperArmL": (0.27, 0.47, 0), "UpperArmR": (-0.27, 0.47, 0),
        "ThighL": (0.12, -0.05, 0), "ThighR": (-0.12, -0.05, 0),
    })
    muscle_body(m)
    limbs(m)
    m.use("HandR")  # grip in the fist, blade down-forward so the point hangs near the ground ahead
    with m.push((0.0, -0.17, 0.0), (118, 0, 0)):
        with m.push((0, 0, 0), (0, 180, 0)):
            sword(m)
    return m


MODELS = [char_boss]
