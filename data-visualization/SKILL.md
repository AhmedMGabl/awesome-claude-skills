---
name: data-visualization
description: Data visualization covering Chart.js and Recharts for React, D3.js fundamentals, dashboard layouts, responsive charts, real-time data updates, color accessibility, tooltip and legend patterns, export-to-image functionality, and performance optimization for large datasets.
---

# Data Visualization

This skill should be used when building charts, dashboards, and data visualizations for web applications. It covers Chart.js, Recharts, D3.js fundamentals, and dashboard patterns.

## When to Use This Skill

Use this skill when you need to:

- Build interactive charts and graphs
- Create dashboards with multiple visualizations
- Implement real-time updating charts
- Handle large datasets in visualizations
- Make charts accessible and responsive

## Recharts (React)

```tsx
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const COLORS = ["#6366F1", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"];

function RevenueChart({ data }: { data: { month: string; revenue: number; users: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis yAxisId="left" tickFormatter={(v) => `$${v / 1000}k`} />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip formatter={(value: number, name: string) =>
          [name === "revenue" ? `$${value.toLocaleString()}` : value.toLocaleString(), name]} />
        <Legend />
        <Line yAxisId="left" type="monotone" dataKey="revenue" stroke="#6366F1" strokeWidth={2} dot={false} />
        <Line yAxisId="right" type="monotone" dataKey="users" stroke="#10B981" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function CategoryBreakdown({ data }: { data: { name: string; value: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100}
             label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
          {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

function BarComparison({ data }: { data: { name: string; current: number; previous: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="previous" fill="#94A3B8" name="Previous" radius={[4, 4, 0, 0]} />
        <Bar dataKey="current" fill="#6366F1" name="Current" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

## Chart.js

```typescript
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

function createTimeSeriesChart(canvas: HTMLCanvasElement, data: { date: string; value: number }[]) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: data.map((d) => d.date),
      datasets: [{
        label: "Value",
        data: data.map((d) => d.value),
        borderColor: "#6366F1",
        backgroundColor: "rgba(99, 102, 241, 0.1)",
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHitRadius: 10,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, grid: { color: "#f0f0f0" } },
      },
    },
  });
}
```

## Dashboard Layout

```tsx
function Dashboard({ metrics }: { metrics: DashboardMetrics }) {
  return (
    <div className="p-6 space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Revenue" value={`$${metrics.revenue.toLocaleString()}`}
                 change={metrics.revenueChange} />
        <KPICard title="Users" value={metrics.users.toLocaleString()}
                 change={metrics.usersChange} />
        <KPICard title="Conversion" value={`${metrics.conversion}%`}
                 change={metrics.conversionChange} />
        <KPICard title="Avg Order" value={`$${metrics.avgOrder.toFixed(2)}`}
                 change={metrics.avgOrderChange} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Revenue Over Time</h3>
          <RevenueChart data={metrics.revenueTimeSeries} />
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">By Category</h3>
          <CategoryBreakdown data={metrics.categoryBreakdown} />
        </div>
      </div>
    </div>
  );
}

function KPICard({ title, value, change }: { title: string; value: string; change: number }) {
  const isPositive = change >= 0;
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className={`text-sm mt-1 ${isPositive ? "text-green-600" : "text-red-600"}`}>
        {isPositive ? "+" : ""}{change}% vs last period
      </p>
    </div>
  );
}
```

## Additional Resources

- Recharts: https://recharts.org/
- Chart.js: https://www.chartjs.org/
- D3.js: https://d3js.org/
- Observable Plot: https://observablehq.com/plot/
- Nivo: https://nivo.rocks/
