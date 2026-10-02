extends SceneTree
## Headless check of handling and staging: arms reach the weapon grips (IK), fists / axe / an empty gun
## strike, the bow looses a real arrow, shotgun pellets add up, nothing is used or filmed through a wall,
## the stand-in never stands in one, an Actor takes an item where it lies, the clinic's roof hatch is indoors.
## flatpak run org.godotengine.Godot --headless --path . -s tests/handling_test.gd


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("HANDLING FAIL: " + msg)
	quit(1)


func _frames(n: int) -> void:
	for i in n:
		await physics_frame


func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "free"
	root.add_child(world)
	var d: Chapter1Director = world.get_node("Chapter1")
	var player: CharacterBody3D = world.get_node("Player")
	await _frames(30)
	var w: Weapons = player.weapons
	var space := (world as Node3D).get_world_3d().direct_space_state
	var open := Vector3(0, 0.1, 30)  # the square's south entrance: flat and clear
	player.respawn(open, PI)
	await _frames(5)

	# shotgun shouldered: both hands on it, the right one actually at its grip
	w.give("shotgun", 6)
	w.swap(w.owned.find("shotgun"))
	await _frames(30)
	player.anim.aim = 1.0
	for i in 20:
		player._hold(0.1)
		await process_frame
	if player.anim.ik_w.R < 0.99 or player.anim.ik_w.L < 0.99:
		return _fail("shotgun not held in both hands: %s" % player.anim.ik_w)
	var want: Vector3 = (player.model.global_transform * (player.anim.ik.R as Transform3D)).origin
	var hand: Node3D = player.model.find_child("HandR", true, false)
	if hand.global_position.distance_to(want) > 0.08:
		return _fail("right hand %.2f m off the shotgun grip" % hand.global_position.distance_to(want))
	player.anim.aim = 0.0

	# pellets add up: point blank on a Marked One
	var e := Enemy.spawn(d, "res://models/char_marked_man.glb", player.global_position + Vector3(0, 0, -2.5), 0.0,
		{"max_health": 500.0})
	await _frames(3)
	var chest := player.global_position + Vector3.UP * 1.3
	var hp := e.health
	var shot: Dictionary = w.shoot(space, chest, (e.global_position + Vector3.UP * 1.2 - chest).normalized(),
		[player.get_rid()], 0.3)
	if hp - e.health <= Weapons.GUNS.shotgun.damage * 1.5:
		return _fail("shotgun pellets didn't add up: %.0f damage" % (hp - e.health))
	if shot.pellets != 7:
		return _fail("shotgun cast %s pellets" % shot.pellets)

	# fists: nothing in hand, the jab lands
	e.health = 500.0
	e.reset_to(player.global_position + Vector3(0, 0, -1.0))
	player.model.rotation.y = PI
	player.pivot.rotation.y = 0.0  # camera behind, looking -Z at it
	await _frames(3)
	w.current = 99
	if w.gun() != "" or w.spec().style != "jab":
		return _fail("empty hands aren't fists")
	player._melee()
	await _frames(40)
	if e.health >= 500.0:
		return _fail("the punch didn't land")
	# an empty gun strikes instead of clicking
	w.give("revolver", 0)
	w.loaded.revolver = 0  # (free roam already armed him)
	w.reserve.revolver = 0
	w.current = w.owned.find("revolver")
	if not w.dry():
		return _fail("a revolver with no rounds isn't dry")
	hp = e.health
	player.stamina = player.stamina_max
	player._melee()
	await _frames(45)
	if e.health >= hp:
		return _fail("the gun-butt bash didn't land")
	# the axe hits hard and staggers
	w.give("axe")
	w.current = w.owned.find("axe")
	hp = e.health
	player.stamina = player.stamina_max
	player._melee()
	await _frames(60)
	if hp - e.health < 50.0:
		return _fail("the axe hit for %.0f" % (hp - e.health))
	e.queue_free()

	# the bow looses a real arrow, then nocks the next
	w.give("bow", 3)
	w.current = w.owned.find("bow")
	await _frames(50)
	var before := world.find_children("*", "Node3D", true, false).filter(func(n: Node) -> bool: return n is Arrow).size()
	player._loose()
	await process_frame
	var arrows := world.find_children("*", "Node3D", true, false).filter(func(n: Node) -> bool: return n is Arrow).size()
	if arrows != before + 1 or w.loaded.bow != 0:
		return _fail("no arrow loosed (%d → %d, %d on the string)" % [before, arrows, w.loaded.bow])
	await _frames(70)
	if w.loaded.bow != 1:
		return _fail("the next arrow wasn't nocked")

	# a wall: the front of Grady's store, west of its door, with the open square in front
	var probe := Vector3(9.0, 1.2, -12.0)
	var wall := space.intersect_ray(PhysicsRayQueryParameters3D.create(probe, probe + Vector3(0, 0, -10), 1,
		[player.get_rid()]))
	if not wall or absf(wall.normal.y) > 0.2:
		return _fail("no store wall found")
	var n: Vector3 = wall.normal
	var front: Vector3 = wall.position + n * 0.9
	front.y = 0.1
	player.respawn(front, 0.0)
	await _frames(5)
	# nothing is used through it
	var behind := Interactable.make(d, wall.position - n * 0.6, "Behind the wall", func(_b: Node) -> void: pass)
	await process_frame
	if player.interact_target() == behind:
		return _fail("interacting through a wall")
	behind.queue_free()
	# the stand-in never stands in it, and a spot asked for behind it stays on the player's side
	var inside: Vector3 = wall.position - n * 0.1
	inside.y = 0.0
	var s := d.spot(inside, player.global_position)
	if d._stand(s) == Vector3.INF or d._solid(player.global_position + Vector3.UP * 1.2, s + Vector3.UP * 1.2):
		return _fail("spot() put Alex in / behind the wall: %s" % s)
	var near := d.near(wall.position - n * 1.5, 1.0)
	if d._solid(player.global_position + Vector3.UP * 1.3, near + Vector3.UP * 1.3):
		return _fail("near() crossed the wall: %s" % near)
	# a close shot from behind the wall swings round to a clear view
	d.shot(wall.position - n * 0.8 + Vector3.UP * 1.5, front + Vector3.UP * 1.4)
	if not d._lens_clear(front + Vector3.UP * 1.4, d.cam.global_position):
		return _fail("the camera films through the wall from %s" % d.cam.global_position)

	# an Actor takes an item where it lies (no copy from nowhere)
	player.respawn(open, PI)
	await _frames(5)
	var a := d.actor("res://models/char_alex.glb", open + Vector3(3, 0, 0), 0.0)
	var note: Node3D = Interactable.ItemFx.item("note")
	d.add_child(note)
	note.global_position = a.global_position + Vector3(0.4, 0.0, 0.6)
	await a.take(note)
	if note.get_parent() != a.model.find_child("HandR", true, false) or a.anim.ik_w.R <= 0.0:
		return _fail("the actor didn't take the note into its hand")
	a.let_go()
	await process_frame
	if is_instance_valid(note):
		return _fail("let_go kept the note")

	# chapter 2: coming down off the clinic roof lands indoors
	var up := space.intersect_ray(PhysicsRayQueryParameters3D.create(Chapter2Director.HATCH + Vector3.UP * 0.5,
		Chapter2Director.HATCH + Vector3.UP * 6.0, 1))
	if not up or d._stand(Chapter2Director.HATCH) == Vector3.INF:
		return _fail("the clinic roof hatch isn't a clear spot indoors")
	print("HANDLING OK")
	quit(0)
