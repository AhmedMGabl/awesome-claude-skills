---
name: feature-flags
description: Feature flag implementation covering LaunchDarkly and Unleash integration, percentage rollouts, A/B testing, user targeting, server-side and client-side evaluation, custom feature flag services with Redis, flag lifecycle management, and gradual release strategies.
---

# Feature Flags

This skill should be used when implementing feature flag systems for controlled releases. It covers flag providers, rollout strategies, A/B testing, targeting, and custom implementations.

## When to Use This Skill

Use this skill when you need to:

- Gradually roll out features to users
- Implement A/B testing for experiments
- Target specific user segments with features
- Build a custom feature flag service
- Manage flag lifecycle (create, test, retire)

## Custom Feature Flag Service

```typescript
import { Redis } from "ioredis";

interface FeatureFlag {
  key: string;
  enabled: boolean;
  percentage?: number;
  allowList?: string[];
  rules?: Array<{
    attribute: string;
    operator: "eq" | "in" | "gt" | "lt";
    value: string | string[] | number;
  }>;
}

class FeatureFlagService {
  constructor(private redis: Redis) {}

  async isEnabled(
    flagKey: string,
    context: { userId: string; [key: string]: any },
  ): Promise<boolean> {
    const raw = await this.redis.get(`flag:${flagKey}`);
    if (!raw) return false;

    const flag: FeatureFlag = JSON.parse(raw);
    if (!flag.enabled) return false;

    // Check allow list
    if (flag.allowList?.includes(context.userId)) return true;

    // Check targeting rules
    if (flag.rules) {
      const ruleMatch = flag.rules.every((rule) => {
        const value = context[rule.attribute];
        switch (rule.operator) {
          case "eq": return value === rule.value;
          case "in": return (rule.value as string[]).includes(value);
          case "gt": return value > rule.value;
          case "lt": return value < rule.value;
          default: return false;
        }
      });
      if (!ruleMatch) return false;
    }

    // Percentage rollout (consistent hashing)
    if (flag.percentage !== undefined) {
      const hash = this.consistentHash(`${flagKey}:${context.userId}`);
      return hash < flag.percentage;
    }

    return true;
  }

  private consistentHash(input: string): number {
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash + char) | 0;
    }
    return Math.abs(hash) % 100;
  }

  async setFlag(flag: FeatureFlag): Promise<void> {
    await this.redis.set(`flag:${flag.key}`, JSON.stringify(flag));
  }
}
```

## LaunchDarkly Integration

```typescript
import * as LaunchDarkly from "@launchdarkly/node-server-sdk";

const client = LaunchDarkly.init(process.env.LAUNCHDARKLY_SDK_KEY!);
await client.waitForInitialization();

const context = {
  kind: "user",
  key: user.id,
  email: user.email,
  custom: { plan: user.plan, region: user.region },
};

const showNewDashboard = await client.variation("new-dashboard", context, false);
```

## React Integration

```tsx
function Dashboard() {
  const showNewChart = useFeatureFlag("new-chart-component");

  return <div>{showNewChart ? <NewChart /> : <LegacyChart />}</div>;
}

// Hook implementation
function useFeatureFlag(key: string, defaultValue: any = false) {
  const [value, setValue] = useState(defaultValue);
  const { user } = useAuth();

  useEffect(() => {
    fetch(`/api/flags/${key}?userId=${user.id}`)
      .then((res) => res.json())
      .then((data) => setValue(data.value));
  }, [key, user.id]);

  return value;
}
```

## Express Middleware

```typescript
function featureFlagMiddleware(flagService: FeatureFlagService) {
  return async (req: Request, _res: Response, next: NextFunction) => {
    const context = {
      userId: req.user?.id || "anonymous",
      plan: req.user?.plan,
      region: req.headers["x-region"] as string,
    };

    req.flags = {
      isEnabled: (key: string) => flagService.isEnabled(key, context),
    };

    next();
  };
}

// Usage in route
app.get("/api/search", async (req, res) => {
  const useNewAlgo = await req.flags.isEnabled("new-search-algorithm");
  const results = useNewAlgo ? await newSearch(req.query) : await legacySearch(req.query);
  res.json(results);
});
```

## Rollout Strategies

```
STRATEGY          DESCRIPTION                   USE CASE
──────────────────────────────────────────────────────────
Boolean toggle    On/off for everyone           Kill switches
Percentage        Gradual % rollout             New feature launch
User targeting    Specific users/groups         Beta testers
Rule-based        Attribute matching            Region, plan tier
A/B experiment    Multiple variants             UI experiments
```

## Flag Lifecycle

```
CREATE → TEST (internal) → CANARY (1%) → ROLLOUT (10→50→100%) → PERMANENT → CLEANUP
```

## Additional Resources

- LaunchDarkly: https://docs.launchdarkly.com/
- Unleash: https://docs.getunleash.io/
- OpenFeature: https://openfeature.dev/
