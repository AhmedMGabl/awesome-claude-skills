---
name: rollup-bundler
description: Rollup bundler patterns covering tree shaking, plugins, code splitting, library bundling, output formats, watch mode, and custom plugin development.
---

# Rollup Bundler

This skill should be used when bundling JavaScript/TypeScript libraries with Rollup. It covers tree shaking, plugins, code splitting, output formats, and custom plugins.

## When to Use This Skill

Use this skill when you need to:

- Bundle JavaScript/TypeScript libraries
- Optimize tree shaking for smaller bundles
- Generate multiple output formats (ESM, CJS, UMD)
- Create custom Rollup plugins
- Configure code splitting strategies

## Basic Configuration

```javascript
// rollup.config.js
import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

export default {
  input: "src/index.ts",
  output: [
    {
      file: "dist/index.esm.js",
      format: "es",
      sourcemap: true,
    },
    {
      file: "dist/index.cjs.js",
      format: "cjs",
      sourcemap: true,
    },
    {
      file: "dist/index.umd.js",
      format: "umd",
      name: "MyLib",
      sourcemap: true,
      globals: { react: "React" },
    },
  ],
  external: ["react", "react-dom"],
  plugins: [
    resolve(),
    commonjs(),
    typescript({ tsconfig: "./tsconfig.json" }),
    terser(),
  ],
};
```

## Multi-Entry Configuration

```javascript
export default [
  {
    input: {
      index: "src/index.ts",
      utils: "src/utils/index.ts",
      hooks: "src/hooks/index.ts",
    },
    output: {
      dir: "dist",
      format: "es",
      entryFileNames: "[name].js",
      chunkFileNames: "chunks/[name]-[hash].js",
      sourcemap: true,
    },
    external: ["react", "react-dom"],
    plugins: [resolve(), commonjs(), typescript()],
  },
];
```

## CSS and Assets

```javascript
import postcss from "rollup-plugin-postcss";
import url from "@rollup/plugin-url";
import svgr from "@svgr/rollup";

export default {
  plugins: [
    postcss({
      modules: true,
      extract: "styles.css",
      minimize: true,
    }),
    url({ limit: 8 * 1024 }),
    svgr(),
  ],
};
```

## Custom Plugin

```javascript
function myPlugin() {
  return {
    name: "my-rollup-plugin",
    resolveId(source) {
      if (source === "virtual-module") return source;
      return null;
    },
    load(id) {
      if (id === "virtual-module") {
        return `export const version = "${process.env.VERSION}"`;
      }
      return null;
    },
    transform(code, id) {
      if (!id.endsWith(".json5")) return;
      const parsed = JSON5.parse(code);
      return {
        code: `export default ${JSON.stringify(parsed)}`,
        map: { mappings: "" },
      };
    },
    generateBundle(options, bundle) {
      // Post-process or add files to bundle
      this.emitFile({
        type: "asset",
        fileName: "manifest.json",
        source: JSON.stringify({ version: "1.0.0" }),
      });
    },
  };
}
```

## Preserving Modules (for tree shaking by consumers)

```javascript
export default {
  input: "src/index.ts",
  output: {
    dir: "dist",
    format: "es",
    preserveModules: true,
    preserveModulesRoot: "src",
  },
  external: (id) => !id.startsWith(".") && !id.startsWith("/"),
};
```

## Watch Mode

```javascript
export default {
  watch: {
    include: "src/**",
    exclude: "node_modules/**",
    clearScreen: false,
  },
};
```

```bash
rollup -c --watch
```

## Additional Resources

- Rollup: https://rollupjs.org/
- Plugin API: https://rollupjs.org/plugin-development/
- Official Plugins: https://github.com/rollup/plugins
