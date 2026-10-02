"""Characters A: Alex (player), Lucía, Elena, Grady. Shared rig from tools/rig.py.

Segmented PS2-style bodies: tapered boxes per joint, 128px painted faces, 64px cloth.
"""
import math

import build_assets as B
import rig

mix, mul = B.mix, B.mul


# ============================================================== textures

def face_tex(skin, iris, brow, lip, hair, hair_y=14, stubble=0.0, age=0.0, dirt=0.0, bruise=False,
             liner=0.0, beard=None, glasses=False, brow_w=2.4):
    """128px front-of-head painting. Layout: brows y~45, eyes y~57, nose to y~83, mouth y~98."""
    def fn(x, y, a, b, r):
        c = mul(skin, 0.9 + 0.12 * a + 0.03 * r)
        edge = min(x, 127 - x)
        if edge < 16:
            c = mul(c, 0.74 + 0.016 * edge)
        if y > 112:
            c = mul(c, 0.84)
        for ex in (42, 86):  # sockets: tired, shadowed
            d = ((x - ex) / 18) ** 2 + ((y - 58) / 12) ** 2
            if d < 1:
                c = mul(c, 0.8 + 0.2 * d)
        if 59 <= x <= 62 and 56 <= y <= 80:
            c = mul(c, 0.86)
        if 64 <= x <= 67 and 60 <= y <= 78:
            c = mul(c, 1.08)
        if 55 <= x <= 73 and 79 <= y <= 84:
            c = mul(c, 0.8)
        for nx in (58, 70):
            if (x - nx) ** 2 + (y - 84) ** 2 < 5:
                c = mul(c, 0.45)
        if 22 < x < 106 and 64 < y < 74 and abs(x - 64) > 20 and r < 0.3:
            c = mix(c, (0.7, 0.42, 0.38), 0.07)  # cold cheeks
        if age:
            if y in (27, 33, 39) and 34 < x < 94 and r < 0.9:
                c = mul(c, 1 - 0.25 * age)
            for sx in (1, -1):
                lx = 64 + sx * (14 + (y - 78) * 0.45)
                if 78 < y < 104 and abs(x - lx) < 1.2:
                    c = mul(c, 1 - 0.3 * age)
                if abs(y - 62 - abs(x - 64 - sx * 34) * 0.4) < 0.8 and 16 < abs(x - 64) < 34 and x * sx > 64 * sx:
                    c = mul(c, 1 - 0.25 * age)
        lip_h = 3.8 - ((x - 64) / 15) ** 2 * 3.5
        in_lips = abs(y - 98) < lip_h and 47 < x < 81
        if stubble and y > 84 and not in_lips and 10 < edge and r < stubble:
            c = mix(c, mul(brow, 0.8), 0.4)
        if in_lips:
            c = mix(c, lip, 0.65)
            if y == 98:
                c = mul(c, 0.55)
        if beard and (y > 90 or (edge < 22 and y > 70)) and not (in_lips and y < 98):
            c = mul(beard, 0.75 + 0.35 * a + 0.2 * (r - 0.5))
            if (x * 7 + y * 3) % 5 == 0:
                c = mul(c, 0.7)
        for ex, side in ((42, -1), (86, 1)):
            dx, dy = x - ex, y - 57
            e = (dx / 9.5) ** 2 + (dy / 4.2) ** 2
            if -9 < dy < -4 and abs(dx) < 11:
                c = mul(c, 0.78 + 0.03 * abs(dy + 6))  # upper-lid crease shadow
            if e < 1:
                c = mix(mul((0.64, 0.6, 0.55), 0.9 + 0.1 * r), mul(skin, 0.6), max(0.0, e - 0.4))
                d2 = (dx + side * 0.5) ** 2 + dy * dy
                if d2 < 13:
                    c = mul(iris, 0.6 + 0.5 * a + (0.25 if d2 < 6 else 0))
                if d2 < 3:
                    c = (0.03, 0.03, 0.03)
                if dx == -2 and dy == -2:
                    c = (0.9, 0.9, 0.88)
                if dy <= -3:
                    c = mul(skin, 0.62)  # heavy upper lid over the iris
            if abs(dy + 3.6 - dx * dx * 0.012) < 0.9 + liner and abs(dx) < 10:
                c = (0.12, 0.08, 0.06)
            if 4 < dy < 7 and abs(dx) < 9:
                c = mul(c, 0.86)  # bags under the eyes
            by = 45 + dx * 0.1 * side * -1 + (dx * dx) * 0.014
            if abs(y - by) < brow_w - 0.08 * max(0, dx * -side) and -11 < dx * side * -1 < 13:
                c = mix(c, brow, 0.85 if r > 0.15 else 0.4)
        if glasses:
            for ex in (42, 86):
                d = max(abs(x - ex) / 14, abs(y - 57) / 9)
                if 0.88 < d < 1.0:
                    c = (0.12, 0.1, 0.08)
            if 56 <= x <= 72 and 55 <= y <= 56:
                c = (0.12, 0.1, 0.08)
        if bruise and ((x - 96) / 13) ** 2 + ((y - 70) / 10) ** 2 < 1:
            c = mix(c, (0.35, 0.22, 0.3), 0.45)
        if bruise and 70 < x < 76 and 99 < y < 108 and r < 0.6:
            c = mix(c, (0.4, 0.08, 0.06), 0.5)  # split lip scab
        if y < hair_y + 3 * math.sin(x * 0.25 + a * 4):
            c = mul(hair, 0.7 + 0.5 * a + 0.2 * math.sin(x * 1.1))
        if dirt and b > 1 - dirt * 0.6:
            c = mix(c, (0.22, 0.18, 0.13), 0.35)
        return c
    return fn


def hair_tex(col):
    """Matte strands: fine streaks along v (surfaces run their v down the hair), darker roots in the noise."""
    def fn(x, y, a, b, r):
        v = math.sin(x * 2.3 + a * 9 + math.sin(y * 0.15) * 1.5)
        return mul(col, 0.72 + 0.28 * a + 0.12 * v + 0.12 * (r - 0.5) - (0.18 if b > 0.68 else 0))
    return fn


def t_denim(x, y, a, b, r):
    c = mul((0.2, 0.25, 0.36), 0.75 + 0.35 * a + (0.08 if (x + y) % 4 < 2 else 0))
    if x % 32 in (0, 1):
        c = mul(c, 0.6) if y % 4 < 2 else mix(c, (0.6, 0.45, 0.2), 0.5)  # stitched side seam
    if b > 0.62:
        c = mix(c, (0.25, 0.2, 0.14), 0.4)  # mud
    return c


def t_denim_torn(x, y, a, b, r):
    if 22 < x < 42 and 28 < y < 40:  # ripped knee showing skin
        return (0.55, 0.4, 0.32) if 25 < x < 39 and 30 < y < 38 and r < 0.8 else (0.8, 0.78, 0.72)
    return t_denim(x, y, a, b, r)


def t_canvas(x, y, a, b, r):
    c = mul((0.34, 0.25, 0.15), 0.72 + 0.35 * a + (0.05 if (x ^ y) & 1 else 0))
    if x % 32 == 0 or y % 32 == 16:
        c = mul(c, 0.65)
    if (x % 32 == 2 or y % 32 == 18) and (x + y) % 3:
        c = mix(c, (0.6, 0.5, 0.3), 0.4)  # topstitch
    if b > 0.66:
        c = mul(c, 0.7)
    return c


def t_tee(x, y, a, b, r):
    c = mul((0.42, 0.42, 0.4), 0.8 + 0.25 * a + (0.04 if y % 2 else 0))
    return mix(c, (0.3, 0.25, 0.2), 0.4) if b > 0.64 else c


def t_rain(x, y, a, b, r):
    c = mul((0.8, 0.62, 0.14), 0.72 + 0.3 * a)
    if b > 0.62:
        c = mix(c, (0.3, 0.28, 0.2), min(0.45, (b - 0.62) * 3))  # grime
    return c


def t_parka(x, y, a, b, r):
    c = mul((0.26, 0.29, 0.18), 0.72 + 0.35 * a + (0.04 if (x + 2 * y) % 5 < 2 else 0))
    if y % 16 == 0 and x % 2:
        c = mul(c, 0.8)
    return mix(c, (0.2, 0.17, 0.12), min(0.4, (b - 0.6) * 3)) if b > 0.6 else c


def t_flannel(x, y, a, b, r):
    base = (0.42, 0.14, 0.11)
    if 4 <= x % 16 <= 7 or 4 <= y % 16 <= 7:
        base = (0.12, 0.12, 0.1)
    if (4 <= x % 16 <= 7) and (4 <= y % 16 <= 7):
        base = (0.06, 0.06, 0.05)
    if x % 16 == 12 or y % 16 == 12:
        base = (0.5, 0.45, 0.3)
    return mul(base, 0.75 + 0.35 * a + 0.05 * r)


def t_apron(x, y, a, b, r):
    c = mul((0.55, 0.5, 0.4), 0.75 + 0.3 * a + (0.03 if (x ^ y) & 1 else 0))
    if b > 0.58:
        c = mix(c, (0.3, 0.2, 0.12), 0.5)
    if b < 0.25 and r < 0.3:
        c = mul(c, 0.8)
    return c


def t_leather(x, y, a, b, r):
    c = mul((0.2, 0.13, 0.08), 0.6 + 0.6 * a + 0.05 * r)
    if y % 16 == 15 and x % 3:
        c = mix(c, (0.5, 0.4, 0.25), 0.5)
    return c


def t_bandage(x, y, a, b, r):
    c = mul((0.78, 0.74, 0.64), 0.8 + 0.2 * a)
    if (y + x // 6) % 8 == 0:
        c = mul(c, 0.75)
    if ((x - 40) / 12) ** 2 + ((y - 28) / 9) ** 2 < 1 and r < 0.8:
        c = mix(c, (0.45, 0.25, 0.18), 0.35 + 0.3 * b)  # old seepage around the brand
    return c


def t_brand_hand(x, y, a, b, r):
    """Back of Alex's left hand: the Veil's Eye branded into the skin."""
    c = mul((0.62, 0.46, 0.37), 0.9 + 0.1 * a)
    dx, dy = (x - 32) / 20, (y - 30) / 11
    lid = 1 - dx * dx
    if lid > 0 and abs(abs(dy) - lid) < 0.22 or (x - 32) ** 2 + (y - 30) ** 2 < 14:
        c = (0.36, 0.1, 0.08)
    return c


def t_beard(x, y, a, b, r):
    return mul((0.58, 0.56, 0.52), 0.6 + 0.4 * a + 0.35 * (r - 0.5))


def t_knit(x, y, a, b, r):
    c = mul((0.22, 0.22, 0.24), 0.75 + 0.3 * a + (0.08 if (x // 2 + y) % 4 < 2 else 0))
    return c


def t_sneaker(x, y, a, b, r):
    c = mul((0.72, 0.7, 0.66), 0.75 + 0.3 * a)
    if y > 52:
        c = (0.85, 0.83, 0.78)
    if b > 0.55:
        c = mix(c, (0.3, 0.24, 0.16), 0.5)
    return c


B.TEXTURES.update({
    "ca_face_alex": face_tex((0.64, 0.48, 0.38), (0.3, 0.2, 0.1), (0.1, 0.07, 0.05), (0.52, 0.32, 0.28),
                             (0.08, 0.06, 0.05), hair_y=13, stubble=0.45, dirt=0.3),
    "ca_face_lucia": face_tex((0.72, 0.55, 0.45), (0.25, 0.17, 0.08), (0.12, 0.08, 0.05), (0.55, 0.3, 0.28),
                              (0.1, 0.07, 0.05), hair_y=16, dirt=0.35, bruise=True, liner=0.5, brow_w=1.4),
    "ca_face_elena": face_tex((0.68, 0.51, 0.41), (0.18, 0.13, 0.08), (0.08, 0.06, 0.05), (0.48, 0.3, 0.27),
                              (0.08, 0.06, 0.05), hair_y=12, dirt=0.15, liner=0.3, brow_w=1.5),
    "ca_face_grady": face_tex((0.72, 0.56, 0.47), (0.3, 0.35, 0.38), (0.6, 0.58, 0.55), (0.5, 0.35, 0.32),
                              (0.6, 0.58, 0.55), hair_y=0, age=1.0, beard=(0.58, 0.56, 0.52)),
    "ca_hair_dark": hair_tex((0.1, 0.075, 0.055)), "ca_hair_black": hair_tex((0.06, 0.05, 0.045)),
    "ca_hair_grey": hair_tex((0.55, 0.53, 0.5)),
    "ca_denim": t_denim, "ca_denim_torn": t_denim_torn, "ca_canvas": t_canvas, "ca_tee": t_tee,
    "ca_rain": t_rain, "ca_parka": t_parka, "ca_flannel": t_flannel, "ca_apron": t_apron,
    "ca_leather": t_leather, "ca_bandage": t_bandage, "ca_brand_hand": t_brand_hand, "ca_knit": t_knit,
    "ca_sneaker": t_sneaker, "ca_beard": t_beard,
})
for _f in ("ca_face_alex", "ca_face_lucia", "ca_face_elena", "ca_face_grady"):
    B.TEX_SIZE[_f] = 128

B.MATS.update({
    "ca_face_alex": B.M("ca_face_alex", fit=True), "ca_face_lucia": B.M("ca_face_lucia", fit=True),
    "ca_face_elena": B.M("ca_face_elena", fit=True), "ca_face_grady": B.M("ca_face_grady", fit=True),
    # flat skin is darkened to sit next to the shaded face paintings
    "ca_skin": B.M("plain", (0.52, 0.38, 0.3), 1), "ca_skin_l": B.M("plain", (0.54, 0.4, 0.32), 1),
    "ca_skin_e": B.M("plain", (0.49, 0.36, 0.28), 1), "ca_skin_g": B.M("plain", (0.54, 0.42, 0.35), 1),
    "ca_brand": B.M("ca_brand_hand", fit=True),
    "ca_hair_dark": B.M("ca_hair_dark", scale=0.3), "ca_hair_black": B.M("ca_hair_black", scale=0.3),
    "ca_hair_grey": B.M("ca_hair_grey", scale=0.3),
    "ca_denim": B.M("ca_denim", scale=0.5), "ca_denim_torn": B.M("ca_denim_torn", fit=True),
    "ca_denim_navy": B.M("ca_denim", (0.55, 0.55, 0.6), 0.5),
    "ca_canvas": B.M("ca_canvas", scale=0.5), "ca_tee": B.M("ca_tee", scale=0.4),
    "ca_rain": B.M("ca_rain", scale=0.6, rough=0.6), "ca_rain_front": B.M("ca_rain", fit=True, rough=0.35),
    "ca_parka": B.M("ca_parka", scale=0.5), "ca_parka_front": B.M("ca_parka", fit=True),
    "ca_flannel": B.M("ca_flannel", scale=0.35), "ca_apron": B.M("ca_apron", scale=0.6),
    "ca_leather": B.M("ca_leather", scale=0.3), "ca_sole": B.M("plain", (0.07, 0.065, 0.06), 1),
    "ca_rubber_boot": B.M("ca_leather", (0.35, 0.6, 0.4), 0.3, rough=0.4),
    "ca_bandage": B.M("ca_bandage", fit=True), "ca_knit": B.M("ca_knit", scale=0.3),
    "ca_sneaker": B.M("ca_sneaker", fit=True), "ca_trousers": B.M("ca_knit", (0.9, 0.95, 1.2), 0.5),
    "ca_grey_pants": B.M("ca_tee", (0.8, 0.82, 0.78), 0.5),
    "ca_metal": B.M("metal", (0.4, 0.4, 0.42), 0.3), "ca_strap": B.M("plain", (0.1, 0.09, 0.08), 1),
    "ca_beard": B.M("ca_beard", scale=0.15),
    "ca_glass": B.M("plain", (0.07, 0.08, 0.09), 1, rough=0.3),
})


# ---- smooth-body textures (Alex redesign + shared)

def t_tee_white(x, y, a, b, r):
    """Plain white tee, days unwashed: grey grime, yellow sweat blooms, dirt smears."""
    c = mul((0.74, 0.72, 0.67), 0.86 + 0.14 * a)
    if b > 0.6:
        c = mix(c, (0.62, 0.55, 0.36), min(0.55, (b - 0.6) * 3))  # sweat
    if a < 0.3:
        c = mix(c, (0.3, 0.26, 0.2), (0.3 - a) * 1.6)  # dirt
    return c


def jeans_tex(base, fade=0.0, mud=0.0):
    def fn(x, y, a, b, r):
        c = mul(base, 0.8 + 0.3 * a + (0.12 if (x + y) % 4 < 2 else 0))
        if fade:
            c = mix(c, (0.36, 0.36, 0.37), fade * (0.5 + 0.5 * b))
        if x % 32 in (0, 1):
            c = mul(c, 0.7) if y % 4 < 2 else mix(c, (0.3, 0.29, 0.27), 0.25)  # seam
        if mud and b + (1 - y / 64) * mud > 0.9:
            c = mix(c, (0.2, 0.15, 0.1), 0.7)
        return c
    return fn


def t_sneaker_worn(x, y, a, b, r):
    c = mul((0.5, 0.49, 0.46), 0.75 + 0.35 * a)
    if b > 0.55:
        c = mix(c, (0.24, 0.19, 0.13), 0.55)
    if x % 16 == 0 and y % 3:
        c = mul(c, 0.7)  # stitching
    return c


def t_skin(x, y, a, b, r):
    return mul((0.92, 0.9, 0.88), 0.93 + 0.1 * a + 0.03 * r)


B.TEXTURES.update({
    "ca_face_alex": face_tex((0.78, 0.6, 0.5), (0.28, 0.45, 0.66), (0.42, 0.32, 0.2), (0.62, 0.38, 0.35),
                             (0.5, 0.42, 0.26), hair_y=10, stubble=0.0, dirt=0.05, brow_w=1.5),
    "ca_hair_ash": hair_tex((0.66, 0.55, 0.36)), "ca_tee_white": t_tee_white,
    "ca_jeans_black": jeans_tex((0.085, 0.085, 0.095)),
    "ca_jeans_fade": jeans_tex((0.085, 0.085, 0.095), fade=0.22),
    "ca_jeans_mud": jeans_tex((0.085, 0.085, 0.095), mud=0.5),
    "ca_sneaker_worn": t_sneaker_worn, "ca_skin": t_skin,
})
B.MATS.update({
    "ca_face_alex": B.M("ca_face_alex", fit=True),
    "ca_hair_ash": B.M("ca_hair_ash", scale=0.25, rough=0.7), "ca_tee_white": B.M("ca_tee_white", scale=0.45, wrinkle=0.005),
    "ca_jeans_black": B.M("ca_jeans_black", scale=0.45, wrinkle=0.006), "ca_jeans_fade": B.M("ca_jeans_fade", scale=0.45, wrinkle=0.006),
    "ca_jeans_mud": B.M("ca_jeans_mud", scale=0.3, wrinkle=0.006), "ca_sneaker_worn": B.M("ca_sneaker_worn", scale=0.3),
    "ca_skin": B.M("ca_skin", (0.56, 0.42, 0.33), 0.4), "ca_skin_l": B.M("ca_skin", (0.57, 0.42, 0.34), 0.4),
    "ca_skin_e": B.M("ca_skin", (0.54, 0.4, 0.31), 0.4), "ca_skin_g": B.M("ca_skin", (0.58, 0.45, 0.37), 0.4),
    "ca_sole_w": B.M("plain", (0.32, 0.3, 0.27), 1),
    "ca_sneaker_l": B.M("ca_sneaker_worn", (0.75, 0.78, 0.9), 0.3),
})


# ============================================================== smooth body helpers

PI = math.pi
HEAD = [  # (y, rx, rz, oz) head sections on the Head joint, chin to crown; face looks +Z
    (-0.004, 0.0, 0.0, 0.07), (0.002, 0.026, 0.02, 0.07), (0.014, 0.042, 0.035, 0.062),
    (0.032, 0.056, 0.058, 0.04), (0.06, 0.066, 0.083, 0.014), (0.09, 0.072, 0.097, 0.002),
    (0.12, 0.076, 0.103, -0.003), (0.145, 0.077, 0.105, -0.004), (0.17, 0.077, 0.105, -0.006),
    (0.2, 0.073, 0.099, -0.01), (0.222, 0.062, 0.084, -0.014), (0.24, 0.04, 0.058, -0.018),
    (0.25, 0.0, 0.0, -0.02)]


def head_secs(w=1.0, d=1.0, jaw=1.0):
    return [(y, rx * w * (jaw if y < 0.07 else 1), rz * d, oz * d) for y, rx, rz, oz in HEAD]


def sec_at(secs, y):
    y = min(max(y, secs[0][0]), secs[-1][0])
    for s0, s1 in zip(secs, secs[1:]):
        if s0[0] <= y <= s1[0]:
            t = (y - s0[0]) / ((s1[0] - s0[0]) or 1)
            return [s0[i] + (s1[i] - s0[i]) * t for i in (1, 2, 3)]


def sp(v, p):
    return math.copysign(abs(v) ** (2 / p), v)


def head_pt(secs, y, phi, p=2.4):
    """Point on the head at height y, azimuth phi (0 = straight ahead +Z, +90deg = +X)."""
    rx, rz, oz = sec_at(secs, y)
    return (rx * sp(math.sin(phi), p), y, oz + rz * sp(math.cos(phi), p))


def xf(p, rot=(0, 0, 0), pos=(0, 0, 0)):
    return B.v_add(B.m_vec(B.rot3(*rot), p), pos)


def ell(m, mat, radii, pos=(0, 0, 0), rot=(0, 0, 0), seg=10, rings=6, uv=None):
    """Ellipsoid built in joint-local coords (so uv fns see real joint-local points)."""
    rows = []
    for k in range(rings + 1):
        t = PI * k / rings
        rows.append([xf((radii[0] * math.sin(t) * math.sin(2 * PI * j / seg), -radii[1] * math.cos(t),
                         radii[2] * math.sin(t) * math.cos(2 * PI * j / seg)), rot, pos) for j in range(seg)])
    m.surface(mat, rows, wrap=True, uv=uv)


def face_uv(w=1.0):
    return lambda p: (0.5 + p[0] / (0.2 * w), (0.255 - p[1]) / 0.26)


def head(m, face, back, secs, w=1.0, nose=1.0, ear_mat=None, brow=1.0):
    """Oval skull + jaw with the painted face projected on the front half; nose, brow, lips, ears, neck."""
    m.use("Head")
    uv = face_uv(w)
    ys = [s[0] for s in secs]
    front = [[head_pt(secs, y, -PI / 2 + PI * j / 10) for j in range(11)] for y in ys]
    rear = [[head_pt(secs, y, PI / 2 + PI * j / 10) for j in range(11)] for y in ys]
    m.surface(face, front, uv=uv)
    m.surface(back, rear)
    m.lathe(back, [(0.05, -0.12), (0.049, -0.02), (0.047, 0.05)], (0, 0, -0.018), scale=(1, 1, 0.92), seg=10)
    zf = lambda y: sec_at(secs, y)[2] + sec_at(secs, y)[1]  # face surface depth at height y
    ell(m, face, (0.011 * nose, 0.03, 0.016 * nose), (0, 0.108, zf(0.108) - 0.004), (-20, 0, 0), 8, 5, uv)
    ell(m, face, (0.012 * nose, 0.01, 0.011 * nose), (0, 0.089, zf(0.089) + 0.005), seg=8, rings=5, uv=uv)
    for s in (1, -1):
        ell(m, face, (0.009 * nose, 0.008, 0.008), (s * 0.012, 0.087, zf(0.087) + 0.002), seg=6, rings=4, uv=uv)
        ell(m, face, (0.03, 0.009 * brow, 0.016 * brow), (s * 0.031, 0.163, zf(0.163) - 0.009 - 0.008 * (1 - brow)), (0, 0, s * -6), 8, 4, uv)
        rx = sec_at(secs, 0.12)[0]
        ell(m, ear_mat or back, (0.011, 0.029, 0.019), (s * (rx + 0.002), 0.118, -0.014), (0, s * 20, s * -6), 8, 5)
    ell(m, face, (0.025, 0.008, 0.011), (0, 0.059, zf(0.059) - 0.004), seg=8, rings=4, uv=uv)  # upper lip
    ell(m, face, (0.021, 0.008, 0.011), (0, 0.047, zf(0.047) - 0.004), seg=8, rings=4, uv=uv)  # lower lip
    ell(m, face, (0.022, 0.016, 0.014), (0, 0.016, zf(0.016) - 0.008), seg=8, rings=4, uv=uv)  # chin


def hair(m, mat, secs, bottom, thick=0.014, top_extra=0.012, spike=0.0, messy=0.004, fall=0.14,
         phis=None, y_top=0.25, cols=24, rows=7, seed=1, flare=0.0):
    """Hair volume shell hugging the skull. bottom(phi_deg in -180..180) -> hairline y. Below `fall` the
    hair hangs straight instead of following the jaw. spike: alternate columns drop lower (messy ends)."""
    rng = __import__("random").Random(seed)
    C = (0, 0.12, -0.01)
    wrap = phis is None
    p0, p1 = phis or (-180, 180)
    n = cols if wrap else cols + 1
    grid = []
    for k in range(rows + 1):
        s = k / rows
        row = []
        for j in range(n):
            deg = p0 + (p1 - p0) * j / cols
            yb = bottom(((deg + 180) % 360) - 180)
            if k == 0 and spike:
                yb -= spike * (0.9 if j % 2 else 0.1) * rng.uniform(0.5, 1.3)
            y = yb + (y_top - yb) * math.sin(s * PI / 2)
            hp = head_pt(secs, max(y, fall) if abs(deg) > 50 else y, math.radians(deg))
            P = (hp[0], y, hp[2])
            d = B.v_sub(P, C)
            ln = math.sqrt(B.v_dot(d, d)) or 1
            t = thick + top_extra * s + (messy * rng.uniform(-1, 1) if k < rows or not wrap else 0)
            if k == 0:
                t += flare * rng.uniform(0.3, 1.0)
            row.append(B.v_add(C, B.mul(d, 1 + t / ln)))
        grid.append(row)
    if wrap and y_top >= secs[-1][0]:
        top = grid[-1][0]
        grid[-1] = [top] * n
    m.surface(mat, grid, wrap=wrap)


def lerp_tab(tab, x):
    """Piecewise-linear lookup in [(x, y), ...] sorted by x."""
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1)
    return tab[0][1] if x < tab[0][0] else tab[-1][1]


def lock(m, mat, root, phi, tilt, length, r=0.022, flat=0.6, twist=0.0):
    """A clump of hair from root, falling at azimuth phi (deg), tilted `tilt` deg outward from straight down."""
    t, f = math.radians(tilt), math.radians(phi)
    d = (math.sin(f) * math.sin(t), -math.cos(t), math.cos(f) * math.sin(t))
    c = B.v_add(root, B.mul(d, length / 2))
    ell(m, mat, (r, length / 2, r * flat), c, (-tilt, phi, twist), 6, 5)


def torso(m, mat, secs, power=2.6, seg=18, joint="Spine"):
    """secs: (y, rx, rz[, ox, oz]) bottom to top, closed by zero rings where wanted."""
    m.use(joint)
    m.loft(mat, secs, seg=seg, power=power)


def finger(m, mat, pos, rot, length, r1, r2, squash=(1, 1)):
    m.capsule(mat, r1, r2, length, pos, rot, seg=6, squash=squash)
    t = B.m_vec(B.rot3(*rot), (0, -length, 0))
    return B.v_add(pos, t)


def hand(m, side, s, skin, back=None, glove=None):
    """Relaxed hand on Hand<side>: palm faces the thigh (-s*X), thumb forward, fingers in two curled groups."""
    m.use("Hand" + side)
    uv = None
    if back:  # project the back-of-hand texture onto the outer (+s*X) face only
        uv = lambda p: (0.5 + p[2] / 0.1, 0.47 - (p[1] + 0.045) / 0.1) if p[0] * s > -0.004 else (0.03, 0.97)
    ell(m, back or skin, (0.018, 0.047, 0.043), (0, -0.045, 0.004), seg=10, rings=6, uv=uv)
    for z, ln in ((0.014, 0.046), (-0.018, 0.04)):
        e = finger(m, skin, (-s * 0.004, -0.078, z), (0, 0, -s * 14), ln, 0.012, 0.011, (0.9, 1.45))
        finger(m, skin, e, (0, 0, -s * 48), 0.028, 0.011, 0.009, (0.9, 1.4))
    finger(m, skin, (-s * 0.008, -0.025, 0.034), (-38, 0, -s * 22), 0.045, 0.014, 0.011)


def arm(m, side, s, skin, sleeve=None, sleeve_to=0.0, fore=None, cuff=None, bulk=1.0, back=None, elbow=None):
    """Capsule limbs + joint spheres. sleeve_to: how far down the upper arm the sleeve reaches (short sleeve
    ~0.14); with fore (long-sleeve material) the forearm is clothed too and cuff sits at the wrist."""
    m.use("UpperArm" + side)
    k = bulk
    if not (sleeve and sleeve_to > 0.28):
        m.capsule(skin, 0.05 * k, 0.041 * k, 0.29, seg=10, squash=(1, 0.95))
    if sleeve:
        L = sleeve_to
        m.lathe(sleeve, [(0.05 * k, -L - 0.004), (0.058 * k, -L), (0.058 * k, -L * 0.5), (0.06 * k, 0.0),
                         (0.05 * k, 0.012), (0.03 * k, 0.024), (0, 0.028)], seg=12, scale=(1, 1, 0.95))
    m.use("Forearm" + side)
    ell(m, elbow or (fore or skin), (0.056 * k if fore else 0.04 * k,) * 3, (0, 0, 0), seg=8, rings=5)
    if fore:
        m.lathe(fore, [(0.047 * k, -0.25), (0.053 * k, -0.24), (0.056 * k, -0.12), (0.058 * k, 0.0),
                       (0.05 * k, 0.04), (0, 0.055)], seg=10)
        if cuff:
            m.lathe(cuff, [(0.042 * k, -0.262), (0.05 * k, -0.255), (0.052 * k, -0.215), (0.046 * k, -0.21)],
                    seg=10)
        m.capsule(skin, 0.032, 0.03, 0.03, (0, -0.235, 0), seg=8)  # wrist
    else:
        m.capsule(skin, 0.043 * k, 0.031 * k, 0.255, seg=10, squash=(0.95, 1.1))
    hand(m, side, s, skin, back)


def shoe(m, upper, sole, L=1.0, W=1.0, H=1.0, toe=None, seg=12):
    """Rounded shoe on the Foot joint (ankle pivot, ground at y=-0.05). Lofted heel->toe along +Z."""
    secs = [(-0.083 * L, 0, 0, 0, 0.02), (-0.082 * L, 0.03 * W, 0.03 * H, 0, 0.015),
            (-0.07 * L, 0.045 * W, 0.052 * H, 0, 0.0), (-0.035 * L, 0.05 * W, 0.066 * H, 0, -0.005),
            (0.0, 0.052 * W, 0.058 * H, 0, 0.002), (0.05 * L, 0.055 * W, 0.042 * H, 0.002, 0.012),
            (0.1 * L, 0.056 * W, 0.032 * H, 0.004, 0.02), (0.145 * L, 0.05 * W, 0.026 * H, 0.005, 0.024),
            (0.175 * L, 0.038 * W, 0.021 * H, 0.005, 0.027), (0.19 * L, 0.018 * W, 0.013 * H, 0.004, 0.03),
            (0.193 * L, 0, 0, 0.004, 0.03)]
    m.loft(upper, secs, rot=(90, 0, 0), seg=seg, power=2.3)
    m.loft(sole, [(-0.088 * L, 0, 0, 0, 0.037), (-0.087 * L, 0.04 * W, 0.012, 0, 0.037),
                  (-0.07 * L, 0.056 * W, 0.013, 0, 0.037), (0.1 * L, 0.061 * W, 0.013, 0.004, 0.037),
                  (0.17 * L, 0.052 * W, 0.012, 0.005, 0.034), (0.2 * L, 0.03 * W, 0.01, 0.004, 0.03),
                  (0.203 * L, 0, 0, 0.004, 0.03)], rot=(90, 0, 0), seg=seg, power=4)
    if toe:
        ell(m, toe, (0.05 * W, 0.022 * H, 0.04 * L), (0.004, -0.02, 0.15 * L), seg=8, rings=4)


def leg(m, side, s, pants, shin_prof, thigh=(0.085, 0.07), knee=None, knee_r=0.075, hem=None, hem_y=-0.36,
        squash=(1.0, 1.05)):
    """Thigh capsule, knee sphere, shin lathe (profile bottom->top in Shin space; below hem_y uses `hem`)."""
    m.use("Thigh" + side)
    m.capsule(pants, thigh[0], thigh[1], 0.43, seg=12, squash=squash)
    m.use("Shin" + side)
    ell(m, knee or pants, (knee_r, knee_r * 0.95, knee_r * 1.02), (0, 0, 0.005), seg=10, rings=6)
    if hem:
        lo = [p for p in shin_prof if p[1] <= hem_y]
        hi = [p for p in shin_prof if p[1] >= hem_y]
        m.lathe(hem, lo, seg=12, scale=(squash[0], 1, squash[1]))
        m.lathe(pants, hi, seg=12, scale=(squash[0], 1, squash[1]))
    else:
        m.lathe(pants, shin_prof, seg=12, scale=(squash[0], 1, squash[1]))


# ============================================================== characters

def jeans_leg(hem_r=0.084, top_r=0.078):
    """Baggy leg profile (Shin space, bottom->top) with fabric stacked in rings over the shoe."""
    return [(hem_r - 0.034, -0.452), (hem_r, -0.448), (hem_r + 0.005, -0.43), (hem_r - 0.004, -0.415),
            (hem_r + 0.004, -0.395), (hem_r - 0.005, -0.375), (hem_r + 0.002, -0.355), (hem_r - 0.006, -0.33),
            (top_r + 0.001, -0.2), (top_r + 0.002, -0.06), (top_r, -0.02)]


def m_alex():
    """Alex Moreno (player): young, clean-shaven, soft swept ash-blonde hair, blue eyes, grimy white tee, baggy black
    jeans, worn sneakers. Veil brand on the back of the left hand."""
    m = rig.skeleton("char_alex")
    hs = head_secs(1.0, 1.0, 0.96)
    with m.push((0, 0.02, 0)):  # lift the head off the shoulders: visible neck
        head(m, "ca_face_alex", "ca_skin", hs, brow=0.6, nose=0.85)
        hair_line = [(-180, 0.04), (-125, 0.07), (-100, 0.11), (-70, 0.14), (-40, 0.16), (0, 0.165),
                     (40, 0.158), (70, 0.14), (100, 0.11), (125, 0.07), (180, 0.04)]
        hair(m, "ca_hair_ash", hs, lambda d: lerp_tab(hair_line, d), thick=0.014, top_extra=0.016, spike=0.02,
             messy=0.004, flare=0.006, cols=30, rows=8, seed=3)
        # layered tapered locks: swept fringe over the forehead, short sides, longer nape tufts
        for phi, tilt, y, ln, r in ((-34, 38, 0.215, 0.09, 0.019), (-14, 34, 0.225, 0.095, 0.019), (6, 30, 0.23, 0.095, 0.019), (24, 34, 0.225, 0.09, 0.019),
                                    (42, 38, 0.215, 0.08, 0.017), (-52, 40, 0.215, 0.065, 0.014), (56, 40, 0.215, 0.065, 0.014),
                                    (-80, 22, 0.19, 0.06, 0.013), (82, 22, 0.19, 0.06, 0.013), (-115, 14, 0.17, 0.07, 0.014),
                                    (115, 14, 0.17, 0.07, 0.014), (150, 10, 0.19, 0.09, 0.016), (-150, 10, 0.19, 0.09, 0.016),
                                    (180, 8, 0.2, 0.1, 0.017), (165, 12, 0.18, 0.085, 0.015), (-165, 12, 0.18, 0.085, 0.015)):
            hp = head_pt(hs, y, math.radians(phi))
            root = (hp[0] * 1.06, y + 0.008, hp[2] * 1.05)
            lock(m, "ca_hair_ash", root, phi, tilt, ln, r=r, flat=0.5, twist=(phi % 7 - 3) * 5)
    torso(m, "ca_tee_white", [
        (-0.13, 0.174, 0.114), (-0.05, 0.167, 0.107), (0.05, 0.158, 0.102, 0, 0.004),
        (0.15, 0.163, 0.106, 0, 0.01), (0.25, 0.177, 0.113, 0, 0.018), (0.33, 0.188, 0.113, 0, 0.018),
        (0.4, 0.196, 0.104, 0, 0.01), (0.45, 0.2, 0.094, 0, 0.0), (0.49, 0.19, 0.084, 0, -0.008),
        (0.515, 0.14, 0.072, 0, -0.01), (0.545, 0.064, 0.056, 0, -0.012), (0.552, 0, 0, 0, -0.012)])
    ell(m, "ca_tee_white", (0.066, 0.01, 0.06), (0, 0.546, -0.012), seg=12, rings=4)  # crew collar
    torso(m, "ca_jeans_black", [(-0.21, 0, 0), (-0.2, 0.08, 0.065), (-0.16, 0.15, 0.1), (-0.08, 0.17, 0.108),
                                (0.0, 0.158, 0.098), (0.07, 0.146, 0.09), (0.1, 0.142, 0.088), (0.1, 0, 0)],
          joint="Hips")

    def limbs(side, s):
        arm(m, side, s, "ca_skin", sleeve="ca_tee_white", sleeve_to=0.13, back="ca_brand" if side == "L" else None)
        leg(m, side, s, "ca_jeans_black", jeans_leg(), thigh=(0.095, 0.083), knee="ca_jeans_fade", knee_r=0.084,
            hem="ca_jeans_mud", hem_y=-0.355)
        m.use("Foot" + side)
        shoe(m, "ca_sneaker_worn", "ca_sole_w")
    rig.mirror(limbs)
    return m



def sash(m, mat, y, tilt, rx=0.245, rz=0.14, oz=0.01):
    """Diagonal strap round the torso (a thin ring whose rim pokes out of the body)."""
    ell(m, mat, (rx, 0.011, rz), (0, y, oz), (0, 0, tilt), seg=16, rings=4)


def front_z(secs, y):
    """Front surface depth of a torso loft at height y."""
    sec = sec_at([(q[0], q[1], q[2], q[4] if len(q) > 4 else 0.0) for q in secs], y)
    return sec[1] + sec[2]


def zipper(m, secs, y0, y1, mat="ca_strap"):
    ys = [y0 + (y1 - y0) * i / 6 for i in range(7)]
    m.loft(mat, [(ys[0], 0, 0, 0, front_z(secs, ys[0]))] + [(y, 0.007, 0.006, 0, front_z(secs, y) + 0.002) for y in ys]
           + [(ys[-1], 0, 0, 0, front_z(secs, ys[-1]))], seg=6)


def m_lucia():
    """Lucía Moreno: photographer, held in the quarry. Olive parka, scarf, camera strap, torn jeans, ponytail."""
    m = rig.skeleton("char_lucia", 0.94)
    with m.push(scale=(0.94, 0.94, 0.94)):
        hs = head_secs(0.95, 0.97, 0.84)
        head(m, "ca_face_lucia", "ca_skin_l", hs, w=0.95, nose=0.8, brow=0.5)
        line = [(-180, 0.05), (-120, 0.07), (-95, 0.1), (-60, 0.15), (-20, 0.2), (0, 0.205), (20, 0.2),
                (60, 0.15), (95, 0.1), (120, 0.07), (180, 0.05)]
        hair(m, "ca_hair_dark", hs, lambda d: lerp_tab(line, d), thick=0.009, top_extra=0.01, spike=0.008,
             messy=0.003, cols=22, seed=5, fall=0.0)
        ell(m, "ca_hair_dark", (0.03, 0.026, 0.028), (0, 0.13, -0.118), seg=8, rings=5)  # tie
        lock(m, "ca_hair_dark", (0, 0.135, -0.13), 180, 14, 0.22, r=0.03, flat=0.8)  # ponytail
        for sd in (1, -1):
            hp = head_pt(hs, 0.19, math.radians(sd * 42))
            lock(m, "ca_hair_dark", (hp[0] * 1.08, 0.19, hp[2] * 1.05), sd * 50, 4, 0.075, r=0.008, flat=0.7)
        parka = [(-0.26, 0.19, 0.13), (-0.15, 0.182, 0.123), (-0.05, 0.172, 0.117), (0.05, 0.166, 0.112, 0, 0.005),
                 (0.15, 0.172, 0.118, 0, 0.014), (0.25, 0.182, 0.125, 0, 0.022), (0.33, 0.186, 0.12, 0, 0.02),
                 (0.4, 0.192, 0.11, 0, 0.012), (0.45, 0.198, 0.098, 0, 0.0), (0.49, 0.188, 0.086, 0, -0.008),
                 (0.515, 0.14, 0.075, 0, -0.01), (0.545, 0.07, 0.06, 0, -0.012), (0.55, 0, 0, 0, -0.012)]
        torso(m, "ca_parka", parka)
        zipper(m, parka, -0.25, 0.5)
        ell(m, "ca_parka", (0.13, 0.05, 0.07), (0, 0.5, -0.1), (-20, 0, 0), 10, 5)  # hood rolled down
        ell(m, "ca_knit", (0.088, 0.034, 0.078), (0, 0.535, -0.004), seg=12, rings=5)  # scarf
        ell(m, "ca_knit", (0.032, 0.1, 0.014), (0.05, 0.43, front_z(parka, 0.43) + 0.008), (6, 0, 5), 8, 5)
        sash(m, "ca_strap", 0.27, 38)
        for sd in (1, -1):
            m.box("ca_parka", (0.1, 0.02, 0.03), (sd * 0.1, 0.06, front_z(parka, 0.06) - 0.004))  # pocket flaps
        torso(m, "ca_denim", [(-0.21, 0, 0), (-0.2, 0.08, 0.065), (-0.16, 0.155, 0.1), (-0.08, 0.175, 0.11),
                              (0.0, 0.17, 0.105), (0.07, 0.16, 0.1), (0.1, 0.155, 0.098), (0.1, 0, 0)], joint="Hips")
        knee_uv = lambda p: (0.5 + p[0] / 0.13, 0.52 - p[1] / 0.12) if p[2] > 0.01 else (0.1, 0.1)

        def limbs(side, sd):
            arm(m, side, sd, "ca_skin_l", sleeve="ca_parka", sleeve_to=0.31, fore="ca_parka", cuff="ca_knit")
            leg(m, side, sd, "ca_denim", [(0.035, -0.442), (0.048, -0.437), (0.05, -0.39), (0.055, -0.3),
                                          (0.06, -0.15), (0.062, -0.05), (0.06, -0.02)], thigh=(0.083, 0.063), knee_r=0.058)
            if side == "L":  # ripped knee
                ell(m, "ca_denim_torn", (0.06, 0.056, 0.061), (0, 0, 0.004), seg=10, rings=6, uv=knee_uv)
            else:
                ell(m, "ca_denim", (0.058, 0.055, 0.059), (0, 0, 0.004), seg=10, rings=6)
            m.use("Foot" + side)
            shoe(m, "ca_sneaker_l", "ca_sole_w", L=0.93, W=0.9, H=0.95)
        rig.mirror(limbs)
    return m


def m_elena():
    """Elena Ruiz 'Moth': yellow rain jacket, cropped hair, dark trousers, rubber boots, bandaged right hand."""
    m = rig.skeleton("char_elena", 0.96)
    with m.push(scale=(0.96, 0.96, 0.96)):
        hs = head_secs(0.96, 0.98, 0.86)
        head(m, "ca_face_elena", "ca_skin_e", hs, w=0.96, nose=0.85, brow=0.55)
        line = [(-180, 0.075), (-110, 0.1), (-90, 0.13), (-60, 0.16), (-30, 0.18), (0, 0.176), (30, 0.17),
                (60, 0.155), (90, 0.13), (110, 0.1), (180, 0.075)]
        hair(m, "ca_hair_black", hs, lambda d: lerp_tab(line, d), thick=0.01, top_extra=0.014, spike=0.014,
             messy=0.004, flare=0.004, cols=24, seed=7)
        for y, ln in ((0.236, 0.1), (0.222, 0.09)):  # side-swept fringe falling toward her left
            hp = head_pt(hs, y, math.radians(-25))
            lock(m, "ca_hair_black", (hp[0] * 1.15, y, hp[2] * 1.16), 75, 64, ln, r=0.02, flat=0.5, twist=10)
        coat = [(-0.42, 0.205, 0.142), (-0.3, 0.195, 0.132), (-0.15, 0.183, 0.122), (-0.05, 0.174, 0.117),
                (0.05, 0.168, 0.113, 0, 0.005), (0.15, 0.174, 0.118, 0, 0.012), (0.25, 0.183, 0.124, 0, 0.02),
                (0.33, 0.188, 0.12, 0, 0.02), (0.4, 0.194, 0.11, 0, 0.012), (0.45, 0.2, 0.098, 0, 0.0),
                (0.49, 0.19, 0.086, 0, -0.008), (0.515, 0.14, 0.075, 0, -0.01), (0.545, 0.07, 0.06, 0, -0.012),
                (0.55, 0, 0, 0, -0.012)]
        torso(m, "ca_rain", coat)
        zipper(m, coat, -0.41, 0.52)
        m.lathe("ca_rain", [(0.074, 0.49), (0.078, 0.53), (0.07, 0.585), (0.062, 0.588)], (0, 0, -0.008),
                seg=12, scale=(1, 1, 0.92))  # stand-up collar
        ell(m, "ca_rain", (0.14, 0.06, 0.075), (0, 0.49, -0.11), (-25, 0, 0), 10, 5)  # hood down
        for sd in (1, -1):
            z = front_z(coat, 0.06) - 0.02
            m.box("ca_rain", (0.11, 0.1, 0.02), (sd * 0.1, 0.03, z))
            m.box("ca_rain", (0.12, 0.022, 0.03), (sd * 0.1, 0.085, z + 0.004))  # pocket flaps
        sash(m, "ca_strap", 0.26, -36, rx=0.25, rz=0.145)
        m.box("ca_metal", (0.07, 0.13, 0.045), (-0.16, -0.05, 0.1), (0, -25, 0))  # handheld radio, channel 7
        m.cyl("ca_metal", 0.007, 0.007, 0.12, (-0.14, 0.01, 0.1), seg=4, caps=False)
        torso(m, "ca_trousers", [(-0.21, 0, 0), (-0.2, 0.08, 0.065), (-0.16, 0.155, 0.1), (-0.08, 0.172, 0.108),
                                 (0.0, 0.168, 0.104), (0.1, 0.155, 0.098), (0.1, 0, 0)], joint="Hips")

        def limbs(side, sd):
            arm(m, side, sd, "ca_skin_e", sleeve="ca_rain", sleeve_to=0.31, fore="ca_rain", cuff="ca_rain")
            leg(m, side, sd, "ca_trousers", [(0.05, -0.35), (0.056, -0.3), (0.062, -0.15), (0.064, -0.05),
                                             (0.062, -0.02)], thigh=(0.086, 0.066), knee_r=0.062)
            m.lathe("ca_rubber_boot", [(0.05, -0.455), (0.056, -0.45), (0.058, -0.36), (0.063, -0.2),
                                       (0.068, -0.165), (0.062, -0.16)], seg=12)
            m.use("Foot" + side)
            shoe(m, "ca_rubber_boot", "ca_sole", W=1.02, H=1.05)
        rig.mirror(limbs)
        m.use("HandR")  # bandage hiding the brand
        ell(m, "ca_bandage", (0.022, 0.042, 0.047), (0, -0.05, 0.004), seg=10, rings=6)
        m.use("ForearmR")
        m.lathe("ca_bandage", [(0.034, -0.265), (0.037, -0.25), (0.04, -0.2), (0.036, -0.19)], seg=10)
    return m


def m_grady():
    """Grady: old shopkeeper. Bald with a grey fringe, beard, glasses, flannel with rolled sleeves, stained apron,
    belly, slight hunch."""
    m = rig.skeleton("char_grady", 0.96, {"Head": (0, 0.53, 0.05)})
    with m.push(scale=(0.96, 0.96, 0.96)):
        hs = head_secs(1.03, 1.02, 1.08)
        head(m, "ca_face_grady", "ca_skin_g", hs, w=1.03, nose=1.15)
        line = [(-180, 0.07), (-100, 0.1), (-70, 0.12), (70, 0.12), (100, 0.1), (180, 0.07)]
        hair(m, "ca_hair_grey", hs, lambda d: lerp_tab(line, d), thick=0.008, top_extra=0.0, spike=0.01,
             messy=0.004, phis=(62, 298), y_top=0.175, cols=16, rows=3, seed=9)
        bl = lambda d: -0.012
        hair(m, "ca_beard", hs, bl, thick=0.012, top_extra=0.0, spike=0.012, messy=0.004, phis=(-95, 95),
             y_top=0.04, cols=14, rows=3, seed=11, fall=0.0)
        for sd in (1, -1):  # cheeks / sideburns
            hair(m, "ca_beard", hs, lambda d: 0.02, thick=0.008, top_extra=0.0, messy=0.003,
                 phis=(sd * 48, sd * 95) if sd > 0 else (-95, -48), y_top=0.12, cols=4, rows=3, seed=12, fall=0.0)
        zf = lambda y: sec_at(hs, y)[1] + sec_at(hs, y)[2]
        ell(m, "ca_beard", (0.032, 0.009, 0.013), (0, 0.07, zf(0.07) + 0.002), seg=8, rings=4)  # moustache
        for sd in (1, -1):  # glasses: dark rim behind a glass lens, arms back to the ears
            x, y, z = sd * 0.035, 0.14, zf(0.14) + 0.014
            ell(m, "ca_strap", (0.025, 0.019, 0.003), (x, y, z - 0.001), seg=10, rings=3)
            ell(m, "ca_glass", (0.022, 0.016, 0.003), (x, y, z + 0.001), seg=10, rings=3)
            m.box("ca_strap", (0.005, 0.005, 0.11), (sd * 0.079, 0.142, 0.035))
        m.box("ca_strap", (0.02, 0.005, 0.005), (0, 0.145, zf(0.14) + 0.012))
        shirt = [(-0.14, 0.19, 0.14, 0, 0.02), (-0.05, 0.192, 0.146, 0, 0.032), (0.05, 0.19, 0.146, 0, 0.036),
                 (0.15, 0.188, 0.135, 0, 0.03), (0.25, 0.19, 0.125, 0, 0.022), (0.33, 0.192, 0.118, 0, 0.014),
                 (0.4, 0.195, 0.108, 0, 0.008), (0.45, 0.197, 0.098, 0, 0.0), (0.49, 0.185, 0.088, 0, -0.005),
                 (0.515, 0.14, 0.078, 0, -0.006), (0.545, 0.07, 0.062, 0, -0.005), (0.55, 0, 0, 0, -0.005)]
        torso(m, "ca_flannel", shirt)
        m.loft("ca_apron", [(y, rx, 0.008, 0, front_z(shirt, y) + 0.004) for y, rx in
                            ((-0.14, 0.16), (-0.02, 0.165), (0.1, 0.16), (0.22, 0.14), (0.32, 0.12), (0.4, 0.11),
                             (0.4, 0.0))], seg=12, power=5)
        for sd in (1, -1):
            m.box("ca_strap", (0.022, 0.2, 0.01), (sd * 0.09, 0.48, front_z(shirt, 0.45) - 0.01), (-25, 0, sd * 12))
            m.box("ca_strap", (0.025, 0.4, 0.01), (sd * 0.1, 0.3, -0.125), (0, 0, sd * -8))  # suspenders
        m.box("ca_apron", (0.13, 0.1, 0.012), (0.05, 0.1, front_z(shirt, 0.1) + 0.012))  # bib pocket
        m.cyl("ca_metal", 0.005, 0.005, 0.1, (0.09, 0.1, front_z(shirt, 0.1) + 0.018), seg=4)  # pencil
        hips = [(-0.21, 0, 0), (-0.2, 0.085, 0.07), (-0.16, 0.16, 0.11), (-0.08, 0.18, 0.125, 0, 0.01),
                (0.0, 0.185, 0.13, 0, 0.02), (0.07, 0.185, 0.135, 0, 0.025), (0.1, 0.18, 0.13, 0, 0.02),
                (0.1, 0, 0, 0, 0.02)]
        torso(m, "ca_grey_pants", hips, joint="Hips")
        ell(m, "ca_leather", (0.187, 0.022, 0.137), (0, 0.06, 0.024), seg=16, rings=3)  # belt
        m.loft("ca_apron", [(y, 0.19, 0.008, 0, front_z(hips, max(y, -0.16)) + 0.012) for y in
                            (-0.56, -0.3, -0.12, 0.0, 0.06)] + [(0.06, 0, 0, 0, 0.14)], seg=12, power=5)

        def limbs(side, sd):
            arm(m, side, sd, "ca_skin_g", sleeve="ca_flannel", sleeve_to=0.24, bulk=1.06)
            m.use("UpperArm" + side)
            ell(m, "ca_flannel", (0.068, 0.024, 0.066), (0, -0.24, 0), seg=10, rings=4)  # rolled cuff
            leg(m, side, sd, "ca_grey_pants", [(0.05, -0.44), (0.058, -0.435), (0.06, -0.3), (0.066, -0.15),
                                               (0.07, -0.05), (0.068, -0.02)], thigh=(0.09, 0.07), knee_r=0.066)
            m.use("Foot" + side)
            shoe(m, "ca_leather", "ca_sole", H=0.85, W=1.02)
        rig.mirror(limbs)
    return m


MODELS = [m_alex, m_lucia, m_elena, m_grady]
