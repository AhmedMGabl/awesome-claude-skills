---
name: godot-gdscript
description: Godot Engine patterns covering GDScript, scene tree, nodes, signals, physics, animations, tilemaps, UI, shaders, and export templates for 2D and 3D games.
---

# Godot GDScript

This skill should be used when developing games with Godot Engine and GDScript. It covers scene tree, nodes, signals, physics, animations, tilemaps, UI, shaders, and export.

## When to Use This Skill

Use this skill when you need to:

- Build 2D or 3D games with Godot Engine
- Write GDScript game logic and systems
- Configure physics, collisions, and input handling
- Create UI with Godot's Control nodes
- Implement animations and shader effects

## Scene Structure

```
Game (Node2D)
├── Player (CharacterBody2D)
│   ├── Sprite2D
│   ├── CollisionShape2D
│   └── AnimationPlayer
├── Enemies (Node2D)
│   └── Enemy (CharacterBody2D)
├── TileMap
├── Camera2D
└── UI (CanvasLayer)
    ├── HUD
    └── PauseMenu
```

## Player Controller

```gdscript
# player.gd
extends CharacterBody2D

@export var speed := 200.0
@export var jump_velocity := -400.0
@export var gravity_multiplier := 1.0

var health := 100
var is_attacking := false

@onready var sprite := $Sprite2D
@onready var anim_player := $AnimationPlayer
@onready var coyote_timer := $CoyoteTimer

signal health_changed(new_health: int)
signal died

func _physics_process(delta: float) -> void:
    # Gravity
    if not is_on_floor():
        velocity.y += get_gravity().y * gravity_multiplier * delta

    # Jump
    if Input.is_action_just_pressed("jump"):
        if is_on_floor() or not coyote_timer.is_stopped():
            velocity.y = jump_velocity

    # Movement
    var direction := Input.get_axis("move_left", "move_right")
    if direction:
        velocity.x = direction * speed
        sprite.flip_h = direction < 0
    else:
        velocity.x = move_toward(velocity.x, 0, speed)

    # Animations
    if not is_on_floor():
        anim_player.play("jump")
    elif direction:
        anim_player.play("run")
    else:
        anim_player.play("idle")

    var was_on_floor := is_on_floor()
    move_and_slide()

    if was_on_floor and not is_on_floor():
        coyote_timer.start()

func take_damage(amount: int) -> void:
    health -= amount
    health_changed.emit(health)
    if health <= 0:
        died.emit()
```

## Signals and Communication

```gdscript
# game_manager.gd (Autoload Singleton)
extends Node

signal score_changed(new_score: int)
signal game_over
signal level_completed

var score := 0
var current_level := 1

func add_score(points: int) -> void:
    score += points
    score_changed.emit(score)

func _ready() -> void:
    # Connect to player signals
    var player = get_tree().get_first_node_in_group("player")
    if player:
        player.died.connect(_on_player_died)

func _on_player_died() -> void:
    game_over.emit()
    get_tree().paused = true
```

## State Machine

```gdscript
# state_machine.gd
extends Node
class_name StateMachine

var current_state: State
var states: Dictionary = {}

func _ready() -> void:
    for child in get_children():
        if child is State:
            states[child.name.to_lower()] = child
            child.transitioned.connect(_on_state_transitioned)
    current_state = get_child(0) as State
    current_state.enter()

func _physics_process(delta: float) -> void:
    current_state.update(delta)

func _on_state_transitioned(new_state_name: String) -> void:
    var new_state = states.get(new_state_name.to_lower())
    if new_state and new_state != current_state:
        current_state.exit()
        current_state = new_state
        current_state.enter()

# state.gd
extends Node
class_name State

signal transitioned(new_state: String)

func enter() -> void: pass
func exit() -> void: pass
func update(_delta: float) -> void: pass
```

## TileMap and Procedural Generation

```gdscript
func generate_level(width: int, height: int) -> void:
    var tilemap := $TileMap
    var noise := FastNoiseLite.new()
    noise.seed = randi()
    noise.frequency = 0.1

    for x in range(width):
        for y in range(height):
            var value = noise.get_noise_2d(x, y)
            if value > 0.0:
                tilemap.set_cell(0, Vector2i(x, y), 0, Vector2i(0, 0))
```

## UI System

```gdscript
# hud.gd
extends CanvasLayer

@onready var health_bar := %HealthBar
@onready var score_label := %ScoreLabel

func _ready() -> void:
    GameManager.score_changed.connect(_on_score_changed)
    var player = get_tree().get_first_node_in_group("player")
    if player:
        player.health_changed.connect(_on_health_changed)

func _on_health_changed(new_health: int) -> void:
    var tween = create_tween()
    tween.tween_property(health_bar, "value", new_health, 0.3)

func _on_score_changed(new_score: int) -> void:
    score_label.text = "Score: %d" % new_score
```

## Additional Resources

- Godot Docs: https://docs.godotengine.org/
- GDScript Reference: https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/
- Godot Asset Library: https://godotengine.org/asset-library/
