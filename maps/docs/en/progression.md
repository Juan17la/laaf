# Progression & Flow — LAAF

Chapter‑by‑chapter flow with triggers, flags and ending conditions. See [story.md](story.md) for narrative and [map.md](map.md) for zones.

## 1. Global flags

| Flag | Type | Default | Set by |
|---|---|---|---|
| `chapter` | int | 0 | Chapter transitions |
| `mark` | float 0–100 | 0 | Mark meter |
| `tokens` | int | 0 | Minigames, loot, shop |
| `upgrades` | dict stat→tier | all 0 | Shop |
| `evidence` | set of ids 1–12 | empty | Picking up evidence |
| `key_parts` | set {1,2,3} | empty | Owen / Nora / Julian (defeat or steal) |
| `has_chapel_key` | bool | false | Marcus (defeat or steal) |
| `traitor_alive` | bool | true | Chapter 6 execution → false |
| `member_state[owen/nora/julian/marcus]` | enum `active / spared / killed / fled` | `active` | Boss resolution |
| `personal_item[member]` | bool | false | Lily's drawing, Sam's file, Clara's photo, parents' lantern |
| `broadcast_sent` | bool | false | Lighthouse transmitter |
| `minigame_daily[name]` | int | 0 | Reset on sleep |
| `first_win[name]` | bool | false | First minigame win |
| `times_taken` | int | 0 | Mark 100% at blackout |
| `difficulty` | enum | normal | Settings |

Derived: `members_spared`, `members_killed`, `members_fled` = counts of `member_state`.

## 2. Chapters

> **Superseded by [chapters.md](chapters.md)** (3 chapters × 10 min). The table below is the original long‑form (5–7 h) plan, kept for reference; flags and ending rules in the rest of this doc still apply.

| # | Name | Location | Main objectives | Unlocks | Trigger to next |
|---|---|---|---|---|---|
| 0 | Arrival | Bridge → square → motel | Walk into town, meet Grady, rent room | — | Sleep in motel |
| 1 | The Mark | Motel & forest edge | Wake up marked, read Moth's note, survive Owen's first hunt (tutorial: hide, sneak, dodge) | Radio (channel 7) | Reach Grady's store |
| 2 | The Square | Hub | Shop tutorial, first minigames (arcade, shooting gallery, card game low stakes), radio contact with Moth | Shop, minigames, journal | Accept Moth's task |
| 3 | The Woodsman | Forest & Sawmill | Find flares, get key part 1, **boss Owen** | Harbor, fishing, lighthouse radio | Boss resolved or fled + key part 1 |
| 4 | Moth | Harbor & Lighthouse | Meet Elena in person, learn the evidence plan, learn about Nora and Julian | School + Clinic (any order) | Talk to Elena |
| 5 | The Teacher / The Medic | School, Clinic | Key parts 2 and 3, personal items, **boss Nora**, **boss Julian** | High‑stakes card table, shotgun later | Both zones resolved |
| 6 | The Traitor | Church & Cemetery | Go to meeting, **Elena's execution (scripted)**, escape the group, **boss Marcus** | Hunters roam everywhere; one safe room per zone burned | Marcus resolved or fled + chapel key |
| 7 | Static | Lighthouse | Grief scene, collect remaining evidence, optional broadcast (needs 12/12, code 1413) | Quarry road | Leave the lighthouse |
| 8 | The Quarry | Quarry & Chapel | Enter chapel, find Lucía, confront The Shepherd, open tunnel gate | Endings | Ending |

Chapter 5 zones and the order within Act II are free; everything else is linear with an open hub.

**Run option:** from the moment `key_parts` has all 3, the tunnel gate can be opened directly from the quarry road (prompt: *"Leave now?"*). Choosing it ends the game with the **Run** ending.

## 3. Elena's execution (Chapter 6) — rules

- Always happens; can't be prevented.
- Who is present: **Marcus** + every member whose state is `active` or `fled`. Spared members are absent (and later tell Alex they refused to go). Killed members' absence is remarked on by Marcus.
- The player watches from a hiding spot (camera forced to a cinematic angle). Moving out of hiding makes the group see Alex → escape chase through the cemetery (no fail state beyond damage).
- After the scene: `traitor_alive = false`, Mark growth ×1.5, hunters become roamers, one safe room per zone burned, The Shepherd starts radio taunts.

## 4. Endings — conditions

Evaluated in order when the player finishes Chapter 8 (or chooses to leave early).

| Priority | Ending | Condition |
|---|---|---|
| 1 | **Run** | Tunnel opened before entering the chapel |
| 2 | **Signal** (hidden) | `broadcast_sent` and `members_killed == 0` |
| 3 | **Unveiled** | `members_spared == 4` |
| 4 | **The New Eye** | `members_killed == 4` |
| 5 | **Mixed** | Anything else |

Finale variations by `member_state`:
- `spared` + personal item → appears as **ally** in the quarry (helps in the fight against the Marked Ones).
- `spared` without personal item → does not appear.
- `fled` → appears as **enemy** in the quarry (last chance to spare/kill).
- `killed` → their mask hangs in the chapel.

## 5. Difficulty curve

| Chapter | Hunter pressure | Marked Ones | Mark growth | Safe rooms | New mechanic |
|---|---|---|---|---|---|
| 1 | Scripted | 0 | Low | Motel | Hide, sneak, dodge |
| 2 | None | 0 | None | Hub | Shop, minigames |
| 3 | 1 hunter (Owen) | Few | Low | 2 | Traps, fire stun, boss choice |
| 4 | None | Few | Low | Lighthouse | Story, fishing, radio |
| 5 | 1 hunter per zone | Medium | Medium | 2 per zone | Remote locks, gas, cameras |
| 6 | Group + Marcus | Many | High (×1.5) | 1 per zone | Roamers, bells |
| 7 | 1 roamer | Medium | High | Lighthouse | Broadcast |
| 8 | Fled members + Marked Ones | Many | High | None | Final choice |

## 6. Pacing rules

- After every boss: a **memory** flashback (calm, 2–4 min), then a return to the hub (shop + minigames).
- Never two hunts in a row without a safe moment in between.
- Each chapter introduces **one** new mechanic at most.
- Minigames are unlocked gradually (arcade/gallery/cards in Ch.2, fishing/radio in Ch.3, high‑stakes cards in Ch.5) so the player always has something new to spend time on.
