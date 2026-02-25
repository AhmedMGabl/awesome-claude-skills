---
name: pixi-js
description: PixiJS 2D rendering patterns covering sprites, containers, graphics, filters, particle systems, text, interaction events, and WebGL/WebGPU performance.
---

# PixiJS 2D Rendering

This skill should be used when building 2D web graphics with PixiJS. It covers sprites, containers, graphics, filters, particles, text, interaction, and GPU-accelerated rendering.

## When to Use This Skill

Use this skill when you need to:

- Build 2D games and interactive visualizations
- Render sprites, graphics, and text with GPU acceleration
- Apply filters and blend modes
- Handle pointer/touch interaction events
- Optimize rendering for large numbers of sprites

## Application Setup

```typescript
import { Application, Sprite, Container, Graphics, Text, Assets } from "pixi.js";

const app = new Application();
await app.init({
  width: 800,
  height: 600,
  backgroundColor: 0x1a1a2e,
  antialias: true,
  resolution: window.devicePixelRatio || 1,
  autoDensity: true,
});

document.body.appendChild(app.canvas);
```

## Loading Assets

```typescript
// Load single asset
const texture = await Assets.load("bunny.png");

// Load multiple assets
await Assets.load([
  { alias: "hero", src: "hero.png" },
  { alias: "enemy", src: "enemy.png" },
  { alias: "spritesheet", src: "sprites.json" },
]);

// Bundle loading
Assets.addBundle("game", {
  hero: "hero.png",
  tileset: "tileset.png",
  level: "level.json",
});
await Assets.loadBundle("game");
```

## Sprites and Containers

```typescript
// Create sprite
const hero = new Sprite(Assets.get("hero"));
hero.anchor.set(0.5);
hero.position.set(400, 300);
hero.scale.set(2);

// Container (grouping)
const gameWorld = new Container();
gameWorld.addChild(hero);

const enemies = new Container();
for (let i = 0; i < 10; i++) {
  const enemy = new Sprite(Assets.get("enemy"));
  enemy.position.set(Math.random() * 800, Math.random() * 600);
  enemies.addChild(enemy);
}
gameWorld.addChild(enemies);

app.stage.addChild(gameWorld);
```

## Graphics Drawing

```typescript
const graphics = new Graphics();

// Rectangle
graphics.rect(0, 0, 200, 100);
graphics.fill({ color: 0xff6b6b });

// Circle
graphics.circle(300, 200, 50);
graphics.fill({ color: 0x4ecdc4, alpha: 0.8 });

// Line
graphics.moveTo(0, 0);
graphics.lineTo(400, 300);
graphics.stroke({ width: 2, color: 0xffffff });

// Rounded rectangle
graphics.roundRect(50, 250, 200, 80, 16);
graphics.fill({ color: 0x2c3e50 });
graphics.stroke({ width: 2, color: 0x3498db });

app.stage.addChild(graphics);
```

## Interaction

```typescript
const button = new Sprite(Assets.get("button"));
button.eventMode = "static";
button.cursor = "pointer";

button.on("pointerdown", () => {
  button.scale.set(0.95);
});

button.on("pointerup", () => {
  button.scale.set(1);
  console.log("Button clicked!");
});

button.on("pointerover", () => {
  button.tint = 0xcccccc;
});

button.on("pointerout", () => {
  button.tint = 0xffffff;
});
```

## Game Loop

```typescript
app.ticker.add((ticker) => {
  const delta = ticker.deltaTime;

  // Move hero
  hero.x += velocity.x * delta;
  hero.y += velocity.y * delta;

  // Rotate enemies
  enemies.children.forEach((enemy) => {
    enemy.rotation += 0.02 * delta;
  });

  // Check bounds
  if (hero.x < 0) hero.x = app.screen.width;
  if (hero.x > app.screen.width) hero.x = 0;
});
```

## Filters

```typescript
import { BlurFilter, ColorMatrixFilter } from "pixi.js";

// Blur
const blurFilter = new BlurFilter({ strength: 4 });
sprite.filters = [blurFilter];

// Color matrix (grayscale)
const colorMatrix = new ColorMatrixFilter();
colorMatrix.desaturate();
container.filters = [colorMatrix];
```

## Text

```typescript
import { Text, TextStyle } from "pixi.js";

const style = new TextStyle({
  fontFamily: "Arial",
  fontSize: 36,
  fontWeight: "bold",
  fill: ["#ffffff", "#00ff00"],
  stroke: { color: "#000000", width: 4 },
  dropShadow: {
    color: "#000000",
    blur: 4,
    angle: Math.PI / 6,
    distance: 6,
  },
});

const text = new Text({ text: "Score: 0", style });
text.position.set(10, 10);
app.stage.addChild(text);
```

## Additional Resources

- PixiJS Docs: https://pixijs.com/guides
- API Reference: https://pixijs.download/release/docs/
- Examples: https://pixijs.com/examples
