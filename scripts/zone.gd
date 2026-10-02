extends Area3D
## Shows the zone title when the player walks in.

@export var zone_name := ""


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node3D) -> void:
	if body is CharacterBody3D:
		get_tree().call_group("hud", "show_zone", zone_name)
