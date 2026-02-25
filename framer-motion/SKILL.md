---
name: framer-motion
description: Framer Motion animation library covering motion components, variants, gesture animations, layout animations, scroll-triggered animations, AnimatePresence for exit animations, spring physics, shared layout, and reduced motion accessibility.
---

# Framer Motion

This skill should be used when implementing animations in React applications with Framer Motion. It covers motion components, variants, gestures, layout animations, and scroll effects.

## When to Use This Skill

Use this skill when you need to:

- Add smooth animations to React components
- Implement gesture-based interactions (drag, hover, tap)
- Create layout animations and shared element transitions
- Build scroll-triggered animations
- Handle mount/unmount animations with AnimatePresence

## Basic Animations

```tsx
import { motion } from "framer-motion";

function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}
```

## Variants (Orchestrated Animations)

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

function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      {items.map((text) => (
        <motion.li key={text} variants={item} className="py-2">
          {text}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

## AnimatePresence (Exit Animations)

```tsx
import { AnimatePresence, motion } from "framer-motion";

function Notification({ message, isVisible }: { message: string; isVisible: boolean }) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          className="fixed top-4 right-4 bg-white shadow-lg rounded-lg p-4"
        >
          {message}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

## Gesture Animations

```tsx
function InteractiveCard() {
  return (
    <motion.div
      whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(0,0,0,0.15)" }}
      whileTap={{ scale: 0.95 }}
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.1}
      className="bg-white rounded-xl p-6 cursor-pointer"
    >
      <h3>Drag me or click me</h3>
    </motion.div>
  );
}
```

## Layout Animations

```tsx
import { motion, LayoutGroup } from "framer-motion";
import { useState } from "react";

function ExpandableCards() {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  return (
    <LayoutGroup>
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((id) => (
          <motion.div
            key={id}
            layout
            onClick={() => setExpandedId(expandedId === id ? null : id)}
            className="bg-white rounded-lg p-4 cursor-pointer"
            style={{ gridColumn: expandedId === id ? "span 3" : "span 1" }}
          >
            <motion.h3 layout="position">Card {id}</motion.h3>
            <AnimatePresence>
              {expandedId === id && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  Expanded content for card {id}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </LayoutGroup>
  );
}
```

## Scroll Animations

```tsx
import { motion, useScroll, useTransform } from "framer-motion";

function ParallaxHero() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, 200]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <motion.div style={{ y, opacity }} className="h-screen flex items-center justify-center">
      <h1 className="text-6xl font-bold">Hero Section</h1>
    </motion.div>
  );
}

// Animate when in viewport
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

## Spring Physics

```tsx
// Spring transition (natural feeling)
<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>

// Presets
<motion.div transition={{ type: "spring", bounce: 0.4 }} />  // Bouncy
<motion.div transition={{ type: "spring", bounce: 0 }} />    // No bounce (snappy)
```

## Reduced Motion

```tsx
import { useReducedMotion } from "framer-motion";

function AccessibleAnimation({ children }: { children: React.ReactNode }) {
  const shouldReduce = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduce ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: shouldReduce ? 0 : 0.5 }}
    >
      {children}
    </motion.div>
  );
}
```

## Additional Resources

- Framer Motion docs: https://www.framer.com/motion/
- Animation examples: https://www.framer.com/motion/examples/
- useScroll: https://www.framer.com/motion/use-scroll/
