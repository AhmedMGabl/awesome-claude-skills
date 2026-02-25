---
name: nim-programming
description: Nim programming patterns covering type system, macros, metaprogramming, memory management, FFI, async/await, nimble packages, and systems programming.
---

# Nim Programming

This skill should be used when writing programs in Nim. It covers types, macros, metaprogramming, memory management, FFI, async, and nimble package management.

## When to Use This Skill

Use this skill when you need to:

- Write efficient systems code with Python-like syntax
- Use compile-time metaprogramming and macros
- Interoperate with C/C++/JavaScript
- Build async applications
- Manage projects with Nimble

## Basics

```nim
import std/[strformat, strutils, sequtils, tables, algorithm]

# Variables
var mutable = 10
let immutable = 20
const compiletime = 30

# Functions
proc greet(name: string): string =
  fmt"Hello, {name}!"

proc factorial(n: int): int =
  if n <= 1: 1
  else: n * factorial(n - 1)

# Type inference
let numbers = @[1, 2, 3, 4, 5]
let doubled = numbers.map(proc(x: int): int = x * 2)
let evens = numbers.filter(proc(x: int): bool = x mod 2 == 0)

echo greet("World")
echo factorial(5)
echo doubled  # @[2, 4, 6, 8, 10]
```

## Types

```nim
# Enums
type Color = enum
  Red, Green, Blue

# Object types
type
  Shape = ref object of RootObj
    x, y: float

  Circle = ref object of Shape
    radius: float

  Rectangle = ref object of Shape
    width, height: float

# Methods
method area(s: Shape): float {.base.} =
  raise newException(CatchableError, "Override area")

method area(c: Circle): float =
  PI * c.radius * c.radius

method area(r: Rectangle): float =
  r.width * r.height

# Distinct types (type-safe aliases)
type
  Meters = distinct float
  Seconds = distinct float

proc `*`(a: Meters, b: float): Meters {.borrow.}
```

## Error Handling

```nim
import std/options

# Option type
proc findUser(id: int): Option[string] =
  if id == 1: some("Alice")
  else: none(string)

let user = findUser(1)
if user.isSome:
  echo user.get()

# Exceptions
type AppError = object of CatchableError

proc riskyOperation(): string =
  raise newException(AppError, "Something went wrong")

try:
  echo riskyOperation()
except AppError as e:
  echo fmt"Error: {e.msg}"

# Result type
type Result[T] = object
  case ok: bool
  of true: value: T
  of false: error: string
```

## Async/Await

```nim
import std/asyncdispatch
import std/asynchttpserver
import std/asyncnet

proc handleRequest(req: Request) {.async.} =
  let headers = {"Content-Type": "text/plain"}.newHttpHeaders()
  await req.respond(Http200, "Hello, async!", headers)

proc main() {.async.} =
  var server = newAsyncHttpServer()
  server.listen(Port(8080))
  echo "Server running on port 8080"
  while true:
    let (address, client) = await server.socket.acceptAddr()
    asyncCheck server.processClient(client, address, handleRequest)

waitFor main()
```

## Macros and Metaprogramming

```nim
import std/macros

# Template (inline code generation)
template benchmark(name: string, body: untyped) =
  let start = cpuTime()
  body
  let elapsed = cpuTime() - start
  echo fmt"{name}: {elapsed:.4f}s"

benchmark("sort"):
  var data = @[5, 3, 1, 4, 2]
  data.sort()

# Macro (AST manipulation)
macro jsonObject(body: untyped): untyped =
  result = newNimNode(nnkStmtList)
  for child in body:
    if child.kind == nnkCall:
      let key = child[0].strVal
      let value = child[1]
      result.add quote do:
        result[`key`] = `value`
```

## C Interop

```nim
# Import C function
proc printf(format: cstring): cint {.importc, varargs, header: "<stdio.h>".}

# Wrap C library
{.passL: "-lm".}
proc c_sqrt(x: cdouble): cdouble {.importc: "sqrt", header: "<math.h>".}

# Nim string to C string
let name: cstring = "Hello from Nim"
discard printf("%s\n", name)
```

## Nimble Package

```ini
# my_project.nimble
version       = "0.1.0"
author        = "Developer"
description   = "My Nim project"
license       = "MIT"
srcDir        = "src"
bin           = @["my_project"]

requires "nim >= 2.0.0"
requires "jester >= 0.6.0"
requires "norm >= 2.8.0"

task test, "Run tests":
  exec "nim r tests/test_all.nim"
```

## Testing

```nim
import std/unittest

suite "Math functions":
  test "factorial":
    check factorial(0) == 1
    check factorial(5) == 120

  test "greet":
    check greet("World") == "Hello, World!"

  test "findUser":
    check findUser(1).isSome
    check findUser(1).get() == "Alice"
    check findUser(999).isNone
```

## Additional Resources

- Nim: https://nim-lang.org/documentation.html
- Nim by Example: https://nim-by-example.github.io/
- Nimble: https://github.com/nim-lang/nimble
