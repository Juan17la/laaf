# Chapters — LAAF (3 × 10 min)

The whole story of [story.md](story.md) told in **three chapters of ~10 minutes each** (≈30 min per playthrough on the critical path). Every chapter has the same shape:

```
 Opening cinematic ─► Main mission (2–4 steps) ─► Small missions + minigames (optional)
        ─► Hunter / boss encounter ─► Closing cinematic + chapter card
```

This structure **replaces** the 8‑chapter table in [progression.md](progression.md) §2. Flags, endings, the Mark meter, spare/kill/flee rules and the economy stay as documented there and in [gameplay.md](gameplay.md) / [minigames.md](minigames.md); only the pacing and what happens in each chapter change.

## 0. Timing rules

- **10 min = critical path**, including cinematics, for a player who knows where to go but isn't speed‑running. Optional small missions and minigames add ~3–6 min per chapter.
- In‑game clock: 1 hour = 2.5 real minutes, so **one chapter = 4 in‑game hours**. Each chapter ends on a fixed clock beat (the 03:00 blackout or the 19:00 meeting), so the story, not the player, closes it.
- Cinematics: **≤ 1 min each, skippable** after the first viewing, max ~2.5 min of cinematics per chapter.
- One new mechanic per chapter at most (see [progression.md](progression.md) §6).
- Autosave at the start of every mission step and before every boss.
- **Time budget per chapter:** cinematics 15% · exploration/stealth 45% · boss 25% · hub/minigames 15%.

## 1. The boss — The Harvester

The boss model (`models/char_boss.glb`) is **The Harvester**: the Veil's executioner, the thing that collects the Taken at the 03:00 blackout.

| Field | Value |
|---|---|
| Look | ~2.8 m tall, heavily muscled, body fully black like wet tar, two burning red eyes, no mouth. Carries a two‑metre **sword of fused skulls**, the skulls of the Taken |
| What it is | Never fully explained. The Shepherd calls it "the Harvest". Townsfolk think it is the first person The Veil ever broke. The five friends have only seen it at a distance, on the Night of Lanterns |
| Role | Chapter 1: seen only (it can't be fought). Chapter 2: appears on the horizon at 03:00 in the Taken sequence. Chapter 3: **final boss** in the quarry |
| Weakness | **Light.** Flares, the lighthouse beam and the chapel floodlights make it recoil (stun 3 s). The skull sword only blocks from the front |
| Tone rule | It never talks. Its footsteps are the only loud thing during a blackout. It isn't a monster to farm: it is the physical shape of "being taken" |

Placed at the Veil's Chapel door in `maps/hollowmere.tscn` (build_world, quarry section).

## 2. Overview

| # | Chapter | Clock | Zones | Main mission | Boss / hunt | Closes with |
|---|---|---|---|---|---|---|
| 1 | **The Mark** | 19:00 → 03:00 (skip to 23:00) | Bridge, motel, forest edge, square, sawmill | Survive the first night, get key part 1 | Owen (hunt, then boss) | Blackout: first sight of The Harvester |
| 2 | **Moth** | 09:00 → 19:00 (skip to 15:00) | Harbor, lighthouse, school, clinic | Meet Elena, get key parts 2 and 3 | Nora + Julian (short bosses) | Elena's execution at the church |
| 3 | **The Veil** | 23:00 → 03:00 | Cemetery, church, lighthouse, quarry, chapel | Escape the group, take the chapel key, reach Lucía | Marcus + **The Harvester** | Ending (5 variants) |

Evidence split (12 total, [map.md](map.md)): Chapter 1 → #11, #1, #2 · Chapter 2 → #3, #4, #5, #6, #9, #10, #12 · Chapter 3 → #7, #8.

---

## 3. Chapter 1 — The Mark (10:00)

**Goal of the chapter:** teach movement, hiding and the Mark; make the player feel hunted; end on a hook.
**New mechanic:** stealth (hide, sneak, noise) + the boss choice.

### Flow

| Time | Beat | Type | Content |
|---|---|---|---|
| 0:00–1:00 | **C1.1 "Last Postcard"** | Cinematic | Alex's car dies at the collapsed bridge at dusk; Lucía's postcard on the dashboard ("Hollowmere is beautiful. Don't come."). Alex walks past the `HOLLOWMERE POP. 1413` sign. Grady at the store window refuses to talk, gives a motel key "for one night". Fade on Room 6. |
| 1:00–1:30 | **C1.2 "3:00 minus four"** | Cinematic (short) | 23:00. A shape behind the window glass (Owen). A hiss, a smell of burning. Alex wakes clutching their hand. |
| 1:30–3:00 | **M1 "Room 6"** | Main mission | 1. Look at the hand: the Veil's Eye is burned into it (Mark meter appears at 10%). 2. The door has the same eye painted on it. 3. Pick up Moth's note under the door: *"Don't let them see you after dark. Radio, channel 7."* 4. **Radio tuning** (tutorial, mandatory, 30 s): Moth's voice: *"They marked you. Get to the square. Stay in the grass."* |
| 3:00–5:00 | **M2 "First Hunt"** | Hunt (scripted) | Owen walks the motel walkway with a bow. Tutorial prompts: crouch, hide in tall grass, throw a bottle to distract, dodge. Route: motel → forest edge → Lake Rd → square. Being caught = damage + Mark +15%, never death. The tension director always lets the player through. |
| 5:00–6:30 | **M3 "The Square"** | Hub | Grady opens the store only because Alex is marked ("Marked folk pay in tokens. Everyone else is already paid for."). Shop tutorial: buy or receive **2 flares** (needed for the boss). Radio: Moth sends Alex to the sawmill: *"Owen carries a piece of the gate key. He's scared of fire."* |
| 6:30–9:00 | **M4 "The Woodsman"** | Main mission + boss | 1. Follow the forest trail past bear traps (footprints in mud show Owen follows yours). 2. Find **key part 1** in the foreman's office and **evidence #1**. 3. **Boss Owen** (burnt sawmill floor, 2 phases): phase 1 bow + traps; phase 2 chainsaw. A flare or a burning barrel stuns him for 6 s: hit him while he freezes. The escape exit opens after phase 1 (flee). 4. **Spare / Kill** prompt. Spare with the parents' lantern = "Tell me it wasn't for nothing." |
| 9:00–10:00 | **C1.3 "Blackout"** | Closing cinematic | 03:00. Every light in Hollowmere goes out, one street at a time (the new street lamps die in sequence). From the sawmill yard Alex sees, across the lake, **The Harvester** walking the quarry road, dragging its skull sword, a Marked townsperson over its shoulder. It stops and turns its red eyes toward Alex. Cut to black. Radio: *"Harbor. Tomorrow. Come alone. — Moth."* Chapter card: **I · THE MARK**. |

### Small missions (optional, +3–5 min)

| Mission | Where | Task | Reward |
|---|---|---|---|
| **Room 4** | Motel | Lockpick (1 pin) the room next door: Lucía's old room | **Evidence #11** (Lucía's camera, last photo: the quarry chapel) |
| **The Parents' Lantern** | Sawmill office loft | Climb the log pile, find the burnt festival lantern | Owen's personal item (full "spare" scene) |
| **Mailbox 12** | Maple Ave | Read a neighbour's letter, bring it to Grady | 15 tokens + Grady's first real line of dialogue |
| **Tripwire** | Forest trail | Disarm 3 tripwire bells without ringing them | 10 tokens, **evidence #2** under the last bell |

### Minigames available

| Minigame | Where | Note |
|---|---|---|
| Radio tuning | Room 6 | Tutorial, mandatory once |
| Lockpicking | Room 4, sawmill lockers | Tutorial on 1 pin |
| Shooting gallery | Festival grounds (square) | Optional, 60 s; loud (20 m), draws Marked Ones at night |

### Close / exit state

- Flags: `chapter = 1`, `key_parts = {1}`, `member_state[owen]` set (or `fled`), `mark ≈ 30–45`.
- Tokens expected: ~60–90.
- If the player fled from Owen, he appears again in Chapter 3 as a roamer.

---

## 4. Chapter 2 — Moth (10:00)

**Goal of the chapter:** give the player an ally and the plan, two quick hunter zones, then take the ally away.
**New mechanic:** zone weaknesses (power room / vents) + free order between two zones.

### Flow

| Time | Beat | Type | Content |
|---|---|---|---|
| 0:00–1:00 | **C2.1 "Moth"** | Opening cinematic | 09:00, fog on the harbor. A woman in a yellow rain jacket on the dock, hand bandaged: **Elena**. She shows her own brand: *"I'm one of them. I'm also the only one who wants them gone."* She explains the three‑part gate key (Owen, Nora, Julian), the chapel key (Marcus), and that **Lucía was taken to the quarry alive**. |
| 1:00–2:00 | **M1 "Channel Seven"** | Main mission (short) | Carry the car battery from the boathouse to the lighthouse radio room. **Radio tuning** clears Elena's hidden recording: **evidence #9**. Elena marks the school and the clinic on Alex's map. Clock skips to 15:00. |
| 2:00–5:30 | **M2 "The Teacher"** | Zone + boss | School. Nora's voice on the PA (*"Lily, sweetheart, we have a guest."*), music boxes as noise traps, mannequins dressed as children. 1. Reach the basement **power room** and cut the power: PA and remote locks die. 2. Find **key part 2** and **Lily's drawing** (classroom 3). 3. **Boss Nora** in the auditorium, in the dark: she calls for Lily and gives away her position; hit her from the shadows (2 phases). 4. Spare / Kill. |
| 5:30–9:00 | **M3 "The Medic"** | Zone + boss | Clinic. Julian gasses corridors and always checks hiding spots he saw you use. 1. Get the **gas mask** from the ambulance bay. 2. Roof HVAC room: **reverse the vents**. 3. **Key part 3** and **Sam's file** (records room). 4. **Boss Julian** in the glass surgery hall: reversed gas triggers his asthma (stun). 5. Spare / Kill. |
| 9:00–10:00 | **C2.2 "The Traitor"** | Closing cinematic | 19:00, the church. Elena waits among the graves with the stolen quarry map. Alex arrives late and is forced into hiding (camera locked to the mausoleum). **Marcus** rings the bell; the group steps out of the fog (Marcus + every member still `active` or `fled`). Spared members are missing. Marcus: *"Three years, Elena."* Elena looks toward Alex's hiding spot, not at them: *"Channel seven… one‑four‑one‑three. Tell them his name was Tomás."* The bell rings once more. Cut to black on the sound. Chapter card: **II · MOTH**. |

School and clinic can be played in **either order** (M2 and M3 swap). Each is ~3.5 min on the critical path.

### Small missions (optional, +4–6 min)

| Mission | Where | Task | Reward |
|---|---|---|---|
| **Old Tom** | Harbor fishing dock | **Fishing**: catch the legendary catfish | 150 tokens + a note about Tomás; sunken box with **evidence #10** |
| **Silas's Table** | The Drowned Lantern bar | **Lantern Hi‑Lo** vs Silas (low stakes). Win 3 hands at the high table | **Evidence #12** (the Shepherd's letter); Silas' rumor tells Julian's patrol route |
| **Recess** | School playground | Silence the 3 music boxes before entering | The PA ambush in M2 is skipped |
| **Triage** | Clinic ward | Free a Marked patient strapped to a bed | Medkit + the patient hints at **evidence #6** in the morgue freezer |
| **Hidden in class** | School classrooms | Search desks | **Evidence #3, #4** |
| **Pharmacy** | Clinic | Lockpick (3 pins) the pharmacy cabinet | Elena's tea ×2, **evidence #5** |

### Minigames available

Fishing (harbor, daytime) · Radio tuning (lighthouse) · Lantern Hi‑Lo (bar) · Lockpicking · Arcade "Moth Run" (diner; the 10,000‑point message from Elena now reads as a goodbye after C2.2).

### Close / exit state

- Flags: `chapter = 2`, `key_parts = {1,2,3}` (if stolen or resolved), `member_state[nora/julian]` set, `traitor_alive = false`.
- Unlocks the **Run** prompt at the tunnel gate (all 3 key parts held).
- After C2.2: Mark growth ×1.5, all surviving hunters become roamers, the Shepherd starts radio taunts.
- Tokens expected: ~350–500 total.

---

## 5. Chapter 3 — The Veil (10:00)

**Goal of the chapter:** grief, rage and the final choice. The player can **run**, **fight** or **kill** their way out.
**New mechanic:** roaming hunters + light as a weapon against The Harvester.

### Flow

| Time | Beat | Type | Content |
|---|---|---|---|
| 0:00–0:30 | **C3.1 "The Bell"** | Opening cinematic | The group turns toward the mausoleum. Someone saw Alex. Marcus: *"The outsider. Bring them."* |
| 0:30–2:00 | **M1 "Run"** | Chase | Escape through the cemetery at night. Bells ring when Alex is seen; Marked Ones close the gates. Hide in mausoleums or break line of sight with a smoke can. Ends in the church nave. No fail state beyond damage. |
| 2:00–4:30 | **M2 "The Bell Tower"** | Boss | **Boss Marcus**, vertical arena with 3 bell platforms. He swings a sledgehammer and rings the bells to call Marked Ones. Drop a bell on him (3 platforms = 3 phases). **Clara's photo** is in the choir room on the way up. Spare / Kill. Reward: **the chapel key**, **evidence #7, #8**. |
| 4:30–6:00 | **M3 "Static"** | Main mission (quiet) | The lighthouse, empty. **Grief scene** (cinematic, 40 s): Elena's radio still on, her jacket on the chair. Grady arrives with the yellow rain jacket: *"She'd want it worn."* Optional **broadcast**: **radio tuning** with code **1413** (needs 12/12 evidence and no one killed → sets `broadcast_sent`). |
| 6:00–6:30 | **Choice point "The Gate"** | Decision | On the quarry road, the Old Pass Tunnel gate with 3 key slots. Prompt: *"Leave now?"* → **Run** ending (skip to 9:00). Otherwise continue to the chapel. |
| 6:30–7:30 | **C3.2 "The Harvest"** | Cinematic | The Veil's Chapel. Candles, festival lanterns, cages. **Lucía** in a cage, alive, marked. The Shepherd's voice on a radio: *"You came for her. They all come for someone."* The floor shakes: **The Harvester** walks out of the chapel dragging its skull sword. Spared members who got their personal item arrive behind Alex. |
| 7:30–9:30 | **M4 "The Harvester"** | Final boss (3 phases) | **Phase 1:** it blocks with the skull sword from the front; circle it, hit its back. **Phase 2:** it calls the Marked Ones; switch on the 3 chapel **floodlights** (each stuns it 3 s). **Phase 3:** the sword sweeps the whole arena; dodge, then light a **flare** in its face and hit the red cracks. Allies (spared members) each help once: Owen throws fire, Nora cuts the power to the Marked Ones' lanterns, Julian gasses them, Marcus holds a gate. `fled` members fight on its side. |
| 9:30–10:00 | **C3.3 "The Shepherd"** | Closing cinematic | Behind the altar: a tired old man with a radio, the brand iron on the table. *"I never took anyone. They brought them to me."* The ending plays (see below) and the ending screen shows stats. Chapter card: **III · THE VEIL**. |

### Small missions (optional, +3–4 min)

| Mission | Where | Task | Reward |
|---|---|---|---|
| **Empty Chairs** | Church nave | Light a candle on each of the friends' family pews (5) | Elena's tea ×2, Mark −20% |
| **Last Recording** | Lighthouse radio room | Play Elena's recorder | Her last message; +1 flare |
| **Ask Grady** | Store | Talk to Grady after the execution | He gives 2 flares + 1 smoke can for free ("Don't pay. Just end it.") |
| **Cages** | Quarry | Lockpick 2 cages of Marked townsfolk before the chapel | They light the quarry lanterns: phase 2 floodlights start already on |

### Minigames available

Radio tuning (broadcast) · Lockpicking (quarry cages) · Grady's shop. The daytime minigames (fishing, arcade, cards) are closed: the town is at war.

### Endings (C3.3 variants, ≤ 30 s each)

Conditions and priority as in [progression.md](progression.md) §4.

| Ending | Final shot |
|---|---|
| **Run** | Alex drives alone through the tunnel. The mark itches. Radio static: "Channel 7…". Lucía is not found. |
| **Signal** (hidden) | Helicopter lights over the lake. Tomás among the freed Taken. Elena's name is the last thing on screen. |
| **Unveiled** | The spared friends carry The Harvester's broken sword out of the chapel. The painted eyes are scraped off the doors at dawn. Alex and Lucía leave by the tunnel. |
| **The New Eye** | The Shepherd offers Alex the brand iron: "You did their work better than they did." Final shot: Alex painting an eye on a stranger's door. |
| **Mixed** | Alex carries a wounded Lucía through the tunnel. Epilogue cards: spared = redeemed, killed = buried, fled = still guarding the town. |

### As built (scripts/chapter3.gd)

Implemented in `scripts/chapter3.gd` (flow), `scripts/ch3_scenes_a.gd` (C3.1 → lighthouse) and `scripts/ch3_scenes_b.gd` (quarry → C3.4). Dev skip: `-- --chapter=3` or `-- --step=<c3_bell|run|marcus|static|gate|harvest|harvester|shepherd|epilogue>`. Placeholder objects and what to model later: [ch3_objects_to_generate.md](ch3_objects_to_generate.md).

**New mechanics**

| Mechanic | Rule | Where |
|---|---|---|
| Smoke can (T) | Lands in a 3.5 m cloud for 10 s; enemies can't see into or through it. Elena's stash ×2, Grady ×1, some loot | `player.gd` `throw_smoke`, `smoke_cloud.gd` |
| Elena's tea (H) | Mark −15 %. The Ch.2 tins carry over; *Empty Chairs* gives 2 | `player.gd` `drink_tea` |
| The Mark creeps | +0.075 %/s at night while in control (×1.5 after Elena), capped at 99 %. Above 50 % every noise carries further (×1.5 at 100 %). Elena's jacket (from Grady) = Mark gain ×0.75 | `chapter3.gd` `_process`, `player.gd` `noise` |
| The bell (M1) | Any chaser that sees Alex rings the church bell: every chaser converges (10 s cooldown). The east gate is chained: the church is the only way out | `chapter3.gd` `_step_run` |
| The nave bells (M2) | The tower is solid in `church.glb`, so the three bells hang **over the nave aisle**. Shoot a bell/chain or release its rope: whoever is under it takes 30 % max HP + 4.5 s stun; the clang stuns every other enemy within 16 m. Marcus: armor ×0.5 unless stunned, hearing ×2.5; at ⅔ and ⅓ HP he rings the hand bell (2 Marked Ones through the door) and speeds up | `bell.gd`, `chapter3.gd` `_step_marcus` |
| Light (M4) | The Harvester's weakness. Flare hits and floodlight beams stun it 3 s, then it's immune 5 s. A flashlight held on its face for 1 s staggers it (6 s cooldown) | `harvester.gd` |
| Floodlights (M4) | 3 rigs on their own generators, dead until phase 2. Throw the switch (a crank QTE, or instant if both cages were freed): the beam burns 8 s on a ground spot and stuns the Harvester standing in it. 10 s cooldown | `floodlight.gd` |

**The Harvester — 900 HP, 3 phases** (a phase line can't be skipped by one big hit)

| Phase | HP | Rule |
|---|---|---|
| 1 Guard | 100–66 % | The skull sword covers its front (±75°): front hits ×0.1. Circle it, hit its back. Stunned ×1.5 |
| 2 Warded | 66–33 % | **03:00 blackout** cinematic: every town light dies, the floodlights come alive. No damage unless it's light-stunned. It calls 4 Marked Ones (2 if Marcus holds the road). Allies help once each: Owen sets fire at its feet (stun), Nora blinds the Marked Ones (sight 7 m), Julian gasses them (8 s stun), Marcus keeps half of them out. Unresolved members join its side |
| 3 Sweep | 33–0 % | Every ~8 s a telegraphed 360° sweep (red ring 5.5 m, 1.3 s): 45 damage unless rolled through or out of reach. Then it's *spent*: kneels 2.5 s with the red cracks open (×2 from any side) |

**Deviations from the table above**

- M2 is fought in the nave, not a vertical tower (no tower interior yet; `bell.gd` works in a future tower as is).
- The Harvester can't fit the chapel door, so in C3.2 it comes home down the quarry road carrying a Taken, instead of walking out of the chapel. The Shepherd sits in the dark beside the altar the whole time and is only revealed in C3.3.
- *Cages*: freeing both cages **primes** the floodlights (no crank) instead of switching them on.
- Clock: C3.1 continues C2.2 at 19:02 → church 19:40 → lighthouse 22:50 → 01:30 → quarry 02:30 → C3.2 02:50 → the 03:00 blackout lands in the middle of the final fight.
- *Run*: Alex walks into the Old Pass (no car is left in town).
- Evidence #2 and #11 (Chapter 1 small missions *Tripwire* and *Room 4*) aren't implemented yet, so 12/12 — and with it the broadcast and the **Signal** ending — can't be reached in a normal playthrough until they are.

**C3.4 "Pop. 1413" — the post-end cinematic** (all endings, ~90 s). On black after the end card, Lucía tells what the Veil was (in *Run* from inside her cage, a letter Alex will never read): the Shepherd is **Elias Morrow**, the old quarry chaplain. Thirty-one years ago the pit fell in on nine men, his son **Caleb** among them, and the town voted to seal it to keep the pass open. Caleb dug himself out on the ninth day, blind to light and without words. Elias told the valley the pit had kept his boy — that it keeps everyone if you feed it — and made his son its executioner: **the Harvester** (red lamp lenses, pitch from the pit, a sword of the nine he couldn't dig out and everyone since). Light hurt Caleb, so **every night at three the town turned its lights off for him**: that is the blackout. The ones who broke went out in the Tuesday trucks; the rest stayed in the pit. *Pop. 1413* is how many lived in Hollowmere the year the pit fell — the number Elena chose as her code. Then the ending's coda: *Signal* (forty cars on the Old Pass, eleven alive, Tomás asks for his sister; a moth on the lighthouse door), *Unveiled* (the four stay and scrape every eye; Elias sits with Caleb in the pit; the bell at dawn calls no one), *The New Eye* (Alex stayed; new eyes on motel doors), *Mixed* (the lights still go out at three — not all of them), *Run* (the lantern by her cage gutters out). Title card, then free roam at dawn.

---

## 6. Cinematics list

| ID | Chapter | Length | Camera / notes |
|---|---|---|---|
| C1.1 Last Postcard | 1 | 60 s | Car interior → long shot of the bridge → walk into town along the lit road |
| C1.2 3:00 minus four | 1 | 30 s | Inside Room 6, fixed camera, silhouette at the window |
| C1.3 Blackout | 1 | 60 s | Street lamps dying in sequence → across‑the‑lake shot of The Harvester → red eyes close‑up |
| C2.1 Moth | 2 | 60 s | Harbor at dawn, two‑shot on the dock, lighthouse behind |
| C2.2 The Traitor | 2 | 60 s | Locked hiding view from the mausoleum; group lit by lanterns; bell |
| C3.1 The Bell | 3 | 30 s | Continues C2.2 directly |
| C3.2 The Harvest | 3 | 60 s | Chapel interior, Lucía's cage, The Harvester's entrance |
| C3.3 The Shepherd + ending | 3 | 30 s + 30 s | Old man by the altar; ending variant |
| C3.4 Pop. 1413 | 3 | ~90 s | Post-end: Lucía's voice over the town sign, the pit, the fallen Harvester (its eyes go out), the square, the lighthouse; per-ending coda; title card |
| Memories (optional) | after each boss | ≤ 45 s | Playable flashback of the Night of Lanterns from the hunter's point of view; **skippable** to keep the 10‑min budget |

## 7. Chapter checklist (for implementation)

| | Ch.1 The Mark | Ch.2 Moth | Ch.3 The Veil |
|---|---|---|---|
| Opening cinematic | C1.1, C1.2 | C2.1 | C3.1 |
| Main missions | 4 | 3 | 4 + choice point |
| Small missions | 4 | 6 | 4 |
| Minigames introduced | Radio, lockpicking, shooting gallery | Fishing, Hi‑Lo, arcade | (broadcast) |
| Bosses | Owen | Nora, Julian | Marcus, The Harvester |
| Evidence | #1, #2, #11 | #3–6, #9, #10, #12 | #7, #8 |
| Key items | Key part 1, parents' lantern, flares | Key parts 2–3, Lily's drawing, Sam's file, gas mask | Clara's photo, chapel key |
| Closing | Blackout + Harvester sighting | Elena's execution | Ending |
| Clock at close | 03:00 | 19:00 | 03:00 |
