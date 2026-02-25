---
name: web-animation
description: Web animation patterns covering CSS transitions and keyframes, Framer Motion for React, GSAP timeline sequencing, scroll-triggered animations, spring physics, layout animations, reduced-motion accessibility, and performance optimization with GPU-accelerated transforms.
---

# Web Animation

This skill should be used when adding animations and motion to web applications. It covers CSS animations, Framer Motion, GSAP, scroll-based effects, and accessibility considerations.

## When to Use This Skill

Use this skill when you need to:

- Add page transitions and micro-interactions
- Build scroll-triggered animations
- Create layout animations and shared element transitions
- Implement spring-based physics animations
- Ensure animations respect reduced-motion preferences
- Optimize animation performance

## Framer Motion (React)

```tsx
import { motion, AnimatePresence } from "framer-motion";

// Fade and slide in
function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

// Staggered list animation
function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: 0.08 } },
      }}
    >
      {items.map((item) => (
        <motion.li
          key={item}
          variants={{
            hidden: { opacity: 0, x: -20 },
            visible: { opacity: 1, x: 0 },
          }}
        >
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}

// Layout animation (shared layout)
function ExpandableCard({ isOpen, onClick }: { isOpen: boolean; onClick: () => void }) {
  return (
    <motion.div
      layout
      onClick={onClick}
      style={{ borderRadius: 12, overflow: "hidden" }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
    >
      <motion.h2 layout="position">Card Title</motion.h2>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <p>Expanded content here...</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// Page transitions with AnimatePresence
function PageTransition({ children, key }: { children: React.ReactNode; key: string }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={key}
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.98 }}
        transition={{ duration: 0.2 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

## Scroll Animations

```tsx
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

function ParallaxSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);

  return (
    <div ref={ref} style={{ position: "relative", height: "100vh" }}>
      <motion.div style={{ y, opacity }}>
        <h2>Parallax Content</h2>
      </motion.div>
    </div>
  );
}

// Scroll-triggered reveal
function ScrollReveal({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  );
}
```

## CSS Animations

```css
/* Keyframe animation */
@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeSlideIn 0.3s ease-out forwards;
}

/* Staggered children with CSS custom properties */
.stagger-item {
  opacity: 0;
  animation: fadeSlideIn 0.4s ease-out forwards;
  animation-delay: calc(var(--index) * 80ms);
}

/* Smooth transitions */
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Loading skeleton */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

/* Reduced motion — ALWAYS include */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## GSAP (Complex Sequences)

```typescript
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

// Timeline sequence
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2.out" } });
tl.from(".hero-title", { y: 50, opacity: 0 })
  .from(".hero-subtitle", { y: 30, opacity: 0 }, "-=0.3")
  .from(".hero-cta", { scale: 0.8, opacity: 0 }, "-=0.2");

// Scroll-triggered animation
gsap.from(".section-content", {
  scrollTrigger: {
    trigger: ".section",
    start: "top 80%",
    end: "bottom 20%",
    toggleActions: "play none none reverse",
  },
  y: 60,
  opacity: 0,
  duration: 0.8,
  stagger: 0.15,
});
```

## Performance Tips

```
GPU-ACCELERATED PROPERTIES (cheap to animate):
  ✓ transform (translate, scale, rotate)
  ✓ opacity

LAYOUT-TRIGGERING PROPERTIES (expensive — avoid animating):
  ✗ width, height, top, left, margin, padding
  ✗ Use transform: translateX() instead of left
  ✗ Use transform: scale() instead of width/height

BEST PRACTICES:
  - Use will-change sparingly, remove after animation
  - Prefer CSS transitions for simple hover/state changes
  - Use Framer Motion or GSAP for complex sequences
  - Always respect prefers-reduced-motion
  - Avoid animating more than 2 properties simultaneously
  - Use requestAnimationFrame for imperative animations
```

## Additional Resources

- Framer Motion: https://www.framer.com/motion/
- GSAP: https://gsap.com/docs/v3/
- Web Animations API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API
- prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
