---
name: falco-runtime
description: Falco runtime security patterns covering threat detection rules, syscall monitoring, container security, Kubernetes audit logs, alerting, and custom rule development.
---

# Falco Runtime Security

This skill should be used when implementing runtime threat detection with Falco. It covers detection rules, syscall monitoring, container security, K8s audit logs, alerting, and custom rules.

## When to Use This Skill

Use this skill when you need to:

- Detect runtime threats in containers and hosts
- Monitor syscalls for suspicious behavior
- Audit Kubernetes API server activities
- Create custom detection rules
- Configure alerting for security events

## Installation

```bash
# Helm chart (Kubernetes)
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set falcosidekick.enabled=true \
  --set falcosidekick.config.slack.webhookurl="https://hooks.slack.com/..."

# Docker
docker run --rm -i -t \
  --privileged \
  -v /var/run/docker.sock:/host/var/run/docker.sock \
  -v /proc:/host/proc:ro \
  falcosecurity/falco
```

## Custom Rules

```yaml
# custom_rules.yaml
- rule: Detect Shell in Container
  desc: Detect a shell being spawned inside a container
  condition: >
    spawned_process and container and
    proc.name in (bash, sh, zsh, dash) and
    not proc.pname in (cron, supervisord)
  output: >
    Shell spawned in container
    (user=%user.name container=%container.name
    shell=%proc.name parent=%proc.pname
    cmdline=%proc.cmdline image=%container.image.repository)
  priority: WARNING
  tags: [container, shell, mitre_execution]

- rule: Sensitive File Access
  desc: Detect reads of sensitive files
  condition: >
    open_read and container and
    fd.name in (/etc/shadow, /etc/passwd, /etc/sudoers) and
    not proc.name in (login, su, sudo, sshd)
  output: >
    Sensitive file read (file=%fd.name user=%user.name
    container=%container.name command=%proc.cmdline)
  priority: CRITICAL
  tags: [filesystem, mitre_credential_access]

- rule: Crypto Mining Detection
  desc: Detect potential cryptocurrency mining
  condition: >
    spawned_process and container and
    (proc.name in (xmrig, minerd, cpuminer) or
     proc.args contains "stratum+tcp" or
     proc.args contains "mining.pool")
  output: >
    Potential crypto mining detected
    (container=%container.name process=%proc.name
    cmdline=%proc.cmdline image=%container.image.repository)
  priority: CRITICAL
  tags: [container, cryptomining]
```

## Kubernetes Audit Rules

```yaml
- rule: K8s Secret Access
  desc: Detect access to Kubernetes secrets
  condition: >
    kevt and secret and kget and
    not ka.user.name in (system:serviceaccount:kube-system:*)
  output: >
    K8s secret accessed (user=%ka.user.name
    secret=%ka.target.name namespace=%ka.target.namespace
    resource=%ka.target.resource)
  priority: WARNING
  tags: [k8s, secrets]

- rule: Privileged Pod Created
  desc: Detect creation of privileged pods
  condition: >
    kevt and kcreate and pod and
    ka.req.pod.containers.privileged=true
  output: >
    Privileged pod created (user=%ka.user.name
    pod=%ka.target.name namespace=%ka.target.namespace)
  priority: CRITICAL
  tags: [k8s, privileged]
```

## Falco Configuration

```yaml
# falco.yaml
rules_file:
  - /etc/falco/falco_rules.yaml
  - /etc/falco/falco_rules.local.yaml
  - /etc/falco/custom_rules.yaml

json_output: true
log_stderr: true
log_syslog: true
log_level: info

outputs:
  rate: 1
  max_burst: 1000

stdout_output:
  enabled: true

file_output:
  enabled: true
  keep_alive: false
  filename: /var/log/falco/events.json

http_output:
  enabled: true
  url: http://falcosidekick:2801/
```

## Falcosidekick Alerting

```yaml
# Falcosidekick config
config:
  slack:
    webhookurl: "https://hooks.slack.com/services/..."
    minimumpriority: "warning"
  pagerduty:
    routingkey: "pagerduty-routing-key"
    minimumpriority: "critical"
  elasticsearch:
    hostport: "https://elasticsearch:9200"
    index: "falco"
    minimumpriority: "notice"
```

## Additional Resources

- Falco Docs: https://falco.org/docs/
- Rules Reference: https://falco.org/docs/rules/
- Falcosidekick: https://github.com/falcosecurity/falcosidekick
