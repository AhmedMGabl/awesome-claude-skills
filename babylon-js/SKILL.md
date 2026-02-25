---
name: babylon-js
description: Babylon.js 3D engine patterns covering scene setup, meshes, PBR materials, lighting, physics, GUI, XR support, node material editor, and performance optimization.
---

# Babylon.js 3D Engine

This skill should be used when building 3D applications with Babylon.js. It covers scenes, meshes, PBR materials, lighting, physics, GUI, XR, node materials, and performance.

## When to Use This Skill

Use this skill when you need to:

- Build 3D web applications and games
- Create PBR materials and realistic lighting
- Implement physics simulations
- Add 3D GUI overlays and controls
- Support WebXR for VR/AR experiences

## Scene Setup

```typescript
import {
  Engine, Scene, ArcRotateCamera, HemisphericLight, DirectionalLight,
  MeshBuilder, Vector3, Color3, Color4
} from "@babylonjs/core";

const canvas = document.getElementById("renderCanvas") as HTMLCanvasElement;
const engine = new Engine(canvas, true, { stencil: true });

const scene = new Scene(engine);
scene.clearColor = new Color4(0.1, 0.1, 0.15, 1);

// Camera
const camera = new ArcRotateCamera("camera", -Math.PI / 2, Math.PI / 3, 10, Vector3.Zero(), scene);
camera.attachControl(canvas, true);
camera.lowerRadiusLimit = 2;
camera.upperRadiusLimit = 50;

// Lighting
const hemiLight = new HemisphericLight("hemi", new Vector3(0, 1, 0), scene);
hemiLight.intensity = 0.3;

const dirLight = new DirectionalLight("dir", new Vector3(-1, -2, -1), scene);
dirLight.intensity = 0.8;
dirLight.position = new Vector3(5, 10, 5);

// Shadows
const shadowGenerator = new ShadowGenerator(2048, dirLight);
shadowGenerator.useBlurExponentialShadowMap = true;

// Render loop
engine.runRenderLoop(() => scene.render());
window.addEventListener("resize", () => engine.resize());
```

## Meshes and Primitives

```typescript
// Ground
const ground = MeshBuilder.CreateGround("ground", { width: 20, height: 20, subdivisions: 32 }, scene);
ground.receiveShadows = true;

// Box
const box = MeshBuilder.CreateBox("box", { size: 1 }, scene);
box.position.y = 0.5;
shadowGenerator.addShadowCaster(box);

// Sphere
const sphere = MeshBuilder.CreateSphere("sphere", { diameter: 1, segments: 32 }, scene);
sphere.position = new Vector3(2, 0.5, 0);

// Custom mesh from vertices
const customMesh = new Mesh("custom", scene);
const vertexData = new VertexData();
vertexData.positions = [0, 0, 0, 1, 0, 0, 0.5, 1, 0];
vertexData.indices = [0, 1, 2];
vertexData.applyToMesh(customMesh);
```

## PBR Materials

```typescript
import { PBRMaterial, Texture, CubeTexture } from "@babylonjs/core";

const pbr = new PBRMaterial("pbr", scene);
pbr.albedoColor = new Color3(0.8, 0.2, 0.1);
pbr.metallic = 0.8;
pbr.roughness = 0.2;

pbr.albedoTexture = new Texture("textures/albedo.png", scene);
pbr.bumpTexture = new Texture("textures/normal.png", scene);
pbr.metallicTexture = new Texture("textures/metallic.png", scene);

// Environment for reflections
const envTexture = CubeTexture.CreateFromPrefilteredData("environment.env", scene);
scene.environmentTexture = envTexture;

box.material = pbr;
```

## Model Loading

```typescript
import { SceneLoader } from "@babylonjs/core";
import "@babylonjs/loaders/glTF";

const result = await SceneLoader.ImportMeshAsync("", "models/", "character.glb", scene);
const model = result.meshes[0];
model.scaling = new Vector3(0.5, 0.5, 0.5);

// Play animation
const animGroups = result.animationGroups;
animGroups[0].start(true); // Loop first animation
```

## Physics (Havok)

```typescript
import { HavokPlugin } from "@babylonjs/core";
import HavokPhysics from "@babylonjs/havok";

const havokInstance = await HavokPhysics();
const havokPlugin = new HavokPlugin(true, havokInstance);
scene.enablePhysics(new Vector3(0, -9.81, 0), havokPlugin);

// Add physics to ground
new PhysicsAggregate(ground, PhysicsShapeType.BOX, { mass: 0 }, scene);

// Add physics to box
new PhysicsAggregate(box, PhysicsShapeType.BOX, { mass: 1, restitution: 0.5 }, scene);

// Apply force
box.physicsBody?.applyImpulse(new Vector3(0, 5, 2), box.getAbsolutePosition());
```

## 3D GUI

```typescript
import { AdvancedDynamicTexture, Button, TextBlock, StackPanel } from "@babylonjs/gui";

const advancedTexture = AdvancedDynamicTexture.CreateFullscreenUI("UI");

const panel = new StackPanel();
panel.width = "200px";
panel.horizontalAlignment = 0; // left
panel.verticalAlignment = 0;   // top
advancedTexture.addControl(panel);

const button = Button.CreateSimpleButton("btn", "Click Me");
button.width = "150px";
button.height = "40px";
button.color = "white";
button.background = "#0066cc";
button.onPointerUpObservable.add(() => {
  console.log("Clicked!");
});
panel.addControl(button);
```

## Additional Resources

- Babylon.js Docs: https://doc.babylonjs.com/
- Playground: https://playground.babylonjs.com/
- Node Material Editor: https://nme.babylonjs.com/
