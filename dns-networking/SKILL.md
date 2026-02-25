---
name: dns-networking
description: DNS and networking fundamentals covering DNS record types (A, AAAA, CNAME, MX, TXT, SRV), domain configuration, SSL/TLS certificate management, Cloudflare DNS, Route 53 hosted zones, subdomain routing, DNS propagation, network troubleshooting with dig/nslookup, and CDN configuration patterns.
---

# DNS & Networking

This skill should be used when configuring DNS records, managing domains, setting up CDNs, or troubleshooting network issues. It covers DNS record types, domain setup, SSL certificates, and CDN patterns.

## When to Use This Skill

Use this skill when you need to:

- Configure DNS records for domains
- Set up subdomains and routing
- Manage SSL/TLS certificates
- Configure Cloudflare or Route 53
- Troubleshoot DNS and network issues
- Set up CDN for static assets

## DNS Record Types

```
TYPE    PURPOSE                          EXAMPLE
─────────────────────────────────────────────────────────────────
A       IPv4 address                     app.example.com → 93.184.216.34
AAAA    IPv6 address                     app.example.com → 2606:2800:220:1:248:1893:25c8:1946
CNAME   Alias to another domain          www.example.com → example.com
MX      Mail server                      example.com → 10 mail.example.com
TXT     Text data (SPF, DKIM, verify)    example.com → "v=spf1 include:_spf.google.com -all"
NS      Nameserver                       example.com → ns1.cloudflare.com
SRV     Service location                 _sip._tcp.example.com → 10 5 5060 sip.example.com
CAA     Certificate authority            example.com → 0 issue "letsencrypt.org"
```

## Common DNS Configurations

```
# Web application
example.com          A      93.184.216.34       # Root domain
www.example.com      CNAME  example.com         # www redirect
api.example.com      A      93.184.216.35       # API server
staging.example.com  CNAME  staging-abc.vercel.app  # Staging

# Email (Google Workspace)
example.com          MX     1 aspmx.l.google.com
example.com          MX     5 alt1.aspmx.l.google.com
example.com          TXT    "v=spf1 include:_spf.google.com -all"
google._domainkey    TXT    "v=DKIM1; k=rsa; p=MIGf..."
_dmarc.example.com   TXT    "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"

# Verification records
example.com          TXT    "google-site-verification=abc123"
example.com          TXT    "v=spf1 include:sendgrid.net -all"
_acme-challenge      TXT    "dns-challenge-token-here"   # Let's Encrypt DNS validation
```

## Cloudflare API

```typescript
const CF_API = "https://api.cloudflare.com/client/v4";
const headers = {
  "Authorization": `Bearer ${process.env.CF_API_TOKEN}`,
  "Content-Type": "application/json",
};

// Create DNS record
async function createRecord(zoneId: string, record: {
  type: string; name: string; content: string; proxied?: boolean; ttl?: number;
}) {
  const res = await fetch(`${CF_API}/zones/${zoneId}/dns_records`, {
    method: "POST",
    headers,
    body: JSON.stringify({ ...record, ttl: record.ttl ?? 1 }),
  });
  return res.json();
}

// List records
async function listRecords(zoneId: string, type?: string) {
  const params = new URLSearchParams({ per_page: "100" });
  if (type) params.set("type", type);
  const res = await fetch(`${CF_API}/zones/${zoneId}/dns_records?${params}`, { headers });
  return res.json();
}

// Purge cache
async function purgeCache(zoneId: string, urls?: string[]) {
  const body = urls ? { files: urls } : { purge_everything: true };
  const res = await fetch(`${CF_API}/zones/${zoneId}/purge_cache`, {
    method: "POST", headers, body: JSON.stringify(body),
  });
  return res.json();
}
```

## AWS Route 53

```typescript
import { Route53Client, ChangeResourceRecordSetsCommand } from "@aws-sdk/client-route-53";

const route53 = new Route53Client({ region: "us-east-1" });

async function upsertRecord(hostedZoneId: string, name: string, type: string, value: string) {
  await route53.send(new ChangeResourceRecordSetsCommand({
    HostedZoneId: hostedZoneId,
    ChangeBatch: {
      Changes: [{
        Action: "UPSERT",
        ResourceRecordSet: {
          Name: name,
          Type: type,
          TTL: 300,
          ResourceRecords: [{ Value: value }],
        },
      }],
    },
  }));
}

// Alias record (for CloudFront/ALB)
async function createAliasRecord(hostedZoneId: string, name: string, targetDns: string, targetZone: string) {
  await route53.send(new ChangeResourceRecordSetsCommand({
    HostedZoneId: hostedZoneId,
    ChangeBatch: {
      Changes: [{
        Action: "UPSERT",
        ResourceRecordSet: {
          Name: name,
          Type: "A",
          AliasTarget: {
            DNSName: targetDns,
            HostedZoneId: targetZone,
            EvaluateTargetHealth: true,
          },
        },
      }],
    },
  }));
}
```

## Network Troubleshooting

```bash
# DNS lookup
dig example.com A              # A record
dig example.com MX             # Mail servers
dig example.com TXT            # TXT records
dig +trace example.com         # Full resolution trace
dig @8.8.8.8 example.com      # Query specific DNS server

# Check propagation
nslookup example.com 8.8.8.8       # Google DNS
nslookup example.com 1.1.1.1       # Cloudflare DNS
nslookup example.com 208.67.222.222 # OpenDNS

# SSL/TLS
openssl s_client -connect example.com:443 -servername example.com
curl -vI https://example.com 2>&1 | grep -E "SSL|subject|expire"

# Connectivity
traceroute example.com         # Network path
mtr example.com                # Continuous traceroute
curl -w "@curl-format.txt" -o /dev/null -s https://example.com  # Timing
```

## Additional Resources

- Cloudflare DNS: https://developers.cloudflare.com/dns/
- Route 53: https://docs.aws.amazon.com/Route53/
- DNS Checker: https://dnschecker.org/
- SSL Labs: https://www.ssllabs.com/ssltest/
