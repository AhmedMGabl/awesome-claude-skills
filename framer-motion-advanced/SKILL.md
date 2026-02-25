---
name: framer-motion-advanced
description: Framer Motion advanced animations covering layout animations, shared layout transitions, gesture-driven interactions, scroll-linked animations, exit animations, orchestration, and SVG path animations.
---

# Framer Motion Advanced

This skill should be used when building advanced animations with Framer Motion. It covers layout animations, gestures, scroll effects, exit transitions, and orchestration.

## When to Use This Skill

Use this skill when you need to:

- Animate layout changes and shared elements
- Build gesture-driven interactions (drag, tap, hover)
- Create scroll-linked animations and parallax effects
- Orchestrate complex multi-element animations
- Animate route transitions and list reordering

## Layout Animations

```tsx
import { motion, AnimatePresence } from "framer-motion";

function ExpandableCard({ item }: { item: Item }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      layout
      onClick={() => setExpanded(!expanded)}
      className="card"
      style={{ borderRadius: 12 }}
      transition={{ layout: { duration: 0.3, type: "spring" } }}
    >
      <motion.h3 layout="position">{item.title}</motion.h3>
      {expanded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <p>{item.description}</p>
          <img src={item.image} alt={item.title} />
        </motion.div>
      )}
    </motion.div>
  );
}
```

## Shared Layout Animation

```tsx
import { motion, LayoutGroup } from "framer-motion";

function Tabs({ tabs }: { tabs: { id: string; label: string }[] }) {
  const [active, setActive] = useState(tabs[0].id);

  return (
    <LayoutGroup>
      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActive(tab.id)}
            className="tab"
          >
            {tab.label}
            {active === tab.id && (
              <motion.div
                layoutId="active-tab"
                className="tab-indicator"
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            )}
          </button>
        ))}
      </div>
    </LayoutGroup>
  );
}
```

## Gesture Animations

```tsx
// Drag
<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: -50, bottom: 50 }}
  dragElastic={0.2}
  whileDrag={{ scale: 1.1, cursor: "grabbing" }}
  onDragEnd={(_, info) => {
    if (Math.abs(info.offset.x) > 100) {
      handleSwipe(info.offset.x > 0 ? "right" : "left");
    }
  }}
/>

// Tap and hover
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>

// Long press
<motion.div
  onTapStart={() => setPressed(true)}
  onTap={() => setPressed(false)}
  onTapCancel={() => setPressed(false)}
  animate={{ scale: pressed ? 0.9 : 1 }}
/>
```

## Scroll Animations

```tsx
import { motion, useScroll, useTransform, useSpring } from "framer-motion";

function ParallaxSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 0.8]);

  return (
    <motion.section ref={ref} style={{ opacity }}>
      <motion.div style={{ y, scale }}>
        <h2>Parallax Content</h2>
      </motion.div>
    </motion.section>
  );
}

// Scroll progress bar
function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30 });

  return (
    <motion.div
      style={{ scaleX, transformOrigin: "left" }}
      className="fixed top-0 left-0 right-0 h-1 bg-blue-500 z-50"
    />
  );
}
```

## AnimatePresence (Exit Animations)

```tsx
function NotificationList({ notifications }: { notifications: Notification[] }) {
  return (
    <AnimatePresence mode="popLayout">
      {notifications.map((n) => (
        <motion.div
          key={n.id}
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, x: 100, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          layout
        >
          <span>{n.message}</span>
          <button onClick={() => dismiss(n.id)}>Dismiss</button>
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
```

## Stagger Children

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      {items.map((text, i) => (
        <motion.li key={i} variants={item}>
          {text}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

## SVG Path Animation

```tsx
<motion.svg viewBox="0 0 100 100">
  <motion.path
    d="M10 80 Q 52.5 10, 95 80"
    fill="none"
    stroke="#3b82f6"
    strokeWidth={2}
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 2, ease: "easeInOut" }}
  />
</motion.svg>
```

## Additional Resources

- Framer Motion docs: https://www.framer.com/motion/
- Layout animations: https://www.framer.com/motion/layout-animations/
- Gestures: https://www.framer.com/motion/gestures/
