extends SceneTree
## Headless check of the Chapter 2 player mechanics: carry restrictions, gas exposure with/without mask,
## bottle throw landing noise, stealth takedown, hid signal, HUD QTE success/fail.
## flatpak run org.godotengine.Godot --headless --path . -s tests/player_ch2_test.gd

const FAKE_ENEMY := """
extends Node3D
var heard: Array = []
var taken := false
func hear(pos: Vector3, radius: float) -> void:
	heard.append([pos, radius])
func can_takedown(_by: Node3D) -> bool:
	return true
func takedown() -> void:
	taken = true
"""

var player: CharacterBody3D


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("CH2 PLAYER FAIL: " + msg)
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


func _tap(action: String) -> void:
	_press(action)
	await _frames(2)
	_press(action, false)
	await _frames(2)


func _frames(n: int) -> void:
	for i in n:
		await physics_frame


func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "free"
	root.add_child(world)
	player = world.get_node("Player")
	await _frames(60)
	player.global_position = Vector3(-86, 0.2, 60)
	await _frames(30)
	var script := GDScript.new()
	script.source_code = FAKE_ENEMY
	script.reload()
	var fake := Node3D.new()
	fake.set_script(script)
	fake.add_to_group("enemies")
	world.add_child(fake)
	fake.global_position = player.global_position + Vector3(0, 0, 30)

	# carry: walk only, no roll / jump / aim
	player.weapons.give("revolver", 12)
	player.carry("battery")
	if player.carrying != "battery":
		return _fail("carry did not set carrying")
	_press("move_forward")
	_press("sprint")
	await _frames(40)
	var v := Vector2(player.velocity.x, player.velocity.z).length()
	_press("sprint", false)
	_press("move_forward", false)
	if v > player.walk_speed + 0.05:
		return _fail("sprinted while carrying: %.2f" % v)
	await _frames(20)
	var y0 := player.global_position.y
	await _tap("jump")
	await _frames(8)
	if player.global_position.y > y0 + 0.2:
		return _fail("jumped while carrying")
	await _tap("roll")
	if player.rolling_invulnerable():
		return _fail("rolled while carrying")
	_press("aim")
	await _frames(3)
	var aimed: bool = player.aiming
	_press("aim", false)
	if aimed:
		return _fail("aimed a gun while carrying")
	player.drop_carry()
	if player.carrying != "":
		return _fail("drop_carry did not clear")
	await _frames(10)

	# hid: crouching next to a hiding spot emits once
	var hid_at: Array = []
	player.hid.connect(func(p: Vector3) -> void: hid_at.append(p))
	player.hidden_spots.append(player.global_position)
	await _tap("crouch")
	await _frames(5)
	if hid_at.size() != 1:
		return _fail("hid emitted %d times" % hid_at.size())
	await _tap("crouch")
	player.hidden_spots.clear()
	await _frames(5)

	# gas: hurts + cough noise without a mask
	player.health = 100.0
	fake.heard.clear()
	for i in 60:
		player.gas_exposure(1.0 / 60.0)
		player.gas_exposure(1.0 / 60.0)  # a second overlapping cloud counts once
		await physics_frame
	if player.health > 95.5 or player.health < 93.0:
		return _fail("gas damage wrong: %.2f" % player.health)
	if fake.heard.is_empty() or not player.in_gas():
		return _fail("no cough noise / not in gas")
	# mask on with filter: no damage, filter drains
	await _tap("mask")
	if player.mask_on:
		return _fail("mask toggled without owning one")
	player.gas_mask = true
	await _tap("mask")
	if not player.mask_on:
		return _fail("mask input did not put the mask on")
	var h: float = player.health
	for i in 60:
		player.gas_exposure(1.0 / 60.0)
		await physics_frame
	if player.health < h or player.mask_filter >= 1.0:
		return _fail("mask did not protect / filter did not drain (%.2f, %.3f)" % [player.health, player.mask_filter])
	player.mask_filter = 0.0
	for i in 30:
		player.gas_exposure(1.0 / 60.0)
		await physics_frame
	if player.health >= h:
		return _fail("empty filter still protects")
	player.refill_filter()
	if player.mask_filter != 1.0:
		return _fail("refill_filter")
	await _tap("mask")
	player.health = 100.0

	# bottle: lands and every enemy hears it (radius 14)
	player.bottles = 1
	fake.heard.clear()
	var aim_at: Vector3 = player.throw_target()
	await _tap("throw")
	if player.bottles != 0:
		return _fail("throw did not use a bottle")
	var landed := false
	for i in 300:
		await physics_frame
		for hh in fake.heard:
			if hh[1] == 14.0 and hh[0].distance_to(player.global_position) > 2.0:
				landed = true
				if hh[0].distance_to(aim_at) > 1.5:
					return _fail("bottle missed the crosshair: landed %s, aimed %s" % [hh[0], aim_at])
		if landed:
			print("bottle landed after %d frames" % i)
			break
	if not landed:
		return _fail("bottle landing noise not heard: %s" % [fake.heard])

	# takedown: close unaware enemy → E calls takedown()
	fake.global_position = player.global_position + Vector3(0.8, 0, 0)
	if player.takedown_target() != fake:
		return _fail("takedown target not found")
	await _tap("interact")
	await _frames(40)
	if not fake.taken:
		return _fail("interact did not take the enemy down")
	fake.queue_free()

	# QTE: works with controls disabled; mash → true, idle → false
	player.controls_enabled = false
	var out := {}
	var run_qte := func(key: String, presses: int, time: float) -> void:
		out[key] = await player.hud.qte("interact", presses, time)
	run_qte.call("ok", 4, 3.0)
	for i in 4:
		Input.action_press("interact")
		await _frames(3)
		Input.action_release("interact")
		await _frames(3)
	await _frames(5)
	if out.get("ok") != true:
		return _fail("QTE mash did not succeed: %s" % [out])
	run_qte.call("fail", 5, 0.4)
	await _frames(40)
	if out.get("fail") != false:
		return _fail("QTE without presses did not fail: %s" % [out])
	player.controls_enabled = true
	player.hud.clock("15:00")
	print("CH2 PLAYER OK")
	quit(0)
