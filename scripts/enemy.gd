class_name Enemy
extends CharacterBody3D
## Hunters and Marked Ones (RF-03): patrol → suspicious → chase → search, melee with a telegraphed
## overhead windup (dodge it with a roll), optional bow, stun (flare / fire), down (bosses kneel for
## the spare/kill choice) and death. Built in code with Enemy.spawn(); the model is any char_*.glb.
## Chapter 2 props (all off by default): lily_calls (Nora in the dark), shadow_bonus, gas_thrower +
## asthma (Julian, see GasCloud), checks_hiding (searches hiding spots it saw used), stealth takedown.
## Chapter 3: hearing + armor (Marcus), SmokeCloud blocks sight, crush() (a dropped bell), subclass spawn
## (Harvester passes its own instance to spawn()).

signal died(enemy: Enemy)
signal downed(enemy: Enemy)  ## boss at 0 HP: kneels, waits for spare / kill
signal damaged(enemy: Enemy)
signal struck_player(enemy: Enemy)
signal called(enemy: Enemy)  ## lily_calls: stopped to call for Lily (glows, takes extra damage)
signal checks_spot(enemy: Enemy, pos: Vector3)  ## checks_hiding: arrived at a hiding spot it saw used

enum State { PATROL, SUSPICIOUS, CHASE, SEARCH, STUNNED, DOWN, DEAD }

@export var display_name := "Marked One"
@export var max_health := 60.0
@export var walk_speed := 1.6
@export var run_speed := 3.4
@export var melee_damage := 12.0
@export var melee_range := 1.7
@export var windup := 0.55
@export var mark_gain := 3.0
@export var sight_range := 20.0
@export var fov_deg := 130.0
@export var ranged := false  ## bow: keeps its distance and fires arrows
@export var bow := false  ## carries the bow (item_bow) even when not shooting it (Owen on the hunt)
@export var arrow_damage := 14.0
@export var arrow_interval := 2.2
@export var flare_stun := 2.5  ## seconds stunned by a flare hit (Owen: long, fire is his weakness)
@export var boss := false  ## at 0 HP kneels (DOWN) instead of dying
@export var invulnerable := false  ## scripted hunts: shots only stagger
@export var give_up_x := INF  ## scripted hunts: stops chasing past this world X (the town lights)
@export var lily_calls := false  ## Nora in the dark: dimmed model, stops every call_interval s to call
@export var call_interval := 7.0
@export var call_time := 1.8  ## how long each call lasts (the punish window)
@export var shadow_bonus := 1.0  ## damage multiplier while not in CHASE (hit from the shadows)
@export var gas_thrower := false  ## Julian: lobs a sedative canister (GasCloud) at the player
@export var gas_interval := 6.0
@export var asthma := false  ## stunned by any GasCloud while GasCloud.vents_reversed
@export var asthma_stun := 3.5
@export var checks_hiding := false  ## remembers hiding spots it saw used; SEARCH visits them first
@export var hearing := 1.0  ## noise radius multiplier (Marcus hears everything)
@export var armor := 1.0  ## damage multiplier while not stunned (Marcus: very tough)

var state := State.PATROL
var health := 60.0
var patrol: Array[Vector3] = []
## The bow in the left hand (item_bow, the same grip as the player's), string drawn by the game, arms by IK.
const BOW_GRIP := Transform3D(Basis(Vector3(-1, 0, 0), Vector3(0, 0, 1), Vector3(0, 1, 0)), Vector3(0, -0.06, -0.02))
var _bow_model: Node3D
var _bow_string: Array[MeshInstance3D] = []
var _bow_arrow: Node3D
var drop: Callable  ## called with the death position (loot)

var _anim: HumanoidAnim
var _model: Node3D
var _player: Node3D
var _target := Vector3.ZERO
var _patrol_i := 0
var _t_state := 0.0
var _t_sense := 0.0
var _attack := -1.0
var _cool := 0.0
var _arrow_t := 1.5
var _stun := 0.0
var _stuck := 0.0
var _strafe := 1.0
var _unseen := 0.0  ## seconds since the player was last seen
var _call_t := 0.0
var _calling := 0.0  ## > 0 while calling for Lily
var _glow: OmniLight3D
var _dim: Array = []  ## [MeshInstance3D, surface, dark material] (lily_calls)
var _gas_t := 2.5
var _throw := -1.0  ## 0..1 canister throw (windup until 0.6)
var _back := 0.0
var _asthma_cd := 0.0
var _spots: Array[Vector3] = []  ## hiding spots seen used (checks_hiding)
var _check: Array[Vector3] = []  ## spots still to check this search

const TAKEDOWN_CONE := 100.0  ## degrees behind the enemy
const THROW_TIME := 0.9

@onready var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")


static func spawn(parent: Node, model_scene: String, pos: Vector3, yaw := 0.0, props := {}, e: Enemy = null) -> Enemy:
	if not e:
		e = Enemy.new()
	for k in props:
		e.set(k, props[k])
	e.collision_layer = 2
	e.collision_mask = 3
	var col := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.35
	cap.height = 1.8
	col.shape = cap
	col.position.y = 0.9
	e.add_child(col)
	var model: Node3D = load(model_scene).instantiate()
	model.name = "Model"
	e.add_child(model)
	var anim := HumanoidAnim.new()
	anim.name = "Anim"
	anim.model_path = ^"../Model"
	e.add_child(anim)
	e.position = pos  # parents are at the world origin; set before _ready so patrol starts here
	model.rotation.y = yaw
	parent.add_child(e)
	return e


func _ready() -> void:
	max_health *= G.settings().enemy  # difficulty
	health = max_health
	add_to_group("enemies")
	_model = $Model
	_anim = $Anim
	_player = get_tree().get_first_node_in_group("player")
	if patrol.is_empty():
		patrol = [global_position]
	_target = patrol[0]
	_call_t = call_interval
	if lily_calls:
		_dim_model()
	if ranged or bow:
		_make_bow()
	if checks_hiding and _player and _player.has_signal("hid"):
		_player.hid.connect(_on_hid)


func _dim_model() -> void:
	## Unlit in the dark: every surface drops to near black; a call restores it for a moment.
	for mi in _model.find_children("*", "MeshInstance3D", true, false):
		for i in mi.get_surface_override_material_count():
			var m := mi.get_active_material(i) as BaseMaterial3D
			if m:
				var dark := m.duplicate() as BaseMaterial3D
				dark.albedo_color = m.albedo_color * Color(0.12, 0.12, 0.15)
				dark.emission_enabled = false
				_dim.append([mi, i, dark])
	_set_dim(true)
	_glow = OmniLight3D.new()
	_glow.light_color = Color(0.75, 0.85, 1.0)
	_glow.omni_range = 7.0
	_glow.light_energy = 0.0
	_glow.position.y = 1.6
	add_child(_glow)


func _set_dim(on: bool) -> void:
	for d in _dim:
		d[0].set_surface_override_material(d[1], d[2] if on else null)


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		velocity.y = 0.0
	_t_state += delta
	_cool = maxf(_cool - delta, 0.0)
	_asthma_cd = maxf(_asthma_cd - delta, 0.0)
	match state:
		State.DEAD:
			return
		State.DOWN:
			_stop(delta)
		State.STUNNED:
			_stun -= delta
			_stop(delta)
			_anim.flinch = maxf(_anim.flinch, 0.6)
			if _stun <= 0.0:
				_anim.crouching = false
				_set_state(State.CHASE)
		_:
			if _player and _player.get("controls_enabled") == false:
				_hold(delta)
			elif not (lily_calls and _lily(delta)):
				_think(delta)
	move_and_slide()
	_anim.speed = Vector2(velocity.x, velocity.z).length()


func _hold(delta: float) -> void:
	## Player out of control (cinematic, minigame, death fade): stand still, sense nothing, drop any windup.
	_stop(delta)
	if _attack >= 0.0 or _throw >= 0.0:
		_attack = -1.0
		_throw = -1.0
		_anim.attack = -1.0
	if _calling > 0.0:
		_end_call()
	_anim.aim = 0.0


func _lily(delta: float) -> bool:
	## Nora: every call_interval s she freezes and calls for Lily. True while calling (skip thinking).
	if _calling > 0.0:
		_calling -= delta
		_stop(delta)
		_glow.light_energy = 2.5 * clampf(_calling / call_time * 3.0, 0.0, 1.0)
		if _calling <= 0.0:
			_end_call()
		return true
	_call_t -= delta
	if _call_t > 0.0 or _attack >= 0.0 or _throw >= 0.0:
		return false
	_call_t = call_interval
	_calling = call_time
	_anim.gesture = "hand_to_face"
	_anim.aim = 0.0
	_set_dim(false)
	called.emit(self)
	return true


func _end_call(dim := true) -> void:
	_calling = 0.0
	if lily_calls:
		_anim.gesture = ""
		_set_dim(dim)
		_glow.light_energy = 0.0


func _think(delta: float) -> void:
	_t_sense -= delta
	_unseen += delta
	if _t_sense <= 0.0:
		_t_sense = 0.2
		if can_see_player():
			_unseen = 0.0
			_target = _player.global_position
			if state != State.CHASE:
				_set_state(State.CHASE)
	if state == State.CHASE and _player.global_position.x > give_up_x:
		_set_state(State.SEARCH)
		_target = patrol[0]
	if _attack >= 0.0:
		_do_attack(delta)
		return
	if gas_thrower:
		_gas_t -= delta
		if _throw >= 0.0:
			_do_throw(delta)
			return
	match state:
		State.PATROL:
			if _go(_target, walk_speed, delta) < 1.0:
				_patrol_i = (_patrol_i + 1) % patrol.size()
				_target = patrol[_patrol_i]
		State.SUSPICIOUS:
			if _go(_target, walk_speed * 1.3, delta) < 1.2 or _t_state > 10.0:
				_set_state(State.SEARCH)
		State.CHASE:
			var d := global_position.distance_to(_player.global_position)
			if _unseen > 5.0:  # lost them: search around the last known position
				_set_state(State.SEARCH)
			elif gas_thrower and _gas_t <= 0.0 and _unseen < 0.5 and d < 16.0:
				_gas(d, delta)
			elif ranged and d > 4.0:
				_bow(d, delta)
			elif d < melee_range and _cool <= 0.0:
				_attack = 0.0
				_face(_player.global_position, delta, 30.0)
			else:
				_go(_player.global_position if _unseen < 1.0 else _target, run_speed, delta)
		State.SEARCH:
			if not _check.is_empty():
				_check_spot(delta)
			elif _go(_target, walk_speed * 1.2, delta) < 1.2:
				_target = _target + Vector3(randf_range(-6, 6), 0, randf_range(-6, 6))
			if _t_state > 12.0:
				_set_state(State.PATROL)
				_target = patrol[_patrol_i]


func _bow(d: float, delta: float) -> void:
	# keep 8-14 m, strafe, loose arrows on a timer
	_arrow_t -= delta
	var to := (_player.global_position - global_position)
	to.y = 0.0
	to = to.normalized()
	var side := Vector3(-to.z, 0, to.x) * _strafe
	var move := side * 0.7
	if d > 14.0:
		move += to
	elif d < 8.0:
		move -= to
	if randf() < delta * 0.4:
		_strafe = -_strafe
	velocity.x = move.x * run_speed * 0.6
	velocity.z = move.z * run_speed * 0.6
	_face(_player.global_position, delta, 12.0)
	_anim.aim = 1.0
	if _arrow_t <= 0.0 and can_see_player():
		_arrow_t = arrow_interval
		_anim.recoil = 1.0
		var from := _bow_model.to_global(Vector3(0.012, 0, -0.1)) if _bow_model else global_position + Vector3.UP * 1.45 + to * 0.5
		var aim_at: Vector3 = _player.global_position + Vector3.UP * 1.1 + _player.velocity * (d / 24.0) * 0.6
		Arrow.fire(get_parent(), from, aim_at, arrow_damage, self)


func _make_bow() -> void:
	var hand := _model.find_child("HandL", true, false) as Node3D
	if not hand or not ResourceLoader.exists("res://models/item_bow.glb"):
		return
	_bow_model = Node3D.new()
	hand.add_child(_bow_model)
	_bow_model.transform = BOW_GRIP
	_bow_model.add_child((load("res://models/item_bow.glb") as PackedScene).instantiate())
	for i in 2:
		var mi := MeshInstance3D.new()
		var b := BoxMesh.new()
		b.size = Vector3(0.003, 0.003, 1.0)
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.85, 0.82, 0.7)
		b.material = mat
		mi.mesh = b
		_bow_model.add_child(mi)
		_bow_string.append(mi)
	if ResourceLoader.exists("res://models/item_arrow.glb"):
		_bow_arrow = (load("res://models/item_arrow.glb") as PackedScene).instantiate()
		_bow_model.add_child(_bow_arrow)


func _process(delta: float) -> void:
	_bow_arms(delta)  # in _process: cutscenes freeze the physics but still raise the bow (anim.aim)


func _bow_arms(delta: float) -> void:
	## Bow carried low in the left hand, or up at arm's length along the aim with the right hand drawing the
	## string to the cheek (same poses as the player's bow: player.gd _bow_pose). Gone once he drops it.
	if not _bow_model:
		return
	var on := (ranged or bow) and state not in [State.DEAD, State.DOWN]
	_bow_model.visible = on
	if not on:
		for k in ["L", "R"]:
			_anim.ik_w[k] = move_toward(_anim.ik_w[k], 0.0, delta * 6.0)
		_anim.stance = 0.0
		return
	var ready := clampf(_anim.aim, 0.0, 1.0) if ranged else 0.0
	var ad := Vector3(0, sin(_anim.aim_pitch), cos(_anim.aim_pitch))
	var aimed := Transform3D(Basis.looking_at(ad, Vector3.UP) * Basis(Vector3.BACK, 0.12), Vector3(0.0, 1.53, 0.12) + ad * 0.6)
	var low := Transform3D(Basis.looking_at(Vector3(0.05, -0.15, 1.0), Vector3.UP), Vector3(0.25, 0.93, 0.1))
	var w := low.interpolate_with(aimed, ready)
	var draw := ready * clampf(1.0 - _anim.recoil * 1.5, 0.0, 1.0)  # the string snaps forward on a shot
	var nock := Vector3(0, 0, 0.16 + 0.45 * draw)
	_anim.ik_pole["R"] = Vector3(-1.0, 0.3, -0.6)  # the drawing elbow out and back, not across the chest
	_anim.ik["L"] = w * BOW_GRIP.affine_inverse()
	_anim.ik_w["L"] = 1.0
	_anim.ik["R"] = w * Transform3D(Basis(), nock + Vector3(0.012, -0.015, 0)) * BOW_GRIP.affine_inverse()
	_anim.ik_w["R"] = ready
	_anim.stance = -1.2 * ready
	for i in 2:
		var tip := Vector3(0, 0.62 if i == 0 else -0.62, 0.1)
		(_bow_string[i].mesh as BoxMesh).size.z = tip.distance_to(nock)
		_bow_string[i].transform = Transform3D(Basis.looking_at(nock - tip, Vector3.RIGHT), (tip + nock) / 2.0)
	if _bow_arrow:
		_bow_arrow.visible = ready > 0.3 and _anim.recoil < 0.3
		_bow_arrow.position = nock + Vector3(0.012, 0, 0)


func _gas(d: float, delta: float) -> void:
	## Canister ready: back off to a safe distance (max 1.5 s), then a telegraphed overhead lob.
	var to := _player.global_position - global_position
	to.y = 0.0
	if d < 5.0:
		_back += delta
		if _back > 1.5:  # cornered: melee now, try the canister again shortly
			_back = 0.0
			_gas_t = 2.0
			return
		velocity.x = -to.normalized().x * run_speed * 0.8
		velocity.z = -to.normalized().z * run_speed * 0.8
		_face(_player.global_position, delta, 12.0)
		return
	_back = 0.0
	_throw = 0.0


func _do_throw(delta: float) -> void:
	_stop(delta)
	var before := _throw
	_throw += delta / THROW_TIME
	_anim.attack = _throw
	if _throw < 0.6:
		_face(_player.global_position, delta, 8.0)
	if before < 0.62 and _throw >= 0.62:
		var at: Vector3 = _player.global_position + _player.velocity * 0.5
		at.y = _player.global_position.y
		if at.distance_to(global_position) > 3.5:
			_lob(at)
	if _throw >= 1.0:
		_throw = -1.0
		_anim.attack = -1.0
		_gas_t = gas_interval


func _lob(at: Vector3) -> void:
	## A canister arcs to `at` (0.8 s) and bursts into a GasCloud.
	var can := MeshInstance3D.new()
	var m := CylinderMesh.new()
	m.top_radius = 0.06
	m.bottom_radius = 0.06
	m.height = 0.22
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.5, 0.55, 0.45)
	m.material = mat
	can.mesh = m
	var parent := get_parent()
	parent.add_child(can)
	var from := global_position + Vector3.UP * 1.9
	can.global_position = from
	var tw := can.create_tween()
	tw.tween_method(func(t: float) -> void:
		can.global_position = from.lerp(at, t) + Vector3.UP * sin(t * PI) * 2.5
		can.rotation.x = t * 9.0, 0.0, 1.0, 0.8)
	tw.tween_callback(func() -> void:
		GasCloud.make(parent, at)
		can.queue_free())


func _check_spot(delta: float) -> void:
	## checks_hiding: walk to the next remembered spot; the player hiding there is pulled out.
	if _go(_check[0], walk_speed * 1.4, delta) >= 1.2:
		return
	var spot: Vector3 = _check.pop_front()
	_t_state = 0.0
	checks_spot.emit(self, spot)
	if not _player.dead and _player.global_position.distance_to(spot) < 1.6:
		_unseen = 0.0
		_target = _player.global_position
		_set_state(State.CHASE)


func _on_hid(pos: Vector3) -> void:
	if state in [State.DEAD, State.DOWN] or _unseen > 1.5:
		return  # only spots it actually saw the player slip into
	for s in _spots:
		if s.distance_to(pos) < 1.5:
			return
	_spots.append(pos)


func _do_attack(delta: float) -> void:
	_stop(delta)
	var before := _attack
	_attack += delta / (windup / 0.6) if _attack < 0.6 else delta / 0.35
	_anim.attack = _attack
	if _attack < 0.6:
		_face(_player.global_position, delta, 6.0)
	if before < 0.62 and _attack >= 0.62:
		var to := _player.global_position - global_position
		var fwd := _model.global_basis.z
		if to.length() < melee_range + 0.5 and fwd.dot(to.normalized()) > 0.3:
			if _player.hurt(melee_damage, global_position, mark_gain):
				struck_player.emit(self)
	if _attack >= 1.0:
		_attack = -1.0
		_anim.attack = -1.0
		_cool = 0.6


func _go(p: Vector3, speed: float, delta: float) -> float:
	var to := p - global_position
	to.y = 0.0
	var d := to.length()
	if d < 0.5:
		_stop(delta)
		return d
	var dir := to / d
	# slide around obstacles: if we're not moving, veer sideways for a moment
	if Vector2(velocity.x, velocity.z).length() < speed * 0.25:
		_stuck += delta
	else:
		_stuck = maxf(_stuck - delta, 0.0)
	if _stuck > 0.6:
		dir = (dir + Vector3(-dir.z, 0, dir.x) * _strafe * 1.5).normalized()
		if _stuck > 1.6:
			_stuck = 0.0
			_strafe = -_strafe
	velocity.x = move_toward(velocity.x, dir.x * speed, 20.0 * delta)
	velocity.z = move_toward(velocity.z, dir.z * speed, 20.0 * delta)
	_face(global_position + dir, delta, 8.0)
	_anim.aim = 0.0
	return d


func _stop(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0.0, 25.0 * delta)
	velocity.z = move_toward(velocity.z, 0.0, 25.0 * delta)


func _face(p: Vector3, delta: float, rate: float) -> void:
	var to := p - global_position
	if Vector2(to.x, to.z).length() > 0.05:
		_model.rotation.y = lerp_angle(_model.rotation.y, atan2(to.x, to.z), rate * delta)


func _set_state(s: State) -> void:
	state = s
	_t_state = 0.0
	if s == State.SEARCH and not _spots.is_empty():
		_check = _spots.duplicate()
		_check.sort_custom(func(a: Vector3, b: Vector3) -> bool:
			return a.distance_to(global_position) < b.distance_to(global_position))


func can_see_player() -> bool:
	if not _player or _player.dead:
		return false
	var eye := global_position + Vector3.UP * 1.6
	var chest: Vector3 = _player.global_position + Vector3.UP * 1.0
	var to := chest - eye
	var d := to.length()
	var vis: float = _player.visibility()
	if d > sight_range * vis:
		return false
	var close := 0.8 if _player.get("crouching") else 3.0  # sneaking up from behind (takedowns)
	if d > close and rad_to_deg(_model.global_basis.z.angle_to(to)) > fov_deg / 2.0:
		return false
	for s in get_tree().get_nodes_in_group("smoke"):
		if s.blocks(eye, chest):
			return false
	var q := PhysicsRayQueryParameters3D.create(eye, chest, 1, [get_rid(), _player.get_rid()])
	return get_world_3d().direct_space_state.intersect_ray(q).is_empty()


func hear(pos: Vector3, radius: float) -> void:
	if state in [State.DEAD, State.DOWN, State.STUNNED, State.CHASE]:
		return
	if pos.distance_to(global_position) < radius * hearing:
		_target = pos
		_set_state(State.SUSPICIOUS)


func hit(dmg: float, point: Vector3, flare := false) -> void:
	if not is_physics_processing():
		return  # frozen for a cutscene: fire / stray shots can't down a boss mid-scene
	if state == State.DOWN:
		kill()  # shooting a kneeling boss is the KILL choice
		return
	if state == State.DEAD:
		return
	if point.y - global_position.y > 1.5 * _model.scale.y:
		dmg *= 2.0  # headshot
	if state == State.STUNNED or _calling > 0.0:
		dmg *= 1.5
	if state != State.CHASE:
		dmg *= shadow_bonus
	if state != State.STUNNED:
		dmg *= armor
	if flare and flare_stun > 0.0:
		stun(flare_stun)
	_anim.flinch = 1.0
	if state != State.STUNNED:
		_target = _player.global_position
		_unseen = 0.0
		_set_state(State.CHASE)
	if invulnerable:
		stun(0.8)
		return
	_take(dmg)


func _take(dmg: float) -> void:
	health -= dmg
	damaged.emit(self)
	if health <= 0.0:
		health = 0.0
		if boss:
			_set_state(State.DOWN)
			_attack = -1.0
			_throw = -1.0
			_end_call(false)  # lit for the spare / kill scene
			_anim.attack = -1.0
			_anim.crouching = true
			_anim.aim = 0.0
			downed.emit(self)
		else:
			kill()


func can_takedown(by: Node3D) -> bool:
	## Stealth takedown: unaware (not chasing), alive, `by` close behind its back.
	if state in [State.CHASE, State.DOWN, State.DEAD]:
		return false
	var to := by.global_position - global_position
	to.y = 0.0
	if to.length() > 1.8:
		return false
	return rad_to_deg((-_model.global_basis.z).angle_to(to)) < TAKEDOWN_CONE / 2.0


func takedown() -> void:
	## Marked One: dies. Boss: 25% max health (× shadow_bonus) + 2 s stun. Invulnerable: stun only.
	if not (boss or invulnerable):
		kill()
		return
	_anim.flinch = 1.0
	if not invulnerable:
		_take(max_health * 0.25 * shadow_bonus)
	stun(2.0)


func crush(frac: float, stun_t: float) -> void:
	## Heavy scripted hit (a dropped bell): `frac` of max health, ignores armor, then a stun.
	if state in [State.DOWN, State.DEAD] or not is_physics_processing():
		return  # frozen by a cutscene
	_anim.flinch = 1.0
	_take(max_health * frac)
	stun(stun_t)


func asthma_attack() -> void:
	## GasCloud with vents reversed: coughing fit, then a short grace to stagger out of the gas.
	if not asthma or _asthma_cd > 0.0:
		return
	_asthma_cd = asthma_stun + 1.5
	stun(asthma_stun)


func stun(t: float) -> void:
	if state in [State.DEAD, State.DOWN] or not is_physics_processing():
		return
	_stun = maxf(_stun, t)
	_attack = -1.0
	_throw = -1.0
	_end_call()
	_anim.attack = -1.0
	_anim.aim = 0.0
	_anim.crouching = t > 1.5
	_set_state(State.STUNNED)


func kill() -> void:
	if state == State.DEAD:
		return
	_set_state(State.DEAD)
	_end_call(false)
	remove_from_group("enemies")
	collision_layer = 0
	velocity = Vector3.ZERO
	_anim.attack = -1.0
	_anim.crouching = false
	_anim.aim = 0.0
	_anim.speed = 0.0
	var tw := create_tween()
	tw.tween_property(_model, "rotation:x", -PI / 2.0, 0.5).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(_model, "position:y", 0.25, 0.5)
	tw.tween_callback(func() -> void: _anim.set_process(false))
	if drop.is_valid():
		drop.call(global_position)
	died.emit(self)
	get_tree().create_timer(30.0).timeout.connect(queue_free)


func lose_track(p: Vector3) -> void:
	## Tension director: after a catch the hunter wanders off to search somewhere else.
	_attack = -1.0
	_anim.attack = -1.0
	_target = p
	_unseen = 99.0
	_set_state(State.SEARCH)
	_t_sense = 3.0  # blind for a moment


func reset_to(pos: Vector3) -> void:
	## Checkpoint reload: back to full health at pos, patrolling.
	global_position = pos
	health = max_health
	_stun = 0.0
	_attack = -1.0
	_throw = -1.0
	_anim.attack = -1.0
	_anim.crouching = false
	_end_call()
	_call_t = call_interval
	_gas_t = 2.5
	_spots.clear()
	_check.clear()
	_set_state(State.PATROL)
	_target = patrol[0]
