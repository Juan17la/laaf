extends SceneTree
## Headless check of the Chapter 2 director: dormant by default, Chapter 1 hands over on a ch2 dev
## step (flags, arming, bottles, spawn), zone setup (music boxes, patrols), lights_out radius.
## flatpak run org.godotengine.Godot --headless --path . -s tests/chapter2_test.gd


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("CH2 FAIL: " + msg)
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
	# free roam: Chapter 2 stays dormant
	var world := _world("free")
	await _frames(30)
	var ch2: Chapter2Director = world.get_node("Chapter2")
	if ch2.step != "" or ch2.cam != null:
		return _fail("Chapter 2 woke up in a Chapter 1 free-roam run")
	world.queue_free()
	await _frames(5)

	# dev skip straight into the zones step
	world = _world("zones")
	await _frames(60)
	ch2 = world.get_node("Chapter2")
	var player: CharacterBody3D = world.get_node("Player")
	if ch2.step != "zones":
		return _fail("dev skip did not reach the zones step (step '%s')" % ch2.step)
	var f: Dictionary = ch2.flags
	if f.nora != "active" or f.julian != "active" or f.key_parts != 1 or not f.key_part \
			or f.music_boxes != 0 or not f.elena_alive or f.drawing or f.sam_file:
		return _fail("flag defaults wrong: %s" % f)
	if f != world.get_node("Chapter1").flags:
		return _fail("Chapter 2 does not share Chapter 1's flags")
	if player.weapons.gun() == "" or player.bottles < 3:
		return _fail("dev skip did not arm the player / hand out bottles")
	if player.global_position.distance_to(Vector3(6, 0.1, 132)) > 3.0:
		return _fail("zones start spot wrong: %s" % player.global_position)
	if get_nodes_in_group("enemies").size() < 10:
		return _fail("zone patrols missing: %d enemies" % get_nodes_in_group("enemies").size())
	if ch2.get_children().filter(func(n: Node) -> bool: return n is MusicBox).size() != 3:
		return _fail("expected 3 music boxes on the playground")
	if GasCloud.vents_reversed:
		return _fail("vents start reversed")

	# leash: a school Marked One chasing Alex outside the school lot gives up
	var yard: Enemy = ch2._marked[0]
	yard._set_state(Enemy.State.CHASE)
	await _frames(45)
	if yard.state == Enemy.State.CHASE:
		return _fail("school Marked One chased Alex out of the school lot")
	# Julian's clinic stalker: never invulnerable, gone while Alex is on the roof, falls back (alive,
	# hidden, out of the enemies group) once hurt to half health, freed with the clinic
	ch2._hunt_on = true
	var j: Enemy = ch2._stalker()
	await _frames(5)
	if j.visible:
		return _fail("Julian's stalker is out while Alex is outside the clinic")
	var outside := player.global_position
	player.global_position = Vector3(68, 0.1, -99)  # into the clinic hall
	await _frames(5)
	if j.invulnerable or not j.visible:
		return _fail("Julian's stalker is invulnerable / not out")
	ch2._hunt_on = false
	await _frames(3)
	if j.visible or j.is_in_group("enemies"):
		return _fail("Julian's stalker still out with the hunt off (roof)")
	ch2._hunt_on = true
	await _frames(3)
	if not j.visible or j.health < j.max_health:
		return _fail("Julian's stalker did not come back healed")
	for i in 3:
		j.hit(34.0, j.global_position + Vector3.UP)
	for i in 240:
		if not j.visible:
			break
		await physics_frame
	if j.visible or j.is_in_group("enemies") or j.state == Enemy.State.DEAD:
		return _fail("hurt stalker did not fall back (visible %s, state %d)" % [j.visible, j.state])
	player.global_position = outside
	ch2._free_marked(Chapter2Director.CLINIC)
	await _frames(2)
	if is_instance_valid(j):
		return _fail("clinic end left Julian's stalker")
	# a finished mission frees its Marked Ones; none are left for the traitor step
	var n := get_nodes_in_group("enemies").size()
	ch2._free_marked(Chapter2Director.SCHOOL)
	await _frames(2)
	if get_nodes_in_group("enemies").size() != n - 6:
		return _fail("school end left Marked Ones: %d -> %d" % [n, get_nodes_in_group("enemies").size()])
	ch2._free_marked()
	await _frames(2)
	if not get_nodes_in_group("enemies").is_empty() or not ch2._marked.is_empty():
		return _fail("Marked Ones alive going into the traitor step")

	# lights_out radius: only lights near `from` die
	var near := OmniLight3D.new()
	var far := OmniLight3D.new()
	world.add_child(near)
	world.add_child(far)
	near.global_position = Vector3(108, 3, 5)
	far.global_position = Vector3(0, 3, 24)
	ch2.lights_out(Vector3(108, 0, 0), 1000.0, 45.0)
	await _frames(30)
	if near.light_energy > 0.01 or far.light_energy < 0.99:
		return _fail("lights_out radius: near %.2f far %.2f" % [near.light_energy, far.light_energy])
	print("CH2 OK")
	quit(0)
