---
name: fsharp-patterns
description: F# patterns covering discriminated unions, pattern matching, computation expressions, async workflows, Railway-oriented programming, and domain modeling.
---

# F# Patterns

This skill should be used when writing F# functional code. It covers discriminated unions, pattern matching, computation expressions, async workflows, and domain modeling.

## When to Use This Skill

Use this skill when you need to:

- Model domains with discriminated unions
- Use pattern matching for control flow
- Write computation expressions and async workflows
- Apply Railway-oriented programming
- Build type-safe domain models

## Discriminated Unions

```fsharp
type Shape =
    | Circle of radius: float
    | Rectangle of width: float * height: float
    | Triangle of base': float * height: float

type Result<'T, 'E> =
    | Ok of 'T
    | Error of 'E

type OrderStatus =
    | Pending
    | Processing of startedAt: DateTime
    | Shipped of trackingNumber: string
    | Delivered of deliveredAt: DateTime
    | Cancelled of reason: string

let area shape =
    match shape with
    | Circle r -> Math.PI * r * r
    | Rectangle(w, h) -> w * h
    | Triangle(b, h) -> 0.5 * b * h
```

## Pattern Matching

```fsharp
// Active patterns
let (|Even|Odd|) n = if n % 2 = 0 then Even else Odd

let describe n =
    match n with
    | Even -> "even"
    | Odd -> "odd"

// Partial active patterns
let (|Int|_|) (s: string) =
    match System.Int32.TryParse(s) with
    | true, v -> Some v
    | _ -> None

let (|Float|_|) (s: string) =
    match System.Double.TryParse(s) with
    | true, v -> Some v
    | _ -> None

let parseInput input =
    match input with
    | Int i -> printfn "Integer: %d" i
    | Float f -> printfn "Float: %f" f
    | s -> printfn "String: %s" s

// Guard clauses
let classify age =
    match age with
    | a when a < 0 -> failwith "Invalid age"
    | a when a < 13 -> "child"
    | a when a < 18 -> "teenager"
    | a when a < 65 -> "adult"
    | _ -> "senior"

// List patterns
let rec sum list =
    match list with
    | [] -> 0
    | head :: tail -> head + sum tail
```

## Pipelines and Composition

```fsharp
// Pipeline operator
let result =
    [1..100]
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * x)
    |> List.take 10
    |> List.sum

// Function composition
let processName = String.trim >> String.toLower >> String.replace " " "-"
let slug = processName "  Hello World  " // "hello-world"

// Partial application
let add x y = x + y
let addFive = add 5
let result = addFive 3 // 8

let multiply x y = x * y
let double = multiply 2
let triple = multiply 3
```

## Railway-Oriented Programming

```fsharp
type ValidationError =
    | NameRequired
    | EmailInvalid of string
    | AgeTooLow of int

type Result<'T> = Result<'T, ValidationError list>

let validateName (name: string) =
    if String.IsNullOrWhiteSpace(name) then Error [NameRequired]
    else Ok name

let validateEmail (email: string) =
    if email.Contains("@") then Ok email
    else Error [EmailInvalid email]

let validateAge age =
    if age >= 18 then Ok age
    else Error [AgeTooLow age]

// Bind operator
let (>>=) result f =
    match result with
    | Ok v -> f v
    | Error e -> Error e

// Combine validations
let validate name email age =
    let results = [
        validateName name |> Result.map ignore
        validateEmail email |> Result.map ignore
        validateAge age |> Result.map ignore
    ]
    let errors =
        results
        |> List.choose (function Error e -> Some e | _ -> None)
        |> List.concat
    if errors.IsEmpty then Ok { Name = name; Email = email; Age = age }
    else Error errors
```

## Async Workflows

```fsharp
open System.Net.Http

let fetchUrl (url: string) = async {
    use client = new HttpClient()
    let! response = client.GetStringAsync(url) |> Async.AwaitTask
    return response
}

let fetchMultiple urls = async {
    let! results =
        urls
        |> List.map fetchUrl
        |> Async.Parallel
    return results |> Array.toList
}

// Task computation expression (.NET 6+)
open System.Threading.Tasks

let fetchAsync (url: string) = task {
    use client = new HttpClient()
    let! response = client.GetStringAsync(url)
    return response
}
```

## Computation Expressions

```fsharp
// Custom builder for option
type OptionBuilder() =
    member _.Bind(opt, f) =
        match opt with
        | Some v -> f v
        | None -> None
    member _.Return(v) = Some v
    member _.ReturnFrom(opt) = opt
    member _.Zero() = None

let option = OptionBuilder()

let tryDivide x y =
    if y = 0 then None else Some(x / y)

let calculation = option {
    let! a = tryDivide 10 2    // Some 5
    let! b = tryDivide a 0     // None -> short-circuits
    return b + 1
}
// result: None
```

## Domain Modeling

```fsharp
// Making illegal states unrepresentable
type EmailAddress = private EmailAddress of string
module EmailAddress =
    let create (s: string) =
        if s.Contains("@") then Ok(EmailAddress s)
        else Error "Invalid email"
    let value (EmailAddress s) = s

type NonEmptyString = private NonEmptyString of string
module NonEmptyString =
    let create (s: string) =
        if String.IsNullOrWhiteSpace(s) then Error "String cannot be empty"
        else Ok(NonEmptyString(s.Trim()))
    let value (NonEmptyString s) = s

type Money = { Amount: decimal; Currency: string }
type OrderLine = { ProductId: int; Quantity: int; Price: Money }
type Order = {
    Id: int
    Lines: OrderLine list
    Status: OrderStatus
}

let orderTotal order =
    order.Lines
    |> List.sumBy (fun l -> l.Price.Amount * decimal l.Quantity)
```

## Additional Resources

- F#: https://learn.microsoft.com/en-us/dotnet/fsharp/
- F# for Fun and Profit: https://fsharpforfunandprofit.com/
- Computation Expressions: https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/computation-expressions
