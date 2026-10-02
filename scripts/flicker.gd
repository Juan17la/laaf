extends Light3D
## Random flicker for unstable lamps.

@export var chance := 0.08

@onready var _base := light_energy


func _process(_delta: float) -> void:
	light_energy = _base * (randf_range(0.0, 0.3) if randf() < chance else 1.0)
