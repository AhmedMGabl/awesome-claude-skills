---
name: three-js
description: Three.js 3D graphics development covering scene setup, geometries and materials, lighting, camera controls, GLTF model loading, animations, post-processing effects, React Three Fiber integration, physics with Rapier, shaders, and performance optimization.
---

# Three.js 3D Graphics

This skill should be used when building 3D graphics and visualizations for the web. It covers Three.js, React Three Fiber, physics, shaders, and performance optimization.

## When to Use This Skill

Use this skill when you need to:

- Build 3D scenes and visualizations
- Load and display 3D models (GLTF/GLB)
- Create animations and interactive 3D experiences
- Use React Three Fiber for declarative 3D
- Add physics simulations

## Basic Scene Setup

```typescript
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 2, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// Mesh
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x6366f1 });
const cube = new THREE.Mesh(geometry, material);
cube.castShadow = true;
scene.add(cube);

// Floor
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(10, 10),
  new THREE.MeshStandardMaterial({ color: 0x333333 }),
);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.y += 0.01;
  controls.update();
  renderer.render(scene, camera);
}
animate();

// Resize handling
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
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

gltfLoader.load("/models/robot.glb", (gltf) => {
  const model = gltf.scene;
  model.scale.set(0.5, 0.5, 0.5);
  model.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.castShadow = true;
    }
  });
  scene.add(model);

  // Play animations
  const mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(gltf.animations[0]);
  action.play();
});
```

## React Three Fiber

```tsx
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Environment, useGLTF } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

function SpinningBox() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta;
    }
  });

  return (
    <mesh ref={meshRef} castShadow>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#6366f1" />
    </mesh>
  );
}

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} scale={0.5} />;
}

export function Scene() {
  return (
    <Canvas shadows camera={{ position: [0, 2, 5], fov: 75 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} castShadow />
      <SpinningBox />
      <Model url="/models/robot.glb" />
      <OrbitControls enableDamping />
      <Environment preset="city" />
    </Canvas>
  );
}
```

## Physics with Rapier

```tsx
import { Physics, RigidBody } from "@react-three/rapier";

function PhysicsScene() {
  return (
    <Canvas shadows>
      <Physics gravity={[0, -9.81, 0]}>
        {/* Falling boxes */}
        {Array.from({ length: 20 }).map((_, i) => (
          <RigidBody key={i} position={[Math.random() * 4 - 2, i * 1.5 + 5, 0]}>
            <mesh castShadow>
              <boxGeometry args={[0.5, 0.5, 0.5]} />
              <meshStandardMaterial color={`hsl(${i * 18}, 70%, 60%)`} />
            </mesh>
          </RigidBody>
        ))}

        {/* Ground */}
        <RigidBody type="fixed">
          <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[20, 20]} />
            <meshStandardMaterial color="#333" />
          </mesh>
        </RigidBody>
      </Physics>
    </Canvas>
  );
}
```

## Performance Tips

```
TECHNIQUE                        IMPACT
──────────────────────────────────────────────────
Instanced meshes                 10-100x fewer draw calls
Geometry merging                 Fewer objects to process
LOD (Level of Detail)            Reduce polygons at distance
Frustum culling                  Skip off-screen objects
Texture compression (KTX2)       Smaller GPU memory
Draco compression                Smaller model downloads
requestAnimationFrame            Synced with display refresh
Dispose unused resources         Prevent memory leaks
```

## Additional Resources

- Three.js docs: https://threejs.org/docs/
- React Three Fiber: https://r3f.docs.pmnd.rs/
- Three.js examples: https://threejs.org/examples/
