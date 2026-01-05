# ForensicSense AI - Live Demo

This document shows actual output from ForensicSense AI commands.

## Installation Verification

```bash
$ forensicsense --version
forensicsense, version 1.0.0
```

## Help System

```bash
$ forensicsense --help
Usage: forensicsense [OPTIONS] COMMAND [ARGS]...

  ForensicSense AI - Forensics-first Penetration Testing Platform

  "Know Before You Strike" - Complete target intelligence before exploitation

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  audit     Show audit log
  config    View or modify configuration
  exploit   Exploit a target (requires authorization)
  htb-list  List Hack The Box machines
  profile   Profile a target (safe reconnaissance only)
```

## Profile Command Demo

### Basic Profile

```bash
$ forensicsense profile localhost --depth basic
```

**Output:**
```
ForensicSense AI - Target Profiling
Target: localhost
Depth: basic

✓ Profiling Complete

Risk Assessment:
  Level: LOW
  Score: 20/100

✓ Profile saved to: profile_localhost_20260105_232536.json
```

### Profile with Report Generation

```bash
$ forensicsense profile example.com --depth basic --format md --output demo_report.md
```

**Generated Report (demo_report.md):**
```markdown
# Forensic Analysis Report

**Target:** example.com
**Profile Depth:** basic
**Completed:** 2026-01-05T23:27:07

## Executive Summary

**Risk Level:** LOW
**Risk Score:** 20/100

## DNS Information

**A Records:** 104.18.26.120, 104.18.27.120
**MX Records:** 1 found

## Risk Factors

- Missing security header: Strict-Transport-Security
- Missing security header: Content-Security-Policy

## Recommendations

1. Implement security headers (HSTS, CSP, X-Frame-Options, etc.)
2. Close unnecessary ports and services

## Evidence

**Evidence Sealed:** True
**Evidence Files:** 2
```

## Exploitation Demo (Safe Environment)

### Authorization Gates - Disabled Config

```bash
$ forensicsense exploit localhost --vuln sqli --reason "Testing"
```

**Output:**
```
⚠️  ForensicSense AI - EXPLOITATION MODE ⚠️

Target: localhost
Vulnerability: sqli
Reason: Testing

Requesting exploitation authorization...

Authorization Gates:
  ✗ Exploitation mode not enabled in config

✗ Exploitation DENIED

Authorization failed. Cannot proceed with exploitation.
```

### Authorization Gates - Enabled with Safe Environment

With exploitation enabled in config:

```bash
$ forensicsense exploit localhost --vuln sqli --reason "Testing safe environment"
```

**Output:**
```
⚠️  ForensicSense AI - EXPLOITATION MODE ⚠️

Target: localhost
Vulnerability: sqli
Reason: Testing safe environment

Requesting exploitation authorization...

Authorization Gates:
  ✓ Exploitation mode enabled
  ✓ Safe environment detected - auto-authorized

✓ Exploitation AUTHORIZED

✓ Exploitation framework ready
Exploitation framework ready (implementation in progress)
```

## Audit Log

```bash
$ forensicsense audit
```

**Output:**
```
Audit Log

✓ Audit log integrity verified
Verified: 3 entries

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Timestamp          ┃ User   ┃ Target    ┃ Action                 ┃ Result ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 2026-01-05 23:26:31│ runner │ localhost │ exploitation_authorized│ success│
│ 2026-01-05 23:26:31│ runner │ localhost │ exploitation_started   │ started│
│ 2026-01-05 23:26:31│ runner │ localhost │ exploitation_completed │ success│
└────────────────────┴────────┴───────────┴────────────────────────┴────────┘
```

## Configuration

```bash
$ forensicsense config
```

**Output (excerpt):**
```json
{
  "mode": {
    "default": "forensics",
    "exploitation": {
      "enabled": false,
      "require_auth": true,
      "require_legal_ack": true
    }
  },
  "safe_environments": [
    "localhost",
    "127.0.0.1",
    "hackthebox.com",
    "tryhackme.com"
  ]
}
```

## Evidence Files

Evidence is cryptographically sealed:

```bash
$ ls -lh evidence/
-rw-rw-r-- 1 runner runner 1.2K dns_resolution_20260105_232536.sealed
-rw-rw-r-- 1 runner runner 1.5K vulnerability_assessment_20260105_232536.sealed
```

**Evidence Structure:**
```json
{
  "evidence": {
    "timestamp": "2026-01-05T23:25:36.675432",
    "data": { ... },
    "metadata": {
      "collector": "TargetProfiler",
      "case_id": "profile_localhost_20260105_232536",
      "evidence_type": "dns_resolution"
    }
  },
  "seal": {
    "algorithm": "sha256",
    "hash": "1753531af247281cf5f95ef20d21c26f46072c15e6a7e42e87dc1ffc2a93a096",
    "sealed_at": "2026-01-05T23:25:36.677891"
  }
}
```

## Key Features Demonstrated

✅ **Safe Reconnaissance** - No exploitation, just intelligence
✅ **Multi-format Reports** - JSON, Markdown, HTML, PDF
✅ **Authorization Gates** - 5-layer security system
✅ **Safe Environment Detection** - Auto-authorization for HTB/localhost
✅ **Audit Trail** - Blockchain-style immutable logging
✅ **Evidence Sealing** - Cryptographic chain of custody
✅ **Risk Assessment** - Automated scoring and recommendations

---

**ForensicSense AI** - Professional pentesting with forensic-grade evidence collection.
