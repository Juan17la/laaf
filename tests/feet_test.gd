extends SceneTree
## Headless check: through a whole run cycle no character's planted foot sinks below the ground.
## flatpak run org.godotengine.Godot --headless --path . -s tests/feet_test.gd


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	for name in ["char_alex", "char_lucia", "char_owen", "char_marcus"]:
		var model: Node3D = load("res://models/%s.glb" % name).instantiate()
		root.add_child(model)
		var anim: Node = load("res://scripts/humanoid_anim.gd").new()
		model.add_child(anim)
		anim.speed = 5.2
		var rest := INF
		for k in ["L", "R"]:
			rest = minf(rest, model.to_local((model.find_child("Foot" + k, true, false) as Node3D).global_position).y)
		var low := INF
		for i in 120:
			anim._process(1.0 / 60.0)
			for k in ["L", "R"]:
				low = minf(low, model.to_local((model.find_child("Foot" + k, true, false) as Node3D).global_position).y)
		if low < rest - 0.002:
			push_error("FEET FAIL: %s ankle dips %.3f m below rest while running" % [name, rest - low])
			quit(1)
			return
		model.queue_free()
	print("FEET OK")
	quit(0)
