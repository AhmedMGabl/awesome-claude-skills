---
name: ocaml-programming
description: OCaml programming patterns covering algebraic types, pattern matching, modules, functors, opam, dune build system, and functional programming with imperative features.
---

# OCaml Programming

This skill should be used when writing programs in OCaml. It covers algebraic types, pattern matching, modules, functors, opam, dune, and OCaml idioms.

## When to Use This Skill

Use this skill when you need to:

- Write strongly-typed functional programs in OCaml
- Use algebraic data types and pattern matching
- Build modular code with modules and functors
- Use opam and dune for project management
- Work with the OCaml standard library and ppx extensions

## Basics

```ocaml
(* Variables and functions *)
let greeting = "Hello, OCaml!"

let add x y = x + y

let factorial n =
  let rec aux acc = function
    | 0 -> acc
    | n -> aux (acc * n) (n - 1)
  in
  aux 1 n

(* Pattern matching *)
let describe_list = function
  | [] -> "empty"
  | [_] -> "singleton"
  | _ :: _ -> "multiple elements"

(* Option type *)
let safe_divide x y =
  if y = 0 then None
  else Some (x / y)

let () =
  match safe_divide 10 3 with
  | Some result -> Printf.printf "Result: %d\n" result
  | None -> print_endline "Division by zero"
```

## Algebraic Data Types

```ocaml
(* Variant types *)
type shape =
  | Circle of float
  | Rectangle of float * float
  | Triangle of float * float * float

let area = function
  | Circle r -> Float.pi *. r *. r
  | Rectangle (w, h) -> w *. h
  | Triangle (a, b, c) ->
    let s = (a +. b +. c) /. 2.0 in
    sqrt (s *. (s -. a) *. (s -. b) *. (s -. c))

(* Record types *)
type user = {
  name : string;
  email : string;
  age : int;
}

let create_user ~name ~email ~age = { name; email; age }

(* Parameterized types *)
type 'a tree =
  | Leaf
  | Node of 'a tree * 'a * 'a tree

let rec insert x = function
  | Leaf -> Node (Leaf, x, Leaf)
  | Node (left, v, right) ->
    if x < v then Node (insert x left, v, right)
    else if x > v then Node (left, v, insert x right)
    else Node (left, v, right)
```

## Modules and Functors

```ocaml
(* Module signature *)
module type STACK = sig
  type 'a t
  val empty : 'a t
  val push : 'a -> 'a t -> 'a t
  val pop : 'a t -> ('a * 'a t) option
  val is_empty : 'a t -> bool
end

(* Module implementation *)
module ListStack : STACK = struct
  type 'a t = 'a list
  let empty = []
  let push x s = x :: s
  let pop = function
    | [] -> None
    | x :: xs -> Some (x, xs)
  let is_empty = function [] -> true | _ -> false
end

(* Functor *)
module type COMPARABLE = sig
  type t
  val compare : t -> t -> int
end

module MakeSet (Elt : COMPARABLE) = struct
  type t = Elt.t list
  let empty = []
  let add x s =
    if List.exists (fun y -> Elt.compare x y = 0) s then s
    else x :: s
  let mem x s = List.exists (fun y -> Elt.compare x y = 0) s
end

module IntSet = MakeSet (Int)
```

## Error Handling

```ocaml
(* Result type *)
type ('a, 'b) result = Ok of 'a | Error of 'b

let parse_int s =
  try Ok (int_of_string s)
  with Failure _ -> Error ("Invalid integer: " ^ s)

(* Monadic bind for Result *)
let ( let* ) r f = match r with Ok v -> f v | Error _ as e -> e

let process input =
  let* x = parse_int input in
  let* y = safe_divide x 2 in
  Ok (y + 1)
```

## Dune Build System

```lisp
;; dune-project
(lang dune 3.0)
(name my_project)
(generate_opam_files true)
(source (github user/my_project))

;; bin/dune
(executable
 (name main)
 (public_name my_project)
 (libraries my_project_lib yojson lwt))

;; lib/dune
(library
 (name my_project_lib)
 (libraries str unix))

;; test/dune
(test
 (name test_main)
 (libraries alcotest my_project_lib))
```

## Testing

```ocaml
(* test/test_main.ml *)
let test_factorial () =
  Alcotest.(check int) "factorial 0" 1 (factorial 0);
  Alcotest.(check int) "factorial 5" 120 (factorial 5)

let test_area () =
  let eps = 1e-6 in
  let check_float msg expected actual =
    Alcotest.(check (float eps)) msg expected actual
  in
  check_float "circle" (Float.pi *. 4.0) (area (Circle 2.0));
  check_float "rectangle" 6.0 (area (Rectangle (2.0, 3.0)))

let () =
  Alcotest.run "My Project" [
    "Math", [
      Alcotest.test_case "factorial" `Quick test_factorial;
      Alcotest.test_case "area" `Quick test_area;
    ];
  ]
```

## Additional Resources

- OCaml: https://ocaml.org/docs
- Real World OCaml: https://dev.realworldocaml.org/
- Dune: https://dune.readthedocs.io/
