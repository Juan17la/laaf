# Progresión y Flujo — LAAF

Flujo por capítulos con disparadores, flags y condiciones de final. Ver [historia.md](historia.md) para la narrativa y [mapa.md](mapa.md) para las zonas.

## 1. Flags globales

| Flag | Tipo | Por defecto | Se asigna en |
|---|---|---|---|
| `chapter` | int | 0 | Cambios de capítulo |
| `mark` | float 0–100 | 0 | Medidor de Marca |
| `tokens` | int | 0 | Minijuegos, botín, tienda |
| `upgrades` | dict estadística→nivel | todo 0 | Tienda |
| `evidence` | conjunto de ids 1–12 | vacío | Recoger evidencias |
| `key_parts` | conjunto {1,2,3} | vacío | Owen / Nora / Julian (derrotar o robar) |
| `has_chapel_key` | bool | false | Marcus (derrotar o robar) |
| `traitor_alive` | bool | true | Ejecución del Capítulo 6 → false |
| `member_state[owen/nora/julian/marcus]` | enum `active / spared / killed / fled` | `active` | Resolución del jefe |
| `personal_item[member]` | bool | false | Dibujo de Lily, expediente de Sam, foto de Clara, farol de los padres |
| `broadcast_sent` | bool | false | Transmisor del faro |
| `minigame_daily[name]` | int | 0 | Se reinicia al dormir |
| `first_win[name]` | bool | false | Primera victoria en un minijuego |
| `times_taken` | int | 0 | Marca 100% en el apagón |
| `difficulty` | enum | normal | Ajustes |

Derivados: `members_spared`, `members_killed`, `members_fled` = conteos de `member_state`.

(Los nombres de flags se mantienen en inglés porque son identificadores de código.)

## 2. Capítulos

> **Reemplazado por [capitulos.md](capitulos.md)** (3 capítulos × 10 min). La tabla de abajo es el plan largo original (5–7 h), se deja como referencia; los flags y las reglas de finales del resto de este documento siguen vigentes.

| # | Nombre | Lugar | Objetivos principales | Desbloquea | Paso al siguiente |
|---|---|---|---|---|---|
| 0 | Llegada | Puente → plaza → motel | Caminar al pueblo, conocer a Grady, alquilar habitación | — | Dormir en el motel |
| 1 | La Marca | Motel y borde del bosque | Despertar marcado, leer la nota de Polilla, sobrevivir a la primera caza de Owen (tutorial: esconderse, sigilo, rodar) | Radio (canal 7) | Llegar a la tienda de Grady |
| 2 | La Plaza | Hub | Tutorial de tienda, primeros minijuegos (arcade, galería, cartas de apuesta baja), contacto por radio con Polilla | Tienda, minijuegos, diario | Aceptar la misión de Polilla |
| 3 | El Leñador | Bosque y Aserradero | Encontrar bengalas, conseguir la parte 1 de la llave, **jefe Owen** | Puerto, pesca, radio del faro | Jefe resuelto o huido + parte 1 |
| 4 | Polilla | Puerto y Faro | Conocer a Elena en persona, conocer el plan de evidencias, saber de Nora y Julian | Escuela + Clínica (cualquier orden) | Hablar con Elena |
| 5 | La Maestra / El Médico | Escuela, Clínica | Partes 2 y 3 de la llave, objetos personales, **jefe Nora**, **jefe Julian** | Mesa de cartas de apuestas altas, escopeta más adelante | Ambas zonas resueltas |
| 6 | La Traidora | Iglesia y Cementerio | Ir a la cita, **ejecución de Elena (guionizada)**, escapar del grupo, **jefe Marcus** | Los cazadores vagan por todo el mapa; se quema un cuarto seguro por zona | Marcus resuelto o huido + llave de la capilla |
| 7 | Estática | Faro | Escena de duelo, recoger evidencias restantes, transmisión opcional (necesita 12/12, código 1413) | Camino de la cantera | Salir del faro |
| 8 | La Cantera | Cantera y Capilla | Entrar a la capilla, encontrar a Lucía, enfrentar al Pastor, abrir la reja del túnel | Finales | Final |

Las zonas del Capítulo 5 y su orden son libres; lo demás es lineal con un hub abierto.

**Opción Huida:** desde que `key_parts` tiene las 3 partes, la reja del túnel se puede abrir directamente desde el camino de la cantera (opción: *"¿Irte ahora?"*). Elegirla termina el juego con el final **Huida**.

## 3. Ejecución de Elena (Capítulo 6) — reglas

- Siempre ocurre; no se puede evitar.
- Presentes: **Marcus** + cada miembro con estado `active` o `fled`. Los perdonados no están (luego le dicen a Alex que se negaron a ir). Marcus comenta la ausencia de los muertos.
- El jugador mira desde un escondite (cámara forzada a un ángulo cinematográfico). Salir del escondite hace que el grupo vea a Alex → persecución por el cementerio (sin fallo más allá del daño).
- Después: `traitor_alive = false`, crecimiento de la Marca ×1,5, los cazadores pasan a ser errantes, se quema un cuarto seguro por zona, El Pastor empieza a burlarse por radio.

## 4. Finales — condiciones

Se evalúan en orden al terminar el Capítulo 8 (o al elegir irse antes).

| Prioridad | Final | Condición |
|---|---|---|
| 1 | **Huida** | Túnel abierto antes de entrar a la capilla |
| 2 | **Señal** (oculto) | `broadcast_sent` y `members_killed == 0` |
| 3 | **Sin Velo** | `members_spared == 4` |
| 4 | **El Nuevo Ojo** | `members_killed == 4` |
| 5 | **Mixto** | Cualquier otro caso |

Variaciones del final según `member_state`:
- `spared` + objeto personal → aparece como **aliado** en la cantera (ayuda contra los Marcados).
- `spared` sin objeto personal → no aparece.
- `fled` → aparece como **enemigo** en la cantera (última oportunidad de perdonar/matar).
- `killed` → su máscara cuelga en la capilla.

## 5. Curva de dificultad

| Capítulo | Presión de cazadores | Marcados | Crecimiento de Marca | Cuartos seguros | Mecánica nueva |
|---|---|---|---|---|---|
| 1 | Guionizada | 0 | Bajo | Motel | Esconderse, sigilo, rodar |
| 2 | Ninguna | 0 | Ninguno | Hub | Tienda, minijuegos |
| 3 | 1 cazador (Owen) | Pocos | Bajo | 2 | Trampas, aturdir con fuego, decisión de jefe |
| 4 | Ninguna | Pocos | Bajo | Faro | Historia, pesca, radio |
| 5 | 1 cazador por zona | Medio | Medio | 2 por zona | Cierres remotos, gas, cámaras |
| 6 | Grupo + Marcus | Muchos | Alto (×1,5) | 1 por zona | Errantes, campanas |
| 7 | 1 errante | Medio | Alto | Faro | Transmisión |
| 8 | Miembros huidos + Marcados | Muchos | Alto | Ninguno | Decisión final |

## 6. Reglas de ritmo

- Tras cada jefe: un **recuerdo** (tranquilo, 2–4 min), luego vuelta al hub (tienda + minijuegos).
- Nunca dos cacerías seguidas sin un momento seguro entre ellas.
- Cada capítulo introduce **como máximo una** mecánica nueva.
- Los minijuegos se desbloquean poco a poco (arcade/galería/cartas en el Cap. 2, pesca/radio en el Cap. 3, cartas de apuestas altas en el Cap. 5) para que el jugador siempre tenga algo nuevo en qué pasar el tiempo.
