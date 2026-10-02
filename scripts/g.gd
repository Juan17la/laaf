class_name G
extends RefCounted
## Safe access to the "Game" autoload (scripts/game.gd) from gameplay code: the headless test scripts run
## without autoloads, and there everything falls back to a plain Normal run with no saves.

const NORMAL := {"name": "Normal", "hurt": 1.0, "enemy": 1.0, "ammo": 1.0}


static func game() -> Node:
	var t := Engine.get_main_loop() as SceneTree
	return t.root.get_node_or_null("Game") if t and t.root else null


static func settings() -> Dictionary:
	var g := game()
	return g.settings() if g else NORMAL


static func loading() -> bool:
	var g := game()
	return g != null and bool(g.get("loading"))


static func take_pending() -> Dictionary:
	var g := game()
	return g.take_pending() if g else {}


static func send(method: String, args := []) -> void:
	## Game.<method>(args...) when the autoload is there (at_step, hurt, unlock, restore_player).
	var g := game()
	if g:
		g.callv(method, args)
