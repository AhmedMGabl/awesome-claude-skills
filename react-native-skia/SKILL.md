---
name: react-native-skia
description: React Native Skia patterns covering canvas drawing, paths, shaders, image filters, blur effects, gradient fills, animated transitions, and high-performance 2D graphics rendering on mobile.
---

# React Native Skia

This skill should be used when building high-performance 2D graphics in React Native with Skia. It covers canvas drawing, paths, shaders, filters, gradients, and animations.

## When to Use This Skill

Use this skill when you need to:

- Draw custom 2D graphics on mobile
- Create shader effects and image filters
- Build animated chart visualizations
- Apply blur, gradient, and shadow effects
- Render performant custom UI elements

## Basic Canvas

```tsx
import { Canvas, Circle, Rect, Group, Paint } from "@shopify/react-native-skia";

function BasicShapes() {
  return (
    <Canvas style={{ width: 300, height: 300 }}>
      <Rect x={20} y={20} width={100} height={100} color="lightblue" />
      <Circle cx={200} cy={70} r={50} color="coral" />
      <Group transform={[{ rotate: Math.PI / 4 }]} origin={{ x: 150, y: 200 }}>
        <Rect x={100} y={150} width={100} height={100} color="mediumpurple" />
      </Group>
    </Canvas>
  );
}
```

## Paths

```tsx
import { Canvas, Path, Skia } from "@shopify/react-native-skia";

function CustomPath() {
  const path = Skia.Path.Make();
  path.moveTo(20, 100);
  path.cubicTo(80, 20, 160, 180, 240, 100);
  path.lineTo(240, 280);
  path.lineTo(20, 280);
  path.close();

  return (
    <Canvas style={{ width: 300, height: 300 }}>
      <Path
        path={path}
        color="rgba(59, 130, 246, 0.3)"
        style="fill"
      />
      <Path
        path={path}
        color="#3b82f6"
        style="stroke"
        strokeWidth={2}
      />
    </Canvas>
  );
}
```

## Gradients

```tsx
import { Canvas, Rect, LinearGradient, RadialGradient, vec } from "@shopify/react-native-skia";

function GradientShapes() {
  return (
    <Canvas style={{ width: 300, height: 300 }}>
      {/* Linear gradient */}
      <Rect x={20} y={20} width={120} height={120}>
        <LinearGradient
          start={vec(20, 20)}
          end={vec(140, 140)}
          colors={["#3b82f6", "#8b5cf6", "#ec4899"]}
        />
      </Rect>

      {/* Radial gradient */}
      <Rect x={160} y={20} width={120} height={120}>
        <RadialGradient
          c={vec(220, 80)}
          r={60}
          colors={["#fbbf24", "#f97316", "#ef4444"]}
        />
      </Rect>
    </Canvas>
  );
}
```

## Image Filters and Blur

```tsx
import {
  Canvas, Image, useImage, Blur, ColorMatrix,
  Shadow, Fill, BackdropFilter, RoundedRect,
} from "@shopify/react-native-skia";

function ImageEffects() {
  const image = useImage(require("./photo.jpg"));
  if (!image) return null;

  return (
    <Canvas style={{ width: 300, height: 400 }}>
      {/* Image with blur */}
      <Image image={image} x={0} y={0} width={300} height={200} fit="cover">
        <Blur blur={4} />
      </Image>

      {/* Frosted glass card */}
      <BackdropFilter
        clip={{ x: 20, y: 120, width: 260, height: 100 }}
        filter={<Blur blur={10} />}
      >
        <Fill color="rgba(255, 255, 255, 0.2)" />
        <RoundedRect x={20} y={120} width={260} height={100} r={16} color="rgba(255, 255, 255, 0.1)" />
      </BackdropFilter>

      {/* Shadow */}
      <RoundedRect x={20} y={250} width={260} height={100} r={16} color="white">
        <Shadow dx={0} dy={4} blur={12} color="rgba(0, 0, 0, 0.15)" />
      </RoundedRect>
    </Canvas>
  );
}
```

## Animations with Reanimated

```tsx
import { Canvas, Circle, Group } from "@shopify/react-native-skia";
import { useSharedValue, withRepeat, withTiming, useDerivedValue } from "react-native-reanimated";
import { useEffect } from "react";

function PulsingCircle() {
  const progress = useSharedValue(0);

  useEffect(() => {
    progress.value = withRepeat(
      withTiming(1, { duration: 2000 }),
      -1,
      true
    );
  }, []);

  const radius = useDerivedValue(() => 30 + progress.value * 20);
  const opacity = useDerivedValue(() => 1 - progress.value * 0.5);

  return (
    <Canvas style={{ width: 200, height: 200 }}>
      <Circle cx={100} cy={100} r={radius} color={`rgba(59, 130, 246, ${opacity.value})`} />
      <Circle cx={100} cy={100} r={30} color="#3b82f6" />
    </Canvas>
  );
}
```

## Shaders

```tsx
import { Canvas, Fill, Shader, Skia, vec } from "@shopify/react-native-skia";
import { useDerivedValue, useSharedValue, withRepeat, withTiming } from "react-native-reanimated";

const source = Skia.RuntimeEffect.Make(`
  uniform float time;
  uniform vec2 resolution;

  half4 main(vec2 pos) {
    vec2 uv = pos / resolution;
    float d = length(uv - 0.5);
    float c = sin(d * 10.0 - time * 3.0) * 0.5 + 0.5;
    return half4(c * 0.3, c * 0.5, c, 1.0);
  }
`)!;

function ShaderEffect() {
  const time = useSharedValue(0);

  useEffect(() => {
    time.value = withRepeat(withTiming(Math.PI * 2, { duration: 4000 }), -1);
  }, []);

  const uniforms = useDerivedValue(() => ({
    time: time.value,
    resolution: vec(300, 300),
  }));

  return (
    <Canvas style={{ width: 300, height: 300 }}>
      <Fill>
        <Shader source={source} uniforms={uniforms} />
      </Fill>
    </Canvas>
  );
}
```

## Additional Resources

- React Native Skia: https://shopify.github.io/react-native-skia/
- Drawing: https://shopify.github.io/react-native-skia/docs/shapes/
- Shaders: https://shopify.github.io/react-native-skia/docs/shaders/overview
