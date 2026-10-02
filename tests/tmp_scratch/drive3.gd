extends SceneTree
## Scratch: headless Chapter 3 playthrough from C3.1 to the free roam after C3.4.
##   -- --route=unveiled | signal | mixed | new_eye | run
## Every cinematic runs (subtitles time out), interactables are pressed directly, minigames finished
## by emitting `done`. Prints the step trail and any "!!" problems.
var ch3: Chapter3Director
var player: CharacterBody3D
var errors := 0
var route := "unveiled"
var shots := ""  ## --shots=<dir>: save a frame every 2.5 game-seconds of cinematic (needs a display)


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--route="):
			route = a.substr(8)
		elif a.begins_with("--shots="):
			shots = a.substr(8)
	Engine.time_scale = 4.0  # cinematics play out in real time otherwise
	_run.call_deferred()


func _frames(n):
	for i in n: await physics_frame


func _until(c: Callable, timeout := 90.0) -> bool:
	var t := 0.0
	while t < timeout and not c.call():
		await physics_frame
		t += 1.0 / 60.0
	return c.call()


func _use_near(pos: Variant, timeout := 90.0) -> bool:
	var t := 0.0
	while t < timeout:
		for n in get_nodes_in_group("interactable"):
			if n.enabled and player.controls_enabled and ((pos is String and n.prompt.begins_with(pos)) \
					or (pos is Vector3 and n.global_position.distance_to(pos) < 0.6)):
				player.global_position = n.global_position + Vector3(0.8, -0.8, 0)
				await physics_frame
				n.interact(player)
				print("  used '", n.prompt, "'")
				return true
		await physics_frame
		t += 1.0 / 60.0
	print("!! NO interactable ", pos, " step=", ch3.step, " controls=", player.controls_enabled)
	errors += 1
	return false


func _game(cls, args: Array) -> void:
	var found := []
	await _until(func():
		for n in player.hud.get_children():
			if is_instance_of(n, cls): found.append(n); return true
		return false, 10)
	var g: Node = found[0] if found else null
	if g == null:
		print("!! no minigame ", cls); errors += 1; return
	g.set_process(false)
	g.set_process_input(false)
	g.callv("emit_signal", ["done"] + args)
	g.queue_free()


func _heal_loop() -> void:
	while true:
		await physics_frame
		if player.health < 60: player.health = 100.0


func _shot_loop() -> void:
	var i := 0
	while i < 400:
		await create_timer(2.5).timeout
		if not player.controls_enabled:
			var img := root.get_texture().get_image()
			img.save_png("%s/%s_%03d_%s.png" % [shots, route, i, ch3.step])
			i += 1


func _boss(name: String) -> Enemy:
	var r := []
	await _until(func():
		for e in get_nodes_in_group("enemies"):
			if e.display_name == name and e.boss: r.append(e); return true
		return false, 90)
	if r.is_empty():
		print("!! no boss ", name); errors += 1
		return null
	return r[0]


func _step(s: String, timeout := 240.0) -> void:
	if not await _until(func(): return ch3.step == s, timeout):
		print("!! stuck before step ", s, " (at ", ch3.step, ")"); errors += 1
	print("STEP ", s, "  mark=%.0f clock=%s" % [player.mark, player.hud._clock.text])


func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "c3_bell"
	root.add_child(world)
	var f: Dictionary = world.get_node("Chapter1").flags  # set before the deferred start reads them
	var kill := route in ["new_eye", "mixed"]
	for m in ["owen", "nora", "julian"]:
		f[m] = "killed" if route == "new_eye" or (route == "mixed" and m == "nora") else "spared"
	f.merge({"lantern": true, "drawing": true, "sam_file": true, "tea": 2, "tokens": 120,
		"evidence": [1, 3, 4, 5, 6, 9, 10, 12] + ([2, 11] if route in ["signal", "mixed"] else [])}, true)
	player = world.get_node("Player")
	ch3 = world.get_node("Chapter3")
	_heal_loop()
	if shots != "":
		_shot_loop()
	await _step("run")
	await _until(func(): return player.controls_enabled, 60)
	await _use_near("Open Elena's stash")
	await _until(func(): return player.controls_enabled, 30)
	player.throw_smoke()
	print("  smokes left ", player.smokes, " teas ", player.teas)
	player.global_position = Chapter3Director.CHURCH_DOOR + Vector3(0.5, 0.2, 0)
	await _step("marcus")
	await _until(func(): return player.controls_enabled, 60)
	if route != "mixed":
		await _use_near("Take the photo from the choir pew")
	await _use_near("Read the bell register")
	for c in Chapter3Director.CANDLES:
		await _use_near("Light a candle for " + c[0])
		await _frames(10)
	player.global_position = Vector3(-79.0, 0.2, -100)
	var marcus := await _boss("Marcus")
	await _until(func(): return player.controls_enabled, 60)
	for b in ch3._bells:  # drop every bell on him (phases 2 and 3 come from the damage)
		await _until(func(): return player.controls_enabled, 60)
		marcus.global_position = b.global_position * Vector3(1, 0, 1)
		b.hit(1.0, b.global_position)
		await _frames(60)
		print("  bell: marcus hp %.0f" % marcus.health)
	for k in 60:
		if marcus.state == Enemy.State.DOWN: break
		await _until(func(): return player.controls_enabled, 60)
		marcus.stun(1.0)
		marcus.hit(60.0, marcus.global_position + Vector3.UP * 0.5)
		await _frames(20)
	await _until(func(): return player.controls_enabled, 60)
	if kill:
		marcus.hit(1.0, marcus.global_position)
	else:
		await _use_near("Spare Marcus")
	await _step("static")
	print("  marcus=", ch3.flags.marcus, " key=", ch3.flags.has_chapel_key, " ev=", ch3.flags.evidence)
	await _until(func(): return player.controls_enabled, 60)
	await _use_near("Talk to Grady")
	await _until(func(): return player.controls_enabled, 60)
	await _use_near("Elena's radio")
	await _until(func(): return player.controls_enabled, 90)
	await _use_near("Play Elena's recorder")
	await _until(func(): return player.controls_enabled, 60)
	if route in ["signal", "mixed"]:
		await _use_near("Transmitter")
		await _game(RadioTuning, [])
		await _until(func(): return ch3.flags.broadcast_sent and player.controls_enabled, 60)
	else:
		await _use_near("Transmitter")  # locked bark
	print("  jacket=", ch3.flags.jacket, " resist=", player.mark_resist, " broadcast=", ch3.flags.broadcast_sent)
	player.global_position = Chapter3Director.QUARRY_MOUTH + Vector3(0, 0.2, 2)
	await _step("gate")
	await _until(func(): return player.controls_enabled, 60)
	if route == "run":
		await _use_near("Tunnel gate")
		await _step("shepherd")
	else:
		for i in 2:
			await _use_near("Pick the cage lock")
			await _game(Lockpick, [true])
			await _until(func(): return player.controls_enabled, 60)
		await _use_near("Unlock the Veil's Chapel")
		await _step("harvest")
		await _step("harvester")
		var h: Harvester = await _boss("The Harvester")
		for k in 200:
			if h.state == Enemy.State.DOWN: break
			await _until(func(): return player.controls_enabled, 60)
			if k == 8:
				for fl in ch3.floods:
					if fl.armed and fl.switch.enabled:
						fl.switch.interact(player)
						print("  floodlight thrown")
						break
			h._immune = 0.0
			h.light_stun()
			h.hit(120.0, h.global_position - h.get_node("Model").global_basis.z * 2.0 + Vector3.UP * 1.5)
			await _frames(30)
		print("  harvester down, cages=", ch3.flags.cages, " allies=", ch3.allies.keys())
	await _step("epilogue", 300)
	print("  ending=", ch3.flags.ending)
	await _step("free", 300)
	await _until(func(): return player.controls_enabled, 30)
	print("END route=", route, " ending=", ch3.flags.ending, " errors=", errors)
	quit(0)
