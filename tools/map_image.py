"""Top-down field map of Hollowmere -> maps/hollowmere_map.png (python3 tools/map_image.py).

Square image, north (-Z) up. World -> pixel: px = (x - MAP_X0) * PPM, py = (z - MAP_Z0) * PPM.
player/guide.gd mirrors these constants; keep them in sync.
"""
import math
import os
import random

import build_assets as B

PPM = 2  # pixels per metre
SPAN = B.Z1 - B.Z0  # 405 m: the taller axis; x is padded to a square around the walkable area
MAP_X0 = (B.X0 + B.X1) / 2 - SPAN / 2  # -217.5
MAP_Z0 = B.Z0  # -220
SIZE = int(SPAN * PPM)  # 810

PAPER = {
    "grass": (168, 150, 112), "forest": (128, 118, 86), "gravel": (182, 170, 140), "mud": (132, 112, 84),
    "rock": (112, 102, 88), "water": (84, 92, 88), "road": (206, 192, 158), "walk": (190, 176, 142),
    "building": (52, 42, 34), "ravine": (70, 62, 54),
}


def main():
    B.EXTRA_PACKS[:] = B._load_packs()
    W = B.build_world()
    buildings = W.rects[len(B.ROADS) + len(B.LOTS):]
    rng = random.Random(7)
    img = [[None] * SIZE for _ in range(SIZE)]

    def world(px, py):
        return MAP_X0 + (px + 0.5) / PPM, MAP_Z0 + (py + 0.5) / PPM

    def fill(x0, z0, x1, z1, c):
        for py in range(max(0, int((z0 - MAP_Z0) * PPM)), min(SIZE, int(math.ceil((z1 - MAP_Z0) * PPM)))):
            row = img[py]
            for px in range(max(0, int((x0 - MAP_X0) * PPM)), min(SIZE, int(math.ceil((x1 - MAP_X0) * PPM)))):
                row[px] = c

    for py in range(SIZE):
        for px in range(SIZE):
            x, z = world(px, py)
            h = B.height(x, z)
            if h < -3:
                c = PAPER["ravine"]
            elif h < -0.6:
                c = PAPER["water"]
            else:
                c = PAPER[B.ground_mat(x, z, h)]
                if h > 1.2:  # mountains: darker with distance, diagonal hatching
                    c = B.mul(c, max(0.6, 1 - h / 80) * (0.8 if (px + py) % 6 < 2 else 1))
            img[py][px] = c
    for (ax, az), (bx, bz), w, mat in B.ROADS:
        if mat == "asphalt":
            fill(min(ax, bx) - w / 2 - B.SIDEWALK, min(az, bz) - w / 2 - B.SIDEWALK,
                 max(ax, bx) + w / 2 + B.SIDEWALK, max(az, bz) + w / 2 + B.SIDEWALK, PAPER["walk"])
    for r in B.ROADS:
        fill(*B._road_rect(r), PAPER["road"] if r[3] == "asphalt" else PAPER["gravel"])
    for x0, z0, x1, z1, _ in B.LOTS:
        fill(x0, z0, x1, z1, PAPER["walk"])
    for cx, cz, r in W.circles:  # trees and props: small ink dots
        fill(cx - 0.8, cz - 0.8, cx + 0.8, cz + 0.8, (96, 86, 62))
    for x0, z0, x1, z1 in buildings:
        fill(x0, z0, x1, z1, PAPER["building"])

    # worn paper: faint 25 m grid, blotchy stains, grain, darkened edges
    stains = [(rng.uniform(0, SIZE), rng.uniform(0, SIZE), rng.uniform(40, 160), rng.uniform(0.05, 0.12)) for _ in range(14)]
    rows = []
    for py in range(SIZE):
        row = bytearray()
        for px in range(SIZE):
            c = img[py][px]
            x, z = world(px, py)
            k = 1.0
            if abs((x + 0.25) % 25) < 0.5 or abs((z + 0.25) % 25) < 0.5:
                k *= 0.93
            for sx, sy, sr, sa in stains:
                d = ((px - sx) ** 2 + (py - sy) ** 2) / (sr * sr)
                if d < 1:
                    k *= 1 - sa * (1 - d)
            e = min(px, py, SIZE - 1 - px, SIZE - 1 - py) / 60
            if e < 1:
                k *= 0.7 + 0.3 * e
            k *= 1 + rng.uniform(-0.05, 0.05)
            row += bytes(max(0, min(255, int(v * k))) for v in c)
        rows.append(row)
    out = os.path.join(B.ROOT, "maps", "hollowmere_map.png")
    with open(out, "wb") as f:
        f.write(B.png(rows, False, SIZE))
    print("%s written (%dx%d, %d buildings)" % (out, SIZE, SIZE, len(buildings)))


if __name__ == "__main__":
    main()
