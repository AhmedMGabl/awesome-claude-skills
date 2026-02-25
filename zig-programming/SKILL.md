---
name: zig-programming
description: Zig programming patterns covering memory management, comptime, error handling, allocators, C interop, build system, testing, and systems programming.
---

# Zig Programming

This skill should be used when writing systems software with Zig. It covers memory management, comptime, error handling, allocators, C interop, build system, and testing.

## When to Use This Skill

Use this skill when you need to:

- Write systems-level code with manual memory management
- Use compile-time code execution (comptime)
- Handle errors with Zig's error union types
- Interoperate with C libraries
- Build and test Zig projects

## Basics

```zig
const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Hello, {s}!\n", .{"world"});

    // Variables
    var x: i32 = 5;
    x += 1;
    const y: i32 = 10; // immutable

    // Optional
    var maybe: ?i32 = null;
    maybe = 42;
    if (maybe) |val| {
        try stdout.print("Value: {}\n", .{val});
    }
}
```

## Error Handling

```zig
const FileError = error{ NotFound, PermissionDenied, IoError };

fn readFile(path: []const u8) FileError![]u8 {
    const file = std.fs.cwd().openFile(path, .{}) catch |err| switch (err) {
        error.FileNotFound => return FileError.NotFound,
        error.AccessDenied => return FileError.PermissionDenied,
        else => return FileError.IoError,
    };
    defer file.close();

    return file.readToEndAlloc(allocator, 1024 * 1024) catch FileError.IoError;
}

// Usage with try (propagates error)
fn processFile(path: []const u8) !void {
    const data = try readFile(path);
    defer allocator.free(data);
    // process data...
}

// Usage with catch (handle error)
const data = readFile("config.json") catch |err| {
    std.log.err("Failed to read: {}", .{err});
    return;
};
```

## Allocators

```zig
const std = @import("std");

pub fn main() !void {
    // General purpose allocator
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    // ArrayList
    var list = std.ArrayList(i32).init(allocator);
    defer list.deinit();
    try list.append(42);
    try list.appendSlice(&[_]i32{ 1, 2, 3 });

    // HashMap
    var map = std.StringHashMap(i32).init(allocator);
    defer map.deinit();
    try map.put("key", 100);
    if (map.get("key")) |val| {
        std.debug.print("Found: {}\n", .{val});
    }

    // Arena allocator (bulk free)
    var arena = std.heap.ArenaAllocator.init(allocator);
    defer arena.deinit();
    const arena_alloc = arena.allocator();
    const buffer = try arena_alloc.alloc(u8, 1024);
    _ = buffer; // freed when arena.deinit() is called
}
```

## Comptime

```zig
fn Matrix(comptime T: type, comptime rows: usize, comptime cols: usize) type {
    return struct {
        data: [rows][cols]T,

        const Self = @This();

        pub fn init(value: T) Self {
            return .{ .data = [_][cols]T{[_]T{value} ** cols} ** rows };
        }

        pub fn get(self: Self, row: usize, col: usize) T {
            return self.data[row][col];
        }

        pub fn set(self: *Self, row: usize, col: usize, value: T) void {
            self.data[row][col] = value;
        }
    };
}

const Mat3x3 = Matrix(f32, 3, 3);
var m = Mat3x3.init(0.0);
m.set(0, 0, 1.0);
```

## Structs and Methods

```zig
const User = struct {
    name: []const u8,
    email: []const u8,
    age: u32,

    pub fn init(name: []const u8, email: []const u8, age: u32) User {
        return .{ .name = name, .email = email, .age = age };
    }

    pub fn isAdult(self: User) bool {
        return self.age >= 18;
    }

    pub fn format(self: User, comptime _: []const u8, _: std.fmt.FormatOptions, writer: anytype) !void {
        try writer.print("{s} <{s}>", .{ self.name, self.email });
    }
};
```

## C Interop

```zig
const c = @cImport({
    @cInclude("stdio.h");
    @cInclude("stdlib.h");
});

pub fn main() void {
    _ = c.printf("Hello from C: %d\n", @as(c_int, 42));

    const ptr = c.malloc(100) orelse {
        std.debug.print("Allocation failed\n", .{});
        return;
    };
    defer c.free(ptr);
}
```

## Testing

```zig
const std = @import("std");
const expect = std.testing.expect;

test "basic addition" {
    try expect(1 + 1 == 2);
}

test "allocator" {
    const allocator = std.testing.allocator;
    var list = std.ArrayList(u8).init(allocator);
    defer list.deinit();
    try list.append(42);
    try expect(list.items.len == 1);
}
```

## Build System (build.zig)

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "my-app",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    exe.linkLibC();
    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    const run_step = b.step("run", "Run the application");
    run_step.dependOn(&run_cmd.step);

    const tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
    });
    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&b.addRunArtifact(tests).step);
}
```

## Additional Resources

- Zig: https://ziglang.org/documentation/master/
- Zig Learn: https://ziglearn.org/
- Standard Library: https://ziglang.org/documentation/master/std/
