---
name: farm-bundler
description: Farm bundler patterns covering configuration, Rust-based plugins, partial bundling strategy, persistent caching, HMR, CSS modules, lazy compilation, and migration from Webpack or Vite for high-performance builds.
---

# Farm Bundler

This skill should be used when building web applications with the Farm bundler. It covers configuration, plugins, partial bundling, caching, and migration from other bundlers.

## When to Use This Skill

Use this skill when you need to:

- Set up a fast Rust-based bundler for web projects
- Configure partial bundling for optimal loading
- Write custom Farm plugins in Rust or JavaScript
- Migrate from Webpack or Vite to Farm
- Enable persistent caching and lazy compilation

## Basic Configuration

```typescript
// farm.config.ts
import { defineConfig } from "@farmfe/core";

export default defineConfig({
  compilation: {
    input: { index: "./index.html" },
    output: {
      path: "dist",
      publicPath: "/",
      filename: "assets/[name]-[hash].[ext]",
    },
    resolve: {
      alias: {
        "@": "./src",
        "@components": "./src/components",
      },
      extensions: [".ts", ".tsx", ".js", ".jsx"],
    },
    define: {
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
    },
    minify: true,
    sourcemap: true,
    persistentCache: true,
    lazyCompilation: true,
  },
  server: {
    port: 3000,
    hmr: true,
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
  plugins: [
    "@farmfe/plugin-react",
    "@farmfe/plugin-sass",
  ],
});
```

## React Project Setup

```typescript
// farm.config.ts
import { defineConfig } from "@farmfe/core";

export default defineConfig({
  compilation: {
    input: { index: "./index.html" },
    output: {
      path: "dist",
      publicPath: "/",
    },
    css: {
      modules: {
        paths: [".module.css$", ".module.scss$"],
      },
    },
  },
  plugins: [
    "@farmfe/plugin-react",
    "@farmfe/plugin-sass",
  ],
});
```

## Partial Bundling

```typescript
// farm.config.ts
export default defineConfig({
  compilation: {
    partialBundling: {
      targetConcurrentRequests: 25,
      targetMinSize: 20 * 1024, // 20KB min per bundle
      targetMaxSize: 200 * 1024, // 200KB max per bundle
      groups: [
        {
          name: "vendor-react",
          test: ["node_modules/react", "node_modules/react-dom"],
          groupType: "mutable",
        },
        {
          name: "vendor-utils",
          test: ["node_modules/lodash", "node_modules/date-fns"],
          groupType: "mutable",
        },
      ],
    },
  },
});
```

## JavaScript Plugin

```typescript
// my-farm-plugin.ts
import type { JsPlugin } from "@farmfe/core";

export default function myPlugin(): JsPlugin {
  return {
    name: "my-farm-plugin",
    priority: 100,

    config(config) {
      // Modify Farm config
      return config;
    },

    transform: {
      filters: { resolvedPaths: ["\\.tsx$"] },
      executor: async (param) => {
        // Transform source code
        let code = param.content;
        if (code.includes("__APP_VERSION__")) {
          code = code.replace(/__APP_VERSION__/g, '"1.0.0"');
        }
        return { content: code };
      },
    },

    load: {
      filters: { resolvedPaths: ["virtual:.*"] },
      executor: async (param) => {
        if (param.resolvedPath === "virtual:config") {
          return {
            content: `export default ${JSON.stringify({ version: "1.0.0" })}`,
            moduleType: "js",
          };
        }
        return null;
      },
    },
  };
}
```

## Environment Variables

```typescript
// farm.config.ts
export default defineConfig({
  compilation: {
    define: {
      "import.meta.env.VITE_API_URL": JSON.stringify(process.env.API_URL),
    },
  },
});

// .env
API_URL=https://api.example.com

// Usage in code
const apiUrl = import.meta.env.VITE_API_URL;
```

## CSS Configuration

```typescript
// farm.config.ts
export default defineConfig({
  compilation: {
    css: {
      modules: {
        paths: ["\\.module\\.css$", "\\.module\\.scss$"],
        indentName: "[name]-[hash:6]",
      },
      prefixer: {
        targets: ["last 2 versions", "> 1%"],
      },
    },
  },
  plugins: [
    "@farmfe/plugin-sass",
    [
      "@farmfe/plugin-postcss",
      {
        postcssLoadConfig: true,
      },
    ],
  ],
});
```

## Build Commands

```bash
# Development server
npx farm start

# Production build
npx farm build

# Preview production build
npx farm preview

# Clean cache
npx farm clean
```

## Additional Resources

- Farm docs: https://www.farmfe.org/
- Plugins: https://www.farmfe.org/docs/plugins/overview
- Migration guide: https://www.farmfe.org/docs/migration/from-vite
