extends SceneTree
## Headless check for Lockpick and Fishing: scripted input to success, to failure and to quit;
## `done` must fire exactly once with sane args and the minigame must free itself.
## flatpak run org.godotengine.Godot --headless --path . -s tests/minigames_a_test.gd

const DT := 1.0 / 30.0
var _calls: Array = []


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	push_error("MINIGAMES FAIL: " + msg)
	quit(1)


func _release_all() -> void:
	for a in ["move_left", "move_right", "move_forward", "fire", "jump", "interact"]:
		Input.action_release(a)


## Drives mg._process by hand (fast, deterministic) until done fires; `policy` presses inputs each step.
func _drive(mg: Control, policy: Callable, max_steps := 6000) -> bool:
	mg.set_process(false)
	for i in max_steps:
		if not _calls.is_empty():
			break
		policy.call(mg)
		mg._process(DT)
	_release_all()
	await process_frame
	await process_frame
	return _calls.size() == 1 and not is_instance_valid(mg)


func _quit_via_esc(mg: Control) -> bool:
	var ev := InputEventAction.new()
	ev.action = &"ui_cancel"
	ev.pressed = true
	Input.parse_input_event(ev)
	await process_frame
	return await _drive(mg, func(_m): pass)


func _hold(action: String, on: bool) -> void:
	if on:
		Input.action_press(action)
	else:
		Input.action_release(action)


func _run() -> void:
	seed(7)
	var layer := CanvasLayer.new()
	root.add_child(layer)
	var rec := func(a = null, b = null): _calls.append([a, b])

	# lockpick: steer the pick onto each sweet spot and lift
	var lp := Lockpick.play(layer, 3)
	lp.done.connect(rec)
	await process_frame
	var pick_policy := func(m: Lockpick) -> void:
		var was := Input.is_action_pressed("fire")
		_release_all()
		if m._cur >= m.pins:
			return
		var err: float = m.sweet_spot(m._cur) - m.pick
		if absf(err) > 0.02:
			Input.action_press("move_right" if err > 0 else "move_left")
		elif m._armed or not was:
			Input.action_press("fire")
	if not await _drive(lp, pick_policy) or _calls[0][0] != true:
		return _fail("lockpick success: %s" % [_calls])
	_calls.clear()
	# lockpick: lifting far from the spot snaps every pick -> false
	lp = Lockpick.play(layer, 2)
	lp.done.connect(rec)
	await process_frame
	lp._sweet = [0.9, 0.9]
	lp.pick = 0.0
	var brute := func(m: Lockpick) -> void: _hold("fire", m._armed or not Input.is_action_pressed("fire"))
	if not await _drive(lp, brute) or _calls[0][0] != false:
		return _fail("lockpick break: %s" % [_calls])
	_calls.clear()
	lp = Lockpick.play(layer)
	lp.done.connect(rec)
	await process_frame
	if not await _quit_via_esc(lp) or _calls[0][0] != false:
		return _fail("lockpick quit: %s" % [_calls])
	_calls.clear()

	# fishing: charge + cast, hook on the bite, reel keeping tension mid-bar and leaning against the pull
	for legendary in [false, true]:
		var fi := Fishing.play(layer, legendary)
		fi.done.connect(rec)
		await process_frame
		var charge := [0]
		var fish_policy := func(m: Fishing) -> void:
			_release_all()
			match m.state:
				Fishing.CAST:
					charge[0] += 1
					_hold("fire", charge[0] > 1 and charge[0] < 25)
				Fishing.BITE:
					_hold("fire", not m._was_held)
				Fishing.REEL:
					Input.action_press("move_left" if m.pull > 0 else "move_right")
					_hold("fire", m.tension < 0.6)
		if not await _drive(fi, fish_policy):
			return _fail("fishing (legendary=%s) no single done: %s" % [legendary, _calls])
		var fish: String = _calls[0][0]
		var tokens: int = _calls[0][1]
		if fish == "" or tokens <= 0 or (legendary and (fish != "Old Tom" or tokens != 150)):
			return _fail("fishing (legendary=%s) bad catch: %s" % [legendary, _calls])
		print("caught %s for %d" % [fish, tokens])
		_calls.clear()
	# fishing: miss the bite -> got away; and quit
	var fi := Fishing.play(layer)
	fi.done.connect(rec)
	await process_frame
	var lazy := func(m: Fishing) -> void: _hold("fire", m.state == Fishing.CAST and not m._was_held)
	if not await _drive(fi, lazy) or _calls[0] != ["", 0]:
		return _fail("fishing miss: %s" % [_calls])
	_calls.clear()
	fi = Fishing.play(layer, true)
	fi.done.connect(rec)
	await process_frame
	if not await _quit_via_esc(fi) or _calls[0] != ["", 0]:
		return _fail("fishing quit: %s" % [_calls])
	print("MINIGAMES OK")
	quit(0)
