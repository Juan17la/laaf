class_name MusicBox
extends Node3D
## Nora's noise trap (Recess): while it plays, walking past it upright within RANGE makes it chime
## (a ♪ pops up and every enemy within HEAR comes to look). Press E on it to silence it for good.

signal silenced

const RANGE := 5.0
const HEAR := 18.0

var playing := true
var interactable: Interactable
var _note: Label3D
var _cd := 0.0
var _idle := 0.0


static func make(parent: Node, pos: Vector3) -> MusicBox:
	var b := MusicBox.new()
	b.add_child(load("res://models/int_music_box.glb").instantiate())
	b.position = pos  # parents sit at the world origin
	parent.add_child(b)
	b.interactable = Interactable.make(b, b.global_position + Vector3.UP * 0.2, "Silence the music box", b._silence)
	return b


func _ready() -> void:
	_note = Label3D.new()
	_note.text = "♪"
	_note.font_size = 14
	_note.outline_size = 4
	_note.pixel_size = Interactable.PX
	_note.fixed_size = true
	_note.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_note.shaded = false
	_note.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_note.modulate = Color(0.95, 0.85, 1.0, 0.0)
	add_child(_note)


func _physics_process(delta: float) -> void:
	if not playing:
		return
	_cd -= delta
	_idle -= delta
	var p := get_tree().get_first_node_in_group("player") as CharacterBody3D
	if p and _cd <= 0.0 and not p.get("crouching") and Vector2(p.velocity.x, p.velocity.z).length() > 0.5 \
			and p.global_position.distance_to(global_position) < RANGE:
		chime()
	elif _idle <= 0.0:
		_idle = 3.0
		_pop(0.35, 0.2)  # faint tinkle: it's live


func chime() -> void:
	_cd = 2.0
	_idle = 3.0
	_pop(1.0, 0.6)
	get_tree().call_group("enemies", "hear", global_position, HEAR)


func _pop(alpha: float, rise: float) -> void:
	_note.position.y = 0.25
	_note.modulate.a = alpha
	var tw := create_tween().set_parallel()
	tw.tween_property(_note, "position:y", 0.25 + rise, 1.2)
	tw.tween_property(_note, "modulate:a", 0.0, 1.2)


func _silence(_by: Node) -> void:
	if not playing:
		return
	playing = false
	silenced.emit()
