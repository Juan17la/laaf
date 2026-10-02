extends SceneTree
## Headless check of Chapter 3: ending priority table, dormant by default, dev skips (run / gate / harvester),
## the gate choice (cage locks + Marked Ones end with it), and the new mechanics — smoke breaks sight, a
## dropped bell crushes / deafens, the Harvester's front guard, phase lines, light stun + immunity, the
## floodlight beam, Elena's tea.
## flatpak run org.godotengine.Godot --headless --path . -s tests/chapter3_test.gd


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("CH3 FAIL: " + msg)
	quit(1)


func _frames(n: int) -> void:
	for i in n:
		await physics_frame


func _world(step: String) -> Node:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = step
	root.add_child(world)
	return world


func _run() -> void:
	# ending priority (progression.md §4)
	var e := func(o: String, n: String, j: String, m: String, extra := {}) -> String:
		return Chapter3Director.pick_ending({"owen": o, "nora": n, "julian": j, "marcus": m}.merged(extra))
	var cases := [
		[e.call("killed", "killed", "killed", "killed", {"ending": "run"}), "run"],
		[e.call("spared", "spared", "spared", "spared", {"broadcast_sent": true}), "signal"],
		[e.call("spared", "spared", "spared", "killed", {"broadcast_sent": true}), "mixed"],
		[e.call("spared", "spared", "spared", "spared"), "unveiled"],
		[e.call("killed", "killed", "killed", "killed"), "new_eye"],
		[e.call("killed", "killed", "killed", "killed", {"broadcast_sent": true}), "new_eye"],
		[e.call("spared", "killed", "spared", "spared"), "mixed"],
		[e.call("fled", "spared", "spared", "spared"), "mixed"]]
	for c in cases:
		if c[0] != c[1]:
			return _fail("pick_ending: got %s, expected %s" % c)

	# free roam: Chapter 3 stays dormant
	var world := _world("free")
	await _frames(30)
	var ch3: Chapter3Director = world.get_node("Chapter3")
	var player: CharacterBody3D = world.get_node("Player")
	if ch3.step != "" or ch3.cam != null:
		return _fail("Chapter 3 woke up in a free-roam run")

	# smoke: blocks a sight line through it, not one beside it
	var smoke := SmokeCloud.make(world, Vector3(0, 0, 0))
	await create_timer(0.8).timeout
	if not smoke.blocks(Vector3(-8, 1.6, 0), Vector3(8, 1.0, 0)) or smoke.blocks(Vector3(-8, 1.6, 6), Vector3(8, 1.0, 6)):
		return _fail("smoke blocking wrong")
	smoke.queue_free()

	# tea: Mark -15, one tin used
	player.mark = 40.0
	player.teas = 1
	player.drink_tea()
	if absf(player.mark - 25.0) > 0.01 or player.teas != 0:
		return _fail("tea: mark %.1f teas %d" % [player.mark, player.teas])

	# bell: the one under it is crushed, the one 8 m away is deafened (stunned)
	var base := Vector3(-86, 0.1, 60)  # open lot by the motel
	player.global_position = base + Vector3(0, 0, 20)
	var under := Enemy.spawn(world, "res://models/char_marcus.glb", base, 0.0, {"boss": true, "max_health": 400.0})
	var near := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(8, 0, 0), 0.0)
	await _frames(5)
	var bell := Bell.make(world, base, base + Vector3(3, 1.3, 0))
	bell.hit(10.0, bell.global_position)  # a shot on the chain
	await create_timer(0.7).timeout
	if absf(under.health - 400.0 * (1.0 - Bell.CRUSH)) > 1.0 or under.state != Enemy.State.STUNNED:
		return _fail("bell crush: hp %.1f state %d" % [under.health, under.state])
	if near.state != Enemy.State.STUNNED or near.health < near.max_health:
		return _fail("bell deafen: state %d hp %.1f" % [near.state, near.health])
	under.queue_free()
	near.queue_free()

	# Harvester: front blocked, back full, phase lines never skipped, light stun + immunity
	var h := Harvester.spawn_at(world, base, 0.0)  # faces +Z
	await _frames(5)
	h.set_physics_process(true)
	var front := base + Vector3(0, 1.5, 2)
	var back := base + Vector3(0, 1.5, -2)
	h.hit(100.0, front)
	if absf(h.health - 890.0) > 0.5:
		return _fail("guard: front hit took %.1f" % (900.0 - h.health))
	h.state = Enemy.State.CHASE
	h.hit(1000.0, back)
	if h.phase != 2 or h.health < 900.0 * 0.66 - 1.0:
		return _fail("phase line skipped: phase %d hp %.1f" % [h.phase, h.health])
	var hp := h.health
	h.state = Enemy.State.CHASE
	h.hit(100.0, back)  # phase 2: warded
	if h.health != hp:
		return _fail("phase 2 took damage while not stunned")
	if not h.light_stun() or h.light_stun():
		return _fail("light stun / immunity wrong")
	h.hit(10.0, front)  # stunned: open from any side, x1.5
	if absf(hp - h.health - 15.0) > 0.5:
		return _fail("stunned hit took %.1f" % (hp - h.health))
	h.queue_free()

	# floodlight: armed + primed, thrown → an enemy standing in the lit spot is light-stunned
	var h2 := Harvester.spawn_at(world, base + Vector3(10, 0, 0), 0.0)
	var fl := Floodlight.make(world, base + Vector3(-4, 0, 0), base + Vector3(10, 0, 0), player.hud)
	fl.primed = true
	await _frames(3)
	if fl.switch.enabled:
		return _fail("floodlight switch live before arm()")
	fl.arm(true)
	fl.switch.interact(player)
	await create_timer(0.5).timeout
	if not fl.is_on() or h2.state != Enemy.State.STUNNED:
		return _fail("floodlight: on %s, harvester state %d" % [fl.is_on(), h2.state])
	h2.queue_free()
	world.queue_free()
	await _frames(5)

	# dev skip into the cemetery chase
	world = _world("run")
	await _frames(60)
	ch3 = world.get_node("Chapter3")
	player = world.get_node("Player")
	if ch3.step != "run":
		return _fail("dev skip did not reach 'run' (step '%s')" % ch3.step)
	var f: Dictionary = ch3.flags
	if f.key_parts != 3 or f.nora != "spared" or f.marcus != "active" or f.elena_alive or f.ending != "":
		return _fail("ch3 dev flags wrong: %s" % f)
	if player.weapons.gun() == "" or player.global_position.distance_to(Chapter3Director.HIDE) > 3.0:
		return _fail("run start: gun '%s' at %s" % [player.weapons.gun(), player.global_position])
	if ch3._marked.size() != 6 or not ch3._gate_bars:
		return _fail("chase setup: %d chasers, gate %s" % [ch3._marked.size(), ch3._gate_bars])
	# the bell rings after a corpse was freed (30 s after the kill): the rest still converge
	ch3._marked[0].free()
	ch3._alert(ch3._marked)
	if ch3._marked[5].state == Enemy.State.PATROL:
		return _fail("bell: _alert stopped at a freed chaser")
	world.queue_free()
	await _frames(5)

	# the gate: cage locks and the quarry's Marked Ones end with the choice; C3.2 plays with no enemy alive
	Engine.time_scale = 4.0
	world = _world("gate")
	await _frames(10)
	ch3 = world.get_node("Chapter3")
	player = world.get_node("Player")
	player.global_position = Chapter3Director.QUARRY_MOUTH + Vector3(0, 0.1, -3)
	for i in 3000:  # quarry_arrive plays out
		await physics_frame
		if ch3._marked.size() == 3 and player.controls_enabled:
			break
	var marks := func(prompt: String) -> Array:
		return get_nodes_in_group("interactable").filter(func(n: Node) -> bool:
			return n.prompt == prompt and not n.is_queued_for_deletion())
	if ch3.step != "gate" or ch3._marked.size() != 3 or marks.call("Pick the cage lock").size() != 2:
		return _fail("gate setup: step %s marked %d" % [ch3.step, ch3._marked.size()])
	marks.call("Unlock the Veil's Chapel")[0].used.emit(player)
	await _frames(5)
	Engine.time_scale = 1.0
	if ch3.step != "harvest" or not get_nodes_in_group("enemies").is_empty() \
			or not marks.call("Pick the cage lock").is_empty():
		return _fail("after the gate: step %s, %d enemies, %d cage locks" % [ch3.step,
			get_nodes_in_group("enemies").size(), marks.call("Pick the cage lock").size()])
	world.queue_free()
	await _frames(5)

	# dev skip into the final fight: 3 floodlights, the Harvester up, Lucía caged
	world = _world("harvester")
	await create_timer(3.0).timeout
	ch3 = world.get_node("Chapter3")
	if ch3.step != "harvester" or ch3.floods.size() != 3 or not is_instance_valid(ch3.harvester) \
			or not is_instance_valid(ch3.lucia):
		return _fail("harvester skip: step %s floods %d" % [ch3.step, ch3.floods.size()])
	if ch3.floods.any(func(x: Floodlight) -> bool: return x.armed):
		return _fail("floodlights armed in phase 1")
	print("CH3 OK")
	quit(0)
