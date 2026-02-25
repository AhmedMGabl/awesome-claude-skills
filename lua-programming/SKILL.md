---
name: lua-programming
description: Lua programming patterns covering tables, metatables, coroutines, C API, LuaRocks, embedding, game scripting, and Neovim plugin development.
---

# Lua Programming

This skill should be used when writing programs in Lua. It covers tables, metatables, coroutines, C API, LuaRocks, embedding, game scripting, and Neovim plugins.

## When to Use This Skill

Use this skill when you need to:

- Write embedded scripting for games or applications
- Use metatables for OOP and operator overloading
- Implement coroutines for cooperative multitasking
- Embed Lua in C/C++ applications
- Create Neovim plugins or game mods

## Basics

```lua
-- Variables
local name = "Lua"
local age = 30
local pi = 3.14
local active = true

-- Functions
local function greet(name)
  return string.format("Hello, %s!", name)
end

-- Multiple returns
local function divide(a, b)
  if b == 0 then
    return nil, "division by zero"
  end
  return a / b, nil
end

local result, err = divide(10, 3)
if err then
  print("Error:", err)
else
  print("Result:", result)
end

-- Closures
local function counter(start)
  local count = start or 0
  return function()
    count = count + 1
    return count
  end
end

local next = counter(0)
print(next()) -- 1
print(next()) -- 2
```

## Tables

```lua
-- Array-like table
local fruits = {"apple", "banana", "cherry"}
table.insert(fruits, "date")

for i, fruit in ipairs(fruits) do
  print(i, fruit)
end

-- Dictionary-like table
local user = {
  name = "Alice",
  email = "alice@example.com",
  age = 30,
}

-- Nested tables
local config = {
  database = {
    host = "localhost",
    port = 5432,
    name = "mydb",
  },
  server = {
    port = 8080,
  },
}

print(config.database.host) -- "localhost"

-- Table as module
local M = {}

function M.add(a, b)
  return a + b
end

function M.multiply(a, b)
  return a * b
end

return M
```

## Metatables and OOP

```lua
-- Class pattern
local Vector = {}
Vector.__index = Vector

function Vector.new(x, y)
  return setmetatable({ x = x, y = y }, Vector)
end

function Vector:length()
  return math.sqrt(self.x ^ 2 + self.y ^ 2)
end

function Vector:__add(other)
  return Vector.new(self.x + other.x, self.y + other.y)
end

function Vector:__tostring()
  return string.format("(%g, %g)", self.x, self.y)
end

local v1 = Vector.new(3, 4)
local v2 = Vector.new(1, 2)
local v3 = v1 + v2
print(v3)          -- (4, 6)
print(v1:length()) -- 5

-- Inheritance
local Entity = {}
Entity.__index = Entity

function Entity.new(name, x, y)
  return setmetatable({ name = name, x = x, y = y }, Entity)
end

function Entity:move(dx, dy)
  self.x = self.x + dx
  self.y = self.y + dy
end

local Player = setmetatable({}, { __index = Entity })
Player.__index = Player

function Player.new(name, x, y, health)
  local self = Entity.new(name, x, y)
  self.health = health or 100
  return setmetatable(self, Player)
end

function Player:takeDamage(amount)
  self.health = math.max(0, self.health - amount)
end
```

## Coroutines

```lua
-- Producer-consumer pattern
local function producer()
  local items = {"apple", "banana", "cherry"}
  for _, item in ipairs(items) do
    coroutine.yield(item)
  end
end

local co = coroutine.create(producer)

while true do
  local ok, value = coroutine.resume(co)
  if not ok or value == nil then break end
  print("Received:", value)
end

-- Iterator with coroutine
local function fibonacci(max)
  return coroutine.wrap(function()
    local a, b = 0, 1
    while a <= max do
      coroutine.yield(a)
      a, b = b, a + b
    end
  end)
end

for num in fibonacci(100) do
  print(num)
end
```

## Error Handling

```lua
-- pcall (protected call)
local ok, result = pcall(function()
  error("something went wrong")
end)

if not ok then
  print("Error:", result)
end

-- xpcall with traceback
local ok, result = xpcall(
  function()
    error("detailed error")
  end,
  function(err)
    return debug.traceback(err, 2)
  end
)

-- Custom error objects
local function validate(input)
  if type(input) ~= "string" then
    error({ code = "INVALID_TYPE", message = "Expected string" })
  end
  if #input == 0 then
    error({ code = "EMPTY", message = "Input cannot be empty" })
  end
  return input
end
```

## Neovim Plugin

```lua
-- lua/myplugin/init.lua
local M = {}

M.config = {
  greeting = "Hello",
  auto_format = true,
}

function M.setup(opts)
  M.config = vim.tbl_deep_extend("force", M.config, opts or {})

  vim.api.nvim_create_user_command("MyGreet", function(args)
    local name = args.args ~= "" and args.args or "World"
    vim.notify(M.config.greeting .. ", " .. name .. "!")
  end, { nargs = "?" })

  vim.api.nvim_create_autocmd("BufWritePre", {
    pattern = "*.lua",
    callback = function()
      if M.config.auto_format then
        vim.lsp.buf.format({ async = false })
      end
    end,
  })
end

return M
```

## LuaRocks

```lua
-- my-project-1.0-1.rockspec
package = "my-project"
version = "1.0-1"
source = {
  url = "git://github.com/user/my-project.git",
  tag = "v1.0",
}
dependencies = {
  "lua >= 5.1",
  "luasocket >= 3.0",
  "cjson >= 2.1",
}
build = {
  type = "builtin",
  modules = {
    ["my-project"] = "src/init.lua",
    ["my-project.utils"] = "src/utils.lua",
  },
}
```

## Additional Resources

- Lua: https://www.lua.org/manual/5.4/
- Programming in Lua: https://www.lua.org/pil/
- LuaRocks: https://luarocks.org/
