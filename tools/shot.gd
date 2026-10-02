extends SceneTree
## Renders one model (or the map) to a PNG so asset changes can be checked by eye.
##   flatpak run org.godotengine.Godot --path . --resolution 900x700 -s tools/shot.gd -- <model.glb|res://maps/x.tscn> <out.png> [cam_x cam_y cam_z look_x look_y look_z]
## A .glb is read straight from disk (absolute path, no import step needed). Models get a neutral key
## light; with no camera args the camera frames the model from the front-left. The map needs its models
## imported first: flatpak run org.godotengine.Godot --headless --path . --import


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var is_model := args[0].ends_with(".glb")
	var scene: Node
	if is_model:
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		if doc.append_from_file(args[0], state) != OK:
			push_error("cannot read " + args[0])
			quit(1)
			return
		scene = doc.generate_scene(state)
	else:
		scene = load(args[0]).instantiate()
	root.add_child(scene)
	var aabb := AABB()
	if is_model:
		for mi in scene.find_children("*", "MeshInstance3D", true, false):
			var box: AABB = mi.global_transform * mi.get_aabb()
			aabb = box if aabb.size == Vector3.ZERO else aabb.merge(box)
		var env := WorldEnvironment.new()
		env.environment = Environment.new()
		env.environment.background_mode = Environment.BG_COLOR
		env.environment.background_color = Color(0.18, 0.18, 0.2)
		env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
		env.environment.ambient_light_color = Color(0.55, 0.55, 0.6)
		root.add_child(env)
		var sun := DirectionalLight3D.new()
		sun.rotation_degrees = Vector3(-35, -30, 0)
		sun.light_energy = 1.4
		root.add_child(sun)
	for p in scene.find_children("Player", "", true, false):
		p.process_mode = Node.PROCESS_MODE_DISABLED
		for c in p.find_children("*", "Camera3D", true, false):
			c.current = false
	var cam := Camera3D.new()
	root.add_child(cam)
	if args.size() >= 8:
		cam.position = Vector3(float(args[2]), float(args[3]), float(args[4]))
		cam.look_at(Vector3(float(args[5]), float(args[6]), float(args[7])))
	else:
		var c := aabb.get_center()
		var r := aabb.size.length() * 0.9
		cam.position = c + Vector3(-0.45, 0.25, 1.0).normalized() * r
		cam.look_at(c)
	cam.current = true
	for i in 12:
		await process_frame
	root.get_viewport().get_texture().get_image().save_png(args[1])
	quit(0)
