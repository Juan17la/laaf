extends SceneTree
## Headless check of item identity (scripts/item_fx.gd): every kind builds a model (or stand-in) + tell,
## a pickup's item flies to the player and goes, one-shot bursts free themselves, guns have muzzles, the carried
## battery has a model, reloading the revolver drops brass.
## flatpak run org.godotengine.Godot --headless --path . -s tests/items_test.gd

const ItemFx := preload("res://scripts/item_fx.gd")


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("ITEMS FAIL: " + msg)
	quit(1)


func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "free"
	root.add_child(world)
	var player: CharacterBody3D = world.get_node("Player")
	for i in 30:
		await physics_frame
	for kind in ItemFx.ITEMS:
		var it: Node3D = ItemFx.item(kind)
		world.add_child(it)
		var fx := it.find_children("*", "CPUParticles3D", true, false)
		if fx.size() != ItemFx.ITEMS[kind][0].size():
			return _fail("%s: %d tells" % [kind, fx.size()])
		if kind != "radio" and it.get_child_count() == 0:
			return _fail("%s: no model" % kind)
		it.queue_free()
	# a pickup: the item hovers with it, and is gone once taken
	var got := [false]
	var p := Interactable.make(world, player.global_position + Vector3(0, 0.3, 30), "Ammo",
		func(_b: Node) -> void: got[0] = true, Color(0.9, 0.8, 0.4), true, "ammo_box")
	await process_frame
	var item: Node3D = p._item
	if not is_instance_valid(item) or item.position.y > 0.0:
		return _fail("pickup item missing / not hovering")
	p.interact(player)
	await process_frame
	if not got[0] or not is_instance_valid(item):
		return _fail("pickup item should fly to the player, not vanish")
	for i in 30:
		await process_frame
	if is_instance_valid(item):
		return _fail("pickup item not removed when taken")
	# one-shot bursts clean up after themselves
	ItemFx.burst(world, player.global_position, "muzzle")
	var n := world.find_children("*", "CPUParticles3D", false, false).size()
	for i in 40:
		await process_frame
	if world.find_children("*", "CPUParticles3D", false, false).size() >= n:
		return _fail("burst not freed")
	# guns: both muzzles are ahead of the grip (down the hand's -Y)
	player.weapons.give("revolver", 12)
	player.weapons.give("flare", 2)
	for g in ["revolver", "flare"]:
		var m: Node3D = player._gun_meshes.get(g)
		if not m:
			return _fail("no %s mesh" % g)
		var tip: Vector3 = (m.get_parent() as Node3D).to_local(m.to_global(player.MUZZLE[g]))
		if tip.y > -0.2:
			return _fail("%s muzzle not down the hand: %s" % [g, tip])
	# reload after two shots: two casings
	var before := world.find_children("*", "CPUParticles3D", false, false).size()
	player.weapons.loaded.revolver = 4
	player.weapons.reload()
	var drop := world.find_children("*", "CPUParticles3D", false, false)
	if drop.size() != before + 1 or drop[-1].amount != 2:
		return _fail("reload did not drop 2 casings")
	player.carry("battery")
	if not player._carry_mesh or player._carry_mesh.find_children("*", "CPUParticles3D", true, false).is_empty():
		return _fail("carried battery has no model / sparks")
	player.drop_carry()
	print("ITEMS OK")
	quit(0)
