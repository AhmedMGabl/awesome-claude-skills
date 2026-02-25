---
name: rspack-bundler
description: Rspack bundler patterns covering configuration, loaders, plugins, module federation, code splitting, CSS extraction, dev server, production optimization, and migration from Webpack for high-performance Rust-based bundling.
---

# Rspack Bundler

This skill should be used when building web applications with Rspack. It covers configuration, loaders, plugins, module federation, and Webpack migration.

## When to Use This Skill

Use this skill when you need to:

- Set up a fast Rust-based bundler compatible with Webpack
- Configure loaders and plugins (Webpack-compatible API)
- Enable module federation for micro-frontends
- Optimize production builds with code splitting
- Migrate from Webpack to Rspack

## Basic Configuration

```javascript
// rspack.config.js
const { defineConfig } = require("@rspack/cli");
const { HtmlRspackPlugin } = require("@rspack/core");

module.exports = defineConfig({
  entry: { main: "./src/index.tsx" },
  output: {
    path: __dirname + "/dist",
    filename: "[name].[contenthash:8].js",
    chunkFilename: "[name].[contenthash:8].js",
    publicPath: "/",
    clean: true,
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js", ".jsx"],
    alias: {
      "@": __dirname + "/src",
    },
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        use: {
          loader: "builtin:swc-loader",
          options: {
            jsc: {
              parser: { syntax: "typescript", tsx: true },
              transform: { react: { runtime: "automatic" } },
            },
          },
        },
      },
      {
        test: /\.css$/,
        type: "css",
      },
      {
        test: /\.module\.css$/,
        type: "css/module",
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        type: "asset",
        parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
      },
    ],
  },
  plugins: [
    new HtmlRspackPlugin({
      template: "./index.html",
    }),
  ],
  devServer: {
    port: 3000,
    hot: true,
    historyApiFallback: true,
  },
});
```

## Production Optimization

```javascript
// rspack.config.js
const { CssExtractRspackPlugin } = require("@rspack/core");

module.exports = defineConfig({
  mode: "production",
  optimization: {
    minimize: true,
    splitChunks: {
      chunks: "all",
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendors",
          chunks: "all",
          priority: 10,
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: "react",
          chunks: "all",
          priority: 20,
        },
      },
    },
    runtimeChunk: "single",
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [CssExtractRspackPlugin.loader, "css-loader"],
      },
    ],
  },
  plugins: [
    new CssExtractRspackPlugin({
      filename: "css/[name].[contenthash:8].css",
    }),
  ],
});
```

## Module Federation

```javascript
// rspack.config.js (Host)
const { ModuleFederationPlugin } = require("@rspack/core").container;

module.exports = defineConfig({
  plugins: [
    new ModuleFederationPlugin({
      name: "host",
      remotes: {
        remoteApp: "remoteApp@http://localhost:3001/remoteEntry.js",
      },
      shared: {
        react: { singleton: true, eager: true },
        "react-dom": { singleton: true, eager: true },
      },
    }),
  ],
});

// rspack.config.js (Remote)
module.exports = defineConfig({
  plugins: [
    new ModuleFederationPlugin({
      name: "remoteApp",
      filename: "remoteEntry.js",
      exposes: {
        "./Button": "./src/components/Button",
        "./Header": "./src/components/Header",
      },
      shared: {
        react: { singleton: true },
        "react-dom": { singleton: true },
      },
    }),
  ],
});
```

## Environment Variables

```javascript
// rspack.config.js
const { DefinePlugin } = require("@rspack/core");
const dotenv = require("dotenv");

dotenv.config();

module.exports = defineConfig({
  plugins: [
    new DefinePlugin({
      "process.env.API_URL": JSON.stringify(process.env.API_URL),
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
    }),
  ],
});
```

## Webpack Migration

```javascript
// Key differences from Webpack:
// 1. Use builtin:swc-loader instead of babel-loader
// 2. Use type: "css" instead of css-loader for basic CSS
// 3. Use @rspack/core plugins instead of webpack plugins
// 4. Most webpack loaders work out of the box

// Before (Webpack)
module.exports = {
  module: {
    rules: [
      { test: /\.tsx?$/, use: "babel-loader" },
      { test: /\.css$/, use: ["style-loader", "css-loader"] },
    ],
  },
};

// After (Rspack)
module.exports = {
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: {
          loader: "builtin:swc-loader",
          options: {
            jsc: {
              parser: { syntax: "typescript", tsx: true },
              transform: { react: { runtime: "automatic" } },
            },
          },
        },
      },
      { test: /\.css$/, type: "css" },
    ],
  },
};
```

## Additional Resources

- Rspack docs: https://rspack.dev/
- Configuration: https://rspack.dev/config/
- Migration from Webpack: https://rspack.dev/guide/migration/webpack
