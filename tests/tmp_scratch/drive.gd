extends SceneTree
var ch2: Chapter2Director
var player: CharacterBody3D

func _initialize() -> void:
	_run.call_deferred()

func _use_near(pos: Variant, timeout := 90.0) -> bool:
	var t := 0.0
	while t < timeout:
		for n in get_nodes_in_group("interactable"):
			if n.enabled and ((pos is String and n.prompt.begins_with(pos)) or (pos is Vector3 and n.global_position.distance_to(pos) < 0.5)) and player.controls_enabled:
				player.global_position = n.global_position + Vector3(0.8, -0.8, 0)
				await physics_frame
				n.used.emit(player)
				if n.once: n.enabled = false
				print("used ", n.prompt, " t=", t)
				return true
		await physics_frame
		t += 1.0 / 60.0
	print("NO interactable at ", pos, " step=", ch2.step, " controls=", player.controls_enabled)
	return false

func _until(c: Callable, timeout := 90.0) -> bool:
	var t := 0.0
	while t < timeout and not c.call():
		await physics_frame
		t += 1.0 / 60.0
	return c.call()

func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = OS.get_cmdline_user_args()[0]
	root.add_child(world)
	player = world.get_node("Player")
	await physics_frame
	await physics_frame
	ch2 = world.get_node("Chapter2")
	if ch2.step == "channel7":
		await _use_near(Chapter2Director.BATTERY)
		await _until(func(): return player.carrying == "battery", 5)
		print("carrying=", player.carrying)
		await _use_near(Chapter2Director.LH_RADIO)
		await _until(func(): return hud_radio() != null, 5)
		hud_radio().done.emit()
		await _until(func(): return ch2.step == "zones", 120)
		print("step=", ch2.step, " ev=", ch2.flags.evidence)
	player.global_position = Vector3(96, 0.2, 0)
	await _frames(5)
	player.global_position = Vector3(102.5, 0.2, 0)
	await _until(func(): return player.controls_enabled == false, 5)
	print("arrive step=", ch2.step)
	await _use_near(Chapter2Director.BREAKER, 120)
	await _use_near(Chapter2Director.KEY2, 120)
	var nora: Enemy = await _find_enemy("Nora")
	print("nora ", nora)
	await _until(func(): return player.controls_enabled, 120)
	nora.hit(200, nora.global_position + Vector3.UP * 0.5)
	await _frames(10)
	nora.hit(400, nora.global_position + Vector3.UP * 0.5)
	await _until(func(): return nora.state == Enemy.State.DOWN, 5)
	await _use_near("Spare", 60)
	await _until(func(): return ch2.flags.nora != "active", 60)
	print("nora=", ch2.flags.nora, " key_parts=", ch2.flags.key_parts)
	# clinic
	await _until(func(): return player.controls_enabled, 120)
	player.global_position = Vector3(50, 0.2, -100)
	await _use_near(Chapter2Director.MASK, 120)
	await _use_near(Chapter2Director.LADDER, 60)
	await _use_near(Chapter2Director.HVAC, 60)
	print("vents=", GasCloud.vents_reversed)
	await _use_near(Chapter2Director.KEY3, 120)
	var j: Enemy = await _find_enemy("Julian", true)
	await _until(func(): return player.controls_enabled, 120)
	for k in 60:
		if j.state == Enemy.State.DOWN: break
		j.hit(150, j.global_position + Vector3.UP * 0.5)
		await _frames(60)
	print("julian state ", j.state)
	await _until(func(): return player.controls_enabled, 60)
	j.hit(1, j.global_position)
	await _until(func(): return ch2.flags.julian != "active", 60)
	print("julian=", ch2.flags.julian, " step=", ch2.step)
	await _until(func(): return ch2.step == "traitor", 60)
	await _until(func(): return player.controls_enabled, 60)
	player.global_position = Vector3(-50, 0.2, -100)
	await _until(func(): return ch2.step == "free", 200)
	print("END step=", ch2.step, " flags=", ch2.flags)
	quit(0)

func _frames(n):
	for i in n: await physics_frame

func _find_enemy(name: String, boss := false) -> Enemy:
	var r := []
	await _until(func():
		for e in get_nodes_in_group("enemies"):
			if e.display_name == name and (not boss or e.boss): r.append(e); return true
		return false, 60)
	return r[0] if r else null

func hud_radio() -> Node:
	for n in player.hud.get_children():
		if n is RadioTuning: return n
	return null
