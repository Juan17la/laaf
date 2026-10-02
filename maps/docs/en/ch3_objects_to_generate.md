# Chapter 3 — Objects to generate later

Chapter 3 (*The Veil*) is playable with **placeholder geometry**: primitive boxes / cylinders built in code,
or existing models reused for something they aren't. This file lists every object that should get a real
model, so it can be made later with the same pipeline as the rest of the game (`tools/models_*.py` →
`B.Model(name)`, PS2 look, one `.glb` in `models/`, collision on `*-col` nodes, `detail` nodes without).

How to read the tables:

- **ID** — the suggested model name (`models/<id>.glb`).
- **Used in** — where the placeholder lives today. Swap it there once the model exists.
- **Placeholder** — what stands in now.
- **Size / pivot** — metres; pivot at the base centre unless stated. Characters and props face **+Z**
  (the game's convention; `yaw 0` faces +Z).

Rendering targets match the existing props: low-poly, baked texture atlas, no normal maps, 300–1,500
tris for hand props, 2,000–6,000 for set pieces, characters on the shared rig (`tools/rig.py`).

---

## 1. New player items (the things Alex can use)

These are the new mechanics' objects. Three are inventory items shown in the HUD belt line
(`Bottle ×n [G]  Smoke ×n [T]  Tea ×n [H]`).

| ID | What it does in game | Used in | Placeholder | Size / pivot | Look |
|---|---|---|---|---|---|
| `item_smoke_can` | **T** throws it; lands in a 3.5 m grey cloud for 10 s. Enemies can't see through or into it (`SmokeCloud.blocks`). Found in Elena's stash (×2), from Grady (×1), 20 % of Chapter 3 loot drops | `player/player.gd` `throw_smoke()` → `_lob()`; pickups in `chapter3.gd` `_drop_loot()` | grey cylinder r 0.05 × 0.24 | 0.07 × 0.24 × 0.07, pivot centre (it spins in flight) | Olive-drab military canister, pull ring on top, stencilled "SMOKE"; one version with a moth scratched on it (Elena's) |
| `item_tea_tin` | **H** drinks Elena's tea: Mark −15 %. Chapter 2 pharmacy gives 2, *Empty Chairs* gives 2 | `player.gd` `drink_tea()`; `chapter3.gd` `_candle()` | none (HUD only); Ch.2 used a brown box | 0.08 × 0.1 × 0.08 | Small dented tin, hand-lettered paper label "E.R. — for the head", string tie |
| `item_elena_jacket` | Given by Grady at the lighthouse. Worn: Mark gain ×0.75 (`player.mark_resist`) | `ch3_scenes_a.gd` `the_bell()` (lying in the mud), `static_grief()` (carried) | yellow box 0.55 × 0.05 × 0.75 | folded: 0.4 × 0.1 × 0.3; draped over an arm: 0.4 × 0.6 × 0.12 | Yellow fisherman's rain jacket, torn at one shoulder, mud on the hem. Two variants: folded/draped prop, and mud-flat on the ground |
| `char_alex_raincoat` | Alex wearing Elena's jacket for the rest of Chapter 3 (cosmetic, `flags.jacket`) | swap `player/player.tscn` Model when `flags.jacket` | not shown (Alex keeps the old model) | shared rig | `char_alex` with the yellow jacket over the clothes; hood down |
| `item_flare_shell` | Flare gun ammo; Grady gives 2, Elena's drawer 1. Flare hits stun the Harvester (light) | `chapter3.gd` `_ask_grady()`, `_recorder()` | banner only | 0.04 × 0.1 × 0.04 | Red paper-cased 12-gauge flare cartridge (for pickups / HUD icon) |

## 2. Cemetery & church (M1 *Run*, M2 *Marcus*)

| ID | What it does in game | Used in | Placeholder | Size / pivot | Look |
|---|---|---|---|---|---|
| `prop_church_bell` ×3 | Hangs 5 m over the nave aisle. **Shoot it / its chain, or release its rope** → it drops: crushes whoever is under it (30 % of max HP + 4.5 s stun), the clang deafens (stuns 3 s) every enemy within 16 m. One use each, re-hung on checkpoint reload | `scripts/bell.gd` `Bell.make()` | bronze cylinder (r 0.32 → 0.72, 1.1 high) + grey chain box | bell Ø 1.4 × 1.1; **pivot at the lip centre**; chain is a separate node that hides on drop | Green-bronze bell with a cast band of names, iron yoke and clapper. A dented "dropped" state would be nice (swap mesh on `_impact`) |
| `prop_bell_rope_cleat` ×3 | The wall cleat the rope is tied to (the interactable "Release the bell rope") | `bell.gd` (rope = thin box from the bell to the cleat) | thin brown box as the rope, nothing for the cleat | cleat 0.25 × 0.1 × 0.1 on the wall; rope 0.03 thick | Iron cleat bolted to the stone, rope wound in figure-eights |
| `prop_bell_register` | Evidence #7: every blackout rung since the festival | `chapter3.gd` `_register()`, `ch3_scenes_a.gd` `register_found()` | dark box | 0.22 × 0.04 × 0.3 on a lectern | Leather ledger on a small iron lectern by the door; last line "One. Elena." |
| `prop_clara_photo` | Marcus's personal item (spare condition), on the choir pew | `_clara_photo()`, `photo_found()`, `marcus_spared()` | cream card | 0.1 × 0.14 | Small framed photo, a laughing woman in a choir robe |
| `prop_votive_candle` ×5 | *Empty Chairs*: light one for each family (Tomás, Clara, the Clarkes, Lily, Sam) | `chapter3.gd` `_candle()` | light only | 0.06 × 0.1 | Glass votive holder, stub candle; unlit and lit states |
| `prop_chapel_key` | The key to the Veil's Chapel (Marcus) | `chapel_key_found()` | dark box | 0.08 × 0.02 × 0.22 | Heavy iron key, the Veil's Eye cast into the bow |
| `prop_quarry_map` | Evidence #8: Elena's stolen quarry map (Marcus kept it) | `chapel_key_found()` | (same pickup) | 0.3 × 0.22 paper | Folded survey map, pencil notes, one cage circled in red |
| `prop_elena_stash` | Elena's tin under the mausoleum step: 2 smoke cans + a bandage | `chapter3.gd` `STASH`, `stash_found()` | grey box | 0.2 × 0.1 × 0.14 | Biscuit tin tucked under a lifted marble step; the moth decal on the step above |
| `prop_hand_bell` | Marcus rings it at each phase change to call Marked Ones | barks only (`marcus_phase()`) | none | 0.12 × 0.25 | Brass hand bell, wooden handle (attach to `HandL`) |
| `prop_sledgehammer` | Marcus's weapon (fight + "the sledgehammer rolls out of his hand") | Enemy melee (no mesh) | none | 0.9 long | Long-handled sledge, taped grip (attach to `HandR`) — check whether `char_marcus.glb` already bakes one |
| `prop_gate_chained` | The east cemetery gate, chained shut by the Marked Ones during the chase | `chapter3.gd` `_bar_gate()` | 3 × `fence_iron.glb` + invisible wall | 10.4 wide × 3 high, pivot centre | Double iron gate, heavy chain and padlock, a lantern hung on it |

## 3. Harbor & lighthouse (M3 *Static*)

| ID | What it does in game | Used in | Placeholder | Size / pivot | Look |
|---|---|---|---|---|---|
| `int_transmitter_desk` | Elena's radio room: the grief scene, **the transmitter** (broadcast, needs 12/12 evidence) | `chapter3.gd` `_transmitter()`, `static_grief()`, `broadcast()` | `crate.glb` + `int_radio.glb` (`Ch2ScenesA._radio_prop`) | desk 1.2 × 0.8 × 0.6 | Plank desk, short-wave set, desk microphone, pencil ticks on the dial ("7, 7, 7"), a thermos |
| `prop_thermos` | Set dressing in the grief scene | `static_grief()` (subtitle only) | none | 0.08 × 0.3 | Dented green thermos |
| `prop_recorder` | *Last Recording*: Elena's pocket recorder (+1 flare) | `_recorder()`, `last_recording()` | dark box | 0.1 × 0.03 × 0.16 | Cheap cassette dictaphone, masking-tape label "IF I DON'T COME BACK" |

## 4. Quarry & chapel (choice point, C3.2, M4, C3.3)

| ID | What it does in game | Used in | Placeholder | Size / pivot | Look |
|---|---|---|---|---|---|
| `prop_floodlight_rig` ×3 | **Final-fight weapon.** Dead until phase 2 (03:00). Throw the switch (crank QTE unless both cages were freed): the beam burns 8 s on a ground spot; the Harvester standing in it is stunned 3 s (then immune 5 s). Bulb pops, 10 s cooldown | `scripts/floodlight.gd` | steel boxes (pole 5 m, head 1 × 0.7) + emissive lens box; generator = `ext_generator.glb` | pole 5.2 high, pivot at base; the head is a **separate node aimed with `look_at`** | Rusted quarry floodlight tower, cage over the lamp, cable running to the generator; a hand crank on the generator. Lit / dark / popped-bulb states |
| `prop_cage_padlock_eye` | The cage padlock: no keyhole, an eye (Lucía's cage; the *Cages* lockpick) | `the_harvest()` subtitle, `_cage()` | the padlock baked into `cage.glb` | 0.12 × 0.14 | Iron padlock shaped like the Veil's Eye |
| `prop_skull_sword` | The Harvester's sword once it falls (C3.3, carried out in *Unveiled*) | `harvester_down()`, `ending_unveiled()` | bone-coloured box 0.3 × 0.2 × 2.0 | 2.0 long, pivot at the grip | Two-metre blade of fused skulls and pitch; a broken version in two halves + loose skulls to scatter |
| `prop_brand_iron` | On the altar; offered to Alex in *The New Eye* | `the_shepherd()`, `ending_new_eye()` | dark box + red emissive box | 0.7 long | Iron rod, wooden grip, the Eye glowing red at the tip |
| `prop_shepherd_ledger` | Lore: "The ledger has every name" (C3.4). Not interactable yet | C3.4 narration | none | 0.25 × 0.06 × 0.35 | Thick parish ledger, candle wax on the cover |
| `quarry_lower_cells` | Where the Taken come out in *Signal*; referenced in C3.4 | `ending_signal()` (actors walk out from behind the chapel) | nothing (they appear from behind the rock) | ~8 × 4 × 10 | Barred doorway cut into the rock behind the chapel, steps going down |
| `chapel_ossuary_stair` | Where the Shepherd sat in the dark "the whole time" | `the_shepherd()` (`SHEP_SPOT`) | nothing | 1.2 × 2 | Narrow stair down beside the altar, a stool and a lamp at the top |
| `veh_rescue_helicopter` | *Signal* ending: "Lights over the lake" | `ending_signal()` | two sweeping `SpotLight3D` 45 m up | ~12 m long | County rescue helicopter; only needs to read as a silhouette + searchlight |
| `decal_scraped_eye` | *Unveiled*: the eyes scraped off every door at dawn | `ending_unveiled()` (Marcus "reach" at the chapel facade) | nothing — the facade eye stays | 1 × 1 decal | The Veil's Eye half scraped away, bare stone showing |

## 5. Characters

| ID | Role | Used in | Placeholder | Notes |
|---|---|---|---|---|
| `char_tomas` | Elena's brother, 17, found alive in *Signal* ("Is Elena with you?") | `ending_signal()` | `char_marked_man.glb` | Thin, pale, long hair, a festival wristband still on; the Eye brand on his hand |
| `char_caleb` | The Harvester unmasked (optional, for a future version of C3.4) | C3.4 narration only | the fallen `char_boss.glb`; its red eye lights fade out (`Harvester.eyes_off`) | Man in his fifties, burn- and tar-scarred, milky eyes; red glass miner's lenses pushed up on his forehead |
| `char_taken` | The townsperson the Harvester carries over its shoulder in C3.2 | `the_harvest()` | `char_marked_man.glb`, rotated | Could stay the Marked model; a limp pose would help |

## 6. Decals & FX

| ID | Used in | Placeholder | Notes |
|---|---|---|---|
| `decal_moth` | Elena's stash step; lighthouse door in the *Signal* epilogue | glow of the interactable only | Elena's moth symbol, scratched / painted, 0.3 m |
| `fx_sweep_ring` | Harvester phase-3 sweep telegraph (1.3 s, radius 5.5 m) | flat red transparent cylinder (`harvester.gd` `_ring`) | Cracked-ground ring that fills from the centre |
| `fx_red_cracks` | Harvester "spent" window (×2 damage) | red `OmniLight3D` on its chest | Emissive crack texture on `char_boss.glb` (second material slot) |
| `fx_smoke_puff` | `SmokeCloud` | `GasCloud` puff texture tinted grey | 32 px dithered PS2 puff sprite |

## 7. Level geometry that Chapter 3 works around

| Area | Current state | What the docs asked for | What to build |
|---|---|---|---|
| Church bell tower | Solid tower in `church.glb` (no interior) | "Vertical arena with 3 bell platforms" (chapters.md §5 M2) | The fight runs in the **nave** with 3 bells hung over the aisle. A later tower interior (3 platforms, ladders, one bell each) can reuse `bell.gd` as is: `Bell.make(parent, floor_point_under_bell, cleat_point)` |
| Veil's Chapel | 8 × 10 m room, door 1.6 × 2.8 m | "The Harvester walks out of the chapel" | It comes home down the quarry road instead (it can't fit the door). A wider back entrance would let the original staging work |
| Quarry | Open pit, lantern poles, 3 cages | "Holding cells" | See `quarry_lower_cells` |

---

When a model lands: put it in `models/`, then replace the placeholder at the **Used in** location
(most are one `load("res://models/<id>.glb").instantiate()` in place of a `_box(...)` / `BoxMesh`).
Keep the collision layers the placeholders use — bells are on layer 2 (bullets) while hanging and
layer 1 once down; floodlight heads and poles have no collision.
