---
name: threejs-3d
description: Three.js 3D graphics patterns covering scene setup, geometries, materials, lighting, cameras, GLTF loading, animations, shaders, post-processing, and performance optimization.
---

# Three.js 3D Graphics

This skill should be used when building 3D web experiences with Three.js. It covers scenes, geometries, materials, lighting, GLTF models, animations, shaders, and post-processing.

## When to Use This Skill

Use this skill when you need to:

- Build 3D web applications and visualizations
- Load and display 3D models (GLTF/GLB)
- Create custom shaders and materials
- Implement camera controls and animations
- Optimize 3D rendering performance

## Scene Setup

```typescript
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);
scene.fog = new THREE.Fog(0x1a1a2e, 10, 50);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 5, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Resize handling
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## Lighting

```typescript
// Ambient light
const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
scene.add(ambientLight);

// Directional light (sun)
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 10, 7);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(2048, 2048);
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 50;
scene.add(dirLight);

// Point light
const pointLight = new THREE.PointLight(0xff6b6b, 1, 20);
pointLight.position.set(0, 3, 0);
pointLight.castShadow = true;
scene.add(pointLight);

// Environment map
const pmremGenerator = new THREE.PMREMGenerator(renderer);
new THREE.RGBELoader().load("environment.hdr", (texture) => {
  const envMap = pmremGenerator.fromEquirectangular(texture).texture;
  scene.environment = envMap;
  texture.dispose();
});
```

## GLTF Model Loading

```typescript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath("/draco/");

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

let mixer: THREE.AnimationMixer;

gltfLoader.load("model.glb", (gltf) => {
  const model = gltf.scene;
  model.traverse((child) => {
    if ((child as THREE.Mesh).isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  scene.add(model);

  // Play animations
  mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(gltf.animations[0]);
  action.play();
});
```

## Custom Shader Material

```typescript
const customMaterial = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color(0x00aaff) },
    uFrequency: { value: 2.0 },
  },
  vertexShader: `
    uniform float uTime;
    uniform float uFrequency;
    varying vec2 vUv;
    varying float vElevation;

    void main() {
      vUv = uv;
      vec3 pos = position;
      float elevation = sin(pos.x * uFrequency + uTime) * 0.2;
      pos.y += elevation;
      vElevation = elevation;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 uColor;
    varying vec2 vUv;
    varying float vElevation;

    void main() {
      float intensity = vElevation + 0.5;
      gl_FragColor = vec4(uColor * intensity, 1.0);
    }
  `,
});
```

## Animation Loop

```typescript
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  const elapsed = clock.getElapsedTime();

  // Update mixer
  if (mixer) mixer.update(delta);

  // Update shader uniforms
  customMaterial.uniforms.uTime.value = elapsed;

  // Update controls
  controls.update();

  renderer.render(scene, camera);
}

animate();
```

## Post-Processing

```typescript
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  0.5, // strength
  0.4, // radius
  0.85 // threshold
);
composer.addPass(bloomPass);

// In animation loop: composer.render() instead of renderer.render()
```

## Additional Resources

- Three.js Docs: https://threejs.org/docs/
- Examples: https://threejs.org/examples/
- Three.js Journey: https://threejs-journey.com/
