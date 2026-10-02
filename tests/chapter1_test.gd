extends SceneTree
## Headless check of the Chapter 1 mechanics: jump, roll i-frames, slide, swap-shot double tap,
## enemy perception + damage, boss down → kill choice.
## flatpak run org.godotengine.Godot --headless --path . -s tests/chapter1_test.gd

var player: CharacterBody3D


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("CH1 FAIL: " + msg)
	quit(1)


func _press(action: String, pressed := true) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = pressed
	Input.parse_input_event(e)
	if pressed:
		Input.action_press(action)
	else:
		Input.action_release(action)


func _frames(n: int) -> void:
	for i in n:
		await physics_frame


func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "free"
	root.add_child(world)
	player = world.get_node("Player")
	await _frames(60)
	# move out onto the open lot so nothing is overhead
	player.global_position = Vector3(-86, 0.2, 60)
	await _frames(30)

	# jump
	var y0 := player.global_position.y
	_press("jump")
	await _frames(12)
	_press("jump", false)
	if player.global_position.y < y0 + 0.4:
		return _fail("jump did not lift the player: %f -> %f" % [y0, player.global_position.y])
	await _frames(60)

	# roll: invulnerable at the start
	_press("roll")
	await _frames(2)
	_press("roll", false)
	if not player.rolling_invulnerable() or player.hurt(50.0):
		return _fail("roll has no i-frames")
	await _frames(40)

	# slide: sprint, then crouch
	_press("move_forward")
	_press("sprint")
	await _frames(20)
	_press("crouch")
	await _frames(2)
	_press("crouch", false)
	if not player.anim.sliding:
		return _fail("crouch while sprinting did not slide")
	_press("sprint", false)
	_press("move_forward", false)
	await _frames(60)

	# swap-shot double tap
	var w: Weapons = player.weapons
	w.give("revolver", 24)
	w.give("flare", 4)
	var space := player.get_world_3d().direct_space_state
	var up := Vector3.UP
	var r1 := w.shoot(space, player.global_position + up * 50, up, [])
	if r1.double_tap:
		return _fail("first shot should not be a double tap")
	w.swap()
	if not w.can_fire():
		return _fail("swap right after a shot must allow an instant shot")
	var r2 := w.shoot(space, player.global_position + up * 50, up, [])
	if not r2.double_tap or r2.gun != "flare":
		return _fail("second shot after a quick swap is not a flare double tap")
	w.swap()
	await _frames(40)  # > SWAP_WINDOW: a slow swap is a normal swap
	w.swap()
	if w.can_fire():
		return _fail("slow swap should have a draw delay")

	# enemy: sees the player, takes damage, boss kneels and can be executed
	var e := Enemy.spawn(world, "res://models/char_marked_man.glb", player.global_position + Vector3(0, 0, 6), PI)
	await _frames(30)
	if e.state != Enemy.State.CHASE:
		return _fail("Marked One did not notice the player at 6 m (state %d)" % e.state)
	e.hit(34.0, e.global_position + Vector3.UP)
	if absf(e.health - 26.0) > 0.01:
		return _fail("body shot damage wrong: %f" % e.health)
	var boss := Enemy.spawn(world, "res://models/char_owen.glb", player.global_position + Vector3(8, 0, 0), 0.0,
			{"boss": true, "max_health": 50.0, "flare_stun": 6.0})
	await _frames(5)
	boss.hit(10.0, boss.global_position + Vector3.UP, true)
	if boss.state != Enemy.State.STUNNED:
		return _fail("flare did not stun Owen")
	boss.hit(100.0, boss.global_position + Vector3.UP)
	if boss.state != Enemy.State.DOWN:
		return _fail("boss did not kneel at 0 HP")
	boss.hit(1.0, boss.global_position + Vector3.UP)
	if boss.state != Enemy.State.DEAD:
		return _fail("shooting a kneeling boss did not kill")

	# M2 hunt: Owen is frozen in the reveal, a catch never kills, and he's gone once the square is reached
	var ch1: Chapter1Director = world.get_node("Chapter1")
	ch1.clear_enemies()
	await _frames(2)
	ch1._step_hunt()
	await _frames(2)
	if not ch1._owen or ch1._owen.process_mode != Node.PROCESS_MODE_DISABLED:
		return _fail("hunting Owen must be frozen during the hunt_start cinematic")
	var left := 900
	while not player.controls_enabled and left > 0:
		await physics_frame
		left -= 1
	if not player.controls_enabled:
		return _fail("hunt_start never handed control back")
	player.health = 5.0
	await _frames(2)
	player.hurt(ch1._owen.melee_damage)
	if player.dead:
		return _fail("being caught by Owen in the first hunt must never kill")
	player.global_position = Vector3(0, 0.1, 30)
	await _frames(3)
	if not get_nodes_in_group("enemies").is_empty() or ch1._owen:
		return _fail("invulnerable hunt Owen still in the world after the hunt ended")
	print("CH1 OK")
	quit(0)
