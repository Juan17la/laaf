class_name SmokeCloud
extends Node3D
## Smoke can (Chapter 3): a grey cluster of billboard puffs that lives LIFE s. Enemy.can_see_player
## asks every cloud in the "smoke" group whether it blocks the eye → chest line (or hides the player
## standing inside it). Reuses GasCloud's puff texture.

const RADIUS := 3.5
const LIFE := 10.0

var _t := 0.0
var _puffs: Array[Sprite3D] = []


static func make(parent: Node, pos: Vector3) -> SmokeCloud:
	var s := SmokeCloud.new()
	s.position = pos  # parents sit at the world origin
	parent.add_child(s)
	return s


func _ready() -> void:
	add_to_group("smoke")
	for i in 16:
		var s := Sprite3D.new()
		s.texture = GasCloud._texture()
		s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		s.shaded = false
		s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		s.pixel_size = RADIUS * 0.06
		var a := randf() * TAU
		var d := sqrt(randf()) * RADIUS * 0.75
		s.position = Vector3(cos(a) * d, randf_range(0.3, 2.2), sin(a) * d)
		s.modulate = Color(0.7, 0.7, 0.68, 0.0)
		add_child(s)
		_puffs.append(s)
	get_tree().call_group("enemies", "hear", global_position, 8.0)  # the hiss


func strength() -> float:
	## 0..1: puffs up in 0.6 s, thins out over the last 2 s.
	return clampf(_t / 0.6, 0.0, 1.0) * clampf((LIFE - _t) / 2.0, 0.0, 1.0)


func blocks(from: Vector3, to: Vector3) -> bool:
	## True when the from → to sight line passes through the cloud (XZ, below 3 m) while it's thick.
	if strength() < 0.5 or minf(from.y, to.y) - global_position.y > 3.0:
		return false
	var a := Vector2(from.x - global_position.x, from.z - global_position.z)
	var b := Vector2(to.x - global_position.x, to.z - global_position.z)
	var ab := b - a
	var k := clampf(-a.dot(ab) / maxf(ab.length_squared(), 0.0001), 0.0, 1.0)
	return (a + ab * k).length() < RADIUS * 0.85


func _process(delta: float) -> void:
	_t += delta
	var k := strength()
	for i in _puffs.size():
		_puffs[i].modulate.a = 0.55 * k
		_puffs[i].position.y += sin(_t * 0.7 + i) * 0.08 * delta
	if _t >= LIFE:
		queue_free()
