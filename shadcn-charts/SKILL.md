---
name: shadcn-charts
description: shadcn/ui chart patterns covering bar, line, area, pie, radar, and radial charts with Recharts, custom tooltips, responsive containers, themes, stacked series, and data visualization best practices.
---

# shadcn Charts

This skill should be used when building data visualizations with shadcn/ui chart components. It covers bar, line, area, pie, radar charts, and customization.

## When to Use This Skill

Use this skill when you need to:

- Build charts with shadcn/ui and Recharts
- Create responsive, themed data visualizations
- Add custom tooltips and legends
- Build stacked, grouped, or combined charts
- Match chart styling to your design system

## Chart Configuration

```tsx
import { type ChartConfig } from "@/components/ui/chart";

const chartConfig = {
  revenue: {
    label: "Revenue",
    color: "hsl(var(--chart-1))",
  },
  expenses: {
    label: "Expenses",
    color: "hsl(var(--chart-2))",
  },
  profit: {
    label: "Profit",
    color: "hsl(var(--chart-3))",
  },
} satisfies ChartConfig;
```

## Bar Chart

```tsx
"use client";
import { Bar, BarChart, XAxis, YAxis } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart";

const data = [
  { month: "Jan", revenue: 4000, expenses: 2400 },
  { month: "Feb", revenue: 3000, expenses: 1398 },
  { month: "Mar", revenue: 5000, expenses: 3800 },
  { month: "Apr", revenue: 4780, expenses: 3908 },
  { month: "May", revenue: 5890, expenses: 4800 },
  { month: "Jun", revenue: 6390, expenses: 3800 },
];

function RevenueChart() {
  return (
    <ChartContainer config={chartConfig} className="h-[300px] w-full">
      <BarChart data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        <ChartTooltip content={<ChartTooltipContent />} />
        <ChartLegend content={<ChartLegendContent />} />
        <Bar dataKey="revenue" fill="var(--color-revenue)" radius={4} />
        <Bar dataKey="expenses" fill="var(--color-expenses)" radius={4} />
      </BarChart>
    </ChartContainer>
  );
}
```

## Line Chart

```tsx
import { Line, LineChart, XAxis, YAxis, CartesianGrid } from "recharts";

function TrendChart({ data }: { data: DataPoint[] }) {
  return (
    <ChartContainer config={chartConfig} className="h-[300px] w-full">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="var(--color-revenue)"
          strokeWidth={2}
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="profit"
          stroke="var(--color-profit)"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ChartContainer>
  );
}
```

## Area Chart

```tsx
import { Area, AreaChart, XAxis, YAxis } from "recharts";

function StackedAreaChart({ data }: { data: DataPoint[] }) {
  return (
    <ChartContainer config={chartConfig} className="h-[300px] w-full">
      <AreaChart data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        <ChartTooltip content={<ChartTooltipContent indicator="dot" />} />
        <Area
          type="natural"
          dataKey="revenue"
          fill="var(--color-revenue)"
          fillOpacity={0.4}
          stroke="var(--color-revenue)"
          stackId="a"
        />
        <Area
          type="natural"
          dataKey="expenses"
          fill="var(--color-expenses)"
          fillOpacity={0.4}
          stroke="var(--color-expenses)"
          stackId="a"
        />
      </AreaChart>
    </ChartContainer>
  );
}
```

## Pie Chart

```tsx
import { Pie, PieChart, Cell } from "recharts";

const pieData = [
  { name: "Desktop", value: 55, fill: "var(--color-revenue)" },
  { name: "Mobile", value: 35, fill: "var(--color-expenses)" },
  { name: "Tablet", value: 10, fill: "var(--color-profit)" },
];

function DeviceChart() {
  return (
    <ChartContainer config={chartConfig} className="h-[300px] w-full">
      <PieChart>
        <ChartTooltip content={<ChartTooltipContent hideLabel />} />
        <Pie
          data={pieData}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={2}
        />
      </PieChart>
    </ChartContainer>
  );
}
```

## Custom Tooltip

```tsx
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload) return null;
  return (
    <div className="rounded-lg bg-background p-3 shadow-md border">
      <p className="font-medium">{label}</p>
      {payload.map((entry: any, i: number) => (
        <div key={i} className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-sm text-muted-foreground">{entry.name}:</span>
          <span className="font-medium">${entry.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}
```

## Additional Resources

- shadcn Charts: https://ui.shadcn.com/charts
- Recharts docs: https://recharts.org/
