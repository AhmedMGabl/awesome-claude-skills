---
name: rust-wasm
description: Rust WebAssembly patterns covering wasm-bindgen, wasm-pack, JavaScript interop, DOM manipulation, web-sys, js-sys, and webpack/Vite integration.
---

# Rust WebAssembly

This skill should be used when building WebAssembly modules with Rust. It covers wasm-bindgen, wasm-pack, JS interop, DOM access, and bundler integration.

## When to Use This Skill

Use this skill when you need to:

- Compile Rust to WebAssembly for browser or Node.js
- Interop between Rust and JavaScript
- Manipulate the DOM from Rust
- Use web APIs via web-sys and js-sys
- Bundle Wasm with webpack or Vite

## Setup

```bash
cargo install wasm-pack
rustup target add wasm32-unknown-unknown
```

```toml
# Cargo.toml
[lib]
crate-type = ["cdylib", "rlib"]

[dependencies]
wasm-bindgen = "0.2"
web-sys = { version = "0.3", features = ["Document", "Element", "HtmlElement", "Window", "console"] }
js-sys = "0.3"
```

## Basic Exports

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}
```

## Structs and Methods

```rust
#[wasm_bindgen]
pub struct Calculator {
    value: f64,
}

#[wasm_bindgen]
impl Calculator {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Calculator {
        Calculator { value: 0.0 }
    }

    pub fn add(&mut self, n: f64) {
        self.value += n;
    }

    pub fn subtract(&mut self, n: f64) {
        self.value -= n;
    }

    pub fn result(&self) -> f64 {
        self.value
    }

    pub fn reset(&mut self) {
        self.value = 0.0;
    }
}
```

## JavaScript Interop

```rust
#[wasm_bindgen]
extern "C" {
    // Call JS functions
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);

    // Import JS function
    #[wasm_bindgen(js_name = "fetch")]
    fn js_fetch(url: &str) -> js_sys::Promise;
}

#[wasm_bindgen]
pub fn log_message(msg: &str) {
    log(&format!("From Rust: {}", msg));
}
```

## DOM Manipulation

```rust
use web_sys::{Document, Element, window};

#[wasm_bindgen]
pub fn create_element(tag: &str, text: &str) -> Result<Element, JsValue> {
    let document = window()
        .unwrap()
        .document()
        .unwrap();

    let element = document.create_element(tag)?;
    element.set_text_content(Some(text));
    Ok(element)
}

#[wasm_bindgen]
pub fn update_counter(id: &str, count: i32) -> Result<(), JsValue> {
    let document = window().unwrap().document().unwrap();
    let element = document.get_element_by_id(id).unwrap();
    element.set_text_content(Some(&count.to_string()));
    Ok(())
}
```

## Using from JavaScript

```javascript
import init, { greet, Calculator } from './pkg/my_wasm.js';

async function main() {
    await init();

    console.log(greet("World"));

    const calc = new Calculator();
    calc.add(10);
    calc.subtract(3);
    console.log(calc.result()); // 7
}

main();
```

## Build and Pack

```bash
# Build for web bundler (webpack/Vite)
wasm-pack build --target bundler

# Build for direct web use
wasm-pack build --target web

# Build for Node.js
wasm-pack build --target nodejs

# Build with optimizations
wasm-pack build --release
```

## Vite Integration

```javascript
// vite.config.js
import wasm from 'vite-plugin-wasm';

export default {
    plugins: [wasm()],
};
```

## Additional Resources

- wasm-bindgen: https://rustwasm.github.io/wasm-bindgen/
- wasm-pack: https://rustwasm.github.io/wasm-pack/
- Rust Wasm Book: https://rustwasm.github.io/docs/book/
