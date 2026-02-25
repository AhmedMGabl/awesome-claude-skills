---
name: grafana-dashboards
description: Grafana dashboard patterns covering panel types, variables, Prometheus data sources, alerting, annotations, provisioning, and dashboard-as-code with JSON models.
---

# Grafana Dashboards

This skill should be used when building monitoring dashboards with Grafana. It covers panel types, variables, data sources, alerting, provisioning, and dashboard-as-code.

## When to Use This Skill

Use this skill when you need to:

- Build monitoring dashboards with Grafana
- Create panels with Prometheus, InfluxDB, or other data sources
- Use template variables for dynamic dashboards
- Configure alerting and annotations
- Provision dashboards as code

## Dashboard JSON Model

```json
{
  "dashboard": {
    "title": "Application Overview",
    "tags": ["app", "production"],
    "timezone": "browser",
    "refresh": "30s",
    "time": { "from": "now-6h", "to": "now" },
    "templating": {
      "list": [
        {
          "name": "namespace",
          "type": "query",
          "datasource": "Prometheus",
          "query": "label_values(kube_pod_info, namespace)",
          "refresh": 2
        }
      ]
    },
    "panels": []
  }
}
```

## Time Series Panel

```json
{
  "type": "timeseries",
  "title": "Request Rate",
  "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
  "targets": [
    {
      "expr": "sum(rate(http_requests_total{namespace=\"$namespace\"}[5m])) by (handler)",
      "legendFormat": "{{ handler }}"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "custom": {
        "drawStyle": "line",
        "lineWidth": 2,
        "fillOpacity": 10
      }
    }
  }
}
```

## Stat Panel

```json
{
  "type": "stat",
  "title": "Error Rate",
  "gridPos": { "h": 4, "w": 6, "x": 0, "y": 0 },
  "targets": [
    {
      "expr": "sum(rate(http_requests_total{status=~\"5..\",namespace=\"$namespace\"}[5m])) / sum(rate(http_requests_total{namespace=\"$namespace\"}[5m])) * 100"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "thresholds": {
        "steps": [
          { "color": "green", "value": null },
          { "color": "yellow", "value": 1 },
          { "color": "red", "value": 5 }
        ]
      }
    }
  }
}
```

## Gauge Panel

```json
{
  "type": "gauge",
  "title": "CPU Usage",
  "targets": [
    {
      "expr": "avg(rate(container_cpu_usage_seconds_total{namespace=\"$namespace\"}[5m])) * 100"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "thresholds": {
        "steps": [
          { "color": "green", "value": null },
          { "color": "yellow", "value": 70 },
          { "color": "red", "value": 90 }
        ]
      }
    }
  }
}
```

## Table Panel

```json
{
  "type": "table",
  "title": "Top Endpoints",
  "targets": [
    {
      "expr": "topk(10, sum by (handler, method) (rate(http_requests_total{namespace=\"$namespace\"}[1h])))",
      "format": "table",
      "instant": true
    }
  ],
  "transformations": [
    { "id": "organize", "options": { "renameByName": { "handler": "Endpoint", "method": "Method", "Value": "Requests/s" } } }
  ]
}
```

## Dashboard Provisioning

```yaml
# provisioning/dashboards/dashboards.yml
apiVersion: 1
providers:
  - name: "default"
    orgId: 1
    folder: "Production"
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

## Data Source Provisioning

```yaml
# provisioning/datasources/datasources.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: "15s"

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
```

## Alerting

```yaml
# Grafana unified alerting rule
groups:
  - name: app-alerts
    folder: Production
    interval: 1m
    rules:
      - title: High Error Rate
        condition: C
        data:
          - refId: A
            queryType: ""
            datasourceUid: prometheus
            model:
              expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
          - refId: C
            queryType: ""
            datasourceUid: "-100"
            model:
              type: threshold
              conditions:
                - evaluator:
                    type: gt
                    params: [0.05]
        for: 5m
        labels:
          severity: critical
```

## Additional Resources

- Grafana: https://grafana.com/docs/grafana/
- Dashboard JSON: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/
- Provisioning: https://grafana.com/docs/grafana/latest/administration/provisioning/
