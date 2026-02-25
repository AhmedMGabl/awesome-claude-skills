---
name: react-three-fiber
description: React Three Fiber patterns covering scene setup, meshes, materials, lights, cameras, GLTF model loading, animations with useFrame, physics with Rapier, post-processing effects, and performance optimization.
---

# React Three Fiber

This skill should be used when building 3D graphics in React with React Three Fiber. It covers scene setup, meshes, models, animations, physics, and performance.

## When to Use This Skill

Use this skill when you need to:

- Build 3D scenes in React applications
- Load and display GLTF/GLB 3D models
- Create animations with useFrame
- Add physics with @react-three/rapier
- Optimize rendering performance

## Basic Scene

```tsx
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";

function App() {
  return (
    <Canvas camera={{ position: [3, 3, 3], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />
      <Box position={[-1.5, 0, 0]} />
      <Sphere position={[1.5, 0, 0]} />
      <OrbitControls />
      <Environment preset="sunset" />
    </Canvas>
  );
}

function Box({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={position}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  );
}

function Sphere({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={position}>
      <sphereGeometry args={[0.7, 32, 32]} />
      <meshStandardMaterial color="hotpink" metalness={0.8} roughness={0.2} />
    </mesh>
  );
}
```

## Animation with useFrame

```tsx
import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

function RotatingCube() {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame((state, delta) => {
    meshRef.current.rotation.x += delta * 0.5;
    meshRef.current.rotation.y += delta * 0.3;

    // Hover effect using sine wave
    meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.3;
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="royalblue" />
    </mesh>
  );
}
```

## Loading GLTF Models

```tsx
import { useGLTF, Clone } from "@react-three/drei";
import { Suspense } from "react";

function Model({ url, ...props }: { url: string } & JSX.IntrinsicElements["group"]) {
  const { scene } = useGLTF(url);
  return <Clone object={scene} {...props} />;
}

// Preload model
useGLTF.preload("/models/robot.glb");

function Scene() {
  return (
    <Canvas>
      <Suspense fallback={null}>
        <Model url="/models/robot.glb" scale={0.5} position={[0, -1, 0]} />
      </Suspense>
      <OrbitControls />
      <Environment preset="city" />
    </Canvas>
  );
}
```

## Interactive Objects

```tsx
import { useState } from "react";

function InteractiveBox() {
  const [hovered, setHovered] = useState(false);
  const [clicked, setClicked] = useState(false);

  return (
    <mesh
      scale={clicked ? 1.5 : 1}
      onClick={() => setClicked(!clicked)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "orange"} />
    </mesh>
  );
}
```

## Physics with Rapier

```tsx
import { Canvas } from "@react-three/fiber";
import { Physics, RigidBody } from "@react-three/rapier";

function PhysicsScene() {
  return (
    <Canvas>
      <Physics gravity={[0, -9.81, 0]}>
        {/* Falling boxes */}
        {Array.from({ length: 10 }).map((_, i) => (
          <RigidBody key={i} position={[Math.random() * 4 - 2, 5 + i * 2, 0]}>
            <mesh>
              <boxGeometry args={[0.5, 0.5, 0.5]} />
              <meshStandardMaterial color="orange" />
            </mesh>
          </RigidBody>
        ))}

        {/* Ground */}
        <RigidBody type="fixed">
          <mesh position={[0, -1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[20, 20]} />
            <meshStandardMaterial color="lightgreen" />
          </mesh>
        </RigidBody>
      </Physics>

      <ambientLight />
      <directionalLight position={[5, 5, 5]} />
    </Canvas>
  );
}
```

## Post-Processing

```tsx
import { EffectComposer, Bloom, ChromaticAberration } from "@react-three/postprocessing";

function PostProcessedScene() {
  return (
    <Canvas>
      <Scene />
      <EffectComposer>
        <Bloom luminanceThreshold={0.9} intensity={0.5} />
        <ChromaticAberration offset={[0.002, 0.002]} />
      </EffectComposer>
    </Canvas>
  );
}
```

## Performance Tips

```tsx
import { useFrame } from "@react-three/fiber";
import { Instances, Instance } from "@react-three/drei";

// Use instancing for many identical objects
function InstancedCubes({ count = 1000 }) {
  return (
    <Instances limit={count}>
      <boxGeometry />
      <meshStandardMaterial />
      {Array.from({ length: count }).map((_, i) => (
        <Instance
          key={i}
          position={[Math.random() * 50 - 25, Math.random() * 50 - 25, Math.random() * 50 - 25]}
          color={`hsl(${Math.random() * 360}, 70%, 50%)`}
        />
      ))}
    </Instances>
  );
}
```

## Additional Resources

- React Three Fiber: https://docs.pmnd.rs/react-three-fiber
- drei helpers: https://github.com/pmndrs/drei
- Rapier physics: https://github.com/pmndrs/react-three-rapier
