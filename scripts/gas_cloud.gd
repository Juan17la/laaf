class_name GasCloud
extends Node3D
## Julian's sedative gas: a cheap PS2-style cluster of green billboard puffs. Each physics frame the
## player is inside it calls player.gas_exposure(delta) (mask/filter logic lives on the player);
## with the clinic vents reversed it also chokes asthmatic enemies (Enemy.asthma_attack).
## life <= 0 = permanent (corridor gas) until clear().

static var vents_reversed := false
static var _tex: Texture2D

var radius := 3.0
var life := 8.0
var _timed := true
var _fade := 0.0  ## 0..1 visual/effect strength (fades in, clear() fades out)
var _clearing := false
var _hurt_t := 0.0
var _t := 0.0
var _puffs: Array[Sprite3D] = []


static func make(parent: Node, pos: Vector3, r := 3.0, life_s := 8.0) -> GasCloud:
	var g := GasCloud.new()
	g.radius = r
	g.life = life_s
	g._timed = life_s > 0.0
	g.position = pos  # parents sit at the world origin
	parent.add_child(g)
	return g


func _ready() -> void:
	add_to_group("gas_clouds")
	Snd.attach(self, "hiss", -6.0)
	for i in int(radius * 4.0):
		var s := Sprite3D.new()
		s.texture = _texture()
		s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		s.shaded = false
		s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		s.pixel_size = radius * 0.05
		var a := randf() * TAU
		var d := sqrt(randf()) * radius * 0.8
		s.position = Vector3(cos(a) * d, randf_range(0.3, 1.7), sin(a) * d)
		s.modulate = Color(0.5, 0.75, 0.3, 0.0)
		add_child(s)
		_puffs.append(s)


static func _texture() -> Texture2D:
	if not _tex:
		var g := Gradient.new()
		g.set_color(0, Color(1, 1, 1, 1))
		g.set_color(1, Color(1, 1, 1, 0))
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(0.5, 0.0)
		t.width = 24
		t.height = 24
		_tex = t
	return _tex


func has_point(p: Vector3) -> bool:
	var to := p - global_position
	return Vector2(to.x, to.z).length() < radius and to.y > -1.0 and to.y < 2.5


func clear() -> void:
	## Vents / scripted: fade out and free.
	_clearing = true


func _physics_process(delta: float) -> void:
	_t += delta
	if _timed:
		life -= delta
		if life <= 0.0:
			_clearing = true
	_fade = move_toward(_fade, 0.0 if _clearing else 1.0, delta / 1.2)
	for i in _puffs.size():
		var s := _puffs[i]
		s.modulate.a = 0.3 * _fade
		s.position.y += sin(_t * 0.8 + i) * 0.1 * delta
	if _clearing and _fade <= 0.0:
		queue_free()
		return
	if _fade < 0.5:
		return
	var p := get_tree().get_first_node_in_group("player") as Node3D
	if p and not p.get("dead") and has_point(p.global_position):
		if p.has_method("gas_exposure"):
			p.gas_exposure(delta)
		else:
			_hurt_t -= delta
			if _hurt_t <= 0.0:
				_hurt_t = 0.5
				p.hurt(3.0, global_position)
	if vents_reversed:
		for e in get_tree().get_nodes_in_group("enemies"):
			if e.get("asthma") and has_point(e.global_position):
				e.asthma_attack()
