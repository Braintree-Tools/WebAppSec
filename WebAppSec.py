#!/usr/bin/env python3

"""
WebAppSec v1.0 - Standalone Web Application Security Testing Tool by Braintree
Fixed version with proper EOF handling and output management
Extracted from the Braintree Security Suite

A comprehensive web application security testing suite featuring:
- Web Application Security Testing (OWASP Top 10)
- SQL Injection Testing (SQLMap integration)
- Web Hacking Automation (Subdomain, Directory enumeration)
- Wordlist Management for web testing

Author: Braintree Security Team
Version: 1.0
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Auto-install required packages
def install_requirements():
    """Install required packages if not available"""
    # Map package import names to pip names
    required_packages = {
        'colorama': 'colorama',
        'requests': 'requests', 
        'pyfiglet': 'pyfiglet',
        'bs4': 'beautifulsoup4',  # bs4 is the import name, beautifulsoup4 is pip name
        'dns': 'dnspython',
        'nmap': 'python-nmap',
        'urllib3': 'urllib3'
    }
    
    missing_packages = []
    
    for import_name, pip_name in required_packages.items():
        try:
            if import_name == 'dns':
                import dns.resolver  # Test the specific module we need
            elif import_name == 'nmap':
                try:
                    import nmap
                except ImportError:
                    # Skip nmap if not available, it's optional
                    continue
            else:
                __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Please install them manually:")
        print(f"sudo apt install -y python3-bs4 python3-requests python3-colorama python3-dnspython")
        print(f"pip3 install pyfiglet python-nmap --break-system-packages")

# Install requirements first
install_requirements()

import colorama
from colorama import Fore, Style
colorama.init()

try:
    import pyfiglet
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError as e:
    print(f"Error importing packages: {e}")
    sys.exit(1)

# Import our modules
try:
    from SecurityScanner import WebApplicationSecuritySuite
    from ReconFramework import WebHackingFramework  
    from SQLInjectionTester import SQLInjectionFramework
    from WordlistManager import WordlistManager
except ImportError as e:
    print(f"Error: Could not import WebAppSec modules: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)

class Colors:
    """Color constants for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def safe_input(prompt="", default=""):
    """Safe input function that handles EOF gracefully"""
    try:
        return input(prompt).strip() or default
    except (EOFError, KeyboardInterrupt):
        print(f"\n{Colors.YELLOW}[*] EOF reached or interrupted. Exiting...{Colors.END}")
        return None

class WebAppSecTool:
    """Main WebAppSec standalone tool class"""
    
    def __init__(self):
        self.version = "1.0"
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize modules
        try:
            self.web_app_security = WebApplicationSecuritySuite()
            self.web_hacking = WebHackingFramework()
            self.sql_injection = SQLInjectionFramework()
            self.wordlist_manager = WordlistManager()
            print(f"{Colors.GREEN}[+] WebAppSec Tool initialized successfully{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[-] Error initializing modules: {e}{Colors.END}")
            self.web_app_security = None
            self.web_hacking = None
            self.sql_injection = None
            self.wordlist_manager = None
    
    def print_banner(self):
        """Display WebAppSec banner"""
        try:
            banner = pyfiglet.figlet_format("WebAppSec", font="slant")
            print(f"{Colors.CYAN}{banner}{Colors.END}")
        except:
            print(f"{Colors.CYAN}=" * 50)
            print(f"WebAppSec - Web Application Security Testing Tool")
            print(f"=" * 50 + f"{Colors.END}")
            
        print(f"{Colors.BOLD}{Colors.WHITE}WebAppSec v{self.version} - Standalone Web Application Security Testing Suite{Colors.END}")
        print(f"{Colors.GREEN}by Braintree - Professional Web Penetration Testing{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}")
        print(f"{Colors.BLUE}SQL Injection | Directory Enum | Subdomain Recon | Vulnerability Scanning{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}\n")
    
    def main_menu(self):
        """Display main interactive menu with proper EOF handling"""
        while True:
            try:
                self.print_banner()
                
                print(f"{Colors.BOLD}{Colors.WHITE}WEB APPLICATION SECURITY TESTING{Colors.END}")
                print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
                
                print(f"\n{Colors.BOLD}WEB RECONNAISSANCE{Colors.END}")
                print(f"{Colors.WHITE}[1] Web Hacking Automation{Colors.END}")
                
                print(f"\n{Colors.BOLD}VULNERABILITY TESTING{Colors.END}")
                print(f"{Colors.WHITE}[2] Web Application Security Testing{Colors.END}")
                print(f"{Colors.WHITE}[3] SQL Injection Framework{Colors.END}")
                
                print(f"\n{Colors.BOLD}TOOLS & UTILITIES{Colors.END}")
                print(f"{Colors.WHITE}[4] Wordlist Management{Colors.END}")
                
                print(f"\n{Colors.BOLD}SYSTEM{Colors.END}")
                print(f"{Colors.WHITE}[5] Tool Dependencies Check{Colors.END}")
                print(f"{Colors.WHITE}[0] Exit WebAppSec{Colors.END}")
                
                print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
                
                choice = safe_input(f"\n{Colors.WHITE}[WebAppSec] Select option: {Colors.END}")
                
                if choice is None:  # EOF or KeyboardInterrupt
                    break
                    
                if choice == '1':
                    self.web_hacking_menu()
                elif choice == '2':
                    self.web_app_security_menu()
                elif choice == '3':
                    self.sql_injection_menu()
                elif choice == '4':
                    self.wordlist_management()
                elif choice == '5':
                    self.check_dependencies()
                elif choice == '0':
                    print(f"\n{Colors.GREEN}[*] Thank you for using WebAppSec!{Colors.END}")
                    print(f"{Colors.CYAN}[*] Stay secure and hack responsibly!{Colors.END}")
                    break
                else:
                    print(f"{Colors.RED}[-] Invalid choice. Please try again.{Colors.END}")
                
                if choice in ['1', '2', '3', '4', '5']:
                    wait_input = safe_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
                    if wait_input is None:  # EOF reached
                        break
            
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[*] Exiting WebAppSec...{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.END}")
    
    def web_hacking_menu(self):
        """Web Hacking Automation menu"""
        if not self.web_hacking:
            print(f"{Colors.RED}[-] Web Hacking module not available{Colors.END}")
            return
            
        print(f"{Colors.BOLD}{Colors.CYAN}WEB HACKING AUTOMATION{Colors.END}")
        print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
        print(f"{Colors.WHITE}[1] Full Web Reconnaissance Scan{Colors.END}")
        print(f"{Colors.WHITE}[2] Subdomain Enumeration Only{Colors.END}")
        print(f"{Colors.WHITE}[3] Directory Brute Force Only{Colors.END}")
        print(f"{Colors.WHITE}[4] Web Technology Detection{Colors.END}")
        print(f"{Colors.WHITE}[0] Back to Main Menu{Colors.END}")
        print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
        
        choice = safe_input(f"\n{Colors.WHITE}[WebHacking] Select option: {Colors.END}")
        
        if choice == '1':
            domain = safe_input(f"{Colors.WHITE}Enter target domain (e.g., example.com): {Colors.END}")
            if domain and domain is not None:
                try:
                    print(f"{Colors.YELLOW}[*] Running comprehensive web reconnaissance on {domain}...{Colors.END}")
                    results = self.web_hacking.comprehensive_scan(domain)
                    print(f"{Colors.GREEN}[+] Comprehensive scan completed{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running comprehensive scan: {e}{Colors.END}")
                    
        elif choice == '2':
            domain = safe_input(f"{Colors.WHITE}Enter target domain for subdomain enumeration: {Colors.END}")
            if domain and domain is not None:
                try:
                    print(f"{Colors.YELLOW}[*] Running subdomain enumeration on {domain}...{Colors.END}")
                    subdomains = self.web_hacking.recon.subdomain_enum(domain)
                    print(f"{Colors.GREEN}[+] Found {len(subdomains)} subdomains{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running subdomain enumeration: {e}{Colors.END}")
                    
        elif choice == '3':
            url = safe_input(f"{Colors.WHITE}Enter target URL for directory brute force: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                try:
                    print(f"{Colors.YELLOW}[*] Running directory brute force on {url}...{Colors.END}")
                    paths = self.web_hacking.recon.directory_bruteforce([{'url': url}])
                    print(f"{Colors.GREEN}[+] Directory brute force completed. Found {len(paths)} paths{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running directory brute force: {e}{Colors.END}")
                    
        elif choice == '4':
            url = safe_input(f"{Colors.WHITE}Enter target URL for technology detection: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                try:
                    print(f"{Colors.YELLOW}[*] Running web technology detection on {url}...{Colors.END}")
                    tech_results = self.web_hacking.recon.whatweb_analysis([url])
                    if tech_results:
                        print(f"{Colors.GREEN}[+] Technology detection completed{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] No technology information found{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running technology detection: {e}{Colors.END}")
                    
        elif choice == '0':
            return
        else:
            print(f"{Colors.RED}[-] Invalid choice{Colors.END}")
    
    def web_app_security_menu(self):
        """Web Application Security Testing menu"""
        if not self.web_app_security:
            print(f"{Colors.RED}[-] Web Application Security module not available{Colors.END}")
            return
            
        print(f"{Colors.BOLD}{Colors.CYAN}WEB APPLICATION SECURITY TESTING{Colors.END}")
        try:
            # Call a safer version that doesn't get stuck in infinite loops
            self.safe_web_security_menu()
        except Exception as e:
            print(f"{Colors.RED}[-] Error running Web Application Security: {e}{Colors.END}")
    
    def safe_web_security_menu(self):
        """A safer version of the web security menu"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}WEB APPLICATION SECURITY - MAIN MENU{Colors.END}")
        print(f"{Colors.BLUE}{'-' * 77}{Colors.END}")
        print(f"{Colors.WHITE}[1] Comprehensive Web Security Scan{Colors.END}")
        print(f"{Colors.WHITE}[2] SQL Injection Testing Only{Colors.END}")
        print(f"{Colors.WHITE}[3] XSS Testing Only{Colors.END}")
        print(f"{Colors.WHITE}[4] Directory Brute Force Only{Colors.END}")
        print(f"{Colors.WHITE}[5] CSRF Testing Only{Colors.END}")
        print(f"{Colors.WHITE}[6] Directory Traversal Testing Only{Colors.END}")
        print(f"{Colors.WHITE}[7] Nuclei Vulnerability Scan Only{Colors.END}")
        print(f"{Colors.WHITE}[8] Custom Scan Configuration{Colors.END}")
        print(f"{Colors.WHITE}[0] Exit{Colors.END}")
        print(f"{Colors.BLUE}{'-' * 77}{Colors.END}")
        
        choice = safe_input(f"\n{Colors.WHITE}[WebAppSec] Select option: {Colors.END}")
        
        if choice is None:
            return
            
        if choice == '2':
            url = safe_input(f"{Colors.WHITE}Enter target URL: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                print(f"{Colors.YELLOW}[*] Running SQL injection test on {url}...{Colors.END}")
                # SQLMap test
                print(f"\n{Colors.BOLD}SQLMap Testing{Colors.END}")
                try:
                    sqlmap_result = self.web_app_security.sql_tester.test_url_with_sqlmap(url)
                    if sqlmap_result and sqlmap_result.get('vulnerable'):
                        print(f"{Colors.RED}[VULNERABLE] SQLMap found vulnerabilities{Colors.END}")
                    else:
                        print(f"{Colors.GREEN}[SAFE] No SQL injection vulnerabilities found{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running SQLMap test: {e}{Colors.END}")
        
        elif choice == '1':
            url = safe_input(f"{Colors.WHITE}Enter target URL for comprehensive scan: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                print(f"{Colors.YELLOW}[*] Running comprehensive web security scan on {url}...{Colors.END}")
                try:
                    results = self.web_app_security.comprehensive_web_scan(url)
                    print(f"{Colors.GREEN}[+] Comprehensive scan completed{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running comprehensive scan: {e}{Colors.END}")
        
        elif choice == '3':
            url = safe_input(f"{Colors.WHITE}Enter target URL for XSS testing: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                print(f"{Colors.YELLOW}[*] Running XSS vulnerability test on {url}...{Colors.END}")
                try:
                    test_params = {'q': 'test', 'search': 'test'}
                    reflected_results = self.web_app_security.xss_tester.test_reflected_xss(url, test_params)
                    dom_results = self.web_app_security.xss_tester.test_dom_xss(url)
                    
                    total_xss = len(reflected_results) + len(dom_results)
                    if total_xss > 0:
                        print(f"{Colors.RED}[VULNERABLE] Found {total_xss} XSS vulnerabilities{Colors.END}")
                    else:
                        print(f"{Colors.GREEN}[SAFE] No XSS vulnerabilities found{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running XSS test: {e}{Colors.END}")
        
        elif choice == '4':
            url = safe_input(f"{Colors.WHITE}Enter target URL for directory brute force: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                print(f"{Colors.YELLOW}[*] Running directory brute force on {url}...{Colors.END}")
                try:
                    results = self.web_app_security.directory_bruteforcer.brute_force_directories(url)
                    print(f"{Colors.GREEN}[+] Directory brute force completed. Found {len(results)} paths{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running directory scan: {e}{Colors.END}")
        
        elif choice == '7':
            url = safe_input(f"{Colors.WHITE}Enter target URL for Nuclei scan: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                print(f"{Colors.YELLOW}[*] Running Nuclei vulnerability scan on {url}...{Colors.END}")
                try:
                    results = self.web_app_security.nuclei_scanner.scan_with_nuclei(url)
                    if results:
                        print(f"{Colors.YELLOW}[FINDINGS] Nuclei found {len(results)} issues{Colors.END}")
                    else:
                        print(f"{Colors.GREEN}[CLEAN] No issues found by Nuclei{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running Nuclei scan: {e}{Colors.END}")
        
        elif choice == '8':
            print(f"{Colors.CYAN}[*] Custom scan configuration available in full interactive mode{Colors.END}")
            print(f"{Colors.BLUE}[INFO] Run without --web-security flag for full options{Colors.END}")
            
        elif choice == '0':
            return
            
        else:
            print(f"{Colors.YELLOW}[*] Option {choice} - Available in full interactive mode{Colors.END}")
    
    def sql_injection_menu(self):
        """SQL Injection Framework menu"""
        if not self.sql_injection:
            print(f"{Colors.RED}[-] SQL Injection module not available{Colors.END}")
            return
            
        print(f"{Colors.BOLD}{Colors.CYAN}SQL INJECTION FRAMEWORK{Colors.END}")
        print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
        print(f"{Colors.WHITE}[1] Comprehensive SQL Injection Scan{Colors.END}")
        print(f"{Colors.WHITE}[2] SQLMap Integration Testing{Colors.END}")
        print(f"{Colors.WHITE}[3] Manual SQL Injection Testing{Colors.END}")
        print(f"{Colors.WHITE}[4] Database Fingerprinting{Colors.END}")
        print(f"{Colors.WHITE}[0] Back to Main Menu{Colors.END}")
        print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
        
        choice = safe_input(f"\n{Colors.WHITE}[SQLInjection] Select option: {Colors.END}")
        
        if choice == '1':
            urls_input = safe_input(f"{Colors.WHITE}Enter target URLs (comma-separated): {Colors.END}")
            if urls_input and urls_input is not None:
                urls = [url.strip() for url in urls_input.split(',')]
                try:
                    print(f"{Colors.YELLOW}[*] Running comprehensive SQL injection scan on {len(urls)} URLs...{Colors.END}")
                    results = self.sql_injection.sqlmap_comprehensive_scan(urls)
                    total_vulns = sum(len(result.get('vulnerabilities', [])) for result in results.values())
                    print(f"{Colors.GREEN}[+] Comprehensive scan completed. Found {total_vulns} vulnerabilities{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running comprehensive scan: {e}{Colors.END}")
                    
        elif choice == '2':
            url = safe_input(f"{Colors.WHITE}Enter target URL for SQLMap testing: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                try:
                    print(f"{Colors.YELLOW}[*] Running SQLMap integration test on {url}...{Colors.END}")
                    results = self.sql_injection.test_url_with_sqlmap(url)
                    if results and results.get('vulnerable'):
                        print(f"{Colors.RED}[VULNERABLE] SQLMap found vulnerabilities{Colors.END}")
                    else:
                        print(f"{Colors.GREEN}[SAFE] No SQL injection vulnerabilities found{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running SQLMap test: {e}{Colors.END}")
                    
        elif choice == '3':
            url = safe_input(f"{Colors.WHITE}Enter target URL for manual testing: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                try:
                    print(f"{Colors.YELLOW}[*] Running manual SQL injection testing on {url}...{Colors.END}")
                    test_params = {'id': '1', 'search': 'test', 'q': 'test', 'page': '1'}
                    results = self.sql_injection.manual_sql_injection_test(url, test_params)
                    if results:
                        print(f"{Colors.RED}[VULNERABLE] Found {len(results)} potential SQL injection issues{Colors.END}")
                    else:
                        print(f"{Colors.GREEN}[SAFE] No manual SQL injection vulnerabilities found{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running manual test: {e}{Colors.END}")
                    
        elif choice == '4':
            url = safe_input(f"{Colors.WHITE}Enter target URL for database fingerprinting: {Colors.END}")
            if url and url is not None:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                try:
                    print(f"{Colors.YELLOW}[*] Running database fingerprinting on {url}...{Colors.END}")
                    db_type = self.sql_injection._detect_database_type(url)
                    if db_type:
                        print(f"{Colors.GREEN}[+] Detected database type: {db_type.upper()}{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] Could not determine database type{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}[-] Error running database fingerprinting: {e}{Colors.END}")
                    
        elif choice == '0':
            return
        else:
            print(f"{Colors.RED}[-] Invalid choice{Colors.END}")
    
    def wordlist_management(self):
        """Wordlist Management menu"""
        if not self.wordlist_manager:
            print(f"{Colors.RED}[-] Wordlist Manager module not available{Colors.END}")
            return
            
        print(f"{Colors.BOLD}{Colors.CYAN}WORDLIST MANAGEMENT{Colors.END}")
        try:
            # Simple wordlist info display
            print(f"{Colors.YELLOW}[*] Available wordlist categories:{Colors.END}")
            categories = ["passwords", "discovery", "usernames", "fuzzing", "payloads"]
            for i, category in enumerate(categories, 1):
                print(f"  {Colors.WHITE}[{i}] {category.title()}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[-] Error accessing Wordlist Manager: {e}{Colors.END}")
    
    def check_dependencies(self):
        """Check and install security tool dependencies"""
        print(f"{Colors.BOLD}{Colors.CYAN}DEPENDENCY CHECK{Colors.END}")
        
        tools = [
            'nmap', 'sqlmap', 'gobuster', 'ffuf', 'subfinder', 
            'amass', 'nuclei', 'nikto', 'whatweb', 'theharvester'
        ]
        
        print(f"{Colors.YELLOW}[*] Checking security tool dependencies...{Colors.END}")
        
        for tool in tools:
            try:
                import subprocess
                result = subprocess.run(['which', tool], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  {Colors.GREEN}[+]{Colors.END} {tool:<15} {Colors.BLUE}({result.stdout.strip()}){Colors.END}")
                else:
                    print(f"  {Colors.RED}[-]{Colors.END} {tool:<15} {Colors.RED}(not found){Colors.END}")
            except Exception as e:
                print(f"  {Colors.RED}[-]{Colors.END} {tool:<15} {Colors.RED}(check failed){Colors.END}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="WebAppSec v1.0 - Standalone Web Application Security Testing Tool by Braintree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 WebAppSec.py                              # Interactive mode
  python3 WebAppSec.py --web-hacking                # Web Hacking Automation
  python3 WebAppSec.py --sql-injection              # SQL Injection Testing
  python3 WebAppSec.py --web-security              # Web Application Security Testing
        """
    )
    
    parser.add_argument('--web-hacking', action='store_true', help='Run Web Hacking Automation')
    parser.add_argument('--sql-injection', action='store_true', help='Run SQL Injection Framework')
    parser.add_argument('--web-security', action='store_true', help='Run Web Application Security Testing')
    parser.add_argument('--check-deps', action='store_true', help='Check tool dependencies')
    parser.add_argument('--output', '-o', help='Output directory', default='output')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet output')
    
    args = parser.parse_args()
    
    # Create WebAppSec tool instance
    websec = WebAppSecTool()
    
    # Handle command line arguments
    if args.web_hacking:
        websec.print_banner()
        print(f"{Colors.GREEN}[*] Starting Web Hacking Automation...{Colors.END}")
        websec.web_hacking_menu()
        return
    
    if args.sql_injection:
        websec.print_banner()
        print(f"{Colors.GREEN}[*] Starting SQL Injection Framework...{Colors.END}")
        websec.sql_injection_menu()
        return
        
    if args.web_security:
        websec.print_banner()
        print(f"{Colors.GREEN}[*] Starting Web Application Security Testing...{Colors.END}")
        websec.web_app_security_menu()
        return
        
    if args.check_deps:
        websec.print_banner()
        websec.check_dependencies()
        return
    
    # If no CLI arguments, start interactive mode
    websec.main_menu()

if __name__ == "__main__":
    main()