---
name: motion-one
description: Motion One animation patterns covering the animate API, spring physics, scroll-triggered animations, timeline sequences, gesture recognition, layout animations, and integration with React and Vue.
---

# Motion One

This skill should be used when creating performant web animations with Motion One. It covers the animate API, springs, scroll animations, timelines, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Create performant CSS-based animations
- Animate with spring physics and easings
- Build scroll-triggered animations
- Sequence animations with timelines
- Integrate animations in React or Vue

## Basic Animation

```typescript
import { animate, spring, stagger } from "motion";

// Simple animation
animate(".box", { opacity: [0, 1], y: [20, 0] }, { duration: 0.5 });

// Spring physics
animate(".element", { scale: 1.2 }, { easing: spring({ stiffness: 200, damping: 10 }) });

// Stagger children
animate("li", { opacity: [0, 1], x: [-20, 0] }, { delay: stagger(0.1) });

// Keyframes
animate(
  ".loader",
  { rotate: [0, 360] },
  { duration: 1, repeat: Infinity, easing: "linear" }
);

// Return controls
const controls = animate(".panel", { height: ["0px", "300px"] }, { duration: 0.3 });
controls.pause();
controls.play();
controls.reverse();
controls.cancel();
```

## Scroll Animations

```typescript
import { animate, scroll, inView } from "motion";

// Scroll-linked animation (progress-based)
scroll(
  animate(".progress-bar", { scaleX: [0, 1] }),
  { target: document.querySelector(".content") }
);

// Parallax effect
scroll(
  animate(".hero-image", { y: [0, -100] }),
  { offset: ["start start", "end start"] }
);

// In-view animations
inView(".card", ({ target }) => {
  animate(target, { opacity: 1, y: 0 }, { duration: 0.5 });
  // Return cleanup function
  return () => {
    animate(target, { opacity: 0, y: 20 }, { duration: 0.2 });
  };
});

// In-view with options
inView(
  ".section",
  (info) => {
    animate(info.target, { opacity: 1 }, { duration: 0.8 });
  },
  { margin: "-100px", amount: 0.3 }
);
```

## Timeline

```typescript
import { timeline } from "motion";

const sequence = timeline([
  [".title", { opacity: [0, 1], y: [30, 0] }, { duration: 0.5 }],
  [".subtitle", { opacity: [0, 1], y: [20, 0] }, { duration: 0.4, at: "-0.2" }],
  [".cta", { opacity: [0, 1], scale: [0.8, 1] }, { duration: 0.3, at: "-0.1" }],
]);

// Control the timeline
sequence.finished.then(() => console.log("Animation complete"));
```

## React Integration (motion/react)

```tsx
import { motion, AnimatePresence } from "motion/react";

function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}

function AnimatedList({ items }: { items: Item[] }) {
  return (
    <AnimatePresence mode="popLayout">
      {items.map((item) => (
        <motion.div
          key={item.id}
          layout
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
        >
          {item.name}
        </motion.div>
      ))}
    </AnimatePresence>
  );
}

// Gesture animations
function InteractiveCard() {
  return (
    <motion.div
      whileHover={{ scale: 1.05, rotate: 1 }}
      whileTap={{ scale: 0.95 }}
      drag
      dragConstraints={{ left: -100, right: 100, top: -50, bottom: 50 }}
      transition={{ type: "spring" }}
    >
      Drag me!
    </motion.div>
  );
}

// Scroll-triggered
function ScrollReveal({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.6 }}
    >
      {children}
    </motion.div>
  );
}
```

## Variants

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

function StaggeredList() {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      {items.map((i) => (
        <motion.li key={i} variants={item}>{i}</motion.li>
      ))}
    </motion.ul>
  );
}
```

## Additional Resources

- Motion: https://motion.dev/
- Motion for React: https://motion.dev/docs/react-quick-start
- Animation docs: https://motion.dev/docs/animate
