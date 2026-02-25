---
name: rive-animations
description: Rive animation patterns covering state machines, inputs, artboard loading, event handling, React/Vue integration, responsive sizing, and interactive animation design for web and mobile applications.
---

# Rive Animations

This skill should be used when integrating Rive animations into web applications. It covers state machines, inputs, event handling, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Add interactive animations to web applications
- Use state machine-driven animation logic
- Integrate Rive files in React or Vue
- Handle animation events and triggers
- Build responsive animated UI elements

## React Integration

```tsx
import { useRive, useStateMachineInput, Layout, Fit, Alignment } from "@rive-app/react-canvas";

function AnimatedButton() {
  const { rive, RiveComponent } = useRive({
    src: "/animations/button.riv",
    stateMachines: "ButtonState",
    autoplay: true,
    layout: new Layout({
      fit: Fit.Contain,
      alignment: Alignment.Center,
    }),
  });

  const hoverInput = useStateMachineInput(rive, "ButtonState", "isHovered");
  const pressInput = useStateMachineInput(rive, "ButtonState", "isPressed");

  return (
    <RiveComponent
      style={{ width: 200, height: 60 }}
      onMouseEnter={() => hoverInput && (hoverInput.value = true)}
      onMouseLeave={() => hoverInput && (hoverInput.value = false)}
      onMouseDown={() => pressInput && pressInput.fire()}
    />
  );
}
```

## State Machine Inputs

```tsx
import { useRive, useStateMachineInput } from "@rive-app/react-canvas";

function ProgressAnimation() {
  const { rive, RiveComponent } = useRive({
    src: "/animations/progress.riv",
    stateMachines: "ProgressMachine",
    autoplay: true,
  });

  // Number input (0-100)
  const progressInput = useStateMachineInput(rive, "ProgressMachine", "progress");

  // Boolean input
  const completeInput = useStateMachineInput(rive, "ProgressMachine", "isComplete");

  // Trigger input
  const pulseInput = useStateMachineInput(rive, "ProgressMachine", "pulse");

  const updateProgress = (value: number) => {
    if (progressInput) {
      progressInput.value = value;
    }
    if (value >= 100 && completeInput) {
      completeInput.value = true;
    }
  };

  return (
    <div>
      <RiveComponent style={{ width: 300, height: 300 }} />
      <input
        type="range"
        min={0}
        max={100}
        onChange={(e) => updateProgress(Number(e.target.value))}
      />
      <button onClick={() => pulseInput?.fire()}>Pulse</button>
    </div>
  );
}
```

## Event Handling

```tsx
import { useRive, EventType, RiveEventPayload } from "@rive-app/react-canvas";

function InteractiveAnimation() {
  const onRiveEvent = (event: RiveEventPayload) => {
    if (event.type === EventType.General) {
      console.log("Rive event:", event.data);
      // Handle custom events from Rive
      if (event.data?.name === "onComplete") {
        handleComplete();
      }
    }
  };

  const { RiveComponent } = useRive({
    src: "/animations/interactive.riv",
    stateMachines: "Main",
    autoplay: true,
    onEvent: onRiveEvent,
  });

  return <RiveComponent style={{ width: "100%", height: 400 }} />;
}
```

## Multiple Artboards

```tsx
function MultiArtboard() {
  const { rive: headerRive, RiveComponent: HeaderAnimation } = useRive({
    src: "/animations/ui-kit.riv",
    artboard: "Header",
    stateMachines: "HeaderState",
    autoplay: true,
  });

  const { rive: loaderRive, RiveComponent: LoaderAnimation } = useRive({
    src: "/animations/ui-kit.riv",
    artboard: "Loader",
    animations: "spin",
    autoplay: true,
  });

  return (
    <div>
      <HeaderAnimation style={{ width: "100%", height: 80 }} />
      <LoaderAnimation style={{ width: 48, height: 48 }} />
    </div>
  );
}
```

## Vanilla JavaScript

```typescript
import { Rive, Layout, Fit, Alignment, StateMachineInput } from "@rive-app/canvas";

const canvas = document.getElementById("rive-canvas") as HTMLCanvasElement;

const rive = new Rive({
  src: "/animations/hero.riv",
  canvas,
  stateMachines: "HeroState",
  autoplay: true,
  layout: new Layout({
    fit: Fit.Cover,
    alignment: Alignment.Center,
  }),
  onLoad: () => {
    // Get inputs after load
    const inputs = rive.stateMachineInputs("HeroState");
    const scrollInput = inputs?.find((i) => i.name === "scrollProgress");

    // Bind to scroll
    window.addEventListener("scroll", () => {
      if (scrollInput) {
        const progress = window.scrollY / (document.body.scrollHeight - window.innerHeight);
        scrollInput.value = progress * 100;
      }
    });
  },
});

// Cleanup
window.addEventListener("beforeunload", () => {
  rive.cleanup();
});
```

## Responsive Sizing

```tsx
function ResponsiveRive() {
  const { RiveComponent } = useRive({
    src: "/animations/hero.riv",
    stateMachines: "Main",
    autoplay: true,
    layout: new Layout({
      fit: Fit.Cover,
      alignment: Alignment.Center,
    }),
  });

  return (
    <div style={{ width: "100%", aspectRatio: "16/9", maxWidth: 800 }}>
      <RiveComponent style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
```

## Additional Resources

- Rive: https://rive.app/
- Rive React: https://help.rive.app/runtimes/overview/react
- Rive editor: https://editor.rive.app/
