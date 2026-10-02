extends Node3D
## Constant yaw rotation (lighthouse beam).

@export var speed := 0.6


func _process(delta: float) -> void:
	rotate_y(speed * delta)
