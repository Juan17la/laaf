extends SceneTree
## Headless check: map loads, player stands at spawn, walking moves, sprint drains stamina.
## flatpak run org.godotengine.Godot --headless --path . -s tests/smoke_test.gd


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("SMOKE FAIL: " + msg)
	quit(1)


func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "free"  # no cinematic: free roam
	root.add_child(world)
	var player: CharacterBody3D = world.get_node("Player")
	for i in 90:
		await physics_frame
	if not player.is_on_floor() or player.global_position.y < -0.5:
		return _fail("player not on floor at spawn: %s" % player.global_position)
	var start := player.global_position
	Input.action_press("move_forward")
	for i in 60:
		await physics_frame
	if player.global_position.distance_to(start) < 1.0:
		return _fail("move_forward did not move the player")
	var stamina: float = player.stamina
	Input.action_press("sprint")
	for i in 60:
		await physics_frame
	Input.action_release("sprint")
	Input.action_release("move_forward")
	if player.stamina >= stamina:
		return _fail("sprint did not drain stamina")
	print("SMOKE OK pos=%s stamina=%.1f" % [player.global_position, player.stamina])
	quit(0)
