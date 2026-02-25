---
name: react-native-reanimated
description: React Native Reanimated patterns covering shared values, worklets, useAnimatedStyle, gesture handler integration, layout animations, entering/exiting transitions, and custom animation builders.
---

# React Native Reanimated

This skill should be used when building performant animations in React Native with Reanimated. It covers shared values, worklets, gestures, layout animations, and transitions.

## When to Use This Skill

Use this skill when you need to:

- Create 60fps animations on the UI thread
- Build gesture-driven interactions
- Animate layout changes smoothly
- Create entering/exiting transitions
- Use spring and timing physics

## Basic Animation

```typescript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
} from "react-native-reanimated";

function FadeInBox() {
  const opacity = useSharedValue(0);
  const scale = useSharedValue(0.5);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ scale: scale.value }],
  }));

  const show = () => {
    opacity.value = withTiming(1, { duration: 300 });
    scale.value = withSpring(1, { damping: 15, stiffness: 150 });
  };

  return (
    <View>
      <Animated.View style={[styles.box, animatedStyle]} />
      <Button title="Show" onPress={show} />
    </View>
  );
}
```

## Gesture Integration

```typescript
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  runOnJS,
} from "react-native-reanimated";

function DraggableCard() {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);
  const scale = useSharedValue(1);

  const gesture = Gesture.Pan()
    .onStart(() => {
      scale.value = withSpring(1.1);
    })
    .onUpdate((event) => {
      translateX.value = event.translationX;
      translateY.value = event.translationY;
    })
    .onEnd(() => {
      translateX.value = withSpring(0);
      translateY.value = withSpring(0);
      scale.value = withSpring(1);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
      { scale: scale.value },
    ],
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View style={[styles.card, animatedStyle]}>
        <Text>Drag me!</Text>
      </Animated.View>
    </GestureDetector>
  );
}
```

## Swipe to Delete

```typescript
function SwipeToDelete({ onDelete }: { onDelete: () => void }) {
  const translateX = useSharedValue(0);
  const height = useSharedValue(70);
  const opacity = useSharedValue(1);

  const gesture = Gesture.Pan()
    .onUpdate((event) => {
      translateX.value = Math.min(0, event.translationX);
    })
    .onEnd(() => {
      if (translateX.value < -100) {
        translateX.value = withTiming(-500);
        height.value = withTiming(0);
        opacity.value = withTiming(0, {}, () => {
          runOnJS(onDelete)();
        });
      } else {
        translateX.value = withSpring(0);
      }
    });

  const itemStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
    height: height.value,
    opacity: opacity.value,
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View style={[styles.item, itemStyle]}>
        <Text>Swipe to delete</Text>
      </Animated.View>
    </GestureDetector>
  );
}
```

## Layout Animations

```typescript
import Animated, {
  FadeIn, FadeOut,
  SlideInRight, SlideOutLeft,
  Layout,
  LinearTransition,
  ZoomIn, ZoomOut,
} from "react-native-reanimated";

function AnimatedList({ items }: { items: Item[] }) {
  return (
    <View>
      {items.map((item, index) => (
        <Animated.View
          key={item.id}
          entering={SlideInRight.delay(index * 100).springify()}
          exiting={SlideOutLeft.duration(200)}
          layout={LinearTransition.springify()}
          style={styles.listItem}
        >
          <Text>{item.name}</Text>
        </Animated.View>
      ))}
    </View>
  );
}

// Custom entering animation
const customEntering = () => {
  "worklet";
  const animations = {
    opacity: withTiming(1, { duration: 300 }),
    transform: [
      { translateY: withSpring(0, { damping: 12 }) },
      { scale: withSpring(1) },
    ],
  };
  const initialValues = {
    opacity: 0,
    transform: [{ translateY: 50 }, { scale: 0.9 }],
  };
  return { animations, initialValues };
};
```

## Interpolation

```typescript
import { interpolate, Extrapolation } from "react-native-reanimated";

function ParallaxHeader() {
  const scrollY = useSharedValue(0);

  const headerStyle = useAnimatedStyle(() => ({
    height: interpolate(scrollY.value, [0, 200], [300, 80], Extrapolation.CLAMP),
    opacity: interpolate(scrollY.value, [0, 150], [1, 0.3], Extrapolation.CLAMP),
  }));

  const titleStyle = useAnimatedStyle(() => ({
    fontSize: interpolate(scrollY.value, [0, 200], [32, 18], Extrapolation.CLAMP),
    transform: [
      { translateY: interpolate(scrollY.value, [0, 200], [0, -20], Extrapolation.CLAMP) },
    ],
  }));

  return (
    <Animated.ScrollView
      onScroll={(e) => { scrollY.value = e.nativeEvent.contentOffset.y; }}
      scrollEventThrottle={16}
    >
      <Animated.View style={[styles.header, headerStyle]}>
        <Animated.Text style={[styles.title, titleStyle]}>Header</Animated.Text>
      </Animated.View>
    </Animated.ScrollView>
  );
}
```

## Additional Resources

- Reanimated: https://docs.swmansion.com/react-native-reanimated/
- Gesture Handler: https://docs.swmansion.com/react-native-gesture-handler/
- Layout animations: https://docs.swmansion.com/react-native-reanimated/docs/layout-animations/entering-exiting-animations
