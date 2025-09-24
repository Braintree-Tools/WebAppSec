# WebAppSec - Advanced Web Application Security Testing Framework

**Professional Grade Penetration Testing Suite by BRAINTREE Security Research Lab**

## CRITICAL LEGAL DISCLAIMER

**⚠️ WARNING: PROFESSIONAL PENETRATION TESTING FRAMEWORK WITH LIVE EXPLOITATION CAPABILITIES ⚠️**

**THIS SOFTWARE CONTAINS ACTUAL ATTACK VECTORS AND EXPLOITATION TOOLS**

### ABSOLUTE TERMS OF USE

**BY DOWNLOADING, INSTALLING, OR USING THIS SOFTWARE, YOU EXPLICITLY ACKNOWLEDGE AND AGREE TO THE FOLLOWING:**

1. **AUTHORIZATION REQUIRED**: This framework is EXCLUSIVELY for authorized security testing on systems you own or have explicit written permission to test
2. **LEGAL COMPLIANCE**: You are SOLELY responsible for compliance with ALL applicable local, state, federal, and international laws
3. **NO LIABILITY**: The author, contributors, and BRAINTREE Security Research Lab assume ZERO liability for any misuse, damage, or illegal activities
4. **USER RESPONSIBILITY**: You accept FULL responsibility for all actions performed using this software
5. **PROFESSIONAL USE ONLY**: Intended exclusively for certified security professionals, authorized penetration testers, and legitimate researchers
6. **NO WARRANTY**: This software is provided "AS IS" without any warranties or guarantees
7. **INDEMNIFICATION**: You agree to indemnify and hold harmless the author and contributors from any claims, damages, or legal actions

### PROHIBITED USES

- Unauthorized access to any computer system or network
- Testing systems without explicit written authorization
- Any malicious, criminal, or illegal activities
- Violation of any applicable laws or regulations
- Use in violation of employer policies or agreements

### LEGAL CONSEQUENCES

Unauthorized computer access is a serious crime in most jurisdictions and may result in:
- Criminal prosecution and imprisonment
- Substantial financial penalties and fines
- Civil liability and damages
- Permanent criminal record
- Professional license revocation

**THE AUTHOR AND CONTRIBUTORS DISCLAIM ALL LIABILITY AND RESPONSIBILITY FOR USER ACTIONS**

## Overview

WebAppSec is a comprehensive web application security testing framework that integrates multiple professional-grade security tools into a unified platform. Built for security professionals and penetration testers, this framework provides extensive capabilities for web application vulnerability assessment and exploitation.

### Key Features

- **Comprehensive Security Testing**: Full web application security assessment capabilities
- **Professional Tool Integration**: Seamless integration with industry-standard security tools
- **Extensive Payload Library**: 71,310+ security payloads across multiple attack vectors
- **Advanced Reconnaissance**: Complete information gathering and enumeration capabilities
- **SQL Injection Testing**: Specialized SQL injection detection and exploitation
- **Web Shell Management**: 39 web shells for post-exploitation activities
- **Wordlist Management**: 149 wordlists containing 36+ million entries
- **Professional CLI Interface**: Command-line and interactive menu-driven operation
- **Modular Architecture**: Extensible framework for additional security modules

## Core Modules

### 1. SecurityScanner.py
Advanced web application security scanner with the following capabilities:
- SQL Injection Detection and Testing
- Cross-Site Scripting (XSS) Testing
- Cross-Site Request Forgery (CSRF) Testing
- Local File Inclusion (LFI) Testing
- Remote File Inclusion (RFI) Testing
- Directory Traversal Testing
- XML External Entity (XXE) Testing
- Server-Side Request Forgery (SSRF) Testing
- Command Injection Testing
- Template Injection Testing
- Directory Brute-forcing
- SSL/TLS Security Assessment

### 2. ReconFramework.py
Comprehensive reconnaissance and information gathering framework:
- Network Scanning and Port Discovery
- Subdomain Enumeration
- Directory and File Discovery
- Web Technology Fingerprinting
- DNS Enumeration
- OSINT Intelligence Gathering
- Service Version Detection
- SSL Certificate Analysis
- Web Application Mapping
- Content Discovery

### 3. SQLInjectionTester.py
Specialized SQL injection testing engine with support for:
- MySQL, PostgreSQL, MSSQL, Oracle databases
- Error-based SQL injection
- Boolean-based blind SQL injection
- Time-based blind SQL injection
- Union-based SQL injection
- Authentication bypass techniques
- Advanced evasion techniques
- Custom payload generation

### 4. Management Modules

#### PayloadManager.py
- 85 payload files containing 71,310+ attack vectors
- SQL injection payloads for all major database systems
- XSS payloads with filter bypass techniques
- LFI/RFI payloads for file inclusion attacks
- Command injection vectors
- XXE and SSRF payloads
- Template injection payloads
- NoSQL injection vectors

#### WordlistManager.py
- 149 curated wordlists
- 36+ million dictionary entries
- Directory and file enumeration lists
- Password and username dictionaries
- Technology-specific wordlists
- Custom wordlist generation capabilities

#### ShellManager.py
- 39 web shells for post-exploitation
- PHP, JSP, ASPX, Python shells
- Obfuscated and encoded variants
- Command execution capabilities
- File upload and management shells

## Integrated Security Tools

The framework integrates with the following professional security tools:

**Network Scanning**
- nmap - Network discovery and port scanning
- masscan - High-speed port scanner

**Web Application Testing**
- sqlmap - Automated SQL injection testing
- ffuf - Fast web fuzzer
- gobuster - Directory/file brute-forcer
- nikto - Web vulnerability scanner
- whatweb - Web application fingerprinting

**Reconnaissance**
- subfinder - Subdomain discovery
- amass - Asset discovery and mapping
- theharvester - OSINT intelligence gathering
- dnsrecon - DNS enumeration
- fierce - Domain scanner

**Vulnerability Assessment**
- nuclei - Template-based vulnerability scanner
- wpscan - WordPress security scanner

## System Requirements

**Operating System**: Linux (Tested on Kali Linux, Ubuntu, Debian)

**Python Requirements**:
- Python 3.8 or higher
- requests
- beautifulsoup4
- urllib3
- colorama
- termcolor

**External Tool Dependencies**:
All integrated tools should be installed and accessible in system PATH.

## Installation

Please refer to `docs/INSTALLATION.md` for complete installation instructions including:
- Repository cloning
- Dependency installation
- Tool setup and verification
- Configuration requirements

## Usage

Please refer to `docs/UsageExample.md` for comprehensive usage examples including:
- Command-line interface usage
- Interactive menu navigation
- Scanning configuration options
- Output interpretation
- Advanced testing scenarios

## Repository Structure

```
WebAppSec/
├── src/                    # Core application modules
│   ├── WebAppSec.py       # Main application launcher
│   ├── SecurityScanner.py # Web security testing engine
│   ├── ReconFramework.py  # Reconnaissance framework
│   ├── SQLInjectionTester.py # SQL injection testing
│   ├── PayloadManager.py  # Payload management system
│   ├── WordlistManager.py # Wordlist management system
│   └── ShellManager.py    # Web shell management
├── payloads/              # Security testing payloads
│   ├── sqli_payloads/     # SQL injection vectors
│   ├── web_payloads/      # Web application payloads
│   └── xss_payloads/      # Cross-site scripting vectors
├── shells/                # Web shells and backdoors
├── wordlists/             # Dictionary and enumeration lists
├── docs/                  # Documentation
│   ├── INSTALLATION.md    # Installation guide
│   └── UsageExample.md    # Usage examples
└── output/                # Scan results and reports
```

## Professional Use Cases

This framework is designed for:
- Authorized penetration testing engagements
- Web application security assessments
- Vulnerability research and analysis
- Security training and education
- Red team exercises
- Bug bounty hunting (with proper authorization)
- Compliance testing and auditing

## Legal and Ethical Use

**IMPORTANT**: This tool must only be used on systems you own or have explicit written permission to test. Unauthorized use of this software may violate local, state, federal, or international laws. Users are solely responsible for ensuring their use of this software complies with applicable laws and regulations.

## Support and Donations

This project represents significant research and development effort. If you find this framework valuable for your security testing needs, consider supporting continued development:

### Cryptocurrency Donations

**Bitcoin (BTC):**
```
12Liorh7G4aB9yKEijAbPjYH1r4kHkraNp
```

**Ethereum (ETH):**
```
0xF9743A08cF00ED29c653CB40FbAFd4618796d43c
```

*Copy the wallet addresses above to send donations. Your support helps maintain and improve this professional security framework.*

## Contributing

This is a professional security research project. Contributions should maintain the high standards of security testing practices and code quality established in the framework.

## License

This project is released under appropriate licensing terms for security research tools. Users must comply with all applicable laws and regulations.

## Author

**BRAINTREE Security Research Lab**  
Advanced Web Application Security Research and Development

---

**Professional Security Framework - Use Responsibly**
