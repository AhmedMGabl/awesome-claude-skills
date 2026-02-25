---
name: webpack-configuration
description: Webpack configuration patterns covering entry/output, loaders, plugins, code splitting, tree shaking, dev server, module federation, and production optimization.
---

# Webpack Configuration

This skill should be used when configuring Webpack for JavaScript/TypeScript projects. It covers loaders, plugins, code splitting, tree shaking, dev server, and module federation.

## When to Use This Skill

Use this skill when you need to:

- Configure Webpack for complex build pipelines
- Set up code splitting and lazy loading
- Optimize bundles for production
- Use Module Federation for micro-frontends
- Configure dev server with HMR

## Basic Configuration

```javascript
// webpack.config.js
const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  entry: "./src/index.ts",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].[contenthash].js",
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
        use: "ts-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader", "postcss-loader"],
      },
      {
        test: /\.(png|svg|jpg|gif)$/,
        type: "asset",
        parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({ template: "./src/index.html" }),
  ],
};
```

## Production Optimization

```javascript
const TerserPlugin = require("terser-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { BundleAnalyzerPlugin } = require("webpack-bundle-analyzer");

module.exports = {
  mode: "production",
  devtool: "source-map",
  output: {
    filename: "[name].[contenthash:8].js",
    chunkFilename: "[name].[contenthash:8].chunk.js",
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: { drop_console: true },
        },
      }),
      new CssMinimizerPlugin(),
    ],
    splitChunks: {
      chunks: "all",
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendors",
          chunks: "all",
        },
        common: {
          minChunks: 2,
          priority: -10,
          reuseExistingChunk: true,
        },
      },
    },
    runtimeChunk: "single",
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "[name].[contenthash:8].css",
    }),
    new BundleAnalyzerPlugin({ analyzerMode: "static", openAnalyzer: false }),
  ],
};
```

## Code Splitting

```javascript
// Dynamic imports for route-based splitting
const routes = {
  "/dashboard": () => import(/* webpackChunkName: "dashboard" */ "./pages/Dashboard"),
  "/settings": () => import(/* webpackChunkName: "settings" */ "./pages/Settings"),
};

// Prefetch hints
import(/* webpackPrefetch: true */ "./pages/Dashboard");
import(/* webpackPreload: true */ "./critical-module");
```

## Dev Server

```javascript
module.exports = {
  mode: "development",
  devtool: "eval-source-map",
  devServer: {
    port: 3000,
    hot: true,
    historyApiFallback: true,
    proxy: [
      {
        context: ["/api"],
        target: "http://localhost:8080",
        changeOrigin: true,
      },
    ],
    static: { directory: path.join(__dirname, "public") },
  },
};
```

## Module Federation

```javascript
const { ModuleFederationPlugin } = require("webpack").container;

// Host app
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "host",
      remotes: {
        dashboard: "dashboard@http://localhost:3001/remoteEntry.js",
        shared: "shared@http://localhost:3002/remoteEntry.js",
      },
      shared: {
        react: { singleton: true, requiredVersion: "^18.0.0" },
        "react-dom": { singleton: true, requiredVersion: "^18.0.0" },
      },
    }),
  ],
};

// Remote app
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "dashboard",
      filename: "remoteEntry.js",
      exposes: {
        "./DashboardApp": "./src/App",
        "./Widget": "./src/components/Widget",
      },
      shared: {
        react: { singleton: true },
        "react-dom": { singleton: true },
      },
    }),
  ],
};
```

## Environment Variables

```javascript
const webpack = require("webpack");
const dotenv = require("dotenv");

const env = dotenv.config().parsed || {};

module.exports = {
  plugins: [
    new webpack.DefinePlugin({
      "process.env": JSON.stringify(
        Object.fromEntries(
          Object.entries(env).filter(([key]) => key.startsWith("APP_"))
        )
      ),
    }),
  ],
};
```

## Additional Resources

- Webpack: https://webpack.js.org/concepts/
- Module Federation: https://webpack.js.org/concepts/module-federation/
- Optimization: https://webpack.js.org/guides/build-performance/
