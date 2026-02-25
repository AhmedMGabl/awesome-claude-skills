---
name: webpack-config
description: Webpack 5 configuration covering entry/output, loaders for TypeScript, CSS, and assets, code splitting with dynamic imports, Module Federation for micro-frontends, dev server with HMR, production optimization, caching strategies, and bundle analysis.
---

# Webpack Configuration

This skill should be used when configuring Webpack 5 for web applications. It covers loaders, code splitting, Module Federation, optimization, and dev server.

## When to Use This Skill

Use this skill when you need to:

- Configure Webpack 5 for a web application
- Set up code splitting and lazy loading
- Implement Module Federation for micro-frontends
- Optimize production bundles
- Configure dev server with HMR

## Basic Configuration

```typescript
// webpack.config.ts
import path from "path";
import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCssExtractPlugin from "mini-css-extract-plugin";
import ForkTsCheckerWebpackPlugin from "fork-ts-checker-webpack-plugin";
import type { Configuration } from "webpack";
import "webpack-dev-server";

const isDev = process.env.NODE_ENV !== "production";

const config: Configuration = {
  mode: isDev ? "development" : "production",
  entry: "./src/index.tsx",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: isDev ? "[name].js" : "[name].[contenthash].js",
    chunkFilename: isDev ? "[name].chunk.js" : "[name].[contenthash].chunk.js",
    clean: true,
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js", ".jsx"],
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "swc-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: [
          isDev ? "style-loader" : MiniCssExtractPlugin.loader,
          "css-loader",
          "postcss-loader",
        ],
      },
      {
        test: /\.(png|jpe?g|gif|svg|webp)$/,
        type: "asset",
        parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
      },
      {
        test: /\.(woff2?|eot|ttf|otf)$/,
        type: "asset/resource",
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({ template: "./public/index.html" }),
    new ForkTsCheckerWebpackPlugin(),
    ...(!isDev ? [new MiniCssExtractPlugin({ filename: "[name].[contenthash].css" })] : []),
  ],
  devServer: {
    port: 3000,
    hot: true,
    historyApiFallback: true,
    proxy: [{ context: ["/api"], target: "http://localhost:8080" }],
  },
  devtool: isDev ? "eval-source-map" : "source-map",
};

export default config;
```

## Code Splitting

```typescript
// Dynamic imports for route-based splitting
const Dashboard = lazy(() => import(/* webpackChunkName: "dashboard" */ "./pages/Dashboard"));
const Settings = lazy(() => import(/* webpackChunkName: "settings" */ "./pages/Settings"));

// Manual chunk splitting in config
optimization: {
  splitChunks: {
    chunks: "all",
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: "vendor",
        chunks: "all",
      },
      common: {
        minChunks: 2,
        chunks: "all",
        name: "common",
        priority: -10,
      },
    },
  },
},
```

## Module Federation (Micro-Frontends)

```typescript
// Host app — webpack.config.ts
import { ModuleFederationPlugin } from "webpack/container";

plugins: [
  new ModuleFederationPlugin({
    name: "host",
    remotes: {
      remoteApp: "remoteApp@http://localhost:3001/remoteEntry.js",
    },
    shared: { react: { singleton: true }, "react-dom": { singleton: true } },
  }),
],

// Remote app — webpack.config.ts
plugins: [
  new ModuleFederationPlugin({
    name: "remoteApp",
    filename: "remoteEntry.js",
    exposes: {
      "./Widget": "./src/components/Widget",
    },
    shared: { react: { singleton: true }, "react-dom": { singleton: true } },
  }),
],
```

## Production Optimization

```typescript
const TerserPlugin = require("terser-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const { BundleAnalyzerPlugin } = require("webpack-bundle-analyzer");

optimization: {
  minimize: true,
  minimizer: [
    new TerserPlugin({ terserOptions: { compress: { drop_console: true } } }),
    new CssMinimizerPlugin(),
  ],
  runtimeChunk: "single",
  moduleIds: "deterministic",
},
plugins: [
  process.env.ANALYZE && new BundleAnalyzerPlugin(),
].filter(Boolean),
```

## Caching Strategy

```typescript
output: {
  filename: "[name].[contenthash].js",  // Cache busting
},
optimization: {
  runtimeChunk: "single",              // Separate runtime for long-term caching
  moduleIds: "deterministic",          // Stable module IDs
},
cache: {
  type: "filesystem",                  // Persistent build cache
  buildDependencies: {
    config: [__filename],
  },
},
```

## CLI Commands

```bash
webpack --mode production             # Production build
webpack serve                         # Start dev server
webpack --profile --json > stats.json # Generate bundle stats
npx webpack-bundle-analyzer stats.json # Analyze bundle
```

## Additional Resources

- Webpack 5 docs: https://webpack.js.org/
- Module Federation: https://webpack.js.org/concepts/module-federation/
- SWC loader: https://swc.rs/docs/usage/webpack
