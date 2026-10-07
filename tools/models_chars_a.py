"""Characters A: Alex (player), Lucía, Elena, Grady. Shared rig from tools/rig.py.

Segmented PS2-style bodies: tapered boxes per joint, 128px painted faces, 64px cloth.
"""
import math

import build_assets as B
import rig

mix, mul = B.mix, B.mul


# ============================================================== textures

def face_tex(skin, iris, brow, lip, hair, hair_y=14, stubble=0.0, age=0.0, dirt=0.0, bruise=False,
             liner=0.0, beard=None, glasses=False, brow_w=2.4, socket=0.8, lid=0.62, bags=0.86, lash=(0.12, 0.08, 0.06), glint=True):
    """128-unit front-of-head painting (sampled at 256px). Layout: brows y~45, eyes y~57, nose to y~83, mouth y~98.
    The base is the body skin (t_skin x skin colour) with no edge shading, so face and neck/scalp match."""
    def fn(x, y, a, b, r):
        c = mul(skin, 0.9 + 0.12 * a + 0.03 * r)
        edge = min(x, 127 - x)
        for ex in (42, 86):  # sockets: tired, shadowed
            d = ((x - ex) / 18) ** 2 + ((y - 58) / 12) ** 2
            if d < 1:
                c = mul(c, socket + (1 - socket) * d)
        for nx in (58, 70):  # nostrils: soft shadows (the sculpt does the rest)
            d2 = (x - nx) ** 2 + ((y - 84.5) * 1.6) ** 2
            if d2 < 6:
                c = mul(c, 0.62 + 0.38 * d2 / 6)
        if 22 < x < 106 and 64 < y < 74 and abs(x - 64) > 20 and r < 0.3:
            c = mix(c, (0.7, 0.42, 0.38), 0.07)  # cold cheeks
        # modelling: soft contour shadows so the features read at a distance
        ax = abs(x - 64)
        g = lambda u, v: math.exp(-u * u - v * v)
        c = mul(c, 1 - 0.12 * g((ax - 30) / 9, (y - 88) / 7))  # hollow under the cheekbone
        c = mul(c, 1 - 0.1 * g((ax - 6.5) / 2.2, (y - 70) / 10))  # sides of the nose
        c = mul(c, 1 - 0.14 * g(ax / 9, (y - 87.5) / 2))  # under the nose
        c = mul(c, 1 - 0.16 * g(ax / 10, (y - 105) / 2.2))  # under the lower lip
        c = mul(c, 1 - 0.07 * g((ax - 44) / 5, (y - 105) / 14))  # jaw edge
        if 82 < y < 100:  # nasolabial folds
            c = mul(c, 1 - 0.13 * g((ax - (13 + (y - 82) * 0.42)) / 1.4, 0))
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
            c = mul(c, 1 - 0.2 * g(dx / 10, (dy + 6.2) / 1.8))  # upper-lid crease shadow
            if e < 1:
                c = mix(mul((0.64, 0.6, 0.55), 0.9 + 0.1 * r), mul(skin, 0.6), max(0.0, e - 0.4))
                d2 = (dx + side * 0.5) ** 2 + dy * dy
                if d2 < 13:
                    c = mul(iris, 0.6 + 0.5 * a + (0.25 if d2 < 6 else 0))
                if d2 < 3:
                    c = (0.03, 0.03, 0.03)
                if glint and abs(dx + 2) < 0.8 and abs(dy + 2) < 0.8:
                    c = (0.9, 0.9, 0.88)
                if dy <= -3:
                    c = mul(skin, lid)  # heavy upper lid over the iris
            if abs(dy + 3.6 - dx * dx * 0.012) < 0.9 + liner and abs(dx) < 10:
                c = lash
            c = mul(c, 1 - (1 - bags) * g(dx / 8, (dy - 5.5) / 1.6))  # bags under the eyes
            by = 45 + dx * 0.1 * side * -1 + (dx * dx) * 0.014
            bt = dx * side * -1  # -11 (outer end) .. 13 (inner end)
            k = min(1.0, max(0.0, (brow_w - 0.08 * max(0, dx * -side) - abs(y - by)) / 0.7 + 0.5))  # soft edge
            k *= min(1.0, max(0.0, (bt + 11) / 3, 0.0)) * min(1.0, max(0.0, (13 - bt) / 2))  # tapered ends
            c = mix(c, brow, k * (0.85 if r > 0.15 else 0.4))
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
    "ca_leather": t_leather, "ca_bandage": t_bandage, "ca_knit": t_knit,
    "ca_sneaker": t_sneaker, "ca_beard": t_beard,
})
for _f in ("ca_face_lucia", "ca_face_elena", "ca_face_grady"):  # 128-unit paintings sampled at 256px: crisp features
    B.TEXTURES[_f] = lambda x, y, a, b, r, fn=B.TEXTURES[_f]: fn(x / 2, y / 2, a, b, r)
    B.TEX_SIZE[_f] = 256

B.MATS.update({
    "ca_face_lucia": B.M("ca_face_lucia", fit=True),
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

def jeans_tex(base, fade=0.0, mud=0.0):
    """Black denim worn for weeks: dust ground into the dye, faded knees, mud caked up from the hem."""
    def fn(x, y, a, b, r):
        c = mul(base, 0.9 + 0.15 * a)
        c = mix(c, (0.34, 0.31, 0.26), 0.12 + 0.3 * max(0.0, b - 0.45))
        if fade:
            c = mix(c, (0.36, 0.35, 0.33), fade * (0.5 + 0.5 * b))
        if x % 32 in (0, 1):
            c = mul(c, 0.7) if y % 4 < 2 else mix(c, (0.3, 0.29, 0.27), 0.25)  # seam
        if mud and b + (1 - y / 64) * mud > 0.85:
            c = mix(c, (0.22, 0.17, 0.11), 0.75)
        return c
    return fn


def t_sneaker_worn(x, y, a, b, r):
    c = mul((0.42, 0.4, 0.36), 0.8 + 0.3 * a)
    if b > 0.5:
        c = mix(c, (0.22, 0.17, 0.11), min(0.7, (b - 0.5) * 2.5))  # mud
    if x % 16 == 0 and y % 3:
        c = mul(c, 0.7)  # stitching
    return c


def t_shoe_black(x, y, a, b, r):
    """Plain black leather shoes, scuffed grey at the toes and caked with dried mud low down."""
    c = mul((0.075, 0.07, 0.065), 0.85 + 0.3 * a)
    if b > 0.62:
        c = mix(c, (0.2, 0.19, 0.18), min(0.5, (b - 0.62) * 3))  # scuffs
    if y > 50 and b > 0.45:
        c = mix(c, (0.2, 0.16, 0.11), 0.45)  # dried mud
    return c


def t_skin(x, y, a, b, r):
    """Body skin: the same base variation as face_tex's, tinted by the material colour (lin(face skin))."""
    return mul((1, 1, 1), 0.9 + 0.12 * a + 0.03 * r)


SKIN_A = (0.68, 0.55, 0.45)  # Alex's skin as displayed (sRGB): the face painting's base and the body material share it
SKIN_A_LIN = tuple(v ** 2.2 for v in SKIN_A)  # glTF baseColorFactor is linear, textures are sRGB


def grime(c, b, k=1.0):
    """Days without a wash: a patchy brown-grey film where the noise b is high. Shared by Alex's face and body."""
    return mix(c, (0.36, 0.3, 0.23), min(0.32, max(0.0, b - 0.55) * 1.4) * k)


def alex_face(x, y, a, b, r):
    """256px face: the 128-unit painting below sampled at half-pixel steps (smooth curves instead of blocky pixels).
    The eye regions are magnified ~15% (sampled closer to each eye centre) so the eyes read larger."""
    x, y = x / 2, y / 2
    fx, fy = x, y
    for ex in (42, 86):
        d = math.hypot(x - ex, (y - 57) * 1.6)
        if d < 17:
            f = 1 + 0.08 * (1 - d / 17) ** 0.5
            x, y = ex + (x - ex) / f, 57 + (y - 57) / f
            break
    c = _alex_face128(x, y, 0.5 + 0.25 * (a - 0.5), b, 0.5)  # damped noise: same skin as the body
    # light stubble over the jaw, upper lip and chin (not on the lips)
    ax = abs(fx - 64)
    g = lambda u, v: math.exp(-u * u - v * v)
    sm = lambda e0, e1, v: min(1.0, max(0.0, (v - e0) / (e1 - e0)))
    zone = max(sm(84, 92, fy), sm(32, 46, ax) * sm(68, 80, fy)) * sm(124, 114, fy) * (1 - g(ax / 17, (fy - 98) / 4.5))
    c = mix(c, (0.3, 0.24, 0.16), zone * (0.08 + 0.14 * (r < 0.4)))  # light stubble
    c = mix(c, (0.34, 0.27, 0.2), 0.3 * g((fx - 36) / 9, (fy - 24) / 5) + 0.22 * g((fx - 98) / 7, (fy - 104) / 8))  # smudges
    t = (fx - 88) / 6  # half-healed scratch across his left cheekbone
    if abs(t) < 1 and abs(fy - (70 - 2.5 * t)) < 0.6 + 0.4 * (1 - t * t):
        c = mix(c, (0.45, 0.16, 0.12), 0.75 * (1 - t * t) ** 0.3)
    elif abs(t) < 1.3 and abs(fy - (70 - 2.5 * t)) < 2.2:
        c = mix(c, (0.72, 0.42, 0.36), 0.2)
    return grime(c, b, 1.4)


def _alex_face128(x, y, a, b, r, _base=face_tex(mul(SKIN_A, 1 / 0.975), (0.38, 0.43, 0.46), (0.3, 0.24, 0.15), (0.54, 0.39, 0.35),
                                                 (0.42, 0.35, 0.24), hair_y=0, stubble=0.0, dirt=0.0, brow_w=1.9,
                                                 socket=0.82, lid=0.68, bags=0.88, lash=mul(SKIN_A, 0.32), glint=False)):
    """Face painting + cheek colour and a mouth line that survives 256px sampling."""
    c = _base(x, y, a, b, r)
    for sx in (1, -1):
        cx, cy = 64 + sx * 30, 76
        d = ((x - cx) / 14) ** 2 + ((y - cy) / 10) ** 2
        if d < 1:
            c = mix(c, (0.62, 0.4, 0.34), 0.06 * (1 - d))  # windburnt cheeks
    lip_h = 3.8 - ((x - 64) / 15) ** 2 * 3.5
    if abs(y - 98) < 0.55 and lip_h > 0 and 47 < x < 81:
        c = mul(c, 0.6)  # mouth line (the base's exact-row line vanishes at 256px)
    return c


def t_skin_a(x, y, a, b, r):
    """Tint over the material colour (SKIN_A): the face painting's faint variation and the same grime."""
    return grime(mul((1.0, 1.0, 1.0), 0.975 + 0.03 * (a - 0.5)), b)


def hair_ash_tex(x, y, a, b, r):
    """Dark ash blond, unwashed and matte: grey-brown strands, a few paler ones, greasy dark clumps,
    darker roots (fine strands run along v)."""
    h = (x * 73 + 11) % 17 / 17
    h2 = (x // 3 * 41 + 7) % 13 / 13
    base = mix((0.27, 0.24, 0.2), (0.37, 0.33, 0.27), 0.45 + 0.15 * h)  # ashy, barely warm: matte, not golden
    c = mix(base, (0.45, 0.41, 0.33), 0.3 * max(0.0, h2 - 0.65) * 2.5)
    if (x // 5 * 29 + 3) % 11 < 2:
        c = mul(c, 0.84)  # greasy clumps
    c = mul(c, 0.8 + 0.25 * a + 0.05 * (r - 0.5) + 0.08 * (b - 0.5))
    return mul(c, 0.78) if y < 24 else c


def t_tee_alex(x, y, a, b, r):
    """Once-white tee worn for weeks: dingy grey-beige, yellowed sweat blooms, ground-in dirt, dried blood flecks."""
    c = mul((0.6, 0.58, 0.52), 0.92 + 0.12 * a)
    if b > 0.55:
        c = mix(c, (0.56, 0.48, 0.3), min(0.35, (b - 0.55) * 2))  # sweat
    if b < 0.34:
        c = mix(c, (0.27, 0.23, 0.18), min(0.5, (0.34 - b) * 3))  # dirt
    if B._hash(x * 131 + y * 71) > 0.9 and 0.47 < b < 0.53 and a > 0.55:
        c = mix(c, (0.3, 0.1, 0.07), 0.6)  # a few dried blood flecks
    return c


def t_brand_hand(x, y, a, b, r):
    """Back of Alex's left hand: his skin (as t_skin_a x SKIN_A) with the Veil's Eye branded into it."""
    c = grime(mul(SKIN_A, 0.975 + 0.03 * (a - 0.5)), b)
    dx, dy = (x - 32) / 20, (y - 30) / 11
    lid = 1 - dx * dx
    if lid > 0 and abs(abs(dy) - lid) < 0.22 or (x - 32) ** 2 + (y - 30) ** 2 < 14:
        c = (0.36, 0.1, 0.08)
    return c


B.TEXTURES.update({
    "ca_face_alex": alex_face, "ca_skin_a": t_skin_a, "ca_hair_ash": hair_ash_tex, "ca_tee_white": t_tee_alex,
    "ca_brand_hand": t_brand_hand,
    "ca_jeans_black": jeans_tex((0.12, 0.12, 0.14)),
    "ca_jeans_fade": jeans_tex((0.12, 0.12, 0.14), fade=0.25),
    "ca_jeans_mud": jeans_tex((0.12, 0.12, 0.14), mud=0.6),
    "ca_sneaker_worn": t_sneaker_worn, "ca_skin": t_skin, "ca_shoe_black": t_shoe_black,
})
for _t in ("ca_skin_a", "ca_tee_white"):
    B.TEX_SIZE[_t] = 128
B.TEX_SIZE["ca_face_alex"] = 256
B.TEX_SIZE["ca_hair_ash"] = 256


def lin(c):
    """glTF colour factors are linear; textures are sRGB."""
    return tuple(v ** 2.2 for v in c)


B.MATS.update({
    "ca_skin_a": B.M("ca_skin_a", SKIN_A_LIN, 0.35),
    "ca_face_alex": B.M("ca_face_alex", fit=True),
    "ca_hair_ash": B.M("ca_hair_ash", scale=0.25, rough=1.0, bump=0.6), "ca_tee_white": B.M("ca_tee_white", scale=0.45),
    "ca_jeans_black": B.M("ca_jeans_black", scale=0.45), "ca_jeans_fade": B.M("ca_jeans_fade", scale=0.45),
    "ca_jeans_mud": B.M("ca_jeans_mud", scale=0.3), "ca_sneaker_worn": B.M("ca_sneaker_worn", scale=0.3),
    # body skin = the face painting's skin colour, linearised (the face texture bakes it in sRGB)
    "ca_skin": B.M("ca_skin", lin((0.64, 0.48, 0.38)), 0.4), "ca_skin_l": B.M("ca_skin", lin((0.72, 0.55, 0.45)), 0.4),
    "ca_skin_e": B.M("ca_skin", lin((0.68, 0.51, 0.41)), 0.4), "ca_skin_g": B.M("ca_skin", lin((0.72, 0.56, 0.47)), 0.4),
    "ca_sole_w": B.M("plain", (0.2, 0.19, 0.17), 1), "ca_sole_black": B.M("plain", (0.03, 0.03, 0.03), 1),
    "ca_shoe_black": B.M("ca_shoe_black", scale=0.3, rough=0.55),
    "ca_sneaker_l": B.M("ca_sneaker_worn", (0.75, 0.78, 0.9), 0.3),
})
B.fabric("knit", "ca_tee_white", bump=0.6, wrinkle=0.006)
B.fabric("twill", "ca_jeans_black", "ca_jeans_fade", "ca_jeans_mud", bump=0.9, wrinkle=0.007)
B.fabric("plain", "ca_sneaker_worn", "ca_sneaker_l", bump=0.8, wrinkle=0)
B.fabric("twill", "ca_denim", "ca_denim_navy", "ca_denim_torn", bump=0.9)
B.fabric("twill", "ca_canvas", "ca_apron")
B.fabric("plain", "ca_flannel", "ca_tee", "ca_grey_pants", "ca_bandage")
B.fabric("nylon", "ca_rain", "ca_rain_front", "ca_parka", "ca_parka_front", bump=0.6, wrinkle=0.006)
B.fabric("knit", "ca_knit", "ca_trousers")
B.fabric("leather", "ca_leather", "ca_rubber_boot", "ca_shoe_black", bump=0.8, wrinkle=0)
B.fabric("plain", "ca_sneaker", bump=0.8, wrinkle=0)


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


def head(m, face, back, secs, w=1.0, nose=1.0, ear_mat=None, brow=1.0, neck=1.0, chin=1.0, ear=1.0):
    """Oval skull + jaw with the painted face projected on the front half; nose, brow, lips, ears, neck."""
    m.use("Head")
    uv = face_uv(w)
    ys = [s[0] for s in secs]
    front = [[head_pt(secs, y, -PI / 2 + PI * j / 10) for j in range(11)] for y in ys]
    rear = [[head_pt(secs, y, PI / 2 + PI * j / 10) for j in range(11)] for y in ys]
    m.surface(face, front, uv=uv)
    m.surface(back, rear)
    m.lathe(back, [(0.058 * neck, -0.12), (0.051 * neck, -0.02), (0.047 * neck, 0.05)], (0, 0, -0.018), scale=(1, 1, 0.92), seg=12)
    zf = lambda y: sec_at(secs, y)[2] + sec_at(secs, y)[1]  # face surface depth at height y
    ell(m, face, (0.011 * nose, 0.03, 0.016 * nose), (0, 0.108, zf(0.108) - 0.004), (-20, 0, 0), 8, 5, uv)
    ell(m, face, (0.012 * nose, 0.01, 0.011 * nose), (0, 0.089, zf(0.089) + 0.005), seg=8, rings=5, uv=uv)
    for s in (1, -1):
        ell(m, face, (0.009 * nose, 0.008, 0.008), (s * 0.012, 0.087, zf(0.087) + 0.002), seg=6, rings=4, uv=uv)
        ell(m, face, (0.03, 0.009 * brow, 0.016 * brow), (s * 0.031, 0.163, zf(0.163) - 0.009 - 0.008 * (1 - brow)), (0, 0, s * -6), 8, 4, uv)
        rx = sec_at(secs, 0.12)[0]
        ell(m, ear_mat or back, (0.011 * ear, 0.029 * ear, 0.019 * ear), (s * (rx + 0.002), 0.118, -0.014), (0, s * 20, s * -6), 8, 5)
    ell(m, face, (0.025, 0.008, 0.011), (0, 0.059, zf(0.059) - 0.004), seg=8, rings=4, uv=uv)  # upper lip
    ell(m, face, (0.021, 0.008, 0.011), (0, 0.047, zf(0.047) - 0.004), seg=8, rings=4, uv=uv)  # lower lip
    ell(m, face, (0.022 * chin, 0.016, 0.014), (0, 0.016, zf(0.016) - 0.008), seg=8, rings=4, uv=uv)  # chin


def hair(m, mat, secs, bottom, thick=0.014, top_extra=0.012, spike=0.0, messy=0.004, fall=0.14,
         phis=None, y_top=0.25, cols=24, rows=7, seed=1, flare=0.0, flat=False, p=2.4):
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
            yy = max(y, fall) if abs(deg) > 50 else y
            hp = head_pt(secs, yy, math.radians(deg), p(yy) if callable(p) else p)
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
    if not flat:
        m.surface(mat, grid, wrap=wrap)
        return
    for k in range(rows):
        for j in range(n if wrap else n - 1):
            i = (j + 1) % n
            poly(m, mat, [grid[k][j], grid[k][i], grid[k + 1][i], grid[k + 1][j]], C)


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
                         (0.057 * k, 0.026), (0.046 * k, 0.045), (0.026 * k, 0.056), (0, 0.06)], seg=12, scale=(1, 1, 0.95))
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
    # rot (90,0,0) maps loft z to -y: keep the upper's underside inside the sole (y >= -0.046), whatever H is
    secs = [(y, rx, rz, ox, min(oz, 0.046 - rz)) for y, rx, rz, ox, oz in secs]
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


# ---- faceted (flat-shaded polygon) building blocks for Alex

def poly(m, mat, pts, center, uv=None, alt=None):
    """Flat polygon, winding fixed to face away from `center`; uv: optional fn(local_pt) -> (u, v)."""
    pts = [q for i, q in enumerate(pts) if q != pts[i - 1]]
    if len(pts) < 3:
        return
    c = tuple(sum(q[i] for q in pts) / len(pts) for i in range(3))
    if B.v_dot(B.newell(pts), B.v_sub(c, center)) < 0:
        pts = pts[::-1]
    if uv is not None and alt:  # planes edge-on to the painted face would smear it: plain skin there
        nn = B.v_norm(B.newell(pts))
        if nn[2] < 0.5:
            uv, mat = None, alt
    if uv is None:
        m.emit(mat, pts)
        return
    Mx, t = m.stack[-1]
    W = [B.v_add(B.m_vec(Mx, q), t) for q in pts]
    n = B.newell(W)
    if B.v_dot(n, n) < 1e-12:
        return
    n = B.v_norm(n)
    pos, nrm, uvs = m.cur["prims"].setdefault(mat, ([], [], []))
    for i in range(1, len(W) - 1):
        for k in (0, i, i + 1):
            pos.append(W[k])
            nrm.append(n)
            uvs.append(uv(pts[k]))


def fbox(m, mat, bot, top, h, pos=(0, 0, 0), rot=(0, 0, 0), shift=(0.0, 0.0), uv=None, alt=None):
    """Frustum from (w, d) at y=0 to (w, d) at y=h (top offset by shift): the workhorse of the faceted look."""
    bw, bd, tw, td = bot[0] / 2, bot[1] / 2, top[0] / 2, top[1] / 2
    sx, sz = shift
    Bp = [(-bw, 0, -bd), (bw, 0, -bd), (bw, 0, bd), (-bw, 0, bd)]
    Tp = [(sx - tw, h, sz - td), (sx + tw, h, sz - td), (sx + tw, h, sz + td), (sx - tw, h, sz + td)]
    c = (sx / 2, h / 2, sz / 2)
    with m.push(pos, rot):
        for i in range(4):
            j = (i + 1) % 4
            poly(m, mat, [Bp[i], Bp[j], Tp[j], Tp[i]], c, uv, alt)
        poly(m, mat, Bp, c, uv, alt)
        poly(m, mat, Tp, c, uv, alt)


def facets(m, mat, secs, seg=8, p=2.0, phase=0.5, uv=None):
    """Flat-shaded polygonal loft: sections (y, rx, rz[, ox, oz]) -> `seg`-sided rings joined by flat quads."""
    rings = []
    for sec in secs:
        y, rx, rz = sec[:3]
        ox, oz = sec[3:5] if len(sec) > 3 else (0.0, 0.0)
        row = []
        for j in range(seg):
            a = 2 * PI * (j + phase) / seg
            row.append((ox + rx * sp(math.sin(a), p), y, oz + rz * sp(math.cos(a), p)))
        rings.append(row)
    ctr = lambda r: tuple(sum(q[i] for q in r) / len(r) for i in range(3))
    for k in range(len(rings) - 1):
        r0, r1 = rings[k], rings[k + 1]
        c = tuple((u + v) / 2 for u, v in zip(ctr(r0), ctr(r1)))
        for j in range(seg):
            i = (j + 1) % seg
            poly(m, mat, [r0[j], r0[i], r1[i], r1[j]], c, uv)
    allc = tuple(sum(ctr(r)[i] for r in rings) / len(rings) for i in range(3))
    poly(m, mat, rings[0], allc, uv)
    poly(m, mat, rings[-1], allc, uv)


def blade(m, mat, root, tip, side, w, th, tipw=0.1):
    """Pointed hair blade from root to tip: base w x th (side = width direction), narrowing to a ridge at the tip."""
    d = B.v_sub(tip, root)
    n = B.v_cross(d, side)
    ln = math.sqrt(B.v_dot(n, n)) or 1
    n = B.mul(n, th / 2 / ln)
    sd = B.mul(side, 1 / (math.sqrt(B.v_dot(side, side)) or 1))
    a = lambda o, sx, sy: B.v_add(B.v_add(o, B.mul(sd, sx)), B.mul(n, sy))
    Bp = [a(root, -w / 2, -1), a(root, w / 2, -1), a(root, w / 2, 1), a(root, -w / 2, 1)]
    Tp = [a(tip, -w * tipw / 2, -0.3), a(tip, w * tipw / 2, -0.3), a(tip, w * tipw / 2, 0.3), a(tip, -w * tipw / 2, 0.3)]
    c = B.v_add(root, B.mul(d, 0.5))
    for i in range(4):
        j = (i + 1) % 4
        poly(m, mat, [Bp[i], Bp[j], Tp[j], Tp[i]], c)
    poly(m, mat, Tp, c)


def skull_pt(secs, y, phi_deg, out=0.0):
    """Point on the skull (head-local) at height y / azimuth phi (0 = front), pushed out along the radius by `out`."""
    hp = head_pt(secs, y, math.radians(phi_deg), 2.8)
    C = (0, 0.12, -0.01)
    d = B.v_sub(hp, C)
    ln = math.sqrt(B.v_dot(d, d)) or 1
    return B.v_add(hp, B.mul(d, out / ln))


def faceted_head(m, face, skin, secs, w=1.0):
    """Skull as flat planes: 10 columns x one ring per section. Front half carries the painted face."""
    m.use("Head")
    uv = face_uv(w)
    cols = [-180 + 18 + 36 * j for j in range(10)]  # points at +-18, 54, 90...: flat plane dead ahead
    grid = [[head_pt(secs, y, math.radians(ph), 2.8) for ph in cols] for y, *_ in secs]
    C = (0, 0.12, -0.01)
    for k in range(len(grid) - 1):
        for j in range(10):
            i = (j + 1) % 10
            quad = [grid[k][j], grid[k][i], grid[k + 1][i], grid[k + 1][j]]
            front = abs(((cols[j] + cols[i] + (360 if i < j else 0)) / 2 + 180) % 360 - 180) < 91
            front = (cols[j] >= -90 and cols[j] < 90) if i > j else False
            poly(m, face if front else skin, quad, C, uv if front else None)


def facial_features(m, face, skin, secs, nose=1.0, brow=1.0):
    """Nose wedge, brow ridge, cheekbones, lips, chin block, ears: all flat planes."""
    uv = face_uv(1.0)
    zf = lambda y: sec_at(secs, y)[2] + sec_at(secs, y)[1]
    c = (0, 0.1, 0.0)
    ny = lambda y, dz, x=0.0: (x, y, zf(y) + dz)
    root = ny(0.132, 0.0)
    bl, br = ny(0.12, 0.004, 0.009 * nose), ny(0.12, 0.004, -0.009 * nose)
    tip = ny(0.093, 0.027 * nose)
    wl, wr = ny(0.087, 0.008, 0.017 * nose), ny(0.087, 0.008, -0.017 * nose)
    base = ny(0.083, 0.012)
    pl, pr = ny(0.104, 0.002, 0.014 * nose), ny(0.104, 0.002, -0.014 * nose)
    for pts in ([root, bl, tip], [root, tip, br], [bl, pl, wl, tip], [br, tip, wr, pr], [tip, wl, base], [tip, base, wr],
                [root, br, bl]):
        poly(m, face, pts, c, uv, skin)
    # brow ridge: a shelf over the eyes, thicker at the centre
    for s in (1, -1):
        fbox(m, face, (0.058, 0.01 * brow), (0.056, 0.004), 0.012, (s * 0.032, 0.158, zf(0.158) - 0.004), (-8, 0, s * 4), (0, 0.003), uv, skin)
        # ear: flat paddle, top at the brow line, lobe at the nose base
        rx = sec_at(secs, 0.12)[0]
        fbox(m, skin, (0.015, 0.034), (0.012, 0.026), 0.052, (s * (rx + 0.006), 0.1, -0.012), (0, 0, s * -14), (0, -0.004))
    fbox(m, face, (0.05, 0.012), (0.044, 0.01), 0.011, (0, 0.056, zf(0.056) - 0.008), (-8, 0, 0), (0, 0.003), uv, skin)  # upper lip
    fbox(m, face, (0.042, 0.012), (0.038, 0.01), 0.011, (0, 0.04, zf(0.04) - 0.008), (0, 0, 0), (0, 0.003), uv, skin)  # lower lip
    fbox(m, face, (0.06, 0.02), (0.05, 0.016), 0.022, (0, 0.002, zf(0.002) - 0.018), (-6, 0, 0), (0, 0.004), uv, skin)  # chin


def lock_curve(m, mat, path, widths, th, n_around=5):
    """Smooth tapered lock: elliptical rings (w wide, th thick) along `path`, closing to a point at the tip."""
    C = (0, 0.12, -0.01)
    rows = []
    for i, pt in enumerate(path):
        t = B.v_sub(path[min(i + 1, len(path) - 1)], path[max(i - 1, 0)])
        nrm = B.v_sub(pt, C)
        nrm = B.mul(nrm, 1 / (math.sqrt(B.v_dot(nrm, nrm)) or 1))
        sd = B.v_cross(t, nrm)
        sd = B.mul(sd, 1 / (math.sqrt(B.v_dot(sd, sd)) or 1))
        w = widths[i]
        t_ = th * (0.35 if i == len(path) - 1 else 1.0)
        rows.append([B.v_add(pt, B.v_add(B.mul(sd, w * math.cos(2 * PI * j / n_around)),
                                         B.mul(nrm, t_ * math.sin(2 * PI * j / n_around)))) for j in range(n_around)])
    rows.append([path[-1]] * n_around)  # tip pole
    # winding: make quad normals face away from the lock's axis
    q = [rows[1][0], rows[1][1], rows[2][1], rows[2][0]]
    nn = B.newell(q)
    axis = B.v_sub(rows[1][0], path[1])
    if B.v_dot(nn, axis) < 0:
        rows = [r[::-1] for r in rows]
    m.surface(mat, rows, wrap=True)


def skull_pt(secs, y, phi_deg, out=0.0):
    x, yy, z = head_pt(secs, y, math.radians(phi_deg), alex_p(y))
    C = (0, 0.12, -0.01)
    d = B.v_sub((x, y, z), C)
    return B.v_add((x, y, z), B.mul(d, out / (math.sqrt(B.v_dot(d, d)) or 1)))


def lock_on_skull(m, mat, secs, y0, ph0, y1, ph1, w, th=0.008, lift=0.012, steps=5, out0=0.012, out1=0.016, taper=0.45):
    """Lock lying on the skull from (y0, ph0) to (y1, ph1), lifting off the surface in the middle (curl)."""
    path, widths = [], []
    for i in range(steps):
        t = i / (steps - 1)
        out = out0 + (out1 - out0) * t + lift * math.sin(PI * t)
        path.append(skull_pt(secs, y0 + (y1 - y0) * t, ph0 + (ph1 - ph0) * t, out))
        widths.append(w * (0.85 + 0.3 * math.sin(PI * t) - taper * t ** 1.5) * (1 + 0.15 * math.sin(i * 7.3 + w * 900)))
    lock_curve(m, mat, path, widths, th)


def alex_hair(m, mat, secs):
    """Classic short-to-medium cut (youthful, not trendy): soft fringe swept to his right, sides just touching the tops
    of the ears, back tapering at the upper nape; tousled, soft-ended locks over a full cap."""
    line = [(-180, 0.098), (-150, 0.1), (-120, 0.108), (-95, 0.135), (-75, 0.16), (-45, 0.182), (0, 0.19),
            (45, 0.182), (75, 0.16), (95, 0.135), (120, 0.108), (150, 0.1), (180, 0.098)]
    hair(m, mat, secs, lambda d: lerp_tab(line, d), thick=0.006, top_extra=0.03, spike=0.0, messy=0.002,
         cols=40, rows=10, seed=5, fall=0.0, p=alex_p)
    rng = __import__("random").Random(31)
    L = lambda *a, **k: lock_on_skull(m, mat, secs, *a, **k)
    # fringe: soft, to mid-forehead, swept to his right with a few gaps
    for k in range(18):
        if k in (5, 12):
            continue
        ph = -66 + k * 7.6 + rng.uniform(-2, 2)
        y1 = (0.188 if k < 4 or k > 14 else 0.175) + rng.uniform(-0.008, 0.01)  # shorter at the corners
        L(0.25, ph * 0.6, y1, ph - 20 + rng.uniform(-6, 6), 0.021 + rng.uniform(-0.003, 0.003),
          th=0.006, lift=0.012 + rng.uniform(0, 0.006), out0=0.02, out1=0.013, steps=6, taper=0.4)
    # sides: just touching the tops of the ears, ends flicking back
    for sg in (1, -1):
        for k in range(8):
            ph = 66 + k * 8 + rng.uniform(-2, 2)
            L(0.232, sg * ph, 0.132 + rng.uniform(-0.008, 0.01), sg * (ph + 16 + rng.uniform(-3, 5)), 0.02, th=0.006,
              lift=0.011, out0=0.022, out1=0.016, steps=6, taper=0.4)
    # back: tapering to the upper nape
    for k in range(14):
        ph = 132 + k * 7 + rng.uniform(-2, 2)
        L(0.238 + rng.uniform(-0.01, 0.006), ph, 0.1 + rng.uniform(-0.016, 0.018), ph + rng.uniform(-12, 12), 0.022, th=0.006,
          lift=0.01, out0=0.02, out1=0.014, steps=6, taper=0.4)
    # crown: a few loose pieces lying back so the top isn't a smooth helmet
    for k in range(10):
        ph = -170 + k * 36 + rng.uniform(-8, 8)
        L(0.254, ph, 0.21 + rng.uniform(-0.01, 0.01), ph + rng.uniform(-28, 28), 0.02, th=0.006,
          lift=0.009, out0=0.022, out1=0.018, taper=0.4)


# ---- sculpted head: dense smooth skull + anatomical bumps/dents (brow, sockets, cheekbones, nose, lips, chin, jaw)

def _g(x, y, cx, cy, sx, sy, amp):
    return amp * math.exp(-((x - cx) / sx) ** 2 - ((y - cy) / sy) ** 2)


# (cx, cy, sx, sy, amp): mirrored about x=0 when cx != 0
FACE_FEATURES = [
    (0.030, 0.158, 0.032, 0.01, 0.009), (0.0, 0.153, 0.018, 0.009, 0.004),      # brow ridge
    (0.034, 0.140, 0.019, 0.012, -0.009),                                          # eye sockets
    (0.033, 0.149, 0.016, 0.004, 0.002),                                          # upper lids
    (0.0, 0.120, 0.014, 0.024, 0.013), (0.0, 0.094, 0.017, 0.013, 0.018),          # nose bridge + tip
    (0.018, 0.088, 0.010, 0.009, 0.005),                                           # nostril wings
    (0.0, 0.084, 0.011, 0.004, -0.003),                                            # under nose
    (0.048, 0.1, 0.032, 0.026, 0.004), (0.042, 0.066, 0.026, 0.02, -0.0022),                                              # broad cheekbone (sharper ones crease)
    (0.0, 0.0615, 0.02, 0.0055, 0.0105), (0.0, 0.0445, 0.018, 0.0065, 0.011),    # lips
    (0.0, 0.0525, 0.024, 0.0020, -0.0025),                                         # mouth line
    (0.0, 0.0300, 0.018, 0.0060, -0.0015), (0.0, 0.016, 0.026, 0.016, 0.009),     # chin groove + chin
]


def alex_p(y):
    """Superellipse power over head height: rounder cheeks/jaw (no corner between face and side planes), fuller skull."""
    t = min(1.0, max(0.0, (y - 0.1) / 0.07))
    return 2.1 + 0.4 * t * t * (3 - 2 * t)


def smooth_secs(secs, n=4):
    """Catmull-Rom through the (y, rx, rz, oz) rows: no creases where linear interpolation would kink at each row."""
    out = []
    P = [secs[0]] + list(secs) + [secs[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(4)))
    out.append(secs[-1])
    return [(y, max(0.0, rx), max(0.0, rz), oz) for y, rx, rz, oz in out]


def sculpt_head(m, face, skin, secs, w=1.0):
    """Painted-face front (uv-projected) + plain-skin rear, both dense smooth grids sharing the seam column."""
    m.use("Head")
    uv = face_uv(w)
    ys = [-0.014 + 0.264 * (k / 33) for k in range(34)]
    half = [0, 4, 8, 12, 16, 21, 26, 32, 38, 44, 50, 57, 65, 73, 81, 89, 97, 105]
    front_phi = [-h for h in reversed(half[1:])] + half
    rear_phi = list(range(105, 256, 15))

    def pt(y, phi):
        x, yy, z = head_pt(secs, min(max(y, secs[0][0] + 1e-4), secs[-1][0] - 1e-4), math.radians(phi), alex_p(y))
        if abs(phi) <= 105 or phi >= 255:
            d = sum(_g(abs(x), y, cx, cy, sx, sy, a) for cx, cy, sx, sy, a in FACE_FEATURES)
            d *= max(0.0, math.cos(math.radians(phi))) ** 0.6
            oz = sec_at(secs, y)[2]
            r = math.hypot(x, z - oz) or 1
            x, z = x + d * x / r, z + d * (z - oz) / r
        return (x, y, z)

    m.surface(face, [[pt(y, ph) for ph in front_phi] for y in ys], uv=uv)
    m.surface(skin, [[pt(y, ph) for ph in rear_phi] for y in ys])


def sculpt_ears(m, skin, secs, ear=1.25):
    for s in (1, -1):
        rx = sec_at(secs, 0.11)[0]
        ell(m, skin, (0.0085 * ear, 0.03 * ear, 0.019 * ear), (s * (rx + 0.004), 0.1, -0.008), (0, s * 12, s * -8), 8, 6)
        ell(m, skin, (0.006 * ear, 0.012 * ear, 0.012 * ear), (s * (rx + 0.001), 0.075, -0.002), (0, 0, 0), 6, 4)  # lobe


def body_loft(m, mat, secs, feats=(), seg=24, power=2.4):
    """loft() plus anatomy: feats (cx, cy, sx, sy, amp, side) are gaussian swellings (amp > 0) or grooves (< 0),
    mirrored in x, on the front (side=+1, +Z) or back (side=-1) of the rings, pushed out radially."""
    rows = []
    for sec in secs:
        y, rx, rz = sec[:3]
        ox, oz = sec[3:5] if len(sec) > 3 else (0.0, 0.0)
        row = []
        for j in range(seg):
            a = -2 * PI * j / seg
            c, sn = math.cos(a), math.sin(a)
            x, z = ox + rx * sp(c, power), oz + rz * sp(sn, power)
            d = sum(amp * math.exp(-((abs(x) - cx) / sx) ** 2 - ((y - cy) / sy) ** 2) * max(0.0, side * sn) ** 0.5
                    for cx, cy, sx, sy, amp, side in feats)
            ln = math.hypot(x - ox, z - oz) or 1
            row.append((x + d * (x - ox) / ln, y, z + d * (z - oz) / ln))
        rows.append(row)
    m.surface(mat, rows, wrap=True)


def alex_leg_sections(prof, sx=1.0, sz=0.95):
    return [(y, r * sx, r * sz) for r, y in prof]


def m_alex():
    """Alex Moreno (player), faceted low-poly: planar jaw/brow/nose, pointed hair blades, angular torso and limbs."""
    # arm pivots a little closer in than the shared rig: slim build, shoulders sit on the narrower torso
    m = rig.skeleton("char_alex", overrides={"UpperArmL": (0.193, 0.465, 0), "UpperArmR": (-0.193, 0.465, 0)})
    hs = [(-0.004, 0.0, 0.0, 0.07), (0.0, 0.034, 0.03, 0.07), (0.01, 0.05, 0.046, 0.062), (0.028, 0.063, 0.066, 0.042),
          (0.055, 0.075, 0.09, 0.02), (0.085, 0.084, 0.098, 0.003), (0.115, 0.083, 0.103, -0.002)] + [(y, rx * 1.025, rz, oz) for y, rx, rz, oz in HEAD[7:]]
    hs = smooth_secs(hs)
    with m.push((0, 0.02, 0)):  # lift the head off the shoulders: visible neck
        sculpt_head(m, "ca_face_alex", "ca_skin_a", hs)
        sculpt_ears(m, "ca_skin_a", hs)
        m.use("Head")
        m.lathe("ca_skin_a", [(0.061, -0.14), (0.064, -0.08), (0.063, -0.02), (0.058, 0.03), (0.055, 0.06)], (0, 0, -0.012), scale=(1, 1, 0.95), seg=14)  # neck
        alex_hair(m, "ca_hair_ash", hs)
    # torso from adult male proportions: ~0.40 m across the shoulders, 0.34 chest, 0.30 waist; trapezius slopes
    # from the neck to the shoulder; pecs, shoulder blades and spine groove read through the tee
    m.use("Spine")
    body_loft(m, "ca_tee_white", [
        (-0.13, 0.176, 0.128, 0, 0.008), (-0.126, 0.188, 0.135, 0, 0.008), (-0.09, 0.178, 0.122, 0, 0.004), (-0.04, 0.162, 0.108, 0, 0.003),
        (0.05, 0.139, 0.097, 0, 0.004), (0.12, 0.145, 0.099, 0, 0.006), (0.19, 0.158, 0.104, 0, 0.009),
        (0.26, 0.166, 0.107, 0, 0.011), (0.32, 0.172, 0.108, 0, 0.012), (0.38, 0.18, 0.105, 0, 0.01), (0.42, 0.203, 0.099, 0, 0.006),
        (0.447, 0.216, 0.093, 0, 0.0), (0.468, 0.212, 0.085, 0, -0.005), (0.488, 0.18, 0.078, 0, -0.008),
        (0.506, 0.148, 0.074, 0, -0.01), (0.522, 0.112, 0.07, 0, -0.011), (0.536, 0.092, 0.066, 0, -0.011),
        (0.542, 0.086, 0.063, 0, -0.011)],
        feats=[(0.065, 0.34, 0.05, 0.035, 0.0035, 1), (0.0, 0.33, 0.012, 0.07, -0.002, 1),      # pecs, sternum
               (0.085, 0.38, 0.05, 0.065, 0.009, -1), (0.0, 0.25, 0.013, 0.2, -0.004, -1)],    # shoulder blades, spine
        seg=28, power=2.4)
    ell(m, "ca_tee_white", (0.088, 0.007, 0.065), (0, 0.541, -0.011), seg=24, rings=4)  # ribbed crew collar
    m.use("Hips")
    body_loft(m, "ca_jeans_black", [(-0.21, 0.0, 0.0), (-0.2, 0.09, 0.07), (-0.15, 0.158, 0.104), (-0.1, 0.168, 0.108),
                                    (-0.05, 0.15, 0.098), (0.03, 0.14, 0.088), (0.1, 0.13, 0.082)],
              feats=[(0.068, -0.125, 0.055, 0.05, 0.016, -1)], seg=24, power=2.4)  # seat

    def limbs(side, s):
        m.use("UpperArm" + side)
        # upper arm: biceps swell in front, triceps behind, narrowing to the elbow
        m.loft("ca_skin_a", [(-0.29, 0.037, 0.038), (-0.24, 0.04, 0.043, 0, 0.002), (-0.17, 0.046, 0.051, 0, 0.003),
                             (-0.1, 0.045, 0.049, 0, 0.001), (-0.03, 0.044, 0.046), (-0.008, 0.04, 0.04),
                             (0.0, 0.0, 0.0)], seg=16, power=2.3)
        # short sleeve: a tube just over the deltoid, top tucked under the torso's shoulder line (no puffed cap)
        m.loft("ca_tee_white", [(-0.12, 0.052, 0.054), (-0.115, 0.055, 0.057), (-0.06, 0.054, 0.056), (-0.01, 0.052, 0.054),
                                (0.008, 0.046, 0.048), (0.018, 0.03, 0.034), (0.024, 0.0, 0.0)], seg=18, power=2.2)
        m.use("Forearm" + side)
        ell(m, "ca_skin_a", (0.039, 0.04, 0.04), seg=12, rings=8)  # elbow: fills the bend between the open tube ends
        # forearm: muscular swell just below the elbow, flattening toward the wrist
        m.loft("ca_skin_a", [(-0.258, 0.029, 0.026), (-0.2, 0.032, 0.028), (-0.13, 0.04, 0.036), (-0.06, 0.05, 0.045, 0.004, 0),
                             (0.0, 0.043, 0.042), (0.02, 0.037, 0.037)], seg=16, power=2.3)
        hand(m, side, s, "ca_skin_a", back="ca_brand" if side == "L" else None)
        if side == "R":  # grubby bandage wound round the forearm
            m.use("ForearmR")
            m.lathe("ca_bandage", [(0.031, -0.236), (0.035, -0.232), (0.037, -0.2), (0.042, -0.16), (0.047, -0.12),
                                   (0.048, -0.112), (0.044, -0.108)], seg=12)
        m.use("Thigh" + side)
        # front of the thigh top flattened under the pelvis: at a high knee drive it stays under the tee hem
        m.loft("ca_jeans_black", [(-0.43, 0.074, 0.073), (-0.34, 0.073, 0.072), (-0.2, 0.086, 0.083, 0, -0.002),
                                  (-0.12, 0.093, 0.085, 0, -0.008), (-0.05, 0.098, 0.08, 0, -0.016),
                                  (0.04, 0.094, 0.07, 0, -0.02)], seg=18, power=2.4)
        m.use("Shin" + side)
        ell(m, "ca_jeans_black", (0.074, 0.074, 0.073), seg=16, rings=8)  # knee: rounds the bend, no gap at the kick
        prof = jeans_leg(hem_r=0.078, top_r=0.076)
        lo = [q for q in prof if q[1] <= -0.355]
        hi = [q for q in prof if q[1] >= -0.355] + [(0.076, 0.03)]
        m.loft("ca_jeans_mud", [(y, r, r * 0.95) for r, y in lo], seg=16, power=2.4)
        m.loft("ca_jeans_black", [(y, r, r * 0.95) for r, y in hi], seg=16, power=2.4)
        m.use("Foot" + side)
        shoe(m, "ca_shoe_black", "ca_sole_black", L=1.05, W=1.0, H=0.95)
    rig.mirror(limbs)
    return m


def sash(m, mat, y, tilt, rx=0.245, rz=0.14, oz=0.01):
    """Diagonal strap round the torso (a thin ring whose rim pokes out of the body)."""
    ell(m, mat, (rx, 0.011, rz), (0, y, oz), (0, 0, tilt), seg=16, rings=4)


def tails(m, mat, secs, power=2.6, seg=10, ov=15, inner=None):
    """A coat's skirt below the waist (secs Hips-local (y, rx, rz[, ox, oz]), bottom to top) split in halves on the
    Skirt joints, which swing with the thighs. Each half wraps ov deg past the front and back centre lines so no
    slit opens as they part; the right one sits a hair outside. inner: lining material."""
    rig.skirt_joints(m)
    for k, s in (("L", 1), ("R", -1)):
        m.use("Skirt" + k)
        g = 1.0 if s > 0 else 1.012
        a0 = -ov if s > 0 else 180 - ov
        ths = [math.radians(a0 + (180 + 2 * ov) * j / seg) for j in range(seg + 1)]  # 0 = front, 90 = +X
        grid = [[((c[3] if len(c) > 3 else 0) + c[1] * g * sp(math.sin(t), power) - s * 0.1, c[0] + 0.05,
                  (c[4] if len(c) > 4 else 0) + c[2] * g * sp(math.cos(t), power)) for t in ths] for c in secs]
        m.surface(mat, grid)
        if inner:
            m.surface(inner, [[(x * 0.98 - s * 0.002, y, z * 0.98) for x, y, z in row[::-1]] for row in grid])


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
        coat = [(-0.2, 0.188, 0.125), (-0.15, 0.183, 0.122), (-0.05, 0.174, 0.117),
                (0.05, 0.168, 0.113, 0, 0.005), (0.15, 0.174, 0.118, 0, 0.012), (0.25, 0.183, 0.124, 0, 0.02),
                (0.33, 0.188, 0.12, 0, 0.02), (0.4, 0.194, 0.11, 0, 0.012), (0.45, 0.2, 0.098, 0, 0.0),
                (0.49, 0.19, 0.086, 0, -0.008), (0.515, 0.14, 0.075, 0, -0.01), (0.545, 0.07, 0.06, 0, -0.012),
                (0.55, 0, 0, 0, -0.012)]
        torso(m, "ca_rain", coat)
        zipper(m, coat, -0.19, 0.52)
        # below the hips the coat swings with the legs (Skirt joints); its top tucks up under the Spine part
        tails(m, "ca_rain", [(-0.34, 0.208, 0.145), (-0.22, 0.2, 0.137), (-0.07, 0.19, 0.127), (0.0, 0.183, 0.12),
                             (0.04, 0.175, 0.114)], inner="ca_rain")
        m.use("Spine")
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
            m.box("ca_strap", (0.025, 0.4, 0.01), (sd * 0.1, 0.3, -0.107), (0, 0, sd * -8))  # suspenders, on the back
        m.box("ca_apron", (0.13, 0.1, 0.012), (0.05, 0.1, front_z(shirt, 0.1) + 0.012))  # bib pocket
        m.cyl("ca_metal", 0.005, 0.005, 0.1, (0.09, 0.1, front_z(shirt, 0.1) + 0.018), seg=4)  # pencil
        hips = [(-0.21, 0, 0), (-0.2, 0.085, 0.07), (-0.16, 0.16, 0.11), (-0.08, 0.18, 0.125, 0, 0.01),
                (0.0, 0.185, 0.13, 0, 0.02), (0.07, 0.185, 0.135, 0, 0.025), (0.1, 0.18, 0.13, 0, 0.02),
                (0.1, 0, 0, 0, 0.02)]
        torso(m, "ca_grey_pants", hips, joint="Hips")
        ell(m, "ca_leather", (0.187, 0.022, 0.137), (0, 0.06, 0.024), seg=16, rings=3)  # belt
        m.loft("ca_apron", [(-0.12, 0, 0, 0, 0.14)] + [(y, 0.19, 0.008, 0, front_z(hips, max(y, -0.16)) + 0.014) for y in
                            (-0.12, 0.0, 0.06)] + [(0.06, 0, 0, 0, 0.14)], seg=12, power=5)
        for k, sd in (("L", 1), ("R", -1)):  # split skirt (halves overlap at the middle) on the thighs: a flat panel
            m.use("Thigh" + k)                # this close to the legs can't lag behind the knee; tops tuck under the band
            m.loft("ca_apron", [(-0.56, 0, 0, 0, 0.14)] + [(y, 0.11, 0.008, sd * 0.08 - sd * 0.1, front_z(hips, max(y, -0.16))
                                + (0.01 if sd > 0 else 0.012)) for y in (-0.56, -0.3, -0.1, 0.0)] + [(0.0, 0, 0, 0, 0.14)],
                   (0, 0.05, 0), seg=12, power=5)

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
