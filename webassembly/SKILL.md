---
name: webassembly
description: This skill should be used when developing WebAssembly (Wasm) modules or integrating Wasm into web and server-side applications. It covers Rust-to-Wasm compilation with wasm-pack and wasm-bindgen, AssemblyScript, JavaScript interop, linear memory management, WASI for server-side Wasm, streaming instantiation, bundler integration with Vite and webpack, and performance considerations for React applications.
---

# WebAssembly Development

Guidance for building and integrating WebAssembly modules using Rust, AssemblyScript, and JavaScript/TypeScript.

## When to Use This Skill

Use this skill when you need to:

- Compile Rust to Wasm with wasm-pack and wasm-bindgen
- Write Wasm modules in AssemblyScript
- Expose Wasm functions to JavaScript or call JS from Wasm
- Manage linear memory and share data via typed arrays
- Run Wasm server-side using WASI
- Stream-instantiate large Wasm binaries for fast startup
- Bundle Wasm with Vite or webpack

## Rust to Wasm with wasm-pack

```bash
cargo install wasm-pack
cargo new --lib wasm-math
```

`Cargo.toml`:

```toml
[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
js-sys = "0.3"
web-sys = { version = "0.3", features = ["console"] }

[profile.release]
opt-level = "z"
lto = true
```

`src/lib.rs`:

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u32 {
    match n { 0 => 0, 1 => 1, _ => fibonacci(n - 1) + fibonacci(n - 2) }
}

#[wasm_bindgen]
pub fn process_array(input: &[f64]) -> Vec<f64> {
    input.iter().map(|x| x * x).collect()
}

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

#[wasm_bindgen]
pub fn greet(name: &str) { log(&format!("Hello, {}!", name)); }
```

Build targets:

```bash
wasm-pack build --target web --out-dir pkg       # browser ES module
wasm-pack build --target bundler --out-dir pkg   # Vite/webpack
wasm-pack build --target nodejs --out-dir pkg    # Node.js/WASI
```

## AssemblyScript Basics

AssemblyScript compiles a TypeScript-like language to Wasm without a Rust toolchain.

```bash
npm install --save-dev assemblyscript && npx asinit .
```

`assembly/index.ts`:

```typescript
export function add(a: i32, b: i32): i32 { return a + b; }

export function sumArray(ptr: i32, len: i32): i64 {
  let total: i64 = 0;
  for (let i = 0; i < len; i++) total += load<i32>(ptr + i * 4);
  return total;
}
```

```bash
npx asc assembly/index.ts --outFile build/release.wasm --optimize
```

## JavaScript Interop

Import a wasm-pack module and call exported functions:

```typescript
import init, { fibonacci, process_array } from "./pkg/wasm_math.js";

await init();
console.log(fibonacci(10));                          // 55
console.log(process_array(new Float64Array([1,2,3]))); // [1, 4, 9]
```

Pass a JS callback into Wasm:

```rust
#[wasm_bindgen]
pub fn apply_to_each(values: &[f64], callback: &js_sys::Function) -> Vec<f64> {
    values.iter().map(|v| {
        callback.call1(&JsValue::null(), &JsValue::from_f64(*v))
            .unwrap().as_f64().unwrap()
    }).collect()
}
```

## Memory Management

Share data without copying by writing directly into Wasm linear memory:

```typescript
import init, { alloc, dealloc, get_memory } from "./pkg/wasm_math.js";

await init();
const memory = get_memory();
const ptr = alloc(1024);
new Uint8Array(memory.buffer, ptr, 4).set([1, 2, 3, 4]);
const result = new Float64Array(memory.buffer, ptr, 128);
console.log(result[0]);
dealloc(ptr, 1024);
```

Expose allocator from Rust:

```rust
#[wasm_bindgen] pub fn get_memory() -> JsValue { wasm_bindgen::memory() }

#[wasm_bindgen]
pub fn alloc(size: usize) -> *mut u8 {
    let mut buf: Vec<u8> = Vec::with_capacity(size);
    let ptr = buf.as_mut_ptr();
    std::mem::forget(buf);
    ptr
}

#[wasm_bindgen]
pub fn dealloc(ptr: *mut u8, size: usize) {
    unsafe { Vec::from_raw_parts(ptr, 0, size) };
}
```

## WASI for Server-Side Wasm

```bash
rustup target add wasm32-wasip1
cargo build --target wasm32-wasip1 --release
wasmtime target/wasm32-wasip1/release/my_app.wasm
```

Node.js integration:

```typescript
import { Wasi, Instance, Module } from "@bytecodealliance/wasmtime-js";

const wasi = new Wasi({ args: [], env: {}, preopens: { "/": "." } });
const module = await Module.fromFile("my_app.wasm");
const instance = await Instance.new(module, { wasi: wasi.exports });
wasi.start(instance);
```

## Streaming Instantiation

```typescript
// Compile and instantiate while the binary is still downloading
const { instance } = await WebAssembly.instantiateStreaming(
  fetch("/wasm/module.wasm"),
  { env: { abort: (_msg, _file, line) => console.error(`Abort at ${line}`) } }
);

// Cache compiled module for reuse (e.g., across Web Workers)
const compiled = await WebAssembly.compileStreaming(fetch("/wasm/module.wasm"));
const instance2 = await WebAssembly.instantiate(compiled, importObject);
```

## Bundler Integration

**Vite** — exclude the wasm-pack package from pre-bundling:

```typescript
// vite.config.ts
export default { optimizeDeps: { exclude: ["my-wasm-pkg"] } };
```

```typescript
import init, { fibonacci } from "my-wasm-pkg";
const wasmReady = init();
export async function compute(n: number) { await wasmReady; return fibonacci(n); }
```

**webpack 5** — enable async Wasm experiments:

```javascript
module.exports = {
  experiments: { asyncWebAssembly: true },
  module: { rules: [{ test: /\.wasm$/, type: "webassembly/async" }] },
};
```

## Performance Considerations

- Prefer `--target bundler` so bundlers can tree-shake JS glue code.
- Minimize JS/Wasm boundary crossings; batch data into typed arrays instead of looping over exported functions.
- Use `opt-level = "z"` and `lto = true` to reduce binary size.
- Use `WebAssembly.instantiateStreaming` to overlap download and compilation.
- Offload Wasm execution to a Web Worker to keep the main thread responsive.
- Pass integer pointers rather than `String` values across the boundary to avoid allocation overhead.
- Profile with Chrome DevTools Wasm debugging or `wasmtime --profile` server-side.
