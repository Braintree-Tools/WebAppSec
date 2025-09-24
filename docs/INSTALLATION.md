# Installation Guide - WebAppSec Framework

**Professional Web Application Security Testing Framework Installation**

## System Requirements

### Supported Operating Systems
- **Kali Linux** (Recommended) - 2023.1 or later
- **Ubuntu** - 20.04 LTS or later
- **Debian** - 11 or later
- **Parrot OS** - 5.0 or later

### Hardware Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 10GB free space (for payloads, wordlists, and results)
- **CPU**: 64-bit processor
- **Network**: Internet connection for tool downloads and updates

### Software Prerequisites
- **Python**: 3.8 or higher
- **Git**: For repository cloning
- **pip**: Python package manager
- **Root/Sudo Access**: Required for tool installation

## Pre-Installation System Preparation

### Update System Packages

**Kali Linux / Debian / Ubuntu:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Parrot OS:**
```bash
sudo apt update && sudo parrot-upgrade -y
```

### Install Essential Dependencies
```bash
# Install Python and development tools
sudo apt install -y python3 python3-pip python3-dev python3-venv

# Install build essentials
sudo apt install -y build-essential git curl wget

# Install networking tools
sudo apt install -y net-tools dnsutils
```

## Clone Repository

### Step 1: Choose Installation Directory
```bash
# Create directory for security tools
mkdir -p ~/security-tools
cd ~/security-tools
```

### Step 2: Clone WebAppSec Repository
```bash
# Clone the repository
git clone https://github.com/Braintree-Tools/WebAppSec.git

# Navigate to the project directory
cd WebAppSec
```

### Step 3: Set Permissions
```bash
# Make scripts executable
chmod +x WebAppSec.py
chmod +x src/*.py

# Set appropriate permissions for payload and wordlist directories
chmod -R 755 payloads/
chmod -R 755 wordlists/
chmod -R 755 shells/
```

## Python Dependencies Installation

### Method 1: Using requirements.txt (Recommended)
```bash
# Install Python dependencies
pip3 install -r requirements.txt
```

### Method 2: Manual Installation
```bash
# Core HTTP and web libraries
pip3 install requests urllib3 beautifulsoup4

# CLI and formatting
pip3 install colorama termcolor

# Additional utilities
pip3 install argparse json logging datetime
```

### Method 3: Virtual Environment (Advanced)
```bash
# Create virtual environment
python3 -m venv webappsec-env

# Activate virtual environment
source webappsec-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Note: Remember to activate the environment before running the tool
```

## External Security Tools Installation

WebAppSec integrates with multiple professional security tools. Install the required tools based on your testing needs:

### Essential Tools (Required)

**Network Scanning:**
```bash
# Install nmap
sudo apt install -y nmap

# Install masscan (if available in repos)
sudo apt install -y masscan
```

**Web Application Testing:**
```bash
# Install core web testing tools
sudo apt install -y gobuster ffuf nikto whatweb

# Install sqlmap
sudo apt install -y sqlmap
```

### Advanced Tools (Recommended)

**Reconnaissance Tools:**
```bash
# Install subdomain discovery tools
sudo apt install -y subfinder amass

# Install OSINT tools
sudo apt install -y theharvester

# Install DNS enumeration
sudo apt install -y dnsrecon fierce
```

**Vulnerability Assessment:**
```bash
# Install nuclei template scanner
sudo apt install -y nuclei

# Install WordPress scanner
sudo apt install -y wpscan
```

### Alternative Installation Methods

**For Kali Linux (Complete Installation):**
```bash
sudo apt install -y nmap masscan gobuster ffuf sqlmap nuclei nikto whatweb subfinder amass theharvester dnsrecon fierce wpscan
```

**For Ubuntu/Debian (using snap/manual installation):**
```bash
# Some tools may need manual installation
# Example for subfinder:
wget https://github.com/projectdiscovery/subfinder/releases/download/v2.6.3/subfinder_2.6.3_linux_amd64.zip
unzip subfinder_2.6.3_linux_amd64.zip
sudo mv subfinder /usr/local/bin/
```

## Directory Structure Setup

### Create Output Directories
```bash
# Create output directories
mkdir -p output/web_security
mkdir -p output/web_hacking
mkdir -p output/sql_injection
mkdir -p output/wordlists

# Set permissions
chmod -R 755 output/
```

### Verify Directory Structure
```bash
# Your final structure should look like:
WebAppSec/
├── WebAppSec.py              # Main launcher
├── src/                      # Core modules
│   ├── SecurityScanner.py   # Web security scanner
│   ├── ReconFramework.py    # Reconnaissance framework
│   ├── SQLInjectionTester.py # SQL injection tester
│   ├── PayloadManager.py    # Payload management
│   ├── WordlistManager.py   # Wordlist management
│   └── ShellManager.py      # Shell management
├── payloads/                 # Security payloads (85 files, 71,310+ vectors)
├── shells/                   # Web shells (39 shells)
├── wordlists/                # Dictionary files (149 wordlists, 36M+ entries)
├── docs/                     # Documentation
├── output/                   # Results output
├── requirements.txt          # Python dependencies
└── README.md                # Main documentation
```

## Installation Verification

### Step 1: Check Python Dependencies
```bash
python3 -c "import requests, urllib3, bs4, colorama, termcolor; print('Python dependencies: OK')"
```

### Step 2: Verify Tool Installation
```bash
# Run dependency check
python3 WebAppSec.py --check-deps
```

### Step 3: Test Framework Launch
```bash
# Test interactive mode
python3 WebAppSec.py

# Test help system
python3 WebAppSec.py --help
```

### Step 4: Verify Tool Accessibility
```bash
# Check if essential tools are in PATH
which nmap gobuster sqlmap ffuf nikto whatweb
```

## Troubleshooting Common Issues

### Issue 1: Python Module Import Errors
```bash
# Solution: Reinstall Python dependencies
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
```

### Issue 2: Tool Not Found Errors
```bash
# Solution: Add tools to PATH or install missing tools
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Issue 3: Permission Denied
```bash
# Solution: Set proper permissions
chmod +x WebAppSec.py
chmod -R 755 src/
```

### Issue 4: Missing Tool Dependencies
```bash
# Solution: Install missing tools manually
# Check specific tool documentation for installation
```

## Advanced Configuration

### Environment Variables
```bash
# Optional: Set environment variables
export WEBAPPSEC_HOME=/path/to/WebAppSec
export WEBAPPSEC_OUTPUT=/path/to/output
```

### Tool Path Configuration
```bash
# If tools are installed in custom locations, create symlinks:
sudo ln -s /custom/path/to/tool /usr/local/bin/tool
```

### Performance Optimization
```bash
# For better performance on large wordlists:
# Increase system limits
echo '* soft nofile 65535' | sudo tee -a /etc/security/limits.conf
echo '* hard nofile 65535' | sudo tee -a /etc/security/limits.conf
```

## Update and Maintenance

### Update Framework
```bash
cd WebAppSec
git pull origin main

# Update Python dependencies
pip3 install -r requirements.txt --upgrade
```

### Update Security Tools
```bash
# Update tools using package manager
sudo apt update && sudo apt upgrade -y

# Update specific tools (example for nuclei)
nuclei -update-templates
```

## Installation Verification Checklist

- [ ] System meets hardware requirements
- [ ] Python 3.8+ installed
- [ ] Repository successfully cloned
- [ ] Python dependencies installed
- [ ] Essential security tools installed
- [ ] Directory structure created
- [ ] Permissions set correctly
- [ ] Framework launches without errors
- [ ] Dependency check passes
- [ ] Tool accessibility verified

## Post-Installation Steps

### Security Considerations
1. **Review Disclaimer**: Ensure you understand the legal implications
2. **Authorized Testing**: Only use on systems you own or have permission to test
3. **Network Isolation**: Consider using isolated networks for testing
4. **Data Protection**: Secure your testing results and reports

### Next Steps
1. Read the comprehensive usage guide: `docs/UsageExample.md`
2. Familiarize yourself with the interactive menu system
3. Review the payload and wordlist collections
4. Plan your first authorized security assessment

## Support

If you encounter installation issues:
1. Check the troubleshooting section above
2. Verify system requirements are met
3. Ensure all dependencies are installed
4. Review error messages carefully

## Installation Complete

Your WebAppSec framework is now ready for professional security testing. Remember to use this tool responsibly and only on authorized systems.

**Next**: Proceed to `docs/UsageExample.md` for comprehensive usage instructions.

---

**BRAINTREE Security Research Lab**  
Professional Security Framework Installation Guide
