extends SceneTree
## Headless check of the Chapter 2 enemy/world mechanics: stealth takedown, Nora's lily calls,
## Julian's gas (cloud damage, canister throw, asthma stun with reversed vents), hiding-spot checks,
## music box chime → enemies hear, silenced signal.
## flatpak run org.godotengine.Godot --headless --path . -s tests/enemy_ch2_test.gd

var player: CharacterBody3D
var world: Node


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("ENEMY CH2 FAIL: " + msg)
	GasCloud.vents_reversed = false
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
	world = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "free"
	root.add_child(world)
	player = world.get_node("Player")
	await _frames(60)
	var base := Vector3(-86, 0.2, 60)  # open lot
	player.global_position = base
	await _frames(30)

	# takedown: crouched right behind an unaware Marked One (it faces +Z, away from the player)
	_press("crouch")
	await _frames(2)
	_press("crouch", false)
	await _frames(20)
	var m := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(0, 0, 1.3), 0.0, {"walk_speed": 0.0})
	await _frames(10)
	if not m.can_takedown(player):
		return _fail("no takedown from behind (state %d)" % m.state)
	m.takedown()
	if m.state != Enemy.State.DEAD:
		return _fail("takedown did not kill a Marked One")
	var boss := Enemy.spawn(world, "res://models/char_nora.glb", base + Vector3(0, 0, 1.3), 0.0,
			{"boss": true, "max_health": 100.0, "shadow_bonus": 2.0, "walk_speed": 0.0})
	await _frames(10)
	if not boss.can_takedown(player):
		return _fail("no takedown on an unaware boss")
	boss.takedown()
	if absf(boss.health - 50.0) > 0.01 or boss.state != Enemy.State.STUNNED:
		return _fail("boss takedown: health %f state %d" % [boss.health, boss.state])
	boss.queue_free()
	_press("crouch")
	await _frames(2)
	_press("crouch", false)
	await _frames(20)

	# Nora: calls for Lily on a timer, glows, and takes extra damage while calling
	var nora := Enemy.spawn(world, "res://models/char_nora.glb", base + Vector3(40, 0, 0), 0.0,
			{"lily_calls": true, "call_interval": 0.3, "max_health": 100.0, "sight_range": 1.0})
	var calls := [0]
	nora.called.connect(func(_e: Enemy) -> void: calls[0] += 1)
	await _frames(30)
	if calls[0] < 1:
		return _fail("lily_calls never emitted called")
	if nora._calling <= 0.0 or nora._glow.light_energy <= 0.0:
		return _fail("Nora is not glowing while calling")
	nora.hit(10.0, nora.global_position + Vector3.UP)  # not in CHASE, calling: 10 × 1.5
	if absf(nora.health - 85.0) > 0.01:
		return _fail("calling damage bonus wrong: %f" % nora.health)
	nora.set_physics_process(false)  # frozen for a cutscene: barrel fire / stray shots do nothing
	nora.hit(50.0, nora.global_position)
	nora.stun(3.0)
	if absf(nora.health - 85.0) > 0.01 or nora.state == Enemy.State.STUNNED:
		return _fail("frozen enemy took a hit/stun: hp %f state %d" % [nora.health, nora.state])
	nora.queue_free()

	# gas: hurts the player inside; with vents reversed an asthmatic enemy chokes
	var hp: float = player.health
	var gas := GasCloud.make(world, player.global_position)
	await _frames(90)
	if player.health >= hp:
		return _fail("gas cloud did not hurt the player (%f)" % player.health)
	gas.clear()
	await _frames(100)
	if is_instance_valid(gas):
		return _fail("cleared gas cloud still there")
	player.health = player.health_max
	var jpos := base + Vector3(40, 0, 20)
	var julian := Enemy.spawn(world, "res://models/char_julian.glb", jpos, 0.0,
			{"asthma": true, "sight_range": 1.0, "walk_speed": 0.0})
	var gas2 := GasCloud.make(world, jpos, 3.0, 0.0)
	await _frames(60)
	if julian.state == Enemy.State.STUNNED:
		return _fail("asthma stun without reversed vents")
	GasCloud.vents_reversed = true
	await _frames(10)
	if julian.state != Enemy.State.STUNNED:
		return _fail("asthma enemy not stunned in reversed gas")
	GasCloud.vents_reversed = false
	gas2.queue_free()
	julian.queue_free()

	# gas thrower: lobs a canister that becomes a cloud near the player
	var thrower := Enemy.spawn(world, "res://models/char_julian.glb", base + Vector3(0, 0, 9), PI,
			{"gas_thrower": true, "gas_interval": 6.0, "melee_damage": 0.0})
	thrower._gas_t = 0.0
	var thrown := false
	for i in 150:
		await physics_frame
		for g in get_nodes_in_group("gas_clouds"):
			if g.global_position.distance_to(player.global_position) < 4.0:
				thrown = true
		if thrown:
			break
	if not thrown:
		return _fail("gas thrower never landed a cloud near the player (state %d)" % thrower.state)
	thrower.queue_free()
	for g in get_nodes_in_group("gas_clouds"):
		g.queue_free()
	await _frames(5)
	player.health = player.health_max

	# controls off (cinematic / minigame): a chaser in melee range stands still, drops its windup, can't hurt
	var chaser := Enemy.spawn(world, "res://models/char_marked_man.glb", player.global_position + Vector3(0, 0, 1.4), PI)
	await _frames(5)
	player.controls_enabled = false
	chaser._set_state(Enemy.State.CHASE)
	chaser._attack = 0.3
	var cpos := chaser.global_position
	await _frames(90)
	if chaser._attack >= 0.0 or chaser.global_position.distance_to(cpos) > 0.1 \
			or player.health < player.health_max or player.hurt(10.0):
		return _fail("enemy acted / player hurt with controls off (attack %f, hp %f)" % [chaser._attack, player.health])
	player.controls_enabled = true
	await _frames(90)
	if player.health >= player.health_max:
		return _fail("chaser never attacked once controls came back")
	chaser.queue_free()
	player.health = player.health_max

	# checks_hiding: remembers a spot it saw the player hide in and searches it first
	var spot := base + Vector3(-30, 0, 0)
	var seeker := Enemy.spawn(world, "res://models/char_julian.glb", spot + Vector3(4, 0, 0), 0.0,
			{"checks_hiding": true, "sight_range": 1.0})
	await _frames(5)
	seeker._unseen = 0.0
	seeker._on_hid(spot)
	var checked := [Vector3.INF]
	seeker.checks_spot.connect(func(_e: Enemy, p: Vector3) -> void: checked[0] = p)
	seeker.lose_track(spot + Vector3(10, 0, 10))
	await _frames(240)
	if checked[0] != spot:
		return _fail("checks_hiding did not visit the remembered spot")
	seeker.queue_free()

	# music box: walking past it chimes and the enemy comes to look; E silences it
	var box := MusicBox.make(world, base + Vector3(2, 0, 0))
	var listener := Enemy.spawn(world, "res://models/char_marked_woman.glb", base + Vector3(14, 0, 0), 0.0,
			{"sight_range": 1.0, "walk_speed": 0.0})
	await _frames(5)
	_press("move_forward")
	await _frames(30)
	_press("move_forward", false)
	if listener.state != Enemy.State.SUSPICIOUS:
		return _fail("enemy did not hear the music box (state %d)" % listener.state)
	var got := [false]
	box.silenced.connect(func() -> void: got[0] = true)
	box.interactable.interact(player)
	if not got[0] or box.playing:
		return _fail("music box not silenced")
	print("ENEMY CH2 OK")
	quit(0)
