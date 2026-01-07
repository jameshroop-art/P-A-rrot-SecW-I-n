# ForensicSense AI 🔍⚔️

**Forensics-first Penetration Testing Platform with AI-Powered Exploitation**

> "Know Before You Strike" - Complete target intelligence before exploitation

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/jameshroop-art/P-A-rrot-SecW-I-n)

---

## 🎯 Core Philosophy

ForensicSense follows a three-phase approach:

```
1. 🔍 RECONNAISSANCE (Always Active)
   └─> Complete target intelligence gathering
   
2. 📊 ANALYSIS (Always Active)  
   └─> Vulnerability assessment and risk scoring
   
3. ⚔️ EXPLOITATION (Opt-in, Gated)
   └─> AI-powered payload generation and adaptive exploitation
```

---

## ✨ Features

### Intelligence Gathering
- **DNS Resolution** - A, AAAA, MX, TXT, NS, CNAME records
- **Network Scanning** - Port scanning with banner grabbing
- **Service Fingerprinting** - HTTP headers, technology detection
- **OSINT Collection** - WHOIS, subdomains, historical data
- **Vulnerability Assessment** - CVE matching and risk scoring

### AI-Powered Exploitation (Gated)
- **Payload Generation** - AI-driven exploit payload creation
- **Adaptive Learning** - Mutates payloads based on target responses
- **WAF/IDS Evasion** - Detects and evades security controls
- **Multi-iteration Attacks** - Learns from failures

### Security & Compliance
- **Multi-layer Authorization** - Password, legal acknowledgment, whitelist
- **Audit Logging** - Blockchain-style immutable logs
- **Evidence Sealing** - Cryptographic chain of custody
- **Safe Environment Detection** - Auto-approves HTB, TryHackMe, etc.

### Integrations
- **Hack The Box** - Profile and exploit HTB machines
- **TryHackMe** - THM integration (planned)
- **Shodan** - Search engine for Internet-connected devices

### Reporting
- **Professional Reports** - PDF, HTML, Markdown, JSON
- **Evidence Chain** - Cryptographically sealed evidence
- **Risk Assessment** - Automated scoring and recommendations

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Quick Install

```bash
# Clone repository
git clone https://github.com/jameshroop-art/P-A-rrot-SecW-I-n.git
cd P-A-rrot-SecW-I-n

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Configuration

Create or edit `config.yaml`:

```yaml
mode:
  default: forensics
  exploitation:
    enabled: false  # Must be explicitly enabled

forensics:
  default_depth: standard
  rate_limiting: true

safe_environments:
  - hackthebox.com
  - tryhackme.com
  - localhost

integrations:
  hackthebox:
    api_token: ${HTB_API_TOKEN}
  shodan:
    api_key: ${SHODAN_API_KEY}
```

Set environment variables:

```bash
export HTB_API_TOKEN="your-htb-token"
export SHODAN_API_KEY="your-shodan-key"
```

---

## 🚀 Usage

### Profile a Target (Safe)

```bash
# Basic profile
forensicsense profile example.com

# Deep profile with PDF report
forensicsense profile target.com --depth deep --format pdf --output report.pdf

# Quick scan
forensicsense profile 10.10.10.10 --depth basic
```

**Profiling Depths:**
- `basic` - DNS and quick port scan
- `standard` - DNS, ports, basic fingerprinting
- `full` - Standard + OSINT + vulnerability assessment
- `deep` - Full + extensive scanning + path discovery

### Hack The Box Integration

```bash
# List active machines
forensicsense htb-list

# Profile HTB machine
forensicsense profile 10.10.11.235 --depth full

# Note: HTB machines are auto-authorized (safe environment)
```

### Exploitation (Requires Authorization)

```bash
# Request exploitation access
forensicsense exploit target.com --vuln sqli --reason "SOW #12345"

# Interactive exploitation
forensicsense exploit target.com --vuln xss --reason "Client authorization" --interactive
```

**Authorization Gates:**
1. ✅ Exploitation enabled in config
2. ✅ Target in whitelist OR safe environment
3. ✅ User authentication (password/2FA)
4. ✅ Legal acknowledgment typed confirmation
5. ✅ All actions logged to immutable audit log

### Audit Log

```bash
# View audit log
forensicsense audit

# Export as JSON
forensicsense audit --format json
```

### Configuration

```bash
# View current config
forensicsense config

# View specific setting
forensicsense config exploitation.enabled
```

---

## 📊 Example Output

### Target Profile

```
ForensicSense AI - Target Profiling
Target: example.com
Depth: full

✓ Profiling Complete

Risk Assessment:
  Level: MEDIUM
  Score: 45/100

Open Ports: 3 found

┏━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Port ┃ Service ┃ State ┃ Banner                  ┃
┡━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 22   │ ssh     │ open  │ SSH-2.0-OpenSSH_8.2p1   │
│ 80   │ http    │ open  │ nginx/1.18.0            │
│ 443  │ https   │ open  │ N/A                     │
└──────┴─────────┴───────┴─────────────────────────┘

Vulnerabilities: 2 found
  ● Missing security header: Strict-Transport-Security
  ● PHP detected - ensure using supported version

✓ Report saved to: report_example.com_20260105_231245.json
```

---

## 🏗️ Architecture

```
forensicsense/
├── intel/                   # Intelligence gathering
│   ├── profiler.py          # Main orchestrator
│   ├── network_scanner.py   # Port scanning
│   ├── service_fingerprint.py
│   ├── osint.py             # OSINT collection
│   ├── vulnerability_db.py  # CVE database
│   └── evidence.py          # Evidence sealing
│
├── ai/                      # AI engines
│   ├── payload_generator.py # Payload generation
│   └── models/              # AI models
│
├── exploit/                 # Exploitation engine
│   └── gated_exploiter.py   # Multi-layer authorization
│
├── integrations/            # Platform integrations
│   ├── hackthebox.py
│   ├── tryhackme.py
│   └── shodan.py
│
├── forensics/               # Forensic capabilities
│   └── report_generator.py  # Professional reports
│
├── cli/                     # Command-line interface
│   └── main.py
│
└── utils/                   # Utilities
    ├── logging.py           # Audit logging
    ├── crypto.py            # Evidence sealing
    └── networking.py
```

---

## 🔐 Security Features

### Authorization System
- **Multi-gate Authorization** - Multiple security checks before exploitation
- **Safe Environment Detection** - Auto-approves HTB, TryHackMe, localhost
- **Whitelist System** - Explicit target authorization required
- **Legal Acknowledgment** - User must type confirmation

### Audit Trail
- **Blockchain-style Logging** - Each entry hashed with previous
- **Immutable Records** - Append-only audit log
- **Integrity Verification** - Detect tampering attempts
- **Complete Accountability** - User, target, action, result, timestamp

### Evidence Management
- **Cryptographic Sealing** - SHA-256 hashing
- **Chain of Custody** - Track all evidence handling
- **Immutable Storage** - Cannot be modified without detection
- **Legal Compliance** - Suitable for court proceedings

---

## ⚖️ Legal & Ethics

### ⚠️ Critical Requirements

- **ALWAYS** obtain written authorization before testing
- **NEVER** test systems without explicit permission
- Unauthorized access to computer systems is **ILLEGAL**
- You are **solely responsible** for your use of this tool

### Authorized Use Only

✅ **Permitted:**
- Your own systems
- Hack The Box, TryHackMe (with account)
- Bug bounty programs (within published scope)
- Penetration tests with written authorization

❌ **Prohibited:**
- Testing without explicit written permission
- Any unauthorized access to computer systems
- Malicious or harmful activities
- Circumventing security without authorization

### Liability

The author is **NOT** liable for:
- Misuse of this software
- Legal consequences of unauthorized use
- Any violations of law
- Damages caused by improper use

---

## 🎓 Use Cases

### Penetration Testing
- Reconnaissance and intelligence gathering
- Vulnerability assessment
- Authorized exploitation testing
- Professional reporting for clients

### Security Research
- Practice on CTF platforms (HTB, TryHackMe)
- Learn reconnaissance techniques
- Study vulnerability patterns
- Understand attack chains

### Bug Bounty Hunting
- Comprehensive target profiling
- Vulnerability discovery
- Exploit verification
- Evidence collection

### Red Team Operations
- Target intelligence
- Attack surface mapping
- Exploitation automation
- Chain of custody for findings

---

## 🛣️ Roadmap

### Phase 1 (Current) ✅
- ✅ Intelligence gathering engine
- ✅ Basic network scanning
- ✅ Service fingerprinting
- ✅ OSINT collection
- ✅ Authorization gates
- ✅ Audit logging
- ✅ Report generation
- ✅ HTB integration (partial)

### Phase 2 (Planned)
- [ ] Full AI payload generation model
- [ ] Interactive exploitation engine
- [ ] Advanced WAF/IDS evasion
- [ ] Complete HTB integration
- [ ] TryHackMe integration
- [ ] Shodan integration
- [ ] Advanced reporting (PDF)

### Phase 3 (Future)
- [ ] Exploit chaining
- [ ] Post-exploitation modules
- [ ] Automated lateral movement
- [ ] Custom payload training
- [ ] Web UI dashboard
- [ ] Team collaboration features

---

## 🤝 Contributing

This is a **proprietary project**. Contributions are by invitation only.

To request access or propose contributions, contact:
- GitHub: [@jameshroop-art](https://github.com/jameshroop-art)

---

## 📝 License

**Proprietary License** - See [LICENSE](LICENSE) file

Copyright © 2026 James Hroop. All Rights Reserved.

**This software is NOT open source.** Use requires explicit written permission.

---

## 🙏 Acknowledgments

- Inspired by industry-leading penetration testing frameworks
- Built for ethical hackers and security professionals
- Designed with legal compliance in mind

---

## 📞 Contact

- **Author:** James Hroop
- **GitHub:** [@jameshroop-art](https://github.com/jameshroop-art)
- **Project:** [P-A-rrot-SecW-I-n](https://github.com/jameshroop-art/P-A-rrot-SecW-I-n)

---

## ⚡ Quick Start Examples

```bash
# Install
pip install -e .

# Profile a target
forensicsense profile example.com --depth full --format pdf

# Check audit log
forensicsense audit

# List HTB machines
export HTB_API_TOKEN="your-token"
forensicsense htb-list

# Practice on HTB (safe environment)
forensicsense profile 10.10.11.235 --depth deep
```

---

**ForensicSense AI** - Built by hackers, for hackers. Ethically. Legally. Powerfully. 🔥
