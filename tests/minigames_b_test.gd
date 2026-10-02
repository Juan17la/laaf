extends SceneTree
## Headless check of HiLo and MothRun: input drives them, `done` fires exactly once with sane args.
## flatpak run org.godotengine.Godot --headless --path . -s tests/minigames_b_test.gd

var layer: CanvasLayer
var calls: Array = []


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("MINIGAMES_B FAIL: " + msg)
	quit(1)


func _key(action: String) -> void:
	for pressed in [true, false]:
		var e := InputEventAction.new()
		e.action = action
		e.pressed = pressed
		Input.parse_input_event(e)
	await process_frame
	await process_frame


func _frames(n: int) -> void:
	for i in n:
		await process_frame


func _run() -> void:
	layer = CanvasLayer.new()
	root.add_child(layer)
	# HiLo: quit at once → lost, no tokens moved
	var h := HiLo.play(layer, 3, 30)
	h.done.connect(func(w: bool, t: int) -> void: calls.append([w, t]))
	await _frames(3)
	await _key("ui_cancel")
	await create_timer(0.7).timeout
	if calls != [[false, 0]] or is_instance_valid(h):
		return _fail("hilo cancel: %s" % [calls])
	# HiLo: play sensibly (higher on low cards), cash out after one right call; 1 win needed
	calls.clear()
	h = HiLo.play(layer, 1, 30)
	h.done.connect(func(w: bool, t: int) -> void: calls.append([w, t]))
	await _frames(3)
	for i in 400:
		if not is_instance_valid(h) or h._phase == "out":
			break
		match h._phase:
			"bet", "end": await _key("interact")
			"guess": await _key("interact" if h._chain > 0 else ("move_forward" if h._cur <= 7 else "move_back"))
			_: await process_frame
	await create_timer(0.7).timeout
	if calls.size() != 1 or is_instance_valid(h):
		return _fail("hilo play: %s" % [calls])
	var won: bool = calls[0][0]
	var delta: int = calls[0][1]
	if delta < -30 or delta > 100:  # winning 3 hands can still net a loss after lost hands
		return _fail("hilo delta: %s" % [calls])
	print("hilo ok: ", calls)
	# MothRun: Esc mid-run → 0
	calls.clear()
	var m := MothRun.play(layer)
	m.done.connect(func(s: int) -> void: calls.append(s))
	Input.action_press("move_back")
	await create_timer(1.6).timeout
	Input.action_release("move_back")
	if m._y <= MothRun.SH / 2.0 or m._score <= 0.0:
		return _fail("moth did not move/score: y %s score %s" % [m._y, m._score])
	await _key("ui_cancel")
	await create_timer(0.7).timeout
	if calls != [0] or is_instance_valid(m):
		return _fail("moth cancel: %s" % [calls])
	# MothRun: lose all lives past 10,000 → secret screen, E leaves with the score
	calls.clear()
	m = MothRun.play(layer, true)
	m.done.connect(func(s: int) -> void: calls.append(s))
	await _frames(5)
	m._score = 10500.0
	for i in 3:
		m.hurt()
	await _frames(3)
	if m._phase != "over":
		return _fail("moth not over")
	await _key("interact")
	await _key("interact")
	await create_timer(0.7).timeout
	if calls != [10500] or is_instance_valid(m):
		return _fail("moth over: %s" % [calls])
	print("MINIGAMES_B OK")
	quit(0)
