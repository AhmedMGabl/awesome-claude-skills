---
name: style-dictionary
description: Style Dictionary patterns covering design token definitions, multi-platform transforms, custom formats, token composition, theming, and CI/CD integration.
---

# Style Dictionary

This skill should be used when managing design tokens with Style Dictionary. It covers token definitions, platform transforms, custom formats, composition, and CI/CD workflows.

## When to Use This Skill

Use this skill when you need to:

- Define design tokens in a platform-agnostic format
- Generate CSS, JS, iOS, and Android outputs
- Create custom transforms and formats
- Implement multi-brand/multi-theme tokens
- Automate token distribution in CI/CD

## Token Definitions

```json
{
  "color": {
    "base": {
      "blue": {
        "50": { "value": "#eff6ff" },
        "500": { "value": "#0066cc" },
        "700": { "value": "#0052a3" }
      },
      "gray": {
        "100": { "value": "#f3f4f6" },
        "900": { "value": "#111827" }
      }
    },
    "brand": {
      "primary": { "value": "{color.base.blue.500}" },
      "text": { "value": "{color.base.gray.900}" },
      "background": { "value": "#ffffff" }
    }
  },
  "size": {
    "spacing": {
      "xs": { "value": "4px" },
      "sm": { "value": "8px" },
      "md": { "value": "16px" },
      "lg": { "value": "24px" },
      "xl": { "value": "32px" }
    },
    "font": {
      "sm": { "value": "14px" },
      "base": { "value": "16px" },
      "lg": { "value": "18px" },
      "xl": { "value": "24px" }
    },
    "radius": {
      "sm": { "value": "4px" },
      "md": { "value": "8px" },
      "lg": { "value": "12px" },
      "full": { "value": "9999px" }
    }
  }
}
```

## Configuration

```javascript
// config.js
const StyleDictionary = require("style-dictionary");

module.exports = {
  source: ["tokens/**/*.json"],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "dist/css/",
      files: [
        {
          destination: "variables.css",
          format: "css/variables",
          options: { outputReferences: true },
        },
      ],
    },
    js: {
      transformGroup: "js",
      buildPath: "dist/js/",
      files: [
        {
          destination: "tokens.js",
          format: "javascript/es6",
        },
        {
          destination: "tokens.d.ts",
          format: "typescript/es6-declarations",
        },
      ],
    },
    ios: {
      transformGroup: "ios-swift",
      buildPath: "dist/ios/",
      files: [
        {
          destination: "Tokens.swift",
          format: "ios-swift/class.swift",
          className: "DesignTokens",
        },
      ],
    },
    android: {
      transformGroup: "android",
      buildPath: "dist/android/",
      files: [
        {
          destination: "tokens.xml",
          format: "android/resources",
        },
      ],
    },
  },
};
```

## Generated Output

```css
/* dist/css/variables.css */
:root {
  --color-brand-primary: #0066cc;
  --color-brand-text: #111827;
  --color-brand-background: #ffffff;
  --size-spacing-xs: 4px;
  --size-spacing-sm: 8px;
  --size-spacing-md: 16px;
  --size-radius-md: 8px;
}
```

```typescript
// dist/js/tokens.js
export const ColorBrandPrimary = "#0066cc";
export const ColorBrandText = "#111827";
export const SizeSpacingMd = "16px";
```

## Custom Transform

```javascript
StyleDictionary.registerTransform({
  name: "size/pxToRem",
  type: "value",
  matcher: (token) => token.attributes.category === "size",
  transformer: (token) => {
    const px = parseFloat(token.value);
    return `${px / 16}rem`;
  },
});

StyleDictionary.registerFormat({
  name: "custom/tailwind",
  formatter: ({ dictionary }) => {
    const tokens = {};
    dictionary.allProperties.forEach((token) => {
      const path = token.path.join(".");
      tokens[path] = token.value;
    });
    return `module.exports = ${JSON.stringify(tokens, null, 2)}`;
  },
});
```

## Multi-Theme

```javascript
// Build light + dark themes
const themes = ["light", "dark"];

themes.forEach((theme) => {
  const sd = StyleDictionary.extend({
    source: [`tokens/base/**/*.json`, `tokens/themes/${theme}/**/*.json`],
    platforms: {
      css: {
        buildPath: `dist/css/`,
        files: [{
          destination: `${theme}.css`,
          format: "css/variables",
          options: { selector: `[data-theme="${theme}"]` },
        }],
      },
    },
  });
  sd.buildAllPlatforms();
});
```

## Build Script

```json
{
  "scripts": {
    "tokens:build": "style-dictionary build --config config.js",
    "tokens:clean": "rm -rf dist/",
    "tokens:watch": "nodemon --watch tokens -e json --exec 'npm run tokens:build'"
  }
}
```

## Additional Resources

- Style Dictionary: https://amzn.github.io/style-dictionary/
- Transforms: https://amzn.github.io/style-dictionary/#/transforms
- Formats: https://amzn.github.io/style-dictionary/#/formats
