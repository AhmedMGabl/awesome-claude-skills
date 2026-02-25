---
name: crystal-programming
description: Crystal programming patterns covering type inference, macros, concurrency with fibers, channels, C bindings, shards dependency manager, and web development with Lucky.
---

# Crystal Programming

This skill should be used when writing programs in Crystal. It covers type inference, macros, fibers, channels, C bindings, shards, and Lucky framework.

## When to Use This Skill

Use this skill when you need to:

- Write Ruby-like code with C performance
- Use compile-time type checking with inference
- Build concurrent apps with fibers and channels
- Bind to C libraries
- Create web apps with Lucky framework

## Basics

```crystal
# Variables (type inference)
name = "Crystal"
age = 10
pi = 3.14

# Methods
def greet(name : String) : String
  "Hello, #{name}!"
end

def factorial(n : Int32) : Int64
  return 1_i64 if n <= 1
  n.to_i64 * factorial(n - 1)
end

# Pattern matching with case
def describe(value)
  case value
  when Int32   then "integer"
  when String  then "string"
  when .nil?   then "nil"
  when .> 100  then "big number"
  else              "unknown"
  end
end

puts greet("World")
```

## Types and Structs

```crystal
# Struct (value type)
struct Point
  property x : Float64
  property y : Float64

  def initialize(@x, @y)
  end

  def distance(other : Point) : Float64
    Math.sqrt((x - other.x) ** 2 + (y - other.y) ** 2)
  end
end

# Class (reference type)
class User
  getter name : String
  getter email : String
  property age : Int32

  def initialize(@name, @email, @age)
  end

  def to_s(io : IO)
    io << "#{name} <#{email}>"
  end
end

# Enum
enum Color
  Red
  Green
  Blue
end

# Union types
alias StringOrInt = String | Int32
```

## Error Handling

```crystal
# Exceptions
class AppError < Exception; end
class NotFoundError < AppError; end

def find_user(id : Int32) : User
  raise NotFoundError.new("User #{id} not found") if id < 0
  User.new("Alice", "alice@example.com", 30)
end

begin
  user = find_user(-1)
rescue ex : NotFoundError
  puts "Not found: #{ex.message}"
rescue ex
  puts "Error: #{ex.message}"
end

# Nilable types
def maybe_find(id : Int32) : User?
  return nil if id < 0
  User.new("Alice", "alice@example.com", 30)
end

if user = maybe_find(1)
  puts user.name  # user is User, not User?
end
```

## Concurrency

```crystal
# Fibers (lightweight threads)
channel = Channel(String).new

spawn do
  3.times do |i|
    channel.send("Message #{i}")
    sleep 0.1
  end
end

3.times do
  puts channel.receive
end

# Multiple producers
results = Channel(Int32).new

10.times do |i|
  spawn do
    sleep rand(0.1..0.5)
    results.send(i * i)
  end
end

10.times { puts results.receive }

# Select on multiple channels
ch1 = Channel(String).new
ch2 = Channel(Int32).new

spawn { ch1.send("hello") }
spawn { ch2.send(42) }

select
when msg = ch1.receive
  puts "String: #{msg}"
when num = ch2.receive
  puts "Number: #{num}"
end
```

## Macros

```crystal
macro define_method(name, &block)
  def {{name.id}}
    {{block.body}}
  end
end

define_method(:say_hello) { puts "Hello!" }

# JSON mapping macro
require "json"

class ApiResponse
  include JSON::Serializable

  property status : String
  property data : Array(String)
  property count : Int32

  @[JSON::Field(key: "created_at")]
  property created_at : Time?
end

response = ApiResponse.from_json(%q({"status":"ok","data":["a","b"],"count":2}))
puts response.status
```

## C Bindings

```crystal
@[Link("m")]
lib LibM
  fun sqrt(x : Float64) : Float64
  fun pow(base : Float64, exp : Float64) : Float64
end

puts LibM.sqrt(16.0)  # => 4.0
```

## HTTP Server

```crystal
require "http/server"

server = HTTP::Server.new do |context|
  context.response.content_type = "application/json"
  context.response.print %({"message": "Hello from Crystal!"})
end

server.bind_tcp("0.0.0.0", 8080)
puts "Listening on http://0.0.0.0:8080"
server.listen
```

## Shards (Dependencies)

```yaml
# shard.yml
name: my_app
version: 0.1.0
crystal: ">= 1.10.0"

dependencies:
  kemal:
    github: kemalcr/kemal
    version: ~> 1.4
  db:
    github: crystal-lang/crystal-db
  pg:
    github: will/crystal-pg

development_dependencies:
  spec-kemal:
    github: kemalcr/spec-kemal
```

## Testing

```crystal
require "spec"

describe User do
  it "creates a user" do
    user = User.new("Alice", "alice@example.com", 30)
    user.name.should eq "Alice"
    user.age.should eq 30
  end

  it "formats to string" do
    user = User.new("Alice", "alice@example.com", 30)
    user.to_s.should eq "Alice <alice@example.com>"
  end
end

describe "factorial" do
  it "handles base case" do
    factorial(0).should eq 1
  end

  it "calculates correctly" do
    factorial(5).should eq 120
  end
end
```

## Additional Resources

- Crystal: https://crystal-lang.org/reference/
- Crystal API: https://crystal-lang.org/api/
- Shards: https://github.com/crystal-lang/shards
