---
name: vite-configuration
description: Vite configuration patterns covering plugins, build optimization, SSR, library mode, environment variables, proxy setup, and custom plugin development.
---

# Vite Configuration

This skill should be used when configuring Vite for modern web projects. It covers plugins, build optimization, SSR, library mode, environment variables, and custom plugins.

## When to Use This Skill

Use this skill when you need to:

- Configure Vite for React/Vue/Svelte projects
- Optimize production builds
- Set up SSR with Vite
- Build libraries with Vite library mode
- Create custom Vite plugins

## Basic Configuration

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@components": path.resolve(__dirname, "src/components"),
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
});
```

## Build Optimization

```typescript
import { defineConfig } from "vite";
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  build: {
    target: "es2020",
    minify: "terser",
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
    chunkSizeWarningLimit: 500,
    terserOptions: {
      compress: { drop_console: true, drop_debugger: true },
    },
  },
  plugins: [
    visualizer({ filename: "dist/stats.html", gzipSize: true }),
  ],
});
```

## Environment Variables

```typescript
// .env files: .env, .env.local, .env.production, .env.development
// Only VITE_ prefixed vars are exposed to client

// vite.config.ts
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    define: {
      __APP_VERSION__: JSON.stringify(env.npm_package_version),
    },
  };
});

// Usage in app
const apiUrl = import.meta.env.VITE_API_URL;
const isDev = import.meta.env.DEV;
const isProd = import.meta.env.PROD;
```

## Library Mode

```typescript
import { defineConfig } from "vite";
import { resolve } from "path";
import dts from "vite-plugin-dts";

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, "src/index.ts"),
      name: "MyLib",
      formats: ["es", "cjs", "umd"],
      fileName: (format) => `my-lib.${format}.js`,
    },
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        globals: { react: "React", "react-dom": "ReactDOM" },
      },
    },
  },
  plugins: [dts({ rollupTypes: true })],
});
```

## SSR Configuration

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  ssr: {
    noExternal: ["@my-org/ui-components"],
    external: ["pg", "better-sqlite3"],
  },
  build: {
    ssr: true,
    rollupOptions: {
      input: "src/entry-server.ts",
    },
  },
});
```

## Custom Plugin

```typescript
import type { Plugin } from "vite";

function myPlugin(): Plugin {
  return {
    name: "vite-plugin-my-transform",
    enforce: "pre",
    transform(code, id) {
      if (!id.endsWith(".md")) return;
      const html = markdownToHtml(code);
      return {
        code: `export default ${JSON.stringify(html)}`,
        map: null,
      };
    },
    configureServer(server) {
      server.middlewares.use("/health", (req, res) => {
        res.end("ok");
      });
    },
  };
}
```

## CSS Configuration

```typescript
export default defineConfig({
  css: {
    modules: {
      localsConvention: "camelCaseOnly",
      generateScopedName: "[name]__[local]___[hash:base64:5]",
    },
    preprocessorOptions: {
      scss: { additionalData: `@import "@/styles/variables.scss";` },
    },
    postcss: "./postcss.config.js",
  },
});
```

## Additional Resources

- Vite: https://vitejs.dev/config/
- Plugins: https://vitejs.dev/plugins/
- SSR: https://vitejs.dev/guide/ssr
