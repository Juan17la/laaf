class_name HumanoidAnim
extends Node
const ItemFx := preload("res://scripts/item_fx.gd")
## Procedural animation for the shared character rig (tools/rig.py joint names).
## Set speed / crouching / roll / look from the owner each frame. A limb hanging
## down rotated by -x swings forward (+Z), +x swings back.

@export var model_path: NodePath = ^".."
@export var run_speed := 5.2
## Gallery/showcase: cycles idle → walk → run by itself.
@export var demo := false

var speed := 0.0
var crouching := false
var roll := -1.0  ## 0..1 while dodge-rolling, -1 otherwise
var look := Vector2.ZERO  ## head yaw / pitch in radians, relative to the body
var airborne := false  ## jumping / falling: legs tuck
var sliding := false  ## knee slide: hips drop, lead leg out, lean back
var aim := 0.0  ## 0..1 right arm raised along aim_pitch (gun hand), left arm supports
var aim_pitch := 0.0  ## radians, + = up
var aim_block := 0.0  ## 0..1 wall right in front of the muzzle: gun tucks to low ready instead of poking through
var stance := 0.0  ## spine turn (radians) while aiming: long guns and the bow blade the shoulders to the target
var throw := -1.0  ## 0..1 left-hand overhand throw (windup until 0.45, release after), -1 = none
var recoil := 0.0  ## 0..1, decays by itself; set to 1 on a shot
var attack := -1.0  ## 0..1 overhead swing (windup until 0.6, strike after), -1 = none
var flinch := 0.0  ## 0..1, decays by itself; set to 1 when hit
var strike := -1.0  ## 0..1 a melee strike's body motion (the hands are IK'd by the player), -1 = none
var strike_style := ""  ## "jab_r" / "jab_l" (fists), "bash" (gun butt), "swing" (bat), "chop" (axe)
## Arm IK: hand bone poses in MODEL space (rig root: +Z front, +X the character's left), blended in by ik_w.
## Whoever holds something (player weapons, Actor.hold / take) sets them; solved last, over every other pose.
var ik := {}
var ik_w := {"R": 0.0, "L": 0.0}
var ik_pole := {}  ## "R" / "L" → model-space direction the elbow bends toward (default: down, out, back)
## Holding things (cutscenes; any character): hold() puts an item in the right hand by its shape and the arm
## IK keeps it where the pose wants it: "show" up before the eyes, "give" held out (also while the "give"
## gesture plays), "reach" the hand onto reach_to (a world pose), "" down by the side. Actor.take() stages a
## pickup with these. The arm lets go on its own once the item is freed or taken by someone else.
var held: Node3D
var hold_pose := ""
var reach_to := Transform3D()
var _holding := false  ## this anim drives ik.R for a held item (the player's weapons drive it otherwise)
## Cinematic body language (Actor.gesture): "" or one of point, wave, give, reach, hand_to_face,
## clutch_hand, arms_crossed, shrug, nod, shake_head, lean, cower, raise_weapon, window_press,
## hands_up, beckon, look_around, slump, frenzy (a charging attacker: stabbing overhead, clawing, hunched).
## Blends in/out over ~0.3 s.
var gesture := ""
var _g_amt := 0.0
var _g_last := ""
var _g_time := 0.0  ## seconds since the gesture started (loops like nod / shrug settle down)

var _j := {}
var _rest := {}
var _phase := 0.0
var _time := 0.0
var _crouch := 0.0


func _ready() -> void:
	var model := get_node(model_path)
	for joint in ["Hips", "Spine", "Head", "UpperArmL", "ForearmL", "HandL", "UpperArmR", "ForearmR",
			"HandR", "ThighL", "ShinL", "FootL", "ThighR", "ShinR", "FootR"]:
		var n := model.find_child(joint, true, false) as Node3D
		if n:
			_j[joint] = n
			_rest[joint] = n.position
	_time = randf() * 10.0


func _process(delta: float) -> void:
	if _j.size() < 15:
		return
	_time += delta
	if demo:
		var cycle := fmod(_time, 12.0)
		speed = 0.0 if cycle < 4.0 else (1.6 if cycle < 8.0 else run_speed)
		look = Vector2(sin(_time * 0.7) * 0.6, sin(_time * 0.45) * 0.2) if cycle < 4.0 else Vector2.ZERO
	var amt := clampf(speed / run_speed, 0.0, 1.0)
	var run := clampf((speed - 2.5) / (run_speed - 2.5), 0.0, 1.0)
	_phase += delta * (2.0 + speed * 1.5) * signf(speed)
	_crouch = move_toward(_crouch, 1.0 if crouching else 0.0, delta * 5.0)
	var s := sin(_phase)
	var c := cos(_phase)
	var breath := sin(_time * 1.8)

	# legs: thigh swing, knee bends on the forward (lifting) half, foot stays level
	var swing := (0.35 + 0.35 * run) * amt
	for side in [["L", 1.0], ["R", -1.0]]:
		var k: String = side[0]
		var ph: float = side[1]
		var thigh := -s * ph * swing - 1.1 * _crouch
		var knee := maxf(0.0, -c * ph) * (0.6 + 0.7 * run) * amt + 0.15 * amt + 2.3 * _crouch
		_j["Thigh" + k].rotation = Vector3(thigh, 0, 0.03 * ph)
		_j["Shin" + k].rotation.x = knee
		_j["Foot" + k].rotation.x = -(thigh + knee) * 0.7 + 0.2 * _crouch

	# hips: bob twice per stride, drop when crouching
	var hips: Node3D = _j["Hips"]
	hips.position = _rest["Hips"] + Vector3(0, -absf(c) * 0.04 * amt - 0.5 * _crouch, 0)
	hips.rotation = Vector3(0, s * 0.12 * amt, s * 0.03 * amt)

	# spine: counter-twist, lean into runs and crouch, breathe when idle
	var spine: Node3D = _j["Spine"]
	spine.rotation = Vector3(0.05 * amt + 0.25 * run + 0.55 * _crouch + breath * 0.015 * (1.0 - amt),
			-s * 0.2 * amt, 0)

	# arms: swing opposite the legs, elbows bend more when running, slightly out from the body
	var arm_swing := (0.3 + 0.5 * run) * amt
	for side in [["L", 1.0], ["R", -1.0]]:
		var k: String = side[0]
		var ph: float = side[1]
		_j["UpperArm" + k].rotation = Vector3(s * ph * arm_swing - 0.3 * _crouch, 0,
				ph * (0.1 + 0.02 * breath * (1.0 - amt)))
		# elbow bends most while the arm is swinging forward (upper arm rotation < 0)
		# whole rotations (not just .x): the arm IK leaves twist on these that must not linger
		_j["Forearm" + k].rotation = Vector3(-0.15 - 0.2 * amt - 0.55 * run - (0.3 + 0.6 * run) * maxf(0.0, -s * ph) * amt, 0, 0)
		_j["Hand" + k].rotation = Vector3(-0.1 * amt, 0, 0)

	# head: look target, cancel the spine twist so the gaze stays forward
	var head: Node3D = _j["Head"]
	head.rotation = Vector3(clampf(look.y, -0.6, 0.6) - 0.2 * run - 0.45 * _crouch + sin(_time * 0.9) * 0.02,
			clampf(look.x, -1.1, 1.1) + s * 0.2 * amt, 0)

	# jump / fall: knees up, arms out for balance
	if airborne:
		for side in [["L", 1.0], ["R", -1.0]]:
			var k: String = side[0]
			var ph: float = side[1]
			_j["Thigh" + k].rotation.x = -0.9 if ph > 0 else -0.3
			_j["Shin" + k].rotation.x = 1.2 if ph > 0 else 0.6
			_j["UpperArm" + k].rotation = Vector3(-0.5, 0, ph * 0.6)

	# knee slide: lead (left) leg straight out, right knee folded under, lean back
	if sliding:
		hips.position.y = _rest["Hips"].y * 0.55
		spine.rotation.x = -0.5
		head.rotation.x += 0.35  # chin down: eyes stay on where he's sliding
		_j["ThighL"].rotation.x = -1.05
		_j["ShinL"].rotation.x = 0.1
		_j["ThighR"].rotation.x = -0.35
		_j["ShinR"].rotation.x = 2.2
		_j["FootL"].rotation.x = 0.3
		_j["UpperArmL"].rotation = Vector3(-0.3, 0, 0.9)

	# gun arms: two-hand isosceles grip, both arms converge in front of the chest (wrists meet), the
	# right wrist turns the gun back onto the aim line; recoil kicks both hands up. Near a wall
	# (aim_block) the gun drops to low ready and pulls in instead of poking through it.
	recoil = move_toward(recoil, 0.0, delta * 6.0)
	if aim > 0.0:
		var arm_x := lerpf(-PI / 2.0 - aim_pitch, -0.55, aim_block) - 0.3 * recoil
		var bend := -0.2 - 0.9 * aim_block - 0.25 * recoil
		_pose("UpperArmR", Vector3(arm_x, 0.4, -0.05), aim)
		_pose("ForearmR", Vector3(bend, 0, 0), aim)
		_pose("HandR", Vector3(0.2 - 0.3 * recoil, 0, -0.35), aim)
		_pose("UpperArmL", Vector3(arm_x, -0.3, 0.0), aim)
		_pose("ForearmL", Vector3(bend + 0.2, 0, 0), aim)
		_pose("HandL", Vector3(0.1, 0, 0.3), aim)
		spine.rotation.y = lerpf(spine.rotation.y, stance, aim)
		head.rotation.y -= stance * aim  # eyes stay on the target over the bladed shoulders

	# overhand throw with the free (left) hand: cock it behind the head, whip it forward, follow through
	if throw >= 0.0:
		var wind := clampf(throw / 0.45, 0.0, 1.0)
		var rel := clampf((throw - 0.45) / 0.55, 0.0, 1.0)
		var w := minf(wind * 2.0, 1.0) * (1.0 - maxf(rel - 0.7, 0.0) / 0.3)  # blend in fast, out at the end
		_pose("UpperArmL", Vector3(lerpf(-3.3, -1.1, rel), 0, lerpf(0.35, -0.2, rel)), w)
		_pose("ForearmL", Vector3(lerpf(-1.7, -0.15, rel), 0, 0), w)
		_pose("HandL", Vector3(lerpf(0.5, -0.4, rel), 0, 0), w)
		spine.rotation.y += lerpf(0.35, -0.3, rel) * w  # shoulders load, then turn through
		spine.rotation.x += lerpf(-0.1, 0.25, rel) * w

	# overhead strike (hunters, Marked Ones): raise both arms, then chop down
	if attack >= 0.0:
		var up := attack / 0.6 if attack < 0.6 else 1.0 - (attack - 0.6) / 0.4 * 1.6
		for k in ["L", "R"]:
			_j["UpperArm" + k].rotation.x = lerpf(-0.3, -2.8, clampf(up, -0.2, 1.0))
			_j["Forearm" + k].rotation.x = -0.6
		spine.rotation.x = 0.35 - 0.5 * clampf(up, 0.0, 1.0)

	# cinematic gestures, blended over whatever the body was doing
	if gesture != "":
		if gesture != _g_last or _g_amt <= 0.0:
			_g_time = 0.0
		_g_last = gesture
	_g_time += delta
	_g_amt = move_toward(_g_amt, 1.0 if gesture != "" else 0.0, delta * 3.5)
	if _g_amt > 0.0:
		_gesture(_g_last, _g_amt)

	# hit reaction: snap back
	flinch = move_toward(flinch, 0.0, delta * 4.0)
	if flinch > 0.0:
		spine.rotation.x -= 0.5 * flinch
		head.rotation.x -= 0.4 * flinch
		head.rotation.y += 0.3 * flinch  # turns the face away from the blow
		if aim <= 0.0 and throw < 0.0:  # guarding hands, unless they're holding the gun on target
			for k in ["L", "R"]:
				_j["UpperArm" + k].rotation.x -= 0.9 * flinch
				_j["Forearm" + k].rotation.x -= 1.1 * flinch

	# melee: the hips and shoulders drive the blow (hands follow their IK targets)
	if strike >= 0.0:
		var hit := sin(clampf(strike, 0.0, 1.0) * PI)
		match strike_style:
			"jab_r", "bash":
				spine.rotation.y += lerpf(0.25, -0.45, clampf(strike * 2.5, 0.0, 1.0)) * hit
				spine.rotation.x += 0.15 * hit
			"jab_l":
				spine.rotation.y += lerpf(-0.25, 0.4, clampf(strike * 2.5, 0.0, 1.0)) * hit
				spine.rotation.x += 0.12 * hit
			"swing":
				spine.rotation.y += lerpf(0.7, -0.8, clampf((strike - 0.15) / 0.5, 0.0, 1.0))
				spine.rotation.x += 0.15 * hit
			"chop":
				spine.rotation.x += lerpf(-0.3, 0.55, clampf((strike - 0.2) / 0.4, 0.0, 1.0))
		for k in ["L", "R"]:  # step into it
			_j["Thigh" + k].rotation.x += (-0.35 if k == ("L" if strike_style != "jab_l" else "R") else 0.15) * hit

	# dodge roll: tuck and spin around the hips
	if roll >= 0.0:
		hips.rotation.x = TAU * roll
		hips.position.y = _rest["Hips"].y * 0.55
		spine.rotation.x = 0.8
		head.rotation.x = 0.5
		for k in ["L", "R"]:
			_j["Thigh" + k].rotation.x = -1.8
			_j["Shin" + k].rotation.x = 2.2
			_j["UpperArm" + k].rotation.x = -1.2
			_j["Forearm" + k].rotation.x = -1.4

	_pose_held(delta)
	if roll < 0.0:
		for k in ["R", "L"]:
			if ik_w[k] > 0.0 and ik.has(k):
				_reach(k, ik[k], ik_w[k])


func crouch_amount() -> float:
	return _crouch


static func of(n: Node) -> HumanoidAnim:
	## The animator of whoever n belongs to (n: a bone, a model, an Actor, an Enemy).
	while n:
		for c in n.get_children():
			if c is HumanoidAnim:
				return c
		n = n.get_parent()
	return null


func hold(item: Node3D, pose := "show") -> Node3D:
	## Puts item in the right hand (where by its shape: ItemFx.grip) and poses the arm. Replaces what was held.
	if held and held != item and is_instance_valid(held):
		held.queue_free()
	var hand: Node3D = _j["HandR"]
	var g := ItemFx.grip(item)
	if item.is_inside_tree():
		item.reparent(hand, false)
	else:
		hand.add_child(item)
	item.transform = g
	item.set_meta("claimed", true)
	for p in item.find_children("*", "CPUParticles3D", true, false):  # its idle tell stays in the world
		p.queue_free()
	held = item
	hold_pose = pose
	return item


func let_go() -> void:
	## Drops (frees) what the right hand holds; the arm returns to the animation.
	if held and is_instance_valid(held):
		held.queue_free()
	held = null
	hold_pose = ""


func _pose_held(delta: float) -> void:
	if held and (not is_instance_valid(held) or held.get_parent() != _j["HandR"]):
		held = null  # freed, or someone took it
		if hold_pose != "reach":
			hold_pose = ""
	var pose := "give" if gesture == "give" and held else hold_pose
	if pose in ["show", "give", "talk"] and not held:
		pose = ""
	if pose == "":
		if _holding:
			ik_w.R = move_toward(ik_w.R, 0.0, delta * 4.0)
			_holding = ik_w.R > 0.0
		return
	var model := get_node(model_path) as Node3D
	var want: Transform3D
	if pose == "reach":
		want = model.global_transform.affine_inverse() * reach_to
	else:
		want = _item_pose(pose) * held.transform.affine_inverse()
	ik.R = want if not _holding else (ik.R as Transform3D).interpolate_with(want, minf(delta * 7.0, 1.0))
	ik_w.R = move_toward(ik_w.R, 1.0, delta * 3.0)
	_holding = true


func _item_pose(pose: String) -> Transform3D:
	## Where the held item goes (model space; the character faces +Z): "show" up before the eyes with its face
	## (+Y) turned to them and its top (-Z) up; "give" held out at chest height, upright, its top toward the other
	## person; "talk" at the mouth (a radio mic, a phone), top up.
	if not held.has_meta("bounds"):
		held.set_meta("bounds", ItemFx.bounds(held))
	var c: Vector3 = (held.get_meta("bounds") as AABB).get_center()
	var at: Vector3 = {"show": Vector3(-0.07, 1.28, 0.34), "give": Vector3(-0.08, 1.12, 0.5),
		"talk": Vector3(-0.07, 1.52, 0.15)}[pose]
	var b := Basis(Vector3.UP, PI)  # item -Z (its top / business end) forward, toward whoever's in front
	if pose == "talk":
		b = Basis(Vector3.RIGHT, PI / 2.0) * Basis(Vector3.UP, PI)  # top up, face (+Y) to the mouth
	elif pose == "show":
		var y := (Vector3(0, 1.62, 0.06) - at).normalized()
		var z := (Vector3.DOWN - y * Vector3.DOWN.dot(y)).normalized()
		b = Basis(y.cross(z), y, z)
	return Transform3D(b, at - b * c)


func _reach(k: String, target_local: Transform3D, w: float) -> void:
	## Two-bone arm IK: the wrist onto target.origin (elbow bent down and out), the hand takes target.basis.
	## Limbs hang along their -Y; each bone turns by the shortest arc from its parent's hanging pose, so the
	## twist stays natural. w < 1 blends from the animated pose.
	var model := get_node(model_path) as Node3D
	var target := model.global_transform * target_local
	var up: Node3D = _j["UpperArm" + k]
	var fo: Node3D = _j["Forearm" + k]
	var ha: Node3D = _j["Hand" + k]
	var s := up.global_position
	var l1 := s.distance_to(fo.global_position)
	var l2 := fo.global_position.distance_to(ha.global_position)
	var to := target.origin - s
	var d := clampf(to.length(), absf(l1 - l2) + 0.001, (l1 + l2) * 0.999)
	var dir := to.normalized()
	var mb := model.global_basis.orthonormalized()
	var pole: Vector3 = mb * (ik_pole[k] as Vector3 if ik_pole.has(k) else Vector3(-0.6 if k == "R" else 0.6, -1.0, -0.4))
	pole = pole - dir * pole.dot(dir)
	pole = pole.normalized() if pole.length() > 0.001 else mb.y * -1.0
	var a := (l1 * l1 - l2 * l2 + d * d) / (2.0 * d)
	var elbow := s + dir * a + pole * sqrt(maxf(l1 * l1 - a * a, 0.0))
	_point(up, elbow, w)
	_point(fo, target.origin, w)
	var local := (fo.global_basis.inverse() * target.basis).orthonormalized()
	ha.quaternion = ha.quaternion.slerp(local.get_rotation_quaternion(), w)


func _point(b: Node3D, at: Vector3, w: float) -> void:
	## Turn limb bone b (hanging along its -Y at rest) so it points at `at`: shortest arc from hanging straight
	## down its parent.
	var pb := (b.get_parent() as Node3D).global_basis
	var rest_dir := -pb.y.normalized()
	var want := (at - b.global_position).normalized()
	if rest_dir.dot(want) < -0.999:  # straight up: nudge off the pole
		want = (want + pb.z.normalized() * 0.02).normalized()
	var g := Basis(Quaternion(rest_dir, want)) * pb
	var local := (pb.inverse() * g).orthonormalized()
	b.quaternion = b.quaternion.slerp(local.get_rotation_quaternion(), w)


func _settle(after: float) -> float:
	## 1 → 0 over 0.5 s once the gesture has run `after` seconds: repeated motions (nod, wave) stop
	## instead of looping like a machine while the pose is held.
	return clampf(1.0 - (_g_time - after) / 0.5, 0.0, 1.0)


func _pose(joint: String, rot: Vector3, w: float) -> void:
	var n: Node3D = _j[joint]
	n.rotation = n.rotation.lerp(rot, w)


func _gesture(g: String, w: float) -> void:
	var t := _time
	var spine: Node3D = _j["Spine"]
	var head: Node3D = _j["Head"]
	match g:
		"point":
			_pose("UpperArmR", Vector3(-1.5, 0.2, -0.1), w)
			_pose("ForearmR", Vector3(-0.05, 0, 0), w)
		"wave":
			_pose("UpperArmR", Vector3(-2.7, 0, -0.35), w)
			_pose("ForearmR", Vector3(-0.3 - 0.35 * sin(t * 9.0) * _settle(2.0), 0, 0), w)
		"give":
			_pose("UpperArmR", Vector3(-1.0, 0.1, -0.05), w)
			_pose("ForearmR", Vector3(-0.45, 0, 0), w)
			_pose("HandR", Vector3(0.3, 0, 0), w)
		"reach":
			for k in ["L", "R"]:
				_pose("UpperArm" + k, Vector3(-1.3, 0, 0), w)
				_pose("Forearm" + k, Vector3(-0.2, 0, 0), w)
			spine.rotation.x = lerpf(spine.rotation.x, 0.2, w)
		"hand_to_face":
			_pose("UpperArmR", Vector3(-0.9, 0, 0.35), w)
			_pose("ForearmR", Vector3(-2.3, 0, 0), w)
			head.rotation.x = lerpf(head.rotation.x, 0.3, w)
		"clutch_hand":  # holding the burned right hand (the Mark) with the left
			_pose("UpperArmR", Vector3(-0.8, 0, 0.35), w)
			_pose("ForearmR", Vector3(-1.2, 0, 0), w)
			_pose("HandR", Vector3(-0.3, 0, 0), w)
			_pose("UpperArmL", Vector3(-0.7, 0, -0.45), w)
			_pose("ForearmL", Vector3(-1.4, 0, 0), w)
			spine.rotation.x = lerpf(spine.rotation.x, 0.3 + 0.04 * sin(t * 7.0), w)
			head.rotation.x = lerpf(head.rotation.x, 0.55, w)
		"arms_crossed":
			_pose("UpperArmL", Vector3(-0.35, 0, -0.3), w)
			_pose("ForearmL", Vector3(-1.9, 0, 0), w)
			_pose("UpperArmR", Vector3(-0.3, 0, 0.3), w)
			_pose("ForearmR", Vector3(-1.95, 0, 0), w)
		"shrug":  # one lift of the shoulders, then they settle
			var up := sin(clampf(_g_time / 0.9, 0.0, 1.0) * PI)
			_pose("UpperArmL", Vector3(-0.3, 0, 0.35 * up + 0.15), w)
			_pose("UpperArmR", Vector3(-0.3, 0, -0.35 * up - 0.15), w)
			_pose("ForearmL", Vector3(-1.1, 0, 0), w)
			_pose("ForearmR", Vector3(-1.1, 0, 0), w)
			head.rotation.z = lerpf(head.rotation.z, 0.15, w)
		"nod":
			head.rotation.x = lerpf(head.rotation.x, 0.1 + 0.2 * sin(t * 6.0) * _settle(1.4), w)
		"shake_head":
			head.rotation.y = lerpf(head.rotation.y, 0.35 * sin(t * 7.0) * _settle(1.5), w)
		"lean":  # bend down to pick something up / look closer
			spine.rotation.x = lerpf(spine.rotation.x, 0.75, w)
			head.rotation.x = lerpf(head.rotation.x, 0.4, w)
			_pose("UpperArmR", Vector3(-0.9, 0, 0), w)
		"cower":
			spine.rotation.x = lerpf(spine.rotation.x, 0.5, w)
			for k in ["L", "R"]:
				_pose("UpperArm" + k, Vector3(-2.0, 0, 0.3 if k == "L" else -0.3), w)
				_pose("Forearm" + k, Vector3(-1.6, 0, 0), w)
		"raise_weapon":
			for k in ["L", "R"]:
				_pose("UpperArm" + k, Vector3(-2.8, 0, 0), w)
				_pose("Forearm" + k, Vector3(-0.4, 0, 0), w)
			spine.rotation.x = lerpf(spine.rotation.x, -0.25, w)
		"window_press":
			for k in ["L", "R"]:
				_pose("UpperArm" + k, Vector3(-1.75, 0, 0.12 if k == "L" else -0.12), w)
				_pose("Forearm" + k, Vector3(-0.45, 0, 0), w)
			head.rotation.x = lerpf(head.rotation.x, -0.05, w)
		"hands_up":
			for k in ["L", "R"]:
				_pose("UpperArm" + k, Vector3(-2.2, 0, 0.5 if k == "L" else -0.5), w)
				_pose("Forearm" + k, Vector3(-1.2, 0, 0), w)
		"beckon":
			_pose("UpperArmR", Vector3(-1.2, 0.3, -0.1), w)
			_pose("ForearmR", Vector3(-0.8 - 0.7 * maxf(0.0, sin(t * 6.0)) * _settle(2.2), 0, 0), w)
		"look_around":
			head.rotation.y = lerpf(head.rotation.y, 0.9 * sin(t * 1.3), w)
			spine.rotation.y = lerpf(spine.rotation.y, 0.25 * sin(t * 1.3), w)
		"frenzy":
			var stab := sin(t * 11.0)
			_pose("UpperArmR", Vector3(-2.3 + 0.8 * stab, 0, -0.3), w)
			_pose("ForearmR", Vector3(-0.9 - 0.6 * maxf(stab, 0.0), 0, 0), w)
			_pose("UpperArmL", Vector3(-1.2 + 0.35 * sin(t * 9.0 + 1.3), 0.2, 0.45), w)
			_pose("ForearmL", Vector3(-0.5 - 0.4 * sin(t * 9.0), 0, 0), w)
			_pose("HandL", Vector3(-0.6, 0, 0), w)
			spine.rotation.x = lerpf(spine.rotation.x, 0.35 + 0.08 * sin(t * 11.0), w)
			head.rotation.x = lerpf(head.rotation.x, -0.25, w)  # eyes up on the prey over the hunch
		"slump":
			spine.rotation.x = lerpf(spine.rotation.x, 0.45, w)
			head.rotation.x = lerpf(head.rotation.x, 0.6, w)
			for k in ["L", "R"]:
				_pose("UpperArm" + k, Vector3(0.1, 0, 0.05 if k == "L" else -0.05), w)
