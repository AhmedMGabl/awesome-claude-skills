---
name: penetration-testing
description: Penetration testing patterns covering reconnaissance, vulnerability scanning, web app testing, API security assessment, network testing, and reporting methodologies.
---

# Penetration Testing

This skill should be used when conducting authorized security assessments. It covers reconnaissance, vulnerability scanning, web app testing, API security, network testing, and reporting.

## When to Use This Skill

Use this skill when you need to:

- Plan and execute authorized penetration tests
- Perform web application security assessments
- Test API endpoints for security vulnerabilities
- Conduct network vulnerability scanning
- Write professional security assessment reports

## Reconnaissance

```bash
# DNS enumeration
dig example.com ANY
dig +short example.com MX
nslookup -type=TXT example.com

# Subdomain enumeration
subfinder -d example.com -o subdomains.txt
amass enum -d example.com -passive

# Port scanning
nmap -sV -sC -oN scan.txt target.com
nmap -p- --min-rate 1000 target.com

# Web technology fingerprinting
whatweb target.com
wappalyzer target.com
```

## Web Application Testing

```bash
# Directory/file discovery
gobuster dir -u https://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

# Nikto web server scanner
nikto -h https://target.com -o report.html -Format html

# SSL/TLS testing
testssl.sh https://target.com
sslyze target.com

# Security headers check
curl -I https://target.com | grep -iE "(x-frame|x-content|strict|x-xss|content-security)"
```

## OWASP Testing Checklist

```markdown
## Authentication Testing
- [ ] Test for default credentials
- [ ] Test password policy enforcement
- [ ] Test account lockout mechanism
- [ ] Test for brute force vulnerabilities
- [ ] Test multi-factor authentication bypass
- [ ] Test session fixation
- [ ] Test session timeout

## Authorization Testing
- [ ] Test for IDOR (Insecure Direct Object Reference)
- [ ] Test horizontal privilege escalation
- [ ] Test vertical privilege escalation
- [ ] Test for missing function-level access control

## Input Validation
- [ ] Test for SQL injection (SQLi)
- [ ] Test for Cross-Site Scripting (XSS)
- [ ] Test for command injection
- [ ] Test for path traversal
- [ ] Test for XML External Entity (XXE)
- [ ] Test for Server-Side Request Forgery (SSRF)

## API Security
- [ ] Test for broken authentication
- [ ] Test for excessive data exposure
- [ ] Test for mass assignment
- [ ] Test rate limiting
- [ ] Test for injection in API parameters
```

## API Security Testing

```bash
# Test for authentication bypass
curl -X GET https://api.target.com/users/admin -H "Authorization: Bearer <expired_token>"

# Test for IDOR
curl -X GET https://api.target.com/users/1 -H "Authorization: Bearer <user2_token>"

# Test for mass assignment
curl -X PUT https://api.target.com/users/me \
  -H "Content-Type: application/json" \
  -d '{"role": "admin", "isVerified": true}'

# Test for rate limiting
for i in $(seq 1 100); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST https://api.target.com/login \
    -d '{"email":"test@test.com","password":"wrong"}'
done
```

## Report Template

```markdown
# Penetration Test Report

## Executive Summary
Brief overview of scope, methodology, and critical findings.

## Scope
- Target systems and IP ranges
- Testing period
- Rules of engagement

## Methodology
- OWASP Testing Guide v4
- PTES (Penetration Testing Execution Standard)

## Findings

### [CRITICAL] SQL Injection in Login Form
- **CVSS Score:** 9.8
- **Location:** POST /api/login - `username` parameter
- **Impact:** Full database access, data exfiltration
- **Evidence:** [screenshot/payload]
- **Remediation:** Use parameterized queries

### [HIGH] Broken Access Control
- **CVSS Score:** 8.1
- **Location:** GET /api/users/{id}
- **Impact:** Access to other users' data
- **Remediation:** Implement server-side authorization checks

## Risk Summary
| Severity | Count |
|----------|-------|
| Critical | 1     |
| High     | 3     |
| Medium   | 5     |
| Low      | 8     |
```

## Additional Resources

- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- PTES: http://www.pentest-standard.org/
- HackTricks: https://book.hacktricks.xyz/
