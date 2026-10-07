extends SceneTree
## Headless check of the adaptive enemy AI (Enemy.habits): each habit is learned from what the player
## does and changes how enemies act (delayed strikes, weaving, glancing back, searching hiding spots).
## flatpak run org.godotengine.Godot --headless --path . -s tests/adaptive_test.gd

var player: CharacterBody3D
var world: Node


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("ADAPTIVE FAIL: " + msg)
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

	# re-learns: a moving average follows the latest behaviour both ways
	h.dodge = 0.0
	for i in 6:
		Enemy.learn("dodge", 1.0)
	if h.dodge < 0.8:
		return _fail("dodge not learned: %f" % h.dodge)
	for i in 6:
		Enemy.learn("dodge", 0.0)
	if h.dodge > 0.2:
		return _fail("dodge not unlearned: %f" % h.dodge)

	# dodge: a strike that meets a roll is learned; against a roller, strikes come late
	var e := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(0, 0, 1.2), PI, {"walk_speed": 0.0})
	await _frames(5)
	e._set_state(Enemy.State.CHASE)
	e._attack = 0.6
	player._roll_left = player.roll_time
	var before: float = h.dodge
	await _frames(3)
	if h.dodge <= before:
		return _fail("rolled-through strike not learned as a dodge")
	h.dodge = 1.0
	var late := false
	for i in 30:
		e._attack = -1.0
		e._cool = 0.0
		e._think(0.0)
		late = late or e._windup_now > e.windup * 1.2
	if not late:
		return _fail("no delayed strike against a roller")
	e.queue_free()
	player._roll_left = 0.0
	player.health = player.health_max

	# ranged: a hit from far away is learned; a ranged player is chased in a zigzag
	var far := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(0, 0, 12), PI, {"sight_range": 1.0})
	await _frames(5)
	h.ranged = 0.0
	far.hit(1.0, far.global_position + Vector3.UP)
	if h.ranged <= 0.0:
		return _fail("long-range hit not learned")
	h.ranged = 0.0
	if far._weave(12.0) != Vector3.ZERO:
		return _fail("weaving against a close-quarters player")
	h.ranged = 1.0
	var widest := 0.0
	for i in 8:  # over a zigzag period (its phase depends on the instance, so one instant can be a crossing)
		far._t_state = i * 0.36
		widest = maxf(widest, far._weave(12.0).length())
	if widest < 0.5:
		return _fail("no weave against a ranged player")
	far.queue_free()

	# stealth: a takedown is learned; a patrol then glances back over its shoulder
	h.stealth = 0.0
	var guard := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(30, 0, 0), 0.0, {"sight_range": 1.0})
	await _frames(5)
	guard.takedown()
	if h.stealth <= 0.0:
		return _fail("takedown not learned")
	h.stealth = 1.0
	var guard2 := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(30, 0, 6), 0.0, {"sight_range": 1.0})
	await _frames(2)
	guard2._glance_t = 0.0
	await _frames(40)
	if guard2._look == Vector3.ZERO or guard2._model.global_basis.z.dot(Vector3.BACK) > 0.0:
		return _fail("no glance back against a sneaky player")
	guard2.queue_free()

	# hide: a hider's searcher checks the nearest hiding spot; a runner's searches ahead of the run
	var spot := base + Vector3(-20, 0, 3)
	player.hidden_spots.append(spot)
	var s := Enemy.spawn(world, "res://models/char_marked_man.glb", base + Vector3(-28, 0, 0), 0.0, {"sight_range": 1.0})
	await _frames(5)
	h.hide = 1.0
	s._target = base + Vector3(-20, 0, 0)
	s._lost_player()
	if not spot in s._check:
		return _fail("hider: nearest hiding spot not searched")
	h.hide = 0.0
	s._check.clear()
	s._target = base + Vector3(-20, 0, 0)
	s._seen_vel = Vector3(4, 0, 0)
	s._lost_player()
	if not s._check.is_empty() or s._target.x <= base.x - 20 + 4.0:
		return _fail("runner: search not ahead of the run (%s)" % s._target)
	s.queue_free()
	player.hidden_spots.erase(spot)
	print("ADAPTIVE OK")
	quit(0)
