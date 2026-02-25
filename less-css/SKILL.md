---
name: less-css
description: Less CSS patterns covering variables, mixins, functions, guards, namespaces, lazy evaluation, and integration with build tools.
---

# Less CSS

This skill should be used when writing stylesheets with Less CSS preprocessor. It covers variables, mixins, functions, guards, namespaces, and build tool integration.

## When to Use This Skill

Use this skill when you need to:

- Write maintainable stylesheets with Less
- Create reusable mixins and functions
- Use guards for conditional styles
- Organize code with namespaces
- Integrate Less with Webpack or Vite

## Variables and Operations

```less
// variables.less
@primary: #0066cc;
@secondary: #6c757d;
@font-stack: "Inter", system-ui, sans-serif;
@base-spacing: 8px;
@border-radius: 4px;

// Operations
@double-spacing: @base-spacing * 2;
@half-primary: lighten(@primary, 20%);

body {
  font-family: @font-stack;
  color: darken(@secondary, 20%);
}

.card {
  padding: @base-spacing * 2;
  border-radius: @border-radius;
  border: 1px solid fade(@secondary, 30%);
}
```

## Mixins

```less
// Parametric mixins
.border-radius(@radius: @border-radius) {
  border-radius: @radius;
}

.flex-center(@direction: row) {
  display: flex;
  flex-direction: @direction;
  align-items: center;
  justify-content: center;
}

.truncate(@lines: 1) when (@lines = 1) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.truncate(@lines) when (@lines > 1) {
  display: -webkit-box;
  -webkit-line-clamp: @lines;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

// Usage
.hero {
  .flex-center(column);
  padding: @base-spacing * 4;
}

.title {
  .truncate(2);
}
```

## Guards (Conditionals)

```less
.button(@bg) when (lightness(@bg) > 50%) {
  color: #333;
  background: @bg;
}

.button(@bg) when (lightness(@bg) <= 50%) {
  color: white;
  background: @bg;
}

.btn-primary { .button(@primary); }
.btn-light { .button(#f8f9fa); }

// Type guards
.set-width(@value) when (isnumber(@value)) {
  width: @value;
}

.set-width(@value) when (ispercentage(@value)) {
  width: @value;
  max-width: 100%;
}
```

## Namespaces

```less
#utils() {
  .visually-hidden() {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
  }

  .clearfix() {
    &::after {
      content: "";
      display: table;
      clear: both;
    }
  }
}

.sr-only {
  #utils.visually-hidden();
}
```

## Loops and Iteration

```less
// Generate spacing utilities
.generate-spacing(@i: 0) when (@i <= 5) {
  .p-@{i} { padding: (@i * @base-spacing); }
  .m-@{i} { margin: (@i * @base-spacing); }
  .generate-spacing(@i + 1);
}

.generate-spacing();

// Generate grid columns
.generate-columns(@n, @i: 1) when (@i =< @n) {
  .col-@{i} {
    width: (@i / @n * 100%);
  }
  .generate-columns(@n, @i + 1);
}

.generate-columns(12);
```

## Imports

```less
// main.less
@import "variables";
@import "mixins";
@import (reference) "bootstrap/less/bootstrap"; // import without output
@import (once) "shared";  // import only once
```

## Build Integration

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.less$/,
        use: ["style-loader", "css-loader", "less-loader"],
      },
    ],
  },
};

// vite.config.ts
export default defineConfig({
  css: {
    preprocessorOptions: {
      less: {
        additionalData: '@import "./src/styles/variables.less";',
        javascriptEnabled: true,
      },
    },
  },
});
```

## Additional Resources

- Less: https://lesscss.org/
- Functions: https://lesscss.org/functions/
- Usage: https://lesscss.org/usage/
