class_name Bell
extends StaticBody3D
## Chapter 3, Marcus's fight: a bronze bell hung over the nave aisle on a chain, its rope tied off at a
## cleat on the wall. Shoot the bell/chain (it's on the bullet layer) or release the rope (E) and it
## drops: whoever stands under it (HIT_R) is crushed (Enemy.crush: CRUSH of max health + a long stun);
## the clang deafens — stuns — every other enemy within DEAF_R ("make the bells scream"). One use each.
## Placeholder meshes: see maps/docs/en/ch3_objects_to_generate.md (prop_church_bell).

signal dropped(crushed: bool)

const HIT_R := 2.2
const DEAF_R := 16.0
const CRUSH := 0.3
const CRUSH_STUN := 4.5
const DEAF_STUN := 3.0
const BRONZE := Color(0.55, 0.4, 0.18)

var down := false
var cleat: Interactable
var _floor := 0.0
var _rope: MeshInstance3D


static func make(parent: Node, pos: Vector3, cleat_pos: Vector3, ceiling := 8.0) -> Bell:
	## pos = floor point under the bell (the bell hangs at 5 m); cleat_pos = the rope's wall cleat.
	var b := Bell.new()
	b.collision_layer = 2  # bullets (and nothing walks up there)
	b.collision_mask = 0
	b._floor = pos.y
	var col := CollisionShape3D.new()
	var cyl := CylinderShape3D.new()
	cyl.radius = 0.7
	cyl.height = 1.3
	col.shape = cyl
	col.position.y = 0.65
	b.add_child(col)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = BRONZE
	mat.metallic = 0.7
	mat.roughness = 0.35
	var bell := MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.32
	cm.bottom_radius = 0.72
	cm.height = 1.1
	cm.material = mat
	bell.mesh = cm
	bell.position.y = 0.6
	b.add_child(bell)
	var chain := b._bar(Vector3(0.08, ceiling - pos.y - 6.1, 0.08), Color(0.2, 0.2, 0.2))
	chain.position.y = 1.15 + (ceiling - pos.y - 6.1) / 2.0
	parent.add_child(b)
	b.global_position = pos + Vector3.UP * 5.0
	b._rope = b._bar(Vector3(0.03, 0.03, 1.0), Color(0.55, 0.45, 0.3))
	b._rope.top_level = true
	var top := b.global_position + Vector3.UP * 1.1
	b._rope.global_position = (top + cleat_pos) / 2.0
	b._rope.look_at(cleat_pos, Vector3.UP)
	b._rope.scale.z = top.distance_to(cleat_pos)
	b.cleat = Interactable.make(parent, cleat_pos, "Release the bell rope", func(_by: Node) -> void: b.drop(),
		Color(0.9, 0.7, 0.35))
	return b


func _bar(size: Vector3, c: Color) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	bm.material = m
	mi.mesh = bm
	add_child(mi)
	return mi


func hit(_dmg: float, _point: Vector3, _flare := false) -> void:
	drop()


func drop() -> void:
	if down:
		return
	down = true
	collision_layer = 0
	if is_instance_valid(cleat):
		cleat.queue_free()
	_rope.visible = false
	get_child(2).visible = false  # the chain goes with it
	var tw := create_tween()
	tw.tween_property(self, "global_position:y", _floor, 0.4).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_callback(_impact)


func _impact() -> void:
	collision_layer = 1  # lies in the aisle now: cover
	var crushed := false
	for e in get_tree().get_nodes_in_group("enemies"):
		var d := Vector2(e.global_position.x - global_position.x, e.global_position.z - global_position.z).length()
		if d < HIT_R and e.has_method("crush"):
			e.crush(CRUSH, CRUSH_STUN)
			crushed = true
		elif d < DEAF_R and e.has_method("stun"):
			e.stun(DEAF_STUN)
	get_tree().call_group("enemies", "hear", global_position, 40.0)
	var flash := OmniLight3D.new()  # sparks off the flagstones
	flash.light_color = Color(1.0, 0.8, 0.4)
	flash.light_energy = 4.0
	flash.omni_range = 6.0
	add_child(flash)
	flash.position.y = 0.3
	flash.create_tween().tween_property(flash, "light_energy", 0.0, 0.4).finished.connect(flash.queue_free)
	dropped.emit(crushed)
