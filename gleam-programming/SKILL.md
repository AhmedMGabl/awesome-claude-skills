---
name: gleam-programming
description: Gleam programming patterns covering type-safe BEAM development, pattern matching, Result types, OTP processes, Lustre web framework, and JavaScript/Erlang targets.
---

# Gleam Programming

This skill should be used when writing programs in Gleam. It covers type safety on BEAM, pattern matching, Result types, OTP, Lustre, and multi-target compilation.

## When to Use This Skill

Use this skill when you need to:

- Write type-safe programs on the BEAM (Erlang VM)
- Use algebraic types and exhaustive pattern matching
- Build fault-tolerant systems with OTP
- Compile to JavaScript or Erlang
- Build web apps with Lustre framework

## Basics

```gleam
import gleam/io
import gleam/int
import gleam/string
import gleam/list

pub fn main() {
  io.println("Hello, Gleam!")

  let name = "World"
  io.println("Hello, " <> name <> "!")

  // Type annotations (optional, inferred)
  let age: Int = 25
  let pi: Float = 3.14

  // List operations
  let numbers = [1, 2, 3, 4, 5]
  let doubled = list.map(numbers, fn(x) { x * 2 })
  let sum = list.fold(numbers, 0, fn(acc, x) { acc + x })

  io.println("Sum: " <> int.to_string(sum))
}

pub fn factorial(n: Int) -> Int {
  case n {
    0 | 1 -> 1
    n -> n * factorial(n - 1)
  }
}
```

## Custom Types

```gleam
// Enum variants
pub type Color {
  Red
  Green
  Blue
  Custom(r: Int, g: Int, b: Int)
}

// Record type
pub type User {
  User(name: String, email: String, age: Int)
}

// Generic type
pub type Option(a) {
  Some(a)
  None
}

pub type Tree(a) {
  Leaf
  Node(left: Tree(a), value: a, right: Tree(a))
}

pub fn tree_insert(tree: Tree(Int), value: Int) -> Tree(Int) {
  case tree {
    Leaf -> Node(Leaf, value, Leaf)
    Node(left, v, right) if value < v ->
      Node(tree_insert(left, value), v, right)
    Node(left, v, right) if value > v ->
      Node(left, v, tree_insert(right, value))
    _ -> tree
  }
}
```

## Pattern Matching

```gleam
pub fn describe(color: Color) -> String {
  case color {
    Red -> "red"
    Green -> "green"
    Blue -> "blue"
    Custom(r, g, b) ->
      "rgb(" <> int.to_string(r) <> "," <> int.to_string(g) <> "," <> int.to_string(b) <> ")"
  }
}

// Multiple patterns
pub fn fizzbuzz(n: Int) -> String {
  case n % 3, n % 5 {
    0, 0 -> "FizzBuzz"
    0, _ -> "Fizz"
    _, 0 -> "Buzz"
    _, _ -> int.to_string(n)
  }
}

// Guard clauses
pub fn classify_age(age: Int) -> String {
  case age {
    a if a < 0 -> "invalid"
    a if a < 13 -> "child"
    a if a < 18 -> "teenager"
    _ -> "adult"
  }
}
```

## Error Handling with Result

```gleam
import gleam/result

pub type AppError {
  NotFound(String)
  InvalidInput(String)
  DatabaseError(String)
}

pub fn find_user(id: Int) -> Result(User, AppError) {
  case id {
    1 -> Ok(User("Alice", "alice@example.com", 30))
    _ -> Error(NotFound("User not found: " <> int.to_string(id)))
  }
}

pub fn get_user_email(id: Int) -> Result(String, AppError) {
  use user <- result.try(find_user(id))
  Ok(user.email)
}

// Chaining with use
pub fn process(id: Int) -> Result(String, AppError) {
  use user <- result.try(find_user(id))
  use validated <- result.try(validate_user(user))
  Ok("Processed: " <> validated.name)
}
```

## OTP Processes

```gleam
import gleam/erlang/process.{type Subject}
import gleam/otp/actor

pub type Message {
  Increment
  Decrement
  GetCount(reply_to: Subject(Int))
}

pub fn counter_actor() {
  let assert Ok(actor) = actor.start(0, fn(message, count) {
    case message {
      Increment -> actor.continue(count + 1)
      Decrement -> actor.continue(count - 1)
      GetCount(client) -> {
        process.send(client, count)
        actor.continue(count)
      }
    }
  })
  actor
}
```

## Web with Wisp

```gleam
import gleam/http.{Get, Post}
import gleam/http/request.{type Request}
import gleam/http/response.{type Response}
import gleam/json
import wisp.{type Request as WispRequest}

pub fn handle_request(req: WispRequest) -> Response(wisp.Body) {
  case wisp.path_segments(req) {
    [] -> home_page(req)
    ["api", "users"] -> users_handler(req)
    ["api", "users", id] -> user_handler(req, id)
    _ -> wisp.not_found()
  }
}

fn users_handler(req: WispRequest) -> Response(wisp.Body) {
  case req.method {
    Get -> list_users()
    Post -> create_user(req)
    _ -> wisp.method_not_allowed([Get, Post])
  }
}

fn list_users() -> Response(wisp.Body) {
  let body = json.object([
    #("users", json.array([
      json.object([#("name", json.string("Alice"))]),
    ])),
  ])
  wisp.json_response(json.to_string_tree(body), 200)
}
```

## gleam.toml

```toml
name = "my_project"
version = "1.0.0"
target = "erlang"

[dependencies]
gleam_stdlib = ">= 0.34.0 and < 2.0.0"
gleam_http = ">= 3.5.0 and < 4.0.0"
wisp = ">= 0.12.0 and < 1.0.0"
gleam_json = ">= 1.0.0 and < 2.0.0"

[dev-dependencies]
gleeunit = ">= 1.0.0 and < 2.0.0"
```

## Testing

```gleam
import gleeunit
import gleeunit/should

pub fn main() {
  gleeunit.main()
}

pub fn factorial_test() {
  factorial(0) |> should.equal(1)
  factorial(5) |> should.equal(120)
}

pub fn find_user_test() {
  find_user(1) |> should.be_ok()
  find_user(999) |> should.be_error()
}
```

## Additional Resources

- Gleam: https://gleam.run/documentation/
- Gleam Tour: https://tour.gleam.run/
- Hex Packages: https://hex.pm/packages?search=gleam
