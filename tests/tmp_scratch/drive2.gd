extends SceneTree
## Scratch: Ch1 blackout → Ch2 intro → channel7 → side missions → clinic first (spare Julian w/ file)
## → school (boxes, desks, drawing, kill Nora, one death mid-fight) → traitor → free.
var ch2: Chapter2Director
var player: CharacterBody3D
var errors := 0


func _initialize() -> void:
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
				n.used.emit(player)
				if n.once: n.enabled = false
				print("  used '", n.prompt, "'")
				return true
		await physics_frame
		t += 1.0 / 60.0
	print("!! NO interactable ", pos, " step=", ch2.step, " controls=", player.controls_enabled)
	errors += 1
	return false


func _game(cls, args: Array) -> void:
	## Wait for a minigame of class cls under the hud, emit its done with args, free it.
	var r := []
	await _until(func():
		for n in player.hud.get_children():
			if is_instance_of(n, cls) and n.is_processing(): r.append(n); return true
		return false, 40)
	var g: Node = r[0] if r else null
	if g == null:
		print("!! no minigame ", cls); errors += 1; return
	g.set_process(false)
	g.set_process_input(false)
	g.callv("emit_signal", ["done"] + args)
	g.queue_free()
	print("  minigame done ", args)


func _mash(sec: float) -> void:
	var t := 0.0
	while t < sec:
		Input.action_press("interact")
		await physics_frame
		Input.action_release("interact")
		await physics_frame
		t += 2.0 / 60.0


func _heal_loop() -> void:
	while true:
		await physics_frame
		if player.health < 60 and not _dying: player.health = 100.0

var _dying := false


func _find_enemy(name: String) -> Enemy:
	var r := []
	await _until(func():
		for e in get_nodes_in_group("enemies"):
			if e.display_name == name and e.boss: r.append(e); return true
		return false, 60)
	return r[0] if r else null


func _fight(e: Enemy, dmg: float) -> void:
	for k in 200:
		if e.state == Enemy.State.DOWN: break
		await _until(func(): return player.controls_enabled, 60)
		if e.state == Enemy.State.DOWN: break
		e.hit(dmg, e.global_position + Vector3.UP * 0.5)
		await _frames(40)


func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "channel7"
	root.add_child(world)
	player = world.get_node("Player")
	ch2 = world.get_node("Chapter2")
	_heal_loop()
	await _until(func(): return ch2.step == "channel7", 200)
	print("C2.1 done, clock/step ", ch2.step, " bottles ", player.bottles)
	await _use_near(Chapter2Director.BATTERY)
	await _use_near(Chapter2Director.LH_RADIO)
	await _game(RadioTuning, [])
	await _until(func(): return ch2.step == "zones", 120)
	print("zones. ev=", ch2.flags.evidence)
	ch2.flags.tokens = 50
	# --- side missions in town
	await _use_near("Read the note by the fishing rod")
	await _use_near("Fish (Old Tom's rod)")
	await _game(Fishing, ["Old Tom", 150])
	await _until(func(): return player.controls_enabled, 60)
	await _use_near("Sit at Silas' table")
	await _game(HiLo, [true, 20])
	await _until(func(): return player.controls_enabled, 60)
	await _use_near("Play Moth Run")
	await _game(MothRun, [12000])
	await _until(func(): return player.controls_enabled, 30)
	print("side: tokens=", ch2.flags.tokens, " ev=", ch2.flags.evidence, " rumor=", ch2.flags.silas_rumor)
	# --- clinic first
	player.global_position = Vector3(50, 0.2, -100)
	await _until(func(): return not player.controls_enabled, 10)
	await _until(func(): return player.controls_enabled, 60)
	await _use_near("Free the strapped patient")
	_mash(3.0)
	await _use_near("Open the morgue freezer", 60)
	await _use_near("Pick the pharmacy cabinet lock")
	await _game(Lockpick, [true])
	await _use_near("Search the records cabinet", 60)
	print("clinic side: ev=", ch2.flags.evidence, " tea=", ch2.flags.get("tea"), " sam=", ch2.flags.sam_file)
	await _use_near(Chapter2Director.MASK, 60)
	await _use_near(Chapter2Director.LADDER, 60)
	await _use_near(Chapter2Director.HVAC, 60)
	await _use_near(Chapter2Director.KEY3, 60)
	var j := await _find_enemy("Julian")
	await _fight(j, 90)
	await _use_near("Spare", 60)
	await _until(func(): return ch2.flags.julian != "active", 60)
	print("julian=", ch2.flags.julian, " parts=", ch2.flags.key_parts)
	# --- school
	await _until(func(): return player.controls_enabled, 60)
	for i in 3:
		await _use_near("Silence the music box", 30)
	player.global_position = Vector3(96, 0.2, 0)
	await _frames(5)
	player.global_position = Vector3(102.5, 0.2, 0)
	await _until(func(): return not player.controls_enabled, 10)
	await _use_near("Search the desk", 60)
	await _use_near("Search the desk", 60)
	await _use_near(Chapter2Director.BREAKER, 60)
	await _use_near(Chapter2Director.DRAWING, 60)
	await _use_near(Chapter2Director.KEY2, 60)
	var nora := await _find_enemy("Nora")
	await _until(func(): return player.controls_enabled, 60)
	nora.hit(80, nora.global_position + Vector3.UP * 0.5)
	await _frames(30)
	_dying = true  # die once mid-fight: checkpoint + boss reset
	player.hurt(999.0)
	await _until(func(): return not player.controls_enabled, 5)
	await _until(func(): return player.controls_enabled, 30)
	_dying = false
	print("after death: nora hp ", nora.health, "/", nora.max_health, " player ", player.global_position)
	await _fight(nora, 90)
	await _until(func(): return player.controls_enabled, 60)
	nora.hit(1, nora.global_position)  # shoot the kneeling boss = KILL
	await _until(func(): return ch2.flags.nora != "active", 60)
	print("nora=", ch2.flags.nora, " parts=", ch2.flags.key_parts, " drawing=", ch2.flags.drawing)
	await _until(func(): return ch2.step == "traitor", 90)
	await _until(func(): return player.controls_enabled, 60)
	player.global_position = Vector3(-50, 0.2, -100)
	await _until(func(): return ch2.step == "free", 200)
	await _until(func(): return player.controls_enabled, 30)
	print("END step=", ch2.step, " errors=", errors, " flags=", ch2.flags)
	quit(0)
