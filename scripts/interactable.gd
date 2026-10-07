class_name Interactable
extends Node3D
## Anything the player can press E on: notes, doors, NPCs, pickups. The chapter director connects
## `used`; `once` disables it after the first use. `auto` fires on touch (ammo, bandages).
## Marker: a glowing dot in view within SHOW_DIST; the one the player would use becomes an
## "[E] action" keycap (billboarded, drawn over geometry). Auto pickups get a bobbing glint + label.
## `item` (an ItemFx kind) shows the thing itself with its particle tell: loose (auto) pickups hover and
## spin, the rest sit on whatever is under the marker. Once used, the model becomes `taken`: a scene may claim
## it (Chapter1Director.claim_item → Actor.take reaches for it where it lies); unclaimed it flies into the
## player's hands. Fixtures (the radio's static) just stop.

signal used(by: Node)

const ItemFx := preload("res://scripts/item_fx.gd")

const SHOW_DIST := 8.0
const PX := 0.0035  ## Sprite3D/Label3D pixel size with fixed_size: ~1 screen px at 640x360, fov 65

@export var prompt := "Use"
@export var once := true
@export var auto := false
var enabled := true
var glow := Color(1.0, 0.85, 0.5)

static var _dot_tex: Texture2D
static var _key_tex: Texture2D
var _light: OmniLight3D
var _mark: Node3D
var _dot: Sprite3D
var _key: Sprite3D
var _key_e: Label3D
var _text: Label3D
var _t := randf() * 10.0
var _seen := true
var _ray_cd := 0.0
var _item: Node3D
var _kind := ""
var taken: Node3D  ## the used item's model, left in the world for a scene to claim
var _flutter := false  ## paper: a faint draught lifts its edge
var _placed := false
var _lift := 0.0


static func make(parent: Node, pos: Vector3, prompt_text: String, cb: Callable, glow_color := Color(), is_auto := false,
		item := "") -> Interactable:
	var n := Interactable.new()
	n.prompt = prompt_text
	n.auto = is_auto
	if glow_color != Color():
		n.glow = glow_color
		n._light = OmniLight3D.new()
		n._light.light_color = glow_color
		n._light.omni_range = 2.0
		n.add_child(n._light)
	if item != "":
		n._item = ItemFx.item(item)
		n._kind = item
		n._flutter = item in ["note", "photo", "drawing"]
		n.add_child(n._item)
	parent.add_child(n)
	n.global_position = pos
	n.used.connect(cb)
	return n


func _ready() -> void:
	add_to_group("interactable")
	_mark = Node3D.new()
	add_child(_mark)
	_dot = _sprite(_dot_texture(), 0)
	_dot.modulate = glow
	_key = _sprite(_keycap_texture(), 1)
	_key_e = _label("E", 2, HORIZONTAL_ALIGNMENT_CENTER)
	_key_e.modulate = Color(1.0, 0.95, 0.8)
	_text = _label(prompt, 2, HORIZONTAL_ALIGNMENT_LEFT)
	_text.offset = Vector2(11, 0)  # start just right of the keycap
	if auto:
		_text.font_size = 9
		_text.offset = Vector2(6, 0)
	_mark.visible = false


func _sprite(tex: Texture2D, prio: int) -> Sprite3D:
	var s := Sprite3D.new()
	s.texture = tex
	s.pixel_size = PX
	s.fixed_size = true
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.no_depth_test = true
	s.shaded = false
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	s.render_priority = prio
	_mark.add_child(s)
	return s


func _label(txt: String, prio: int, align: HorizontalAlignment) -> Label3D:
	var l := Label3D.new()
	l.text = txt
	l.font_size = 10
	l.outline_size = 4
	l.outline_modulate = Color(0, 0, 0, 0.9)
	l.pixel_size = PX
	l.fixed_size = true
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	l.shaded = false
	l.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	l.horizontal_alignment = align
	l.render_priority = prio + 1
	l.outline_render_priority = prio
	_mark.add_child(l)
	return l


static func _dot_texture() -> Texture2D:
	if not _dot_tex:
		var g := Gradient.new()
		g.set_color(0, Color(1, 1, 1, 1))
		g.set_color(1, Color(1, 1, 1, 0))
		g.add_point(0.25, Color(1, 1, 1, 0.95))
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(0.5, 0.0)
		t.width = 18
		t.height = 18
		_dot_tex = t
	return _dot_tex


static func _keycap_texture() -> Texture2D:
	## 15x16 PS2-ish keycap: light rim, dark face, thicker bottom edge.
	if not _key_tex:
		var img := Image.create(15, 16, false, Image.FORMAT_RGBA8)
		img.fill(Color(0, 0, 0, 0))
		img.fill_rect(Rect2i(1, 0, 13, 16), Color(0.85, 0.8, 0.68))
		img.fill_rect(Rect2i(0, 1, 15, 14), Color(0.85, 0.8, 0.68))
		img.fill_rect(Rect2i(1, 13, 13, 3), Color(0.45, 0.42, 0.36))
		img.fill_rect(Rect2i(1, 1, 13, 12), Color(0.1, 0.09, 0.08, 0.92))
		_key_tex = ImageTexture.create_from_image(img)
	return _key_tex


func _process(delta: float) -> void:
	_t += delta
	if _item and auto:
		_item.rotation.y += delta * 1.5
		_item.position.y = -0.2 + sin(_t * 2.0) * 0.03
	elif _item and _flutter:
		_item.rotation.z = sin(_t * 5.0) * sin(_t * 0.7) * 0.04
	var pulse := 0.5 + 0.5 * sin(_t * 3.0)
	if _light:
		_light.light_energy = 0.45 + 0.35 * pulse if enabled else 0.0
	var p := get_tree().get_first_node_in_group("player") as Node3D
	var cam := get_viewport().get_camera_3d()
	var on := enabled and p != null and cam != null and bool(p.get("controls_enabled")) \
		and p.global_position.distance_to(global_position) < SHOW_DIST \
		and not cam.is_position_behind(global_position)
	var target: bool = on and not auto and p.has_method("interact_target") and p.interact_target() == self
	if on and not target:
		_ray_cd -= delta
		if _ray_cd <= 0.0:
			_ray_cd = 0.2
			_seen = _visible_from(cam, p)
		on = _seen
	_mark.visible = on
	if not on:
		return
	_mark.position.y = sin(_t * 2.2) * 0.04 + (0.12 if target else 0.0)
	_key.visible = target
	_key_e.visible = target
	_dot.visible = not target
	_text.visible = auto  # in reach, the HUD keycap prompt carries the text (no duplicate)
	if target:
		_text.text = prompt
		_key.modulate = Color(1, 1, 1).lerp(glow, 0.35 * pulse)
		_text.modulate = Color(0.95, 0.92, 0.82)
	else:
		var s := 0.8 + 0.35 * pulse
		_dot.scale = Vector3.ONE * s
		_dot.modulate.a = 0.65 + 0.35 * pulse
		_text.modulate = Color(glow, 0.85)


func _visible_from(cam: Camera3D, p: Node) -> bool:
	## Line of sight camera → marker (anything within 0.8 m of the marker counts as the object itself).
	var q := PhysicsRayQueryParameters3D.create(cam.global_position, global_position, 1)
	if p is CollisionObject3D:
		q.exclude = [p.get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	return hit.is_empty() or hit.position.distance_to(global_position) < 0.8


func _rest_item() -> void:
	## Sit the item on whatever is under the marker (desk, floor); over nothing it stays just below it.
	var q := PhysicsRayQueryParameters3D.create(global_position + Vector3.UP * 0.3,
		global_position + Vector3.DOWN * 0.6, 1)
	var p := get_tree().get_first_node_in_group("player")
	if p is CollisionObject3D:
		q.exclude = [p.get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	_item.global_position.y = (hit.position.y if hit else global_position.y - 0.15) + _lift


func lay(yaw := 0.0) -> Interactable:
	## The item lies on its side (a weapon on the floor rather than stood on its edge).
	if _item:
		_item.rotation = Vector3(0, yaw, PI / 2.0)
		_lift = 0.03
	return self


func _physics_process(_delta: float) -> void:
	if _item and not auto and not _placed:
		_placed = true
		_rest_item()
	if not auto or not enabled:
		return
	var p := get_tree().get_first_node_in_group("player") as Node3D
	if p and p.global_position.distance_to(global_position) < 1.2:
		interact(p)


func interact(by: Node) -> void:
	if not enabled:
		return
	Snd.sfx("pickup" if once else "click", global_position, -5.0)
	if once:
		enabled = false
		if _item and ItemFx.ITEMS.get(_kind, [[], Vector3.ONE])[1] != Vector3.ZERO:  # a thing: hand it over (header)
			taken = _item
			_item = null
			taken.reparent(get_parent())
			get_tree().create_timer(0.0 if auto else 0.12).timeout.connect(_collect.bind(taken, by))
		elif _item:  # a fixture's tell
			_item.queue_free()
			_item = null
		visible = false
	used.emit(by)


static func _collect(item: Node3D, by: Node) -> void:
	## Nobody staged the pickup: it zips into the player's hands and is gone.
	if not is_instance_valid(item) or item.has_meta("claimed"):
		return
	item.set_meta("claimed", true)
	for p in item.find_children("*", "CPUParticles3D", true, false):
		p.emitting = false
	var to: Vector3 = (by as Node3D).global_position + Vector3.UP * 1.0 if by is Node3D else item.global_position
	var tw := item.create_tween().set_parallel()
	tw.tween_property(item, "global_position", to, 0.2).set_ease(Tween.EASE_IN)
	tw.tween_property(item, "scale", Vector3.ONE * 0.15, 0.2)
	tw.chain().tween_callback(item.queue_free)
