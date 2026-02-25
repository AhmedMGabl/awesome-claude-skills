---
name: vite-build-tool
description: Vite build tool configuration covering project setup, dev server optimization, build configuration, environment variables, library mode, SSR, plugin development, path aliases, proxy configuration, chunk splitting strategies, and migration from Webpack/CRA.
---

# Vite Build Tool

This skill should be used when configuring and optimizing Vite for web projects. It covers configuration, plugins, build optimization, library mode, and SSR.

## When to Use This Skill

Use this skill when you need to:

- Configure Vite for React, Vue, or Svelte projects
- Optimize build output and chunk splitting
- Set up path aliases and environment variables
- Build libraries with Vite's library mode
- Write custom Vite plugins
- Migrate from Webpack or Create React App

## Project Configuration

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@lib": path.resolve(__dirname, "./src/lib"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  build: {
    target: "esnext",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          router: ["react-router-dom"],
          ui: ["@radix-ui/react-dialog", "@radix-ui/react-dropdown-menu"],
        },
      },
    },
  },
});
```

## Environment Variables

```bash
# .env
VITE_API_URL=http://localhost:8080
VITE_APP_TITLE=My App

# .env.production
VITE_API_URL=https://api.example.com
```

```typescript
// Access in code (only VITE_ prefixed vars are exposed)
const apiUrl = import.meta.env.VITE_API_URL;
const isProd = import.meta.env.PROD;
const isDev = import.meta.env.DEV;
const mode = import.meta.env.MODE;

// Type definitions
// env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_APP_TITLE: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## Library Mode

```typescript
// vite.config.ts — building a library
import { defineConfig } from "vite";
import { resolve } from "path";
import dts from "vite-plugin-dts";

export default defineConfig({
  plugins: [dts({ rollupTypes: true })],
  build: {
    lib: {
      entry: resolve(__dirname, "src/index.ts"),
      name: "MyLib",
      formats: ["es", "cjs"],
      fileName: (format) => `index.${format === "es" ? "mjs" : "cjs"}`,
    },
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        globals: { react: "React", "react-dom": "ReactDOM" },
      },
    },
  },
});
```

## Custom Plugin

```typescript
import type { Plugin } from "vite";

function myPlugin(): Plugin {
  return {
    name: "my-plugin",
    configResolved(config) {
      console.log("Resolved config:", config.command);
    },
    transformIndexHtml(html) {
      return html.replace(
        "<!-- INJECT -->",
        `<script>window.__BUILD_TIME__ = "${new Date().toISOString()}"</script>`,
      );
    },
    transform(code, id) {
      if (id.endsWith(".svg")) {
        return `export default ${JSON.stringify(code)}`;
      }
    },
  };
}
```

## SSR Configuration

```typescript
// vite.config.ts
export default defineConfig({
  ssr: {
    external: ["pg", "redis"],          // Don't bundle these
    noExternal: ["@my-org/ui-library"], // Do bundle this
  },
  build: {
    ssr: true,
    rollupOptions: {
      input: "src/entry-server.ts",
    },
  },
});
```

## Optimization Tips

```
TECHNIQUE                        CONFIG
──────────────────────────────────────────────────────
Chunk splitting                  rollupOptions.output.manualChunks
Dependency pre-bundling          optimizeDeps.include / exclude
CSS code splitting               build.cssCodeSplit: true (default)
Asset inlining threshold         build.assetsInlineLimit: 4096
Target browsers                  build.target: 'es2020'
Minification                     build.minify: 'esbuild' (default)
Tree shaking                     Automatic with ES modules
```

## CLI Commands

```bash
npm create vite@latest my-app -- --template react-ts
vite                  # Start dev server
vite build            # Production build
vite preview          # Preview production build
vite optimize         # Pre-bundle dependencies
```

## Additional Resources

- Vite docs: https://vite.dev/
- Vite plugins: https://vite.dev/plugins/
- Rollup options: https://rollupjs.org/configuration-options/
