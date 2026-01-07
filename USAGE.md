# ForensicSense AI - Usage Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Target Profiling](#target-profiling)
4. [Exploitation](#exploitation)
5. [Reporting](#reporting)
6. [Evidence Management](#evidence-management)
7. [Audit Trail](#audit-trail)
8. [Hack The Box Integration](#hack-the-box-integration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/jameshroop-art/P-A-rrot-SecW-I-n.git
cd P-A-rrot-SecW-I-n

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Verify installation
forensicsense --version
```

### First Profile

```bash
# Profile a target (safe reconnaissance)
forensicsense profile example.com

# Generate PDF report
forensicsense profile example.com --depth full --format pdf --output report.pdf
```

---

## Configuration

### Configuration File: `config.yaml`

The configuration file controls all aspects of ForensicSense behavior.

```yaml
mode:
  default: forensics
  exploitation:
    enabled: false  # Must be explicitly enabled
    require_auth: true
    require_legal_ack: true

forensics:
  default_depth: standard  # basic, standard, full, deep
  aggressive_scanning: false
  rate_limiting: true
  
safe_environments:
  - localhost
  - 127.0.0.1
  - hackthebox.com
  - tryhackme.com
  - "10.10.*.*"  # HTB VPN range

integrations:
  hackthebox:
    api_token: ${HTB_API_TOKEN}
  shodan:
    api_key: ${SHODAN_API_KEY}
```

### Environment Variables

```bash
export HTB_API_TOKEN="your-htb-token-here"
export SHODAN_API_KEY="your-shodan-key-here"
export HIBP_API_KEY="your-hibp-key-here"
```

### View Current Configuration

```bash
forensicsense config
```

---

## Target Profiling

### Profile Depths

**Basic**: DNS resolution + risk assessment
```bash
forensicsense profile target.com --depth basic
```

**Standard** (default): Basic + port scanning + fingerprinting
```bash
forensicsense profile target.com --depth standard
```

**Full**: Standard + OSINT + vulnerability assessment
```bash
forensicsense profile target.com --depth full
```

**Deep**: Full + extensive scanning + path discovery
```bash
forensicsense profile target.com --depth deep
```

### Profile Options

```bash
# Specify output file
forensicsense profile target.com --output custom_report.json

# Choose output format
forensicsense profile target.com --format pdf
forensicsense profile target.com --format html
forensicsense profile target.com --format md

# Deep profile with PDF report
forensicsense profile target.com --depth deep --format pdf --output pentest_report.pdf
```

### What Gets Profiled

1. **DNS Information**
   - A, AAAA, MX, TXT, NS, CNAME records
   - Reverse DNS lookup
   - Geolocation

2. **Network Scanning**
   - Open ports (respectful, rate-limited)
   - Service identification
   - Banner grabbing

3. **Service Fingerprinting**
   - HTTP/HTTPS services
   - Technology stack (React, Laravel, WordPress, etc.)
   - Server versions
   - Security headers

4. **OSINT Collection** (full/deep only)
   - WHOIS data
   - Subdomain enumeration (passive)
   - Historical data (Wayback Machine)
   - Exposed credentials check (HIBP)

5. **Vulnerability Assessment**
   - CVE matching
   - Known exploits
   - Misconfigurations
   - Risk scoring (0-100)

---

## Exploitation

### ⚠️ CRITICAL: Authorization Required

**NEVER** use exploitation features without explicit written authorization!

### Authorization Gates

ForensicSense implements **5 layers of authorization**:

1. ✅ Exploitation enabled in config
2. ✅ Target in whitelist OR safe environment
3. ✅ User authentication (password/2FA)
4. ✅ Legal acknowledgment (typed confirmation)
5. ✅ All actions logged to immutable audit log

### Safe Environments (Auto-Authorized)

The following environments **bypass** manual authorization:
- Hack The Box (hackthebox.com, 10.10.*.*)
- TryHackMe (tryhackme.com)
- PentesterLab (pentesterlab.com)
- localhost / 127.0.0.1

### Enabling Exploitation

Edit `config.yaml`:

```yaml
mode:
  exploitation:
    enabled: true  # Enable exploitation
```

### Exploit Command

```bash
# Exploit with authorization
forensicsense exploit target.com --vuln sqli --reason "SOW #12345"

# Interactive mode
forensicsense exploit target.com --vuln xss --reason "Client authorization" --interactive
```

### Supported Vulnerability Types

- `sqli` - SQL Injection
- `xss` - Cross-Site Scripting
- `rce` - Remote Code Execution
- `lfi` - Local File Inclusion
- `bof` - Buffer Overflow

### Authorization Flow

```
1. Request submitted
   ↓
2. Check if exploitation enabled → FAIL: Denied
   ↓
3. Check if safe environment → PASS: Auto-authorized
   ↓
4. Check whitelist → FAIL: Denied
   ↓
5. Request password → FAIL: Denied
   ↓
6. Legal acknowledgment → FAIL: Denied
   ↓
7. Generate auth token
   ↓
8. Log to audit trail
   ↓
9. Proceed with exploitation
```

---

## Reporting

### Report Formats

**JSON** (machine-readable)
```bash
forensicsense profile target.com --format json --output report.json
```

**Markdown** (lightweight)
```bash
forensicsense profile target.com --format md --output report.md
```

**HTML** (web view)
```bash
forensicsense profile target.com --format html --output report.html
```

**PDF** (professional)
```bash
forensicsense profile target.com --format pdf --output report.pdf
```

### Report Contents

1. **Executive Summary**
   - Target information
   - Risk assessment
   - Timeline

2. **Technical Findings**
   - DNS information
   - Open ports and services
   - Technology stack
   - Discovered vulnerabilities

3. **OSINT Intelligence**
   - WHOIS data
   - Subdomains
   - Historical data
   - Exposed credentials

4. **Risk Assessment**
   - Risk score (0-100)
   - Risk level (CRITICAL, HIGH, MEDIUM, LOW, MINIMAL)
   - Contributing factors
   - Prioritized recommendations

5. **Evidence**
   - Sealed evidence files
   - Chain of custody
   - Cryptographic hashes

---

## Evidence Management

### Evidence Collection

Evidence is **automatically collected** during profiling with `--depth standard` or higher.

### Evidence Sealing

All evidence is **cryptographically sealed** with:
- SHA-256 hash
- Timestamp
- Collector information
- Chain of custody

### Evidence Verification

```python
from forensicsense.utils.crypto import EvidenceSealer

sealer = EvidenceSealer()
evidence = sealer.load_sealed_evidence('evidence/network_scan.sealed')

# Automatically verifies integrity
# Raises ValueError if tampered
```

### Chain of Custody

Every evidence item tracks:
- Collection timestamp
- Collector name
- Case ID
- All handling events
- Cryptographic seal

### Evidence Files

Evidence stored in `evidence/` directory:
```
evidence/
├── dns_resolution_20260105_120000.sealed
├── network_scan_20260105_120030.sealed
├── osint_20260105_120100.sealed
└── vulnerability_assessment_20260105_120130.sealed
```

---

## Audit Trail

### Viewing Audit Log

```bash
# Text view
forensicsense audit

# JSON export
forensicsense audit --format json
```

### Audit Log Features

- **Blockchain-style chaining**: Each entry hashes previous
- **Immutable**: Append-only, tampering detected
- **Comprehensive**: User, target, action, result, timestamp
- **Verifiable**: Integrity check built-in

### What Gets Logged

- Exploitation authorization requests
- Authorization approvals/denials
- Exploitation attempts
- Configuration changes
- Evidence handling

### Integrity Verification

The audit log automatically verifies its own integrity:

```
✓ Audit log integrity verified
Verified: 25 entries
```

If tampered:
```
✗ Audit log integrity check FAILED
Hash chain broken at line 15
```

---

## Hack The Box Integration

### Setup

Get your HTB API token from: https://app.hackthebox.com/profile/settings

```bash
export HTB_API_TOKEN="your-token-here"
```

### List Active Machines

```bash
forensicsense htb-list
```

### Profile HTB Machine

```bash
# Get machine IP from htb-list, then:
forensicsense profile 10.10.11.235 --depth full
```

### Auto-Authorization

HTB machines are **automatically authorized** (safe environment).

No manual authorization gates required!

---

## Best Practices

### Reconnaissance (Safe)

✅ **Always profile before exploiting**
- Understand the attack surface
- Identify vulnerabilities
- Assess risk
- Plan attack strategy

✅ **Generate reports**
- Document findings
- Track progress
- Share with team
- Legal evidence

✅ **Use appropriate depth**
- `basic`: Quick check
- `standard`: Normal recon
- `full`: Comprehensive intel
- `deep`: Complete picture

### Exploitation (Gated)

⚠️ **Authorization First**
- Obtain written permission
- Verify scope
- Document authorization
- Review audit log

⚠️ **Safe Environments**
- Practice on HTB/THM
- Test in lab environments
- Use localhost for demos
- Never test production without authorization

⚠️ **Audit Trail**
- Review audit log regularly
- Export for compliance
- Verify integrity
- Archive securely

### Evidence Handling

🔒 **Chain of Custody**
- Seal all evidence
- Document handling
- Verify integrity
- Archive securely

🔒 **Legal Compliance**
- Follow organizational policies
- Meet regulatory requirements
- Document everything
- Consult legal counsel

---

## Troubleshooting

### Installation Issues

**Problem**: `pip install` fails

**Solution**:
```bash
# Update pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -e . -v
```

### Permission Denied

**Problem**: `forensicsense: command not found`

**Solution**:
```bash
# Check PATH
echo $PATH

# Use full path
python -m forensicsense.cli.main profile target.com

# Or reinstall
pip install -e .
```

### Network Scanning Slow

**Problem**: Port scanning takes too long

**Solution**:
```bash
# Use basic depth (no port scanning)
forensicsense profile target.com --depth basic

# Or adjust config
# Edit config.yaml:
forensics:
  rate_limiting: false
  max_concurrent_scans: 20
```

### Exploitation Denied

**Problem**: "Exploitation DENIED"

**Solution**:
1. Check `config.yaml` - ensure `exploitation.enabled: true`
2. Verify target in whitelist or safe environment
3. Check password (default: "password" - change in production!)
4. Review audit log: `forensicsense audit`

### Evidence Verification Failed

**Problem**: "Evidence seal verification failed"

**Solution**:
- Evidence file was tampered with
- Do NOT use this evidence
- Re-collect evidence from original source
- Investigate security incident

### API Token Issues

**Problem**: HTB/Shodan API errors

**Solution**:
```bash
# Verify token is set
echo $HTB_API_TOKEN

# Test with curl
curl -H "Authorization: Bearer $HTB_API_TOKEN" \
  https://labs.hackthebox.com/api/v4/machine/list

# Check token validity (may be expired)
```

---

## Support

For issues, questions, or feature requests:

- **GitHub Issues**: https://github.com/jameshroop-art/P-A-rrot-SecW-I-n/issues
- **Author**: @jameshroop-art

---

## Legal Notice

**This tool is for AUTHORIZED USE ONLY.**

- Obtain written authorization before testing
- Unauthorized access is ILLEGAL
- You are responsible for your actions
- Author is NOT liable for misuse

**By using this tool, you agree to use it legally and ethically.**

---

*ForensicSense AI v1.0.0 - Built by hackers, for hackers. Ethically. Legally. Powerfully.*
