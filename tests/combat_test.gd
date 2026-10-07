extends SceneTree
## Headless check of dynamic combat (Enemy): no stun-lock (stagger: guard window, shorter repeats, learned),
## dodging a swing it sees coming, pouncing in from a few metres, boss follow-up combos, varied downed poses
## and death falls, and the player being told when a habit takes hold.
## flatpak run org.godotengine.Godot --headless --path . -s tests/combat_test.gd

var player: CharacterBody3D
var world: Node


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("COMBAT FAIL: " + msg)
	quit(1)


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
	var h := Enemy.habits()
	h.stun = 0.0

	# no stun-lock: a flare stuns fully once, is shrugged off right after, and lands shorter the next time
	var owen := Enemy.spawn(world, "res://models/char_owen.glb", base + Vector3(8, 0, 0), 0.0,
			{"boss": true, "max_health": 400.0, "flare_stun": 6.0, "agile": false})
	await _frames(5)
	owen.hit(1.0, owen.global_position + Vector3.UP, true)
	if owen.state != Enemy.State.STUNNED or owen._stun < 5.9:
		return _fail("first flare: state %d stun %f" % [owen.state, owen._stun])
	owen._stun = 0.01
	await _frames(3)
	if owen.state == Enemy.State.STUNNED or owen._guard <= 0.0:
		return _fail("no guard window after a stun")
	owen.hit(1.0, owen.global_position + Vector3.UP, true)
	if owen.state == Enemy.State.STUNNED:
		return _fail("stunned again inside the guard window (stun-lock)")
	owen._guard = 0.0
	owen.hit(1.0, owen.global_position + Vector3.UP, true)
	if owen.state != Enemy.State.STUNNED or owen._stun > 6.0 * 0.6:
		return _fail("repeat stun not shorter: %f" % owen._stun)
	if h.stun <= 0.0 or owen._rage <= 0.0:
		return _fail("stun habit / rage not raised (%f, %f)" % [h.stun, owen._rage])

	# varied downed poses: a beaten boss kneels in one of them, watching Alex
	owen._stun = 0.0
	owen.hit(9999.0, owen.global_position + Vector3.UP)
	if owen.state != Enemy.State.DOWN or not owen._anim.down_pose in Enemy.DOWN_POSES:
		return _fail("downed pose: state %d pose '%s'" % [owen.state, owen._anim.down_pose])
	owen.queue_free()

	# the player is told once a habit takes hold
	for i in 8:
		Enemy.learn("stun", 1.0)
	if not Enemy._noted.get("stun", false):
		return _fail("strong stun habit not told to the player")

	# dodge: a brawler's swing coming at it gets a backstep away from Alex, then a pounce back in
	h.melee = 1.0
	var m := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(0, 0, 2.0), PI, {"walk_speed": 0.0})
	await _frames(30)  # landed (dodges start from the ground)
	player.model.rotation.y = 0.0  # facing +Z, at the enemy
	player._strike_t = 0.1
	var dodged := false
	for i in 30:
		m._threat_was = ""
		m._dodge_cd = 0.0
		if m._try_dodge(2.0):
			dodged = true
			break
	player._strike_t = -1.0
	if not dodged:
		return _fail("never dodged a swing from a brawler-trained enemy")
	if m._dodge_vel.dot(m.global_position - player.global_position) <= 0.0 or m._pounce_cd > 0.0:
		return _fail("dodge not away from the swing / no pounce queued")
	m.queue_free()

	# pounce: from a few metres it gathers, leaps, and strikes on landing
	var p := Enemy.spawn(world, "res://models/char_marked_woman.glb", base + Vector3(0, 0, 4.5), PI, {"walk_speed": 0.0})
	await _frames(30)
	p._set_state(Enemy.State.CHASE)
	p._unseen = 0.0
	p._pounce_cd = 0.0
	var start: float = p.global_position.distance_to(player.global_position)
	var leapt := false
	var struck := false
	for i in 90:
		await physics_frame
		leapt = leapt or p._leapt
		struck = struck or (leapt and p._attack >= 0.0)
		if struck:
			break
	if not (leapt and struck) or p.global_position.distance_to(player.global_position) > start - 1.0:
		return _fail("no pounce into a strike (leapt %s struck %s)" % [leapt, struck])
	p.queue_free()
	player.health = player.health_max

	# combos: an enraged boss chains follow-up strikes
	var b := Enemy.spawn(world, "res://models/char_marcus.glb", base + Vector3(20, 0, 0), 0.0, {"boss": true, "sight_range": 1.0})
	await _frames(3)
	b._rage = 1.0
	var chained := false
	for i in 20:
		b._strike_start()
		chained = chained or b._combo > 0
	if not chained:
		return _fail("an enraged boss never chains a follow-up")
	b.queue_free()

	# deaths: not every body goes down the same way
	var falls := {}
	for i in 8:
		var d := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(-10 - 2 * i, 0, -8), 0.0, {"sight_range": 1.0})
		await _frames(2)
		d.kill()
		await _frames(80)
		var r: Vector3 = d._model.rotation
		falls["%d,%d" % [roundi(r.x), roundi(r.z)]] = true
	if falls.size() < 2:
		return _fail("every death fell the same way: %s" % [falls.keys()])
	print("COMBAT OK")
	quit(0)
