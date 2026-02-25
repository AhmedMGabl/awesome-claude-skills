---
name: phaser-gamedev
description: Phaser 3 game development patterns covering scenes, sprites, physics, animations, tilemaps, input handling, audio, particle effects, and mobile deployment.
---

# Phaser Game Development

This skill should be used when building browser games with Phaser 3. It covers scenes, sprites, physics, animations, tilemaps, input, audio, particles, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build 2D browser/mobile games with Phaser 3
- Implement arcade or matter.js physics
- Create sprite animations and tilemaps
- Handle keyboard, mouse, and touch input
- Deploy games to web or mobile platforms

## Game Configuration

```typescript
import Phaser from "phaser";

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: "game-container",
  physics: {
    default: "arcade",
    arcade: {
      gravity: { x: 0, y: 300 },
      debug: false,
    },
  },
  scene: [BootScene, GameScene, UIScene],
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
};

const game = new Phaser.Game(config);
```

## Scene Lifecycle

```typescript
class GameScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite;
  private platforms!: Phaser.Physics.Arcade.StaticGroup;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private score = 0;
  private scoreText!: Phaser.GameObjects.Text;

  constructor() {
    super({ key: "GameScene" });
  }

  preload() {
    this.load.spritesheet("player", "assets/player.png", { frameWidth: 32, frameHeight: 48 });
    this.load.image("platform", "assets/platform.png");
    this.load.image("coin", "assets/coin.png");
    this.load.tilemapTiledJSON("level1", "assets/level1.json");
    this.load.audio("jump", "assets/jump.wav");
  }

  create() {
    // Tilemap
    const map = this.make.tilemap({ key: "level1" });
    const tileset = map.addTilesetImage("tiles", "platform");
    const groundLayer = map.createLayer("Ground", tileset!);
    groundLayer?.setCollisionByProperty({ collides: true });

    // Player
    this.player = this.physics.add.sprite(100, 450, "player");
    this.player.setBounce(0.1);
    this.player.setCollideWorldBounds(true);

    // Collisions
    if (groundLayer) {
      this.physics.add.collider(this.player, groundLayer);
    }

    // Animations
    this.anims.create({
      key: "run",
      frames: this.anims.generateFrameNumbers("player", { start: 0, end: 5 }),
      frameRate: 10,
      repeat: -1,
    });

    this.anims.create({
      key: "idle",
      frames: [{ key: "player", frame: 0 }],
      frameRate: 1,
    });

    // Input
    this.cursors = this.input.keyboard!.createCursorKeys();

    // UI
    this.scoreText = this.add.text(16, 16, "Score: 0", {
      fontSize: "24px",
      color: "#fff",
    }).setScrollFactor(0);

    // Camera
    this.cameras.main.startFollow(this.player);
    this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
  }

  update() {
    if (this.cursors.left.isDown) {
      this.player.setVelocityX(-160);
      this.player.anims.play("run", true);
      this.player.setFlipX(true);
    } else if (this.cursors.right.isDown) {
      this.player.setVelocityX(160);
      this.player.anims.play("run", true);
      this.player.setFlipX(false);
    } else {
      this.player.setVelocityX(0);
      this.player.anims.play("idle", true);
    }

    if (this.cursors.up.isDown && this.player.body!.touching.down) {
      this.player.setVelocityY(-330);
      this.sound.play("jump");
    }
  }
}
```

## Collectibles and Scoring

```typescript
// In create()
const coins = this.physics.add.group({
  key: "coin",
  repeat: 11,
  setXY: { x: 12, y: 0, stepX: 70 },
});

coins.children.iterate((child) => {
  const coin = child as Phaser.Physics.Arcade.Image;
  coin.setBounceY(Phaser.Math.FloatBetween(0.2, 0.4));
  return true;
});

this.physics.add.overlap(this.player, coins, (player, coin) => {
  (coin as Phaser.Physics.Arcade.Image).disableBody(true, true);
  this.score += 10;
  this.scoreText.setText(`Score: ${this.score}`);
}, undefined, this);
```

## Enemy AI

```typescript
class Enemy extends Phaser.Physics.Arcade.Sprite {
  private direction = 1;
  private moveSpeed = 100;
  private patrolDistance = 200;
  private startX: number;

  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y, "enemy");
    this.startX = x;
    scene.add.existing(this);
    scene.physics.add.existing(this);
    this.setCollideWorldBounds(true);
  }

  update() {
    this.setVelocityX(this.moveSpeed * this.direction);

    if (Math.abs(this.x - this.startX) > this.patrolDistance) {
      this.direction *= -1;
      this.setFlipX(this.direction < 0);
    }
  }
}
```

## Particle Effects

```typescript
const emitter = this.add.particles(0, 0, "particle", {
  speed: { min: 100, max: 200 },
  angle: { min: 0, max: 360 },
  scale: { start: 0.5, end: 0 },
  lifespan: 800,
  gravityY: 200,
  quantity: 10,
  emitting: false,
});

// Emit on event
function onCoinCollect(x: number, y: number) {
  emitter.setPosition(x, y);
  emitter.explode(20);
}
```

## Additional Resources

- Phaser 3 Docs: https://phaser.io/docs/3.60.0
- Examples: https://phaser.io/examples
- Phaser 3 API: https://newdocs.phaser.io/docs/3.60.0
