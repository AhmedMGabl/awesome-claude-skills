---
name: feature-flags
description: Feature flag implementation covering LaunchDarkly and Unleash SDKs, custom flag services with percentage rollouts, A/B testing, user targeting, flag lifecycle management, kill switches, React hooks for flags, server-side evaluation, and gradual rollout strategies.
---

# Feature Flags

This skill should be used when implementing feature flags, gradual rollouts, or A/B testing in applications. It covers flag services, targeting rules, and lifecycle management.

## When to Use This Skill

Use this skill when you need to:

- Roll out features gradually to users
- Implement A/B testing
- Add kill switches for production features
- Target features to specific user segments
- Decouple deployment from release

## Custom Feature Flag Service

```typescript
interface FeatureFlag {
  key: string;
  enabled: boolean;
  rolloutPercentage: number;          // 0-100
  targetedUserIds: string[];          // Always enabled for these
  targetedSegments: string[];         // e.g., "beta", "enterprise"
  variants?: Record<string, number>;  // A/B variant weights
}

class FeatureFlagService {
  private flags = new Map<string, FeatureFlag>();

  constructor(private store: FlagStore) {
    this.refresh();
  }

  async refresh() {
    const flags = await this.store.getAll();
    this.flags.clear();
    flags.forEach((f) => this.flags.set(f.key, f));
  }

  isEnabled(key: string, context?: { userId?: string; segments?: string[] }): boolean {
    const flag = this.flags.get(key);
    if (!flag || !flag.enabled) return false;

    // Always on for targeted users
    if (context?.userId && flag.targetedUserIds.includes(context.userId)) return true;

    // Segment targeting
    if (context?.segments?.some((s) => flag.targetedSegments.includes(s))) return true;

    // Percentage rollout (consistent per user)
    if (flag.rolloutPercentage >= 100) return true;
    if (flag.rolloutPercentage <= 0) return false;
    if (context?.userId) {
      const hash = this.hashUserId(key, context.userId);
      return hash < flag.rolloutPercentage;
    }

    return false;
  }

  getVariant(key: string, userId: string): string | null {
    const flag = this.flags.get(key);
    if (!flag?.enabled || !flag.variants) return null;

    const hash = this.hashUserId(key, userId);
    let cumulative = 0;
    for (const [variant, weight] of Object.entries(flag.variants)) {
      cumulative += weight;
      if (hash < cumulative) return variant;
    }
    return null;
  }

  private hashUserId(flagKey: string, userId: string): number {
    // Simple consistent hash (0-100)
    let hash = 0;
    const str = `${flagKey}:${userId}`;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash + str.charCodeAt(i)) | 0;
    }
    return Math.abs(hash) % 100;
  }
}
```

## React Integration

```tsx
import { createContext, useContext, ReactNode } from "react";

const FlagContext = createContext<FeatureFlagService | null>(null);

function FlagProvider({ service, children }: { service: FeatureFlagService; children: ReactNode }) {
  return <FlagContext.Provider value={service}>{children}</FlagContext.Provider>;
}

function useFeatureFlag(key: string): boolean {
  const service = useContext(FlagContext);
  const user = useCurrentUser();
  if (!service) return false;
  return service.isEnabled(key, { userId: user?.id, segments: user?.segments });
}

function useVariant(key: string): string | null {
  const service = useContext(FlagContext);
  const user = useCurrentUser();
  if (!service || !user) return null;
  return service.getVariant(key, user.id);
}

// Usage
function PricingPage() {
  const showNewPricing = useFeatureFlag("new-pricing-page");
  const ctaVariant = useVariant("cta-experiment"); // "A" | "B" | null

  if (showNewPricing) return <NewPricingPage />;
  return <CurrentPricingPage ctaVariant={ctaVariant} />;
}
```

## LaunchDarkly Integration

```typescript
import * as LaunchDarkly from "@launchdarkly/node-server-sdk";

const ldClient = LaunchDarkly.init(process.env.LAUNCHDARKLY_SDK_KEY!);
await ldClient.waitForInitialization();

// Evaluate flag
const context = { kind: "user", key: userId, email: user.email, custom: { plan: user.plan } };
const showFeature = await ldClient.variation("new-feature", context, false);

// React SDK
import { LDProvider, useFlags } from "launchdarkly-react-client-sdk";

function App() {
  return (
    <LDProvider clientSideID={process.env.NEXT_PUBLIC_LD_CLIENT_ID!} context={{ kind: "user", key: userId }}>
      <Dashboard />
    </LDProvider>
  );
}

function Dashboard() {
  const { newDashboard, betaFeatures } = useFlags();
  return newDashboard ? <NewDashboard beta={betaFeatures} /> : <OldDashboard />;
}
```

## Flag Lifecycle

```
FLAG LIFECYCLE:
  1. CREATE   — Add flag with default OFF
  2. DEVELOP  — Code behind flag check
  3. TEST     — Enable for internal team / staging
  4. ROLLOUT  — 5% → 25% → 50% → 100% over days
  5. MONITOR  — Watch error rates and metrics at each step
  6. CLEANUP  — Remove flag and dead code path

CLEANUP CHECKLIST:
  [ ] Flag is at 100% for 2+ weeks with no issues
  [ ] Remove flag checks from code
  [ ] Remove old code path
  [ ] Delete flag from flag service
  [ ] Update tests
```

## Additional Resources

- LaunchDarkly: https://docs.launchdarkly.com/
- Unleash: https://docs.getunleash.io/
- OpenFeature: https://openfeature.dev/
- GrowthBook: https://docs.growthbook.io/
