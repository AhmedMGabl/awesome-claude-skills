---
name: love2d-gamedev
description: LOVE2D game development patterns covering Lua game loops, sprites, physics with Box2D, audio, input handling, tilemaps, state machines, and game distribution.
---

# LOVE2D Game Development

This skill should be used when building 2D games with the LOVE framework in Lua. It covers game loops, sprites, Box2D physics, audio, input, tilemaps, state machines, and distribution.

## When to Use This Skill

Use this skill when you need to:

- Build 2D games with LOVE2D framework
- Implement game physics with Box2D
- Handle keyboard, mouse, and gamepad input
- Create sprite animations and tilemaps
- Package and distribute LOVE2D games

## Main Game Loop

```lua
-- main.lua
function love.load()
    love.window.setTitle("My Game")
    love.window.setMode(800, 600)

    -- Load resources
    player = {
        x = 400, y = 300,
        speed = 200,
        sprite = love.graphics.newImage("player.png"),
        width = 32, height = 32,
        health = 100
    }

    bullets = {}
    enemies = {}
    score = 0

    font = love.graphics.newFont(24)
end

function love.update(dt)
    -- Player movement
    if love.keyboard.isDown("w") or love.keyboard.isDown("up") then
        player.y = player.y - player.speed * dt
    end
    if love.keyboard.isDown("s") or love.keyboard.isDown("down") then
        player.y = player.y + player.speed * dt
    end
    if love.keyboard.isDown("a") or love.keyboard.isDown("left") then
        player.x = player.x - player.speed * dt
    end
    if love.keyboard.isDown("d") or love.keyboard.isDown("right") then
        player.x = player.x + player.speed * dt
    end

    -- Update bullets
    for i = #bullets, 1, -1 do
        bullets[i].x = bullets[i].x + bullets[i].dx * dt
        bullets[i].y = bullets[i].y + bullets[i].dy * dt

        -- Remove off-screen bullets
        if bullets[i].x < 0 or bullets[i].x > 800 or
           bullets[i].y < 0 or bullets[i].y > 600 then
            table.remove(bullets, i)
        end
    end

    -- Collision detection
    checkCollisions()
end

function love.draw()
    -- Draw player
    love.graphics.draw(player.sprite, player.x, player.y)

    -- Draw bullets
    love.graphics.setColor(1, 1, 0)
    for _, b in ipairs(bullets) do
        love.graphics.circle("fill", b.x, b.y, 4)
    end
    love.graphics.setColor(1, 1, 1)

    -- Draw HUD
    love.graphics.setFont(font)
    love.graphics.print("Score: " .. score, 10, 10)
    love.graphics.print("HP: " .. player.health, 10, 40)
end
```

## Input Handling

```lua
function love.keypressed(key)
    if key == "space" then
        shoot()
    end
    if key == "escape" then
        love.event.quit()
    end
    if key == "p" then
        paused = not paused
    end
end

function love.mousepressed(x, y, button)
    if button == 1 then -- Left click
        local dx = x - player.x
        local dy = y - player.y
        local len = math.sqrt(dx * dx + dy * dy)
        table.insert(bullets, {
            x = player.x, y = player.y,
            dx = (dx / len) * 500,
            dy = (dy / len) * 500
        })
    end
end

-- Gamepad support
function love.gamepadpressed(joystick, button)
    if button == "a" then
        jump()
    end
end
```

## Physics (Box2D)

```lua
function love.load()
    world = love.physics.newWorld(0, 400, true) -- gravity

    -- Ground
    ground = {}
    ground.body = love.physics.newBody(world, 400, 580, "static")
    ground.shape = love.physics.newRectangleShape(800, 40)
    ground.fixture = love.physics.newFixture(ground.body, ground.shape)

    -- Player physics body
    player.body = love.physics.newBody(world, 400, 300, "dynamic")
    player.shape = love.physics.newRectangleShape(32, 48)
    player.fixture = love.physics.newFixture(player.body, player.shape, 1)
    player.fixture:setRestitution(0.1)
    player.fixture:setFriction(0.8)

    -- Collision callbacks
    world:setCallbacks(beginContact, endContact)
end

function love.update(dt)
    world:update(dt)
end

function beginContact(a, b, contact)
    local userData_a = a:getUserData()
    local userData_b = b:getUserData()
    -- Handle collision logic
end
```

## Sprite Animation

```lua
function newAnimation(image, frameWidth, frameHeight, duration)
    local animation = {}
    animation.spriteSheet = image
    animation.quads = {}

    for y = 0, image:getHeight() - frameHeight, frameHeight do
        for x = 0, image:getWidth() - frameWidth, frameWidth do
            table.insert(animation.quads,
                love.graphics.newQuad(x, y, frameWidth, frameHeight,
                    image:getDimensions()))
        end
    end

    animation.duration = duration or 1
    animation.currentTime = 0
    return animation
end

function updateAnimation(animation, dt)
    animation.currentTime = animation.currentTime + dt
    if animation.currentTime >= animation.duration then
        animation.currentTime = animation.currentTime - animation.duration
    end
end

function drawAnimation(animation, x, y, r, sx, sy)
    local frameIndex = math.floor(animation.currentTime / animation.duration
        * #animation.quads) + 1
    love.graphics.draw(animation.spriteSheet, animation.quads[frameIndex],
        x, y, r or 0, sx or 1, sy or 1)
end
```

## State Machine

```lua
local states = {}
local currentState = nil

function addState(name, state)
    states[name] = state
end

function setState(name)
    if currentState and currentState.exit then
        currentState.exit()
    end
    currentState = states[name]
    if currentState.enter then
        currentState.enter()
    end
end

-- Define states
addState("menu", {
    enter = function() end,
    update = function(dt) end,
    draw = function()
        love.graphics.printf("Press ENTER to Play", 0, 250, 800, "center")
    end,
    keypressed = function(key)
        if key == "return" then setState("playing") end
    end
})
```

## Additional Resources

- LOVE2D Wiki: https://love2d.org/wiki/Main_Page
- API Reference: https://love2d.org/wiki/love
- LOVE2D Forums: https://love2d.org/forums/
