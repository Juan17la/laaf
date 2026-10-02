"""Shared humanoid rig for every LAAF character (segmented PS2-style, no skinning).

All characters face +Z, Y up, feet on y=0. The character's LEFT side is +X.
Each joint is a glTF node; geometry added after m.use("<Joint>") is in that
joint's local space (origin = the joint pivot). scripts/humanoid_anim.gd drives
these exact node names, so never rename them; proportions may change freely.

    Hips ─ Spine ─ Head
         │       ├ UpperArmL ─ ForearmL ─ HandL
         │       └ UpperArmR ─ ForearmR ─ HandR
         ├ ThighL ─ ShinL ─ FootL
         └ ThighR ─ ShinR ─ FootR

Limbs hang straight down from their joint (-Y). The foot pivot is the ankle;
toes point +Z. Hands hang down from the wrist.
"""
import build_assets as B

# name, parent, offset from parent pivot (1.78 m adult)
RIG = [
    ("Hips", None, (0, 0.95, 0)),
    ("Spine", "Hips", (0, 0.08, 0)),
    ("Head", "Spine", (0, 0.55, 0)),
    ("UpperArmL", "Spine", (0.2, 0.47, 0)),
    ("ForearmL", "UpperArmL", (0, -0.29, 0)),
    ("HandL", "ForearmL", (0, -0.26, 0)),
    ("UpperArmR", "Spine", (-0.2, 0.47, 0)),
    ("ForearmR", "UpperArmR", (0, -0.29, 0)),
    ("HandR", "ForearmR", (0, -0.26, 0)),
    ("ThighL", "Hips", (0.1, -0.05, 0)),
    ("ShinL", "ThighL", (0, -0.43, 0)),
    ("FootL", "ShinL", (0, -0.42, 0)),
    ("ThighR", "Hips", (-0.1, -0.05, 0)),
    ("ShinR", "ThighR", (0, -0.43, 0)),
    ("FootR", "ShinR", (0, -0.42, 0)),
]


def skeleton(name, scale=1.0, overrides=None):
    """New Model with all joints created. overrides: {joint: offset} replaces the default
    offset (unscaled). Use scale ~0.93 for shorter adults; keep leg offsets summing to the
    Hips height so feet land on y=0."""
    m = B.Model(name)
    m.smooth = m.ao = True  # trilinear textures + baked occlusion for every character
    for joint, parent, off in RIG:
        off = (overrides or {}).get(joint, off)
        m.node(joint, parent, tuple(v * scale for v in off))
    return m


def mirror(fn):
    """Call fn(side, sign) for 'L' (+1, +X) and 'R' (-1, -X) so limbs are built once."""
    for side, sign in (("L", 1), ("R", -1)):
        fn(side, sign)
