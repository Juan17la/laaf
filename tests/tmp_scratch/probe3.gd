extends SceneTree
## Scratch: which candidate Chapter 3 points sit inside static geometry.
func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var world: Node = load("res://maps/hollowmere.tscn").instantiate()
	world.get_node("Chapter1").start_step = "free"
	root.add_child(world)
	for i in 20: await physics_frame
	var space: PhysicsDirectSpaceState3D = world.get_world_3d().direct_space_state
	var pts := {}
	for a in OS.get_cmdline_user_args():
		var p := a.split(":")
		var v := p[1].split(",")
		pts[p[0]] = Vector3(float(v[0]), float(v[1]), float(v[2]))
	for k in pts:
		var q := PhysicsShapeQueryParameters3D.new()
		var s := SphereShape3D.new()
		s.radius = 0.35
		q.shape = s
		q.transform = Transform3D(Basis(), pts[k])
		q.collision_mask = 1
		var hits: Array = space.intersect_shape(q, 4)
		var names := []
		for h in hits: names.append(str(h.collider.get_parent().name if h.collider.get_parent() else h.collider.name))
		# ground height
		var r: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(pts[k] + Vector3.UP * 20, pts[k] + Vector3.DOWN * 20, 1))
		print("%-14s %s %s ground=%s" % [k, "BLOCKED" if hits.size() else "ok", names, str(snappedf(r.position.y, 0.01)) if not r.is_empty() else "-"])
	quit(0)
