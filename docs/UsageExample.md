# UsageExample - WebAppSec Framework

**Professional Usage Guide for Advanced Web Application Security Testing**

## Framework Overview

WebAppSec is a comprehensive security testing framework featuring:
- **85 Payload Files**: 71,310+ attack vectors across multiple categories
- **39 Web Shells**: PHP, JSP, ASPX, and Python shells for post-exploitation
- **149 Wordlists**: 36+ million dictionary entries for enumeration
- **Professional Tool Integration**: Seamless integration with industry-standard tools

## Command Line Interface

### Basic Usage Patterns

```bash
# Interactive menu mode (recommended for beginners)
python3 WebAppSec.py

# Display help and available options
python3 WebAppSec.py --help

# Check system dependencies
python3 WebAppSec.py --check-deps

# Version information
python3 WebAppSec.py --version
```

### Direct Module Access

```bash
# Direct web security scanning
python3 src/SecurityScanner.py

# Direct reconnaissance framework
python3 src/ReconFramework.py

# Direct SQL injection testing
python3 src/SQLInjectionTester.py
```

## Interactive Menu System

### Main Menu Navigation

When launching WebAppSec in interactive mode, you'll see:

```
BRAINTREE Security Suite - WebAppSec v1.0
Professional Web Application Security Testing Framework

[1] Web Application Security Scanner
[2] Reconnaissance Framework
[3] SQL Injection Testing Suite
[4] Payload Management
[5] Wordlist Management
[6] Shell Management
[7] System Configuration
[0] Exit

Select option:
```

### Menu Option Details

**Option 1: Web Application Security Scanner**
- SQL Injection Testing
- Cross-Site Scripting (XSS) Detection
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

**Option 2: Reconnaissance Framework**
- Network Scanning and Port Discovery
- Subdomain Enumeration
- Directory and File Discovery
- Web Technology Fingerprinting
- DNS Enumeration
- OSINT Intelligence Gathering
- Service Version Detection
- SSL Certificate Analysis

**Option 3: SQL Injection Testing Suite**
- MySQL Injection Testing
- PostgreSQL Injection Testing
- MSSQL Injection Testing
- Oracle Injection Testing
- Error-based Testing
- Blind SQL Injection
- Time-based Testing
- Union-based Testing

## Comprehensive Usage Examples

### Example 1: Complete Web Application Assessment

```bash
# Step 1: Launch WebAppSec
python3 WebAppSec.py

# Step 2: Select Reconnaissance Framework (Option 2)
# Step 3: Enter target domain: example.com
# Step 4: Select comprehensive reconnaissance
# Step 5: Review reconnaissance results in output/web_hacking/

# Step 6: Select Web Application Security Scanner (Option 1)
# Step 7: Enter target URL: https://example.com
# Step 8: Select comprehensive security testing
# Step 9: Review security scan results in output/web_security/

# Step 10: If SQL injection points found, use SQL Testing Suite (Option 3)
# Step 11: Review SQL injection results in output/sql_injection/
```

### Example 2: Targeted SQL Injection Testing

```bash
# Launch framework
python3 WebAppSec.py

# Select SQL Injection Testing Suite (Option 3)
# Enter target URL with parameter: https://example.com/page.php?id=1
# Select database type (MySQL/PostgreSQL/MSSQL/Oracle)
# Choose testing method:
#   - Error-based injection
#   - Boolean-based blind injection
#   - Time-based blind injection
#   - Union-based injection

# Available payloads per database:
# MySQL: 15,000+ payloads
# PostgreSQL: 8,500+ payloads
# MSSQL: 12,000+ payloads
# Oracle: 9,800+ payloads
# Generic: 26,000+ payloads
```

### Example 3: Advanced Reconnaissance

```bash
# Launch framework
python3 WebAppSec.py

# Select Reconnaissance Framework (Option 2)
# Enter target domain: example.com

# Reconnaissance modules will execute:
# 1. Subdomain Enumeration (using subfinder, amass)
# 2. Port Scanning (using nmap)
# 3. Directory Discovery (using gobuster, ffuf)
# 4. Technology Fingerprinting (using whatweb, nikto)
# 5. OSINT Gathering (using theharvester)
# 6. DNS Enumeration (using dnsrecon, fierce)

# Wordlists used:
# Subdomains: 500,000+ entries
# Directories: 2.3 million+ entries
# Files: 1.8 million+ entries
```

### Example 4: Payload Management

```bash
# Access payload management
python3 WebAppSec.py
# Select Option 4: Payload Management

# Available payload categories:
# SQL Injection Payloads: 42,000+ vectors
#   - MySQL specific: 15,000+
#   - PostgreSQL specific: 8,500+
#   - MSSQL specific: 12,000+
#   - Oracle specific: 9,800+
#   - Generic: 26,000+

# XSS Payloads: 8,500+ vectors
#   - Reflected XSS: 3,200+
#   - Stored XSS: 2,800+
#   - DOM XSS: 2,500+

# Web Application Payloads: 20,800+ vectors
#   - LFI/RFI: 6,500+
#   - Command Injection: 4,200+
#   - XXE: 2,100+
#   - SSRF: 3,000+
#   - Template Injection: 2,500+
#   - Path Traversal: 2,500+
```

### Example 5: Web Shell Management

```bash
# Access shell management
python3 WebAppSec.py
# Select Option 6: Shell Management

# Available shell categories:
# PHP Shells: 18 variants
#   - Simple command shells
#   - File upload shells
#   - Database management shells
#   - Obfuscated variants

# JSP Shells: 8 variants
#   - Command execution shells
#   - File management shells
#   - Network connectivity shells

# ASPX Shells: 7 variants
#   - Windows command shells
#   - PowerShell execution shells
#   - File system access shells

# Python Shells: 6 variants
#   - Basic command shells
#   - Advanced system shells
#   - Network reverse shells
```

## Output and Reporting

### Output Directory Structure

```
output/
├── web_security/           # Security scanner results
│   ├── scan_results.json  # Structured vulnerability data
│   ├── scan_report.txt    # Human-readable report
│   └── scan_log.log      # Detailed scan log
├── web_hacking/           # Reconnaissance results
│   ├── subdomains.txt    # Discovered subdomains
│   ├── directories.txt   # Directory enumeration
│   ├── ports.txt         # Port scan results
│   └── technologies.txt  # Technology fingerprinting
├── sql_injection/         # SQL injection test results
│   ├── injection_points.json # Vulnerable parameters
│   ├── payloads_tested.log   # Payload testing log
│   └── database_info.txt     # Database information
└── wordlists/             # Generated custom wordlists
    ├── target_specific.txt
    └── custom_payloads.txt
```

### Report Format Examples

**Vulnerability Report Structure:**
```json
{
  "scan_info": {
    "target": "https://example.com",
    "timestamp": "2025-09-23T22:30:00Z",
    "scan_duration": "45 minutes",
    "modules_used": ["sqli", "xss", "lfi", "directory_traversal"]
  },
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "severity": "High",
      "parameter": "id",
      "payload": "1' OR '1'='1",
      "response_indicators": ["MySQL error", "database version"]
    }
  ],
  "statistics": {
    "total_requests": 15420,
    "vulnerabilities_found": 3,
    "false_positives": 0
  }
}
```

## Advanced Configuration

### Custom Payload Integration

```bash
# Add custom payloads to existing categories
# SQL injection payloads:
cp custom_sqli.txt payloads/sqli_payloads/

# XSS payloads:
cp custom_xss.txt payloads/xss_payloads/

# Web application payloads:
cp custom_web.txt payloads/web_payloads/
```

### Performance Tuning

```bash
# Environment variables for optimization
export WEBAPPSEC_THREADS=20        # Number of testing threads
export WEBAPPSEC_TIMEOUT=30        # Request timeout in seconds
export WEBAPPSEC_DELAY=100         # Delay between requests (ms)
export WEBAPPSEC_MAX_PAYLOADS=1000 # Maximum payloads per test
```

### Proxy Configuration

```bash
# Configure proxy for testing through security tools
export HTTP_PROXY="http://127.0.0.1:8080"
export HTTPS_PROXY="http://127.0.0.1:8080"

# Burp Suite integration
export WEBAPPSEC_PROXY="127.0.0.1:8080"
```

## Integration with External Tools

### Integrated Tool Usage

**Network Scanning:**
- nmap: Port discovery and service detection
- masscan: High-speed port scanning

**Web Testing:**
- sqlmap: Advanced SQL injection testing
- gobuster: Directory and file discovery
- ffuf: High-performance web fuzzing
- nikto: Web vulnerability scanning
- whatweb: Web application fingerprinting

**Reconnaissance:**
- subfinder: Passive subdomain discovery
- amass: Asset discovery and mapping
- theharvester: OSINT data collection
- dnsrecon: DNS enumeration
- fierce: Domain scanning

**Vulnerability Assessment:**
- nuclei: Template-based vulnerability scanning
- wpscan: WordPress security assessment

### Tool Integration Examples

```bash
# Automatic tool chaining example:
# 1. Subdomain discovery (subfinder) -> 500+ subdomains found
# 2. Port scanning (nmap) -> 50+ open ports discovered
# 3. Directory discovery (gobuster) -> 200+ directories found
# 4. Vulnerability scanning (nuclei) -> 15+ potential issues
# 5. Web application testing (custom modules) -> 8+ confirmed vulnerabilities
```

## Testing Methodology

### Comprehensive Assessment Workflow

**Phase 1: Information Gathering**
1. DNS enumeration and subdomain discovery
2. Port scanning and service identification
3. Web technology fingerprinting
4. Directory and file discovery

**Phase 2: Vulnerability Discovery**
1. Automated vulnerability scanning
2. SQL injection testing (42,000+ payloads)
3. XSS testing (8,500+ payloads)
4. File inclusion testing (6,500+ payloads)
5. Command injection testing (4,200+ payloads)

**Phase 3: Exploitation and Verification**
1. Manual verification of discovered vulnerabilities
2. Proof-of-concept development
3. Impact assessment
4. Report generation

### Testing Statistics

**Typical Comprehensive Assessment:**
- Duration: 2-6 hours
- HTTP Requests: 50,000-200,000
- Payloads Tested: 15,000-50,000
- Directories Checked: 10,000-100,000
- Subdomains Discovered: 100-5,000

## Best Practices

### Pre-Testing Checklist

- [ ] Authorization documentation verified
- [ ] Testing scope clearly defined
- [ ] Network connectivity confirmed
- [ ] Tool dependencies verified
- [ ] Output directory prepared
- [ ] Backup and restore plans ready

### During Testing

1. **Monitor Resource Usage**: Framework can be resource-intensive
2. **Respect Rate Limits**: Avoid overwhelming target systems
3. **Document Findings**: Maintain detailed testing logs
4. **Verify Results**: Manually confirm automated findings
5. **Maintain Ethics**: Follow responsible disclosure practices

### Post-Testing

1. **Secure Test Data**: Protect sensitive information discovered
2. **Generate Reports**: Create professional assessment reports
3. **Clean Up**: Remove temporary files and clear caches
4. **Follow Up**: Coordinate with target system owners

## Troubleshooting

### Common Issues and Solutions

**Issue: High False Positive Rate**
```bash
# Solution: Adjust detection thresholds
export WEBAPPSEC_STRICT_MODE=true
export WEBAPPSEC_VERIFICATION=double
```

**Issue: Slow Performance**
```bash
# Solution: Optimize resource usage
export WEBAPPSEC_THREADS=10
export WEBAPPSEC_BATCH_SIZE=100
```

**Issue: Tool Integration Problems**
```bash
# Solution: Verify tool installation and PATH
which nmap sqlmap gobuster ffuf subfinder
```

### Performance Optimization

**For Large-Scale Testing:**
- Use SSD storage for wordlists and payloads
- Increase system file descriptor limits
- Configure appropriate network timeouts
- Use load balancing for distributed testing

**Memory Management:**
- Monitor RAM usage during large wordlist operations
- Use streaming for large payload files
- Implement garbage collection for long-running tests

## Security Considerations

### Testing Ethics

1. **Authorization Required**: Never test without explicit permission
2. **Scope Compliance**: Stay within defined testing boundaries
3. **Data Protection**: Secure all discovered information
4. **Responsible Disclosure**: Follow coordinated vulnerability disclosure

### Legal Compliance

- Verify local laws and regulations
- Obtain proper authorization documentation
- Maintain detailed testing logs
- Follow industry best practices

## Professional Tips

### Effective Testing Strategies

1. **Start with Reconnaissance**: Understand the target before testing
2. **Use Layered Approach**: Combine multiple testing techniques
3. **Verify Findings**: Manual verification of automated results
4. **Document Everything**: Maintain comprehensive testing records
5. **Continuous Learning**: Stay updated with latest vulnerabilities

### Report Generation

```bash
# Generate professional reports
python3 WebAppSec.py --generate-report output/web_security/
python3 WebAppSec.py --export-findings json
python3 WebAppSec.py --create-executive-summary
```

## Conclusion

WebAppSec provides comprehensive web application security testing capabilities with professional-grade tools and extensive payload libraries. The framework's modular architecture and extensive integration capabilities make it suitable for both targeted assessments and comprehensive security evaluations.

Remember to use this powerful framework responsibly and only on authorized systems. The 71,310+ payloads, 39 web shells, and 149 wordlists provide extensive testing capabilities that must be used ethically and legally.

---

**BRAINTREE Security Research Lab**  
Professional Security Framework Usage Guide

**For support and updates**: Continue following best practices and responsible security testing methodologies.