---
name: unplugin-patterns
description: Unplugin patterns covering universal plugin development for Vite, Webpack, Rollup, and esbuild, with auto-imports, component resolution, icon loading, virtual modules, and build-time code transformations.
---

# Unplugin Patterns

This skill should be used when building or using universal bundler plugins with the unplugin ecosystem. It covers plugin creation, auto-imports, component resolution, and build-time transformations.

## When to Use This Skill

Use this skill when you need to:

- Build plugins that work across Vite, Webpack, Rollup, and esbuild
- Set up auto-imports for APIs and components
- Load icons as components at build time
- Create virtual modules and code transformations
- Use unplugin-vue-router or unplugin-auto-import

## Auto Import

```typescript
// vite.config.ts
import AutoImport from "unplugin-auto-import/vite";

export default defineConfig({
  plugins: [
    AutoImport({
      imports: [
        "react",
        "react-router-dom",
        {
          "@tanstack/react-query": ["useQuery", "useMutation", "useQueryClient"],
          "date-fns": ["format", "parseISO", "differenceInDays"],
        },
      ],
      dts: "src/auto-imports.d.ts",
      dirs: ["src/hooks", "src/utils"],
      eslintrc: {
        enabled: true,
        filepath: "./.eslintrc-auto-import.json",
      },
    }),
  ],
});

// After setup, use imports without explicit import statements:
// useState, useEffect, useQuery, format are all available globally

function UserProfile({ id }: { id: string }) {
  // useState auto-imported from react
  const [editing, setEditing] = useState(false);

  // useQuery auto-imported from @tanstack/react-query
  const { data: user } = useQuery({
    queryKey: ["user", id],
    queryFn: () => fetchUser(id),
  });

  // format auto-imported from date-fns
  return <p>Joined: {format(parseISO(user.createdAt), "MMM d, yyyy")}</p>;
}
```

## Vue Component Auto-Resolution

```typescript
// vite.config.ts
import Components from "unplugin-vue-components/vite";
import { NaiveUiResolver } from "unplugin-vue-components/resolvers";

export default defineConfig({
  plugins: [
    Components({
      dirs: ["src/components"],
      resolvers: [NaiveUiResolver()],
      dts: "src/components.d.ts",
      deep: true,
      directoryAsNamespace: true,
    }),
  ],
});

// Components are auto-imported in templates:
// <template>
//   <NButton type="primary">Click me</NButton>
//   <MyCustomComponent />
// </template>
```

## Icons Plugin

```typescript
// vite.config.ts
import Icons from "unplugin-icons/vite";
import IconsResolver from "unplugin-icons/resolver";
import Components from "unplugin-vue-components/vite";

export default defineConfig({
  plugins: [
    Icons({
      compiler: "jsx",
      autoInstall: true,
    }),
    Components({
      resolvers: [
        IconsResolver({
          prefix: "Icon",
        }),
      ],
    }),
  ],
});

// React usage
import IconMdiHome from "~icons/mdi/home";
import IconLucideSettings from "~icons/lucide/settings";

function Nav() {
  return (
    <nav>
      <IconMdiHome className="icon" />
      <IconLucideSettings className="icon" />
    </nav>
  );
}
```

## Creating a Custom Unplugin

```typescript
// my-unplugin/src/index.ts
import { createUnplugin } from "unplugin";

interface Options {
  include?: string[];
  exclude?: string[];
  prefix?: string;
}

const myPlugin = createUnplugin((options: Options = {}) => {
  return {
    name: "my-unplugin",
    enforce: "pre",

    // Transform source code
    transformInclude(id) {
      return id.endsWith(".ts") || id.endsWith(".tsx");
    },
    transform(code, id) {
      // Modify code at build time
      if (code.includes("__DEV__")) {
        return code.replace(/__DEV__/g, "process.env.NODE_ENV !== 'production'");
      }
    },

    // Virtual modules
    resolveId(id) {
      if (id === "virtual:my-module") return "\0virtual:my-module";
    },
    load(id) {
      if (id === "\0virtual:my-module") {
        return `export const config = ${JSON.stringify(options)};`;
      }
    },

    // Build hooks
    buildStart() {
      console.log("Build started with options:", options);
    },
  };
});

// Export for each bundler
export const vitePlugin = myPlugin.vite;
export const webpackPlugin = myPlugin.webpack;
export const rollupPlugin = myPlugin.rollup;
export const esbuildPlugin = myPlugin.esbuild;
export default myPlugin;
```

## File-Based Routing (Vue Router)

```typescript
// vite.config.ts
import VueRouter from "unplugin-vue-router/vite";

export default defineConfig({
  plugins: [
    VueRouter({
      routesFolder: "src/pages",
      dts: "src/typed-router.d.ts",
      extensions: [".vue"],
    }),
  ],
});

// File structure -> routes:
// src/pages/
//   index.vue        -> /
//   about.vue        -> /about
//   users/
//     index.vue      -> /users
//     [id].vue       -> /users/:id
//   [...path].vue    -> catch-all 404
```

## Additional Resources

- unplugin: https://github.com/unjs/unplugin
- unplugin-auto-import: https://github.com/unplugin/unplugin-auto-import
- unplugin-vue-components: https://github.com/unplugin/unplugin-vue-components
- unplugin-icons: https://github.com/unplugin/unplugin-icons
