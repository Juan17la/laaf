# LAAF — Requirements / Requisitos

Design documentation for **LAAF**, a 3D third‑person action / survival horror game built in Godot 4.7.
Documentación de diseño de **LAAF**, un juego 3D de acción / survival horror en tercera persona hecho en Godot 4.7.

## Documents / Documentos

| Topic | English | Español |
|---|---|---|
| Story & endings | [en/story.md](en/story.md) | [es/historia.md](es/historia.md) |
| Characters | [en/characters.md](en/characters.md) | [es/personajes.md](es/personajes.md) |
| Map & zones | [en/map.md](en/map.md) | [es/mapa.md](es/mapa.md) |
| Gameplay & systems | [en/gameplay.md](en/gameplay.md) | [es/jugabilidad.md](es/jugabilidad.md) |
| Minigames & economy | [en/minigames.md](en/minigames.md) | [es/minijuegos.md](es/minijuegos.md) |
| Progression & flags | [en/progression.md](en/progression.md) | [es/progresion.md](es/progresion.md) |
| Chapters (3 × 10 min) | [en/chapters.md](en/chapters.md) | [es/capitulos.md](es/capitulos.md) |
| Chapter 3 objects to model later | [en/ch3_objects_to_generate.md](en/ch3_objects_to_generate.md) | — |

## Summary / Resumen

**EN:** An outsider looking for their missing sister is marked in the isolated town of Hollowmere. Five childhood friends who lost their loved ones to The Veil now serve it, each guarding one zone and marking newcomers. One of them, Elena ("Moth"), secretly helps the player until the group executes her. The player must escape, fight (spare) or kill each hunter. Optional minigames earn Lantern Tokens to buy upgrades.

**ES:** Un forastero que busca a su hermana desaparecida es marcado en el pueblo aislado de Hollowmere. Cinco amigos de la infancia que perdieron a sus seres queridos a manos de El Velo ahora lo sirven; cada uno vigila una zona y marca a los recién llegados. Una de ellos, Elena ("Polilla"), ayuda en secreto al jugador hasta que el grupo la ejecuta. El jugador debe escapar, pelear (perdonar) o matar a cada cazador. Minijuegos opcionales dan Fichas de Farol para comprar mejoras.

## Functional requirements / Requisitos funcionales

| ID | Requirement (EN) | Requisito (ES) |
|---|---|---|
| RF‑01 | Third‑person character controller: walk, sprint, crouch, dodge, climb low walls | Control en tercera persona: caminar, correr, agacharse, esquivar, trepar muros bajos |
| RF‑02 | Stealth system: noise radius, visibility by light/movement, hiding spots, distractions | Sigilo: radio de ruido, visibilidad por luz/movimiento, escondites, distracciones |
| RF‑03 | Hunter AI state machine: patrol, suspicious, hunt, chase, search, stunned | IA de cazadores: patrulla, sospecha, caza, persecución, búsqueda, aturdido |
| RF‑04 | Each zone has exactly one owner hunter with a unique weakness | Cada zona tiene exactamente un cazador dueño con una debilidad única |
| RF‑05 | Melee, firearms, throwables; regular enemies (Marked Ones) | Cuerpo a cuerpo, armas de fuego, arrojables; enemigos comunes (Marcados) |
| RF‑06 | Boss fights with Spare / Kill resolution and a Flee exit | Jefes con resolución Perdonar / Matar y salida para Huir |
| RF‑07 | Mark meter (0–100%) with effects and the "Taken" sequence | Medidor de Marca (0–100%) con efectos y secuencia "Llevado" |
| RF‑08 | Day/night cycle with nightly blackout at 03:00 | Ciclo día/noche con apagón nocturno a las 03:00 |
| RF‑09 | Traitor storyline: radio calls, notes, meetings, scripted execution in Chapter 6 | Historia de la traidora: radio, notas, encuentros, ejecución guionizada en el Capítulo 6 |
| RF‑10 | Six minigames: lockpicking, fishing, arcade, card game, shooting gallery, radio tuning | Seis minijuegos: ganzúa, pesca, arcade, cartas, galería de tiro, sintonizar radio |
| RF‑11 | Currency (Lantern Tokens) with daily minigame limits | Moneda (Fichas de Farol) con límites diarios en minijuegos |
| RF‑12 | Shop with permanent upgrades, weapons, mods and supplies | Tienda con mejoras permanentes, armas, modificaciones y suministros |
| RF‑13 | 12 evidence collectibles and journal | 12 evidencias coleccionables y diario |
| RF‑14 | Five endings evaluated from flags (Run, Signal, Unveiled, The New Eye, Mixed) | Cinco finales evaluados por flags (Huida, Señal, Sin Velo, El Nuevo Ojo, Mixto) |
| RF‑15 | Save system: 3 slots, manual in safe rooms, autosave on zone entry and after bosses | Guardado: 3 ranuras, manual en cuartos seguros, autoguardado al entrar a zona y tras jefes |
| RF‑16 | HUD: health, stamina, Mark, clock, tokens, objective hint | HUD: vida, estamina, Marca, reloj, fichas, pista de objetivo |
| RF‑17 | Menus: main, settings, pause, journal, map, inventory, shop, minigame overlays, ending stats | Menús: principal, ajustes, pausa, diario, mapa, inventario, tienda, minijuegos, estadísticas del final |
| RF‑18 | Three difficulty levels: Story, Normal, Hard | Tres dificultades: Historia, Normal, Difícil |

## Non‑functional requirements / Requisitos no funcionales

| ID | Requirement (EN) | Requisito (ES) |
|---|---|---|
| RNF‑01 | Engine: Godot 4.7, Forward+ renderer, Jolt physics | Motor: Godot 4.7, renderizador Forward+, física Jolt |
| RNF‑02 | 60 FPS at 1080p on mid‑range hardware; 30 FPS minimum on low | 60 FPS a 1080p en hardware medio; mínimo 30 FPS en bajo |
| RNF‑03 | Keyboard/mouse and gamepad, full rebinding | Teclado/ratón y mando, reasignación completa |
| RNF‑04 | Localization English and Spanish (text + subtitles) | Localización inglés y español (texto + subtítulos) |
| RNF‑05 | Accessibility: subtitles, colorblind‑safe HUD, toggle vs hold, camera shake off, hint toggle | Accesibilidad: subtítulos, HUD apto para daltonismo, alternar vs mantener, sin sacudida de cámara, pistas opcionales |
| RNF‑06 | Zone loading under 10 s on SSD; hub ↔ zone transitions seamless or with short load | Carga de zona < 10 s en SSD; transiciones hub ↔ zona fluidas o con carga corta |
| RNF‑07 | Save files human‑readable (Godot `ConfigFile`/JSON) and versioned | Archivos de guardado legibles (`ConfigFile`/JSON de Godot) y versionados |
| RNF‑08 | Content rating target: mature (violence, horror), no gore close‑ups on execution scenes | Clasificación: adulto (violencia, terror), sin primeros planos gore en ejecuciones |
