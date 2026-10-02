# Capítulos — LAAF (3 × 10 min)

Toda la historia de [historia.md](historia.md) contada en **tres capítulos de ~10 minutos** (≈30 min por partida en la ruta crítica). Todos los capítulos tienen la misma forma:

```
 Cinemática de apertura ─► Misión principal (2–4 pasos) ─► Misiones pequeñas + minijuegos (opcionales)
        ─► Encuentro con cazador / jefe ─► Cinemática de cierre + cartel del capítulo
```

Esta estructura **reemplaza** la tabla de 8 capítulos de [progresion.md](progresion.md) §2. Flags, finales, el medidor de Marca, las reglas de perdonar/matar/huir y la economía siguen como están documentados ahí y en [jugabilidad.md](jugabilidad.md) / [minijuegos.md](minijuegos.md); solo cambian el ritmo y lo que pasa en cada capítulo.

## 0. Reglas de tiempo

- **10 min = ruta crítica**, con cinemáticas incluidas, para un jugador que sabe a dónde ir pero no hace speedrun. Las misiones pequeñas y los minijuegos opcionales suman ~3–6 min por capítulo.
- Reloj del juego: 1 hora = 2,5 minutos reales, así que **un capítulo = 4 horas de juego**. Cada capítulo termina en un momento fijo del reloj (el apagón de las 03:00 o la reunión de las 19:00): lo cierra la historia, no el jugador.
- Cinemáticas: **≤ 1 min cada una, saltables** después de verlas una vez; máx. ~2,5 min de cinemáticas por capítulo.
- Como mucho una mecánica nueva por capítulo (ver [progresion.md](progresion.md) §6).
- Autoguardado al inicio de cada paso de misión y antes de cada jefe.
- **Presupuesto por capítulo:** cinemáticas 15% · exploración/sigilo 45% · jefe 25% · hub/minijuegos 15%.

## 1. El jefe — El Segador

El modelo de jefe (`models/char_boss.glb`) es **El Segador**: el verdugo del Velo, lo que recoge a los Llevados en el apagón de las 03:00.

| Campo | Valor |
|---|---|
| Aspecto | ~2,8 m de alto, muy musculoso, cuerpo totalmente negro como alquitrán mojado, dos ojos rojos encendidos, sin boca. Lleva una **espada de calaveras fundidas** de dos metros: las calaveras de los Llevados |
| Qué es | Nunca se explica del todo. El Pastor lo llama "la Cosecha". Los del pueblo creen que es la primera persona que El Velo rompió. Los cinco amigos solo lo han visto de lejos, en la Noche de los Faroles |
| Papel | Capítulo 1: solo se ve (no se puede pelear). Capítulo 2: aparece en el horizonte a las 03:00 en la secuencia "Llevado". Capítulo 3: **jefe final** en la cantera |
| Debilidad | **La luz.** Bengalas, el haz del faro y los reflectores de la capilla lo hacen retroceder (aturdido 3 s). La espada de calaveras solo bloquea de frente |
| Regla de tono | Nunca habla. Sus pasos son lo único que suena fuerte durante un apagón. No es un monstruo para farmear: es la forma física de "ser llevado" |

Colocado en la puerta de la Capilla del Velo en `maps/hollowmere.tscn` (build_world, sección de la cantera).

## 2. Resumen

| # | Capítulo | Reloj | Zonas | Misión principal | Jefe / caza | Cierra con |
|---|---|---|---|---|---|---|
| 1 | **La Marca** | 19:00 → 03:00 (salto a 23:00) | Puente, motel, borde del bosque, plaza, aserradero | Sobrevivir la primera noche, conseguir la parte 1 de la llave | Owen (caza, luego jefe) | Apagón: primera vista del Segador |
| 2 | **Polilla** | 09:00 → 19:00 (salto a 15:00) | Puerto, faro, escuela, clínica | Conocer a Elena, conseguir las partes 2 y 3 | Nora + Julian (jefes cortos) | Ejecución de Elena en la iglesia |
| 3 | **El Velo** | 23:00 → 03:00 | Cementerio, iglesia, faro, cantera, capilla | Escapar del grupo, tomar la llave de la capilla, llegar a Lucía | Marcus + **El Segador** | Final (5 variantes) |

Reparto de evidencias (12 en total, [mapa.md](mapa.md)): Capítulo 1 → #11, #1, #2 · Capítulo 2 → #3, #4, #5, #6, #9, #10, #12 · Capítulo 3 → #7, #8.

---

## 3. Capítulo 1 — La Marca (10:00)

**Objetivo del capítulo:** enseñar movimiento, escondites y la Marca; que el jugador se sienta cazado; terminar con un gancho.
**Mecánica nueva:** sigilo (esconderse, agacharse, ruido) + la elección del jefe.

### Flujo

| Tiempo | Momento | Tipo | Contenido |
|---|---|---|---|
| 0:00–1:00 | **C1.1 "Última postal"** | Cinemática | El auto de Alex muere en el puente derrumbado al anochecer; la postal de Lucía en el tablero ("Hollowmere es hermoso. No vengas."). Alex pasa junto al cartel `HOLLOWMERE POP. 1413`. Grady, desde la ventana de la tienda, no quiere hablar; le da una llave del motel "por una noche". Fundido en la Habitación 6. |
| 1:00–1:30 | **C1.2 "Cuatro horas antes de las 3"** | Cinemática (corta) | 23:00. Una silueta tras el vidrio de la ventana (Owen). Un siseo, olor a quemado. Alex despierta agarrándose la mano. |
| 1:30–3:00 | **M1 "Habitación 6"** | Misión principal | 1. Mirar la mano: el Ojo del Velo está quemado en ella (aparece el medidor de Marca al 10%). 2. La puerta tiene el mismo ojo pintado. 3. Recoger la nota de Polilla bajo la puerta: *"Que no te vean después del anochecer. Radio, canal 7."* 4. **Sintonizar radio** (tutorial, obligatorio, 30 s): la voz de Polilla: *"Te marcaron. Ve a la plaza. Quédate en el pasto."* |
| 3:00–5:00 | **M2 "Primera caza"** | Caza (guionizada) | Owen recorre el pasillo del motel con un arco. Tutorial: agacharse, esconderse en el pasto alto, lanzar una botella para distraer, esquivar. Ruta: motel → borde del bosque → Lake Rd → plaza. Si te atrapa = daño + Marca +15%, nunca muerte. El director de tensión siempre deja pasar al jugador. |
| 5:00–6:30 | **M3 "La plaza"** | Hub | Grady abre la tienda solo porque Alex está marcado ("La gente marcada paga en fichas. Los demás ya están pagados."). Tutorial de tienda: comprar o recibir **2 bengalas** (necesarias para el jefe). Radio: Polilla manda a Alex al aserradero: *"Owen lleva una pieza de la llave de la reja. Le tiene miedo al fuego."* |
| 6:30–9:00 | **M4 "El Leñador"** | Misión principal + jefe | 1. Seguir el sendero del bosque esquivando cepos (las huellas en el barro muestran que Owen sigue las tuyas). 2. Encontrar la **parte 1 de la llave** en la oficina del capataz y la **evidencia #1**. 3. **Jefe Owen** (piso quemado del aserradero, 2 fases): fase 1 arco + trampas; fase 2 motosierra. Una bengala o un barril en llamas lo paraliza 6 s: golpéalo mientras está congelado. La salida de escape se abre tras la fase 1 (huir). 4. Aviso **Perdonar / Matar**. Perdonar con el farol de sus padres = "Dime que no fue en vano." |
| 9:00–10:00 | **C1.3 "Apagón"** | Cinemática de cierre | 03:00. Todas las luces de Hollowmere se apagan, calle por calle (los faroles nuevos mueren en secuencia). Desde el patio del aserradero Alex ve, al otro lado del lago, al **Segador** caminando por el camino de la cantera, arrastrando su espada de calaveras, con un Marcado del pueblo al hombro. Se detiene y gira sus ojos rojos hacia Alex. Corte a negro. Radio: *"Puerto. Mañana. Ven solo. — Polilla."* Cartel: **I · LA MARCA**. |

### Misiones pequeñas (opcionales, +3–5 min)

| Misión | Dónde | Tarea | Recompensa |
|---|---|---|---|
| **Habitación 4** | Motel | Ganzúa (1 pin) en la habitación de al lado: la antigua habitación de Lucía | **Evidencia #11** (cámara de Lucía, última foto: la capilla de la cantera) |
| **El farol de los padres** | Altillo de la oficina del aserradero | Trepar la pila de troncos, encontrar el farol del festival quemado | Objeto personal de Owen (escena completa de "perdonar") |
| **Buzón 12** | Maple Ave | Leer la carta de un vecino y llevársela a Grady | 15 fichas + la primera frase sincera de Grady |
| **Cable trampa** | Sendero del bosque | Desactivar 3 campanas trampa sin hacerlas sonar | 10 fichas, **evidencia #2** bajo la última campana |

### Minijuegos disponibles

| Minijuego | Dónde | Nota |
|---|---|---|
| Sintonizar radio | Habitación 6 | Tutorial, obligatorio una vez |
| Ganzúa | Habitación 4, taquillas del aserradero | Tutorial con 1 pin |
| Galería de tiro | Recinto del festival (plaza) | Opcional, 60 s; ruidosa (20 m), atrae Marcados de noche |

### Cierre / estado de salida

- Flags: `chapter = 1`, `key_parts = {1}`, `member_state[owen]` definido (o `fled`), `mark ≈ 30–45`.
- Fichas esperadas: ~60–90.
- Si el jugador huyó de Owen, vuelve a aparecer en el Capítulo 3 como errante.

---

## 4. Capítulo 2 — Polilla (10:00)

**Objetivo del capítulo:** darle al jugador una aliada y el plan, dos zonas de cazadores rápidas, y luego quitarle la aliada.
**Mecánica nueva:** debilidades de zona (sala de energía / ventilación) + orden libre entre dos zonas.

### Flujo

| Tiempo | Momento | Tipo | Contenido |
|---|---|---|---|
| 0:00–1:00 | **C2.1 "Polilla"** | Cinemática de apertura | 09:00, niebla en el puerto. Una mujer con impermeable amarillo en el muelle, la mano vendada: **Elena**. Muestra su propia marca: *"Soy una de ellos. También soy la única que quiere que desaparezcan."* Explica la llave de tres partes de la reja (Owen, Nora, Julian), la llave de la capilla (Marcus), y que **Lucía fue llevada viva a la cantera**. |
| 1:00–2:00 | **M1 "Canal siete"** | Misión principal (corta) | Llevar la batería de auto del cobertizo de botes a la sala de radio del faro. **Sintonizar radio** limpia la grabación oculta de Elena: **evidencia #9**. Elena marca la escuela y la clínica en el mapa de Alex. El reloj salta a las 15:00. |
| 2:00–5:30 | **M2 "La Maestra"** | Zona + jefe | Escuela. La voz de Nora por los altavoces (*"Lily, cariño, tenemos visita."*), cajas de música como trampas de ruido, maniquíes vestidos de niños. 1. Llegar a la **sala de energía** del sótano y cortar la luz: mueren los altavoces y las cerraduras remotas. 2. Encontrar la **parte 2 de la llave** y el **dibujo de Lily** (aula 3). 3. **Jefa Nora** en el auditorio, a oscuras: llama a Lily y revela su posición; golpéala desde las sombras (2 fases). 4. Perdonar / Matar. |
| 5:30–9:00 | **M3 "El Médico"** | Zona + jefe | Clínica. Julian llena los pasillos de gas y siempre revisa los escondites que te vio usar. 1. Conseguir la **máscara de gas** en la bahía de ambulancias. 2. Sala de climatización del techo: **invertir la ventilación**. 3. **Parte 3 de la llave** y el **expediente de Sam** (archivo). 4. **Jefe Julian** en la sala de cirugía de vidrio: el gas invertido dispara su asma (aturdido). 5. Perdonar / Matar. |
| 9:00–10:00 | **C2.2 "La Traidora"** | Cinemática de cierre | 19:00, la iglesia. Elena espera entre las tumbas con el mapa robado de la cantera. Alex llega tarde y tiene que esconderse (cámara fija desde el mausoleo). **Marcus** toca la campana; el grupo sale de la niebla (Marcus + cada miembro todavía `active` o `fled`). Los perdonados no están. Marcus: *"Tres años, Elena."* Elena mira hacia el escondite de Alex, no a ellos: *"Canal siete… uno‑cuatro‑uno‑tres. Diles que se llamaba Tomás."* La campana suena una vez más. Corte a negro sobre el sonido. Cartel: **II · POLILLA**. |

La escuela y la clínica se juegan en **cualquier orden** (M2 y M3 se intercambian). Cada una dura ~3,5 min en la ruta crítica.

### Misiones pequeñas (opcionales, +4–6 min)

| Misión | Dónde | Tarea | Recompensa |
|---|---|---|---|
| **Viejo Tom** | Muelle de pesca del puerto | **Pesca**: atrapar el bagre legendario | 150 fichas + una nota sobre Tomás; caja hundida con la **evidencia #10** |
| **La mesa de Silas** | Bar Farol Ahogado | **Mayor o Menor del Farol** contra Silas (apuestas bajas). Ganar 3 manos en la mesa alta | **Evidencia #12** (la carta del Pastor); el rumor de Silas revela la ruta de patrulla de Julian |
| **Recreo** | Patio de la escuela | Silenciar las 3 cajas de música antes de entrar | Se evita la emboscada de los altavoces en M2 |
| **Triaje** | Sala de la clínica | Liberar a un paciente Marcado atado a una cama | Botiquín + el paciente da la pista de la **evidencia #6** en la cámara frigorífica de la morgue |
| **Escondido en clase** | Aulas de la escuela | Registrar pupitres | **Evidencias #3, #4** |
| **Farmacia** | Clínica | Ganzúa (3 pines) en el armario de farmacia | Té de Elena ×2, **evidencia #5** |

### Minijuegos disponibles

Pesca (puerto, de día) · Sintonizar radio (faro) · Mayor o Menor del Farol (bar) · Ganzúa · Arcade "Moth Run" (cafetería; el mensaje de Elena a los 10.000 puntos se lee como una despedida después de C2.2).

### Cierre / estado de salida

- Flags: `chapter = 2`, `key_parts = {1,2,3}` (si se robaron o resolvieron), `member_state[nora/julian]` definidos, `traitor_alive = false`.
- Desbloquea el aviso de **Huir** en la reja del túnel (las 3 partes de la llave).
- Después de C2.2: crecimiento de Marca ×1,5, todos los cazadores vivos pasan a ser errantes, El Pastor empieza a burlarse por radio.
- Fichas esperadas: ~350–500 en total.

---

## 5. Capítulo 3 — El Velo (10:00)

**Objetivo del capítulo:** duelo, rabia y la elección final. El jugador puede **huir**, **pelear** o **matar** para salir.
**Mecánica nueva:** cazadores errantes + la luz como arma contra El Segador.

### Flujo

| Tiempo | Momento | Tipo | Contenido |
|---|---|---|---|
| 0:00–0:30 | **C3.1 "La campana"** | Cinemática de apertura | El grupo se gira hacia el mausoleo. Alguien vio a Alex. Marcus: *"El forastero. Tráiganlo."* |
| 0:30–2:00 | **M1 "Corre"** | Persecución | Escapar por el cementerio de noche. Las campanas suenan cuando ven a Alex; los Marcados cierran las rejas. Esconderse en mausoleos o cortar la línea de visión con una lata de humo. Termina en la nave de la iglesia. Sin fallo más allá del daño. |
| 2:00–4:30 | **M2 "El campanario"** | Jefe | **Jefe Marcus**, arena vertical con 3 plataformas de campanas. Golpea con una maza y toca las campanas para llamar a los Marcados. Dejarle caer una campana encima (3 plataformas = 3 fases). La **foto de Clara** está en la sala del coro en la subida. Perdonar / Matar. Recompensa: **la llave de la capilla**, **evidencias #7, #8**. |
| 4:30–6:00 | **M3 "Estática"** | Misión principal (tranquila) | El faro, vacío. **Escena de duelo** (cinemática, 40 s): la radio de Elena sigue encendida, su chaqueta en la silla. Llega Grady con el impermeable amarillo: *"Ella querría que alguien lo usara."* **Transmisión** opcional: **sintonizar radio** con el código **1413** (requiere 12/12 evidencias y nadie muerto → activa `broadcast_sent`). |
| 6:00–6:30 | **Punto de decisión "La reja"** | Decisión | En el camino de la cantera, la reja del Túnel del Paso Viejo con 3 ranuras de llave. Aviso: *"¿Irse ahora?"* → final **Huir** (salta a 9:00). Si no, seguir a la capilla. |
| 6:30–7:30 | **C3.2 "La Cosecha"** | Cinemática | La Capilla del Velo. Velas, faroles del festival, jaulas. **Lucía** en una jaula, viva, marcada. La voz del Pastor en una radio: *"Viniste por ella. Todos vienen por alguien."* El suelo tiembla: **El Segador** sale de la capilla arrastrando su espada de calaveras. Los miembros perdonados que recibieron su objeto personal llegan detrás de Alex. |
| 7:30–9:30 | **M4 "El Segador"** | Jefe final (3 fases) | **Fase 1:** bloquea de frente con la espada de calaveras; rodéalo y golpea su espalda. **Fase 2:** llama a los Marcados; encender los 3 **reflectores** de la capilla (cada uno lo aturde 3 s). **Fase 3:** la espada barre toda la arena; esquiva, enciende una **bengala** en su cara y golpea las grietas rojas. Los aliados (perdonados) ayudan una vez cada uno: Owen lanza fuego, Nora corta la luz de los faroles de los Marcados, Julian los gasea, Marcus sostiene una reja. Los miembros `fled` pelean de su lado. |
| 9:30–10:00 | **C3.3 "El Pastor"** | Cinemática de cierre | Detrás del altar: un anciano cansado con una radio, el hierro de marcar sobre la mesa. *"Yo nunca me llevé a nadie. Me los traían."* Se reproduce el final (ver abajo) y la pantalla final muestra las estadísticas. Cartel: **III · EL VELO**. |

### Misiones pequeñas (opcionales, +3–4 min)

| Misión | Dónde | Tarea | Recompensa |
|---|---|---|---|
| **Sillas vacías** | Nave de la iglesia | Encender una vela en el banco de la familia de cada uno de los amigos (5) | Té de Elena ×2, Marca −20% |
| **Última grabación** | Sala de radio del faro | Reproducir la grabadora de Elena | Su último mensaje; +1 bengala |
| **Pregúntale a Grady** | Tienda | Hablar con Grady después de la ejecución | Regala 2 bengalas + 1 lata de humo ("No pagues. Solo termina con esto.") |
| **Jaulas** | Cantera | Ganzúa en 2 jaulas de Marcados del pueblo antes de la capilla | Encienden los faroles de la cantera: los reflectores de la fase 2 empiezan encendidos |

### Minijuegos disponibles

Sintonizar radio (transmisión) · Ganzúa (jaulas de la cantera) · Tienda de Grady. Los minijuegos de día (pesca, arcade, cartas) están cerrados: el pueblo está en guerra.

### Finales (variantes de C3.3, ≤ 30 s cada uno)

Condiciones y prioridad como en [progresion.md](progresion.md) §4.

| Final | Plano final |
|---|---|
| **Huir** | Alex maneja solo por el túnel. La marca pica. Estática en la radio: "Canal 7…". Lucía no aparece. |
| **Señal** (oculto) | Luces de helicóptero sobre el lago. Tomás entre los Llevados liberados. El nombre de Elena es lo último en pantalla. |
| **Sin Velo** | Los amigos perdonados sacan de la capilla la espada rota del Segador. Al amanecer raspan los ojos pintados de las puertas. Alex y Lucía salen por el túnel. |
| **El Nuevo Ojo** | El Pastor le ofrece a Alex el hierro de marcar: "Hiciste su trabajo mejor que ellos." Plano final: Alex pintando un ojo en la puerta de un desconocido. |
| **Mixto** | Alex carga a una Lucía herida por el túnel. Tarjetas de epílogo: perdonados = redimidos, muertos = enterrados, huidos = siguen vigilando el pueblo. |

---

## 6. Lista de cinemáticas

| ID | Capítulo | Duración | Cámara / notas |
|---|---|---|---|
| C1.1 Última postal | 1 | 60 s | Interior del auto → plano largo del puente → caminata al pueblo por la calle iluminada |
| C1.2 Cuatro horas antes de las 3 | 1 | 30 s | Dentro de la Habitación 6, cámara fija, silueta en la ventana |
| C1.3 Apagón | 1 | 60 s | Faroles muriendo en secuencia → plano al otro lado del lago del Segador → primer plano de los ojos rojos |
| C2.1 Polilla | 2 | 60 s | Puerto al amanecer, plano a dos en el muelle, el faro detrás |
| C2.2 La Traidora | 2 | 60 s | Vista fija desde el escondite en el mausoleo; grupo iluminado por faroles; campana |
| C3.1 La campana | 3 | 30 s | Continúa directamente C2.2 |
| C3.2 La Cosecha | 3 | 60 s | Interior de la capilla, jaula de Lucía, entrada del Segador |
| C3.3 El Pastor + final | 3 | 30 s + 30 s | Anciano junto al altar; variante del final |
| Recuerdos (opcionales) | tras cada jefe | ≤ 45 s | Flashback jugable de la Noche de los Faroles desde el punto de vista del cazador; **saltable** para respetar los 10 min |

## 7. Checklist de capítulos (para implementación)

| | Cap.1 La Marca | Cap.2 Polilla | Cap.3 El Velo |
|---|---|---|---|
| Cinemática de apertura | C1.1, C1.2 | C2.1 | C3.1 |
| Misiones principales | 4 | 3 | 4 + punto de decisión |
| Misiones pequeñas | 4 | 6 | 4 |
| Minijuegos que se presentan | Radio, ganzúa, galería de tiro | Pesca, Mayor o Menor, arcade | (transmisión) |
| Jefes | Owen | Nora, Julian | Marcus, El Segador |
| Evidencias | #1, #2, #11 | #3–6, #9, #10, #12 | #7, #8 |
| Objetos clave | Parte 1 de la llave, farol de los padres, bengalas | Partes 2–3, dibujo de Lily, expediente de Sam, máscara de gas | Foto de Clara, llave de la capilla |
| Cierre | Apagón + aparición del Segador | Ejecución de Elena | Final |
| Reloj al cerrar | 03:00 | 19:00 | 03:00 |
