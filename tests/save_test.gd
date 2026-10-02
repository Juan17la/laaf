extends SceneTree
## Headless check of saving (scripts/game.gd): a Chapter 2 run is saved to a slot, then loaded into a fresh
## world: the same step starts again with the saved flags, inventory and weapons. Also the difficulty
## multipliers reach enemies, and runs outside the menu ("" mode) never autosave.
## flatpak run org.godotengine.Godot --headless --path . -s tests/save_test.gd


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("SAVE FAIL: " + msg)
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
	var g: Node = G.game()  # the autoload is there (only its global name isn't, under -s)
	if not g:
		g = load("res://scripts/game.gd").new()
		g.name = "Game"
		root.add_child(g)
	var autos: int = g.saves().filter(func(e: Array) -> bool: return str(e[0]).begins_with("auto")).size()
	var world := _world("zones")
	await _frames(90)
	var ch2: Chapter2Director = world.get_node("Chapter2")
	var player: CharacterBody3D = world.get_node("Player")
	if g.director != ch2 or ch2.step != "zones":
		return _fail("Game didn't follow the running director / step")
	if g.saves().filter(func(e: Array) -> bool: return str(e[0]).begins_with("auto")).size() != autos:
		return _fail("a non-story run autosaved")
	ch2.flags.key_parts = 2
	ch2.flags.evidence = [3, 9]
	player.bottles = 5
	player.teas = 1
	player.weapons.give("shotgun", 9)
	player.weapons.current = player.weapons.owned.find("shotgun")
	if not g.save_game("test_slot", "Test"):
		return _fail("save_game failed")
	var s: Dictionary = g.load_save("test_slot")
	if s.is_empty() or s.step != "zones" or s.chapter != 2:
		return _fail("save read back wrong: %s" % s)
	world.queue_free()
	await _frames(5)
	# load it: a fresh world picks the save up from Game.pending
	g.pending = s.duplicate(true)
	g.loading = true
	world = _world("intro")
	await _frames(90)
	ch2 = world.get_node("Chapter2")
	player = world.get_node("Player")
	var w: Weapons = player.weapons
	if ch2.step != "zones":
		return _fail("loaded into step '%s'" % ch2.step)
	if int(ch2.flags.key_parts) != 2 or ch2.flags.evidence != [3, 9]:
		return _fail("flags not restored: %s" % ch2.flags)
	if player.bottles < 5 or player.teas != 1 or w.gun() != "shotgun" or w.reserve.shotgun + w.loaded.shotgun != 9:
		return _fail("inventory not restored: bottles %d teas %d gun %s" % [player.bottles, player.teas, w.gun()])
	DirAccess.remove_absolute("user://saves/test_slot.sav")
	# difficulty: Hard enemies are tougher
	g.difficulty = 2
	var e := Enemy.spawn(world, "res://models/char_marked_man.glb", player.global_position + Vector3(0, 0, 30), 0.0,
		{"max_health": 100.0})
	await _frames(2)
	if absf(e.max_health - 130.0) > 0.1:
		return _fail("Hard didn't toughen enemies: %.0f" % e.max_health)
	g.difficulty = 1
	print("SAVE OK")
	quit(0)
