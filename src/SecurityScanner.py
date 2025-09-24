#!/usr/bin/env python3

"""
WebAppSec v1.0 - Advanced Web Application Security Suite by Braintree
Real web vulnerability testing with SQLMap, Nuclei, FFUF, and custom modules
Compatible with Kali Linux and NetHunter Android

Author: Braintree Security Team
Version: 1.0
"""

import os
import sys
import time
import json
import subprocess
import threading
import tempfile
import socket
import urllib.parse
import re
from datetime import datetime
import argparse
import concurrent.futures
from pathlib import Path
import base64
import hashlib
import xml.etree.ElementTree as ET

# Import Braintree managers
try:
    from .PayloadManager import PayloadManager
    from .WordlistManager import WordlistManager
    from .ShellManager import ShellManager
except ImportError:
    # Fallback for when running as standalone script
    from PayloadManager import PayloadManager
    from WordlistManager import WordlistManager
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
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import pyfiglet
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pyfiglet"], check=True)
    import pyfiglet

try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "beautifulsoup4"], check=True)
    from bs4 import BeautifulSoup

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

class SQLInjectionTester:
    """SQL Injection testing using SQLMap and custom payloads"""
    
    def __init__(self):
        self.sqlmap_path = self._find_sqlmap()
        self.payload_manager = PayloadManager()
        self.wordlist_manager = WordlistManager()
        self.payloads = self._load_sql_payloads_from_manager()
        self.results = []
    
    def _find_sqlmap(self):
        """Find SQLMap installation"""
        possible_paths = [
            '/usr/bin/sqlmap',
            '/usr/share/sqlmap/sqlmap.py',
            '/opt/sqlmap/sqlmap.py',
            'sqlmap'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
            elif path == 'sqlmap':
                try:
                    result = subprocess.run(['which', 'sqlmap'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return 'sqlmap'
                except:
                    continue
        
        return None
    
    def _load_sql_payloads_from_manager(self):
        """Load SQL injection payloads from PayloadManager"""
        print(f"{Colors.CYAN}[INFO] Loading SQL injection payloads from PayloadManager...{Colors.END}")
        
        payloads = {
            'error_based': self.payload_manager.get_payload_list('sqli', 'error_based') or [],
            'blind_based': self.payload_manager.get_payload_list('sqli', 'blind_payloads') or [],
            'union_based': self.payload_manager.get_payload_list('sqli', 'union_select') or [],
            'generic': self.payload_manager.get_payload_list('sqli', 'generic_sqli') or [],
            'mysql': self.payload_manager.get_payload_list('sqli', 'mysql') or [],
            'mssql': self.payload_manager.get_payload_list('sqli', 'mssql') or [],
            'oracle': self.payload_manager.get_payload_list('sqli', 'oracle') or [],
            'auth_bypass': self.payload_manager.get_payload_list('sqli', 'auth_bypass') or [],
            'time_based': self.payload_manager.get_payload_list('sqli', 'time_based') or []
        }
        
        # Count total payloads loaded
        total_payloads = sum(len(p) for p in payloads.values())
        print(f"{Colors.GREEN}[+] Loaded {total_payloads} SQL injection payloads from manager{Colors.END}")
        
        # Fallback to built-in if manager fails
        if total_payloads == 0:
            print(f"{Colors.YELLOW}[!] No payloads from manager, using fallback payloads{Colors.END}")
            payloads = self._get_fallback_payloads()
        
        return payloads
    
    def _get_fallback_payloads(self):
        """Fallback SQL injection payloads if manager fails"""
        return {
            'error_based': ["' OR 1=1--", "\" OR 1=1--", "' OR '1'='1"],
            'blind_based': ["' AND 1=1--", "' AND 1=2--", "' AND SLEEP(5)--"],
            'union_based': ["' UNION SELECT 1,2,3,4,5--", "' UNION SELECT null,@@version,null,null--"]
        }
    
    def get_payloads_for_target(self, url, db_type=None):
        """Get appropriate payloads based on target and database type"""
        print(f"{Colors.CYAN}[INFO] Selecting payloads for target: {url}{Colors.END}")
        
        # Auto-detect database type if not specified
        if not db_type:
            db_type = self._detect_database_type(url)
            
        if db_type:
            print(f"{Colors.GREEN}[+] Detected/Using database type: {db_type.upper()}{Colors.END}")
            # Get specific payloads for the database type
            specific_payloads = self.payloads.get(db_type.lower(), [])
            if specific_payloads:
                print(f"{Colors.GREEN}[+] Using {len(specific_payloads)} {db_type}-specific payloads{Colors.END}")
                return specific_payloads
        else:
            print(f"{Colors.YELLOW}[!] Database type not detected, using generic payloads{Colors.END}")
        
        # Fallback to generic and error-based payloads
        combined_payloads = []
        for payload_type in ['generic', 'error_based', 'union_based']:
            combined_payloads.extend(self.payloads.get(payload_type, []))
        
        print(f"{Colors.GREEN}[+] Using {len(combined_payloads)} combined payloads{Colors.END}")
        return combined_payloads
    
    def _detect_database_type(self, url):
        """Attempt to detect database type from URL or error responses"""
        print(f"{Colors.BLUE}[*] Attempting to detect database type...{Colors.END}")
        
        # URL-based detection
        url_lower = url.lower()
        if 'mysql' in url_lower or 'phpmyadmin' in url_lower:
            return 'mysql'
        elif 'mssql' in url_lower or 'sqlserver' in url_lower:
            return 'mssql'
        elif 'oracle' in url_lower:
            return 'oracle'
        elif 'postgres' in url_lower or 'postgresql' in url_lower:
            return 'postgresql'
        
        # Try error-based detection
        try:
            test_payloads = ["'", '"', "1'"]
            for payload in test_payloads:
                test_url = f"{url}{'&' if '?' in url else '?'}test={payload}"
                response = requests.get(test_url, timeout=10, verify=False)
                error_text = response.text.lower()
                
                if any(mysql_err in error_text for mysql_err in ['mysql', 'mysqld', 'mariadb']):
                    return 'mysql'
                elif any(mssql_err in error_text for mssql_err in ['microsoft sql', 'sqlserver', 'mssql']):
                    return 'mssql'
                elif any(oracle_err in error_text for oracle_err in ['oracle', 'ora-', 'oci']):
                    return 'oracle'
                elif any(postgres_err in error_text for postgres_err in ['postgresql', 'postgres']):
                    return 'postgresql'
        except:
            pass
            
        return None
    
    def test_url_with_sqlmap(self, url, data=None, cookie=None):
        """Test URL with SQLMap"""
        print(f"{Colors.YELLOW}[*] Testing {url} with SQLMap...{Colors.END}")
        
        if not self.sqlmap_path:
            print(f"{Colors.RED}[-] SQLMap not found. Install with: apt install sqlmap{Colors.END}")
            return None
        
        # Build SQLMap command
        sqlmap_cmd = [
            'python3' if self.sqlmap_path.endswith('.py') else 'sqlmap',
            self.sqlmap_path if self.sqlmap_path.endswith('.py') else '',
            '-u', url,
            '--batch',
            '--level=3',
            '--risk=2',
            '--timeout=10',
            '--retries=2',
            '--threads=5'
        ]
        
        # Remove empty strings
        sqlmap_cmd = [cmd for cmd in sqlmap_cmd if cmd]
        
        # Add POST data if provided
        if data:
            sqlmap_cmd.extend(['--data', data])
        
        # Add cookie if provided
        if cookie:
            sqlmap_cmd.extend(['--cookie', cookie])
        
        # Add output options
        output_file = f"/tmp/sqlmap_output_{int(time.time())}.txt"
        sqlmap_cmd.extend(['--output-dir', '/tmp', '--flush-session'])
        
        try:
            print(f"{Colors.PURPLE}[CMD] Running: {' '.join(sqlmap_cmd)}{Colors.END}")
            print(f"{Colors.CYAN}[INFO] SQLMap is analyzing the target... This may take a few minutes{Colors.END}")
            print(f"{Colors.YELLOW}[LOGS] Real-time SQLMap output:{Colors.END}")
            
            # Run SQLMap with real-time output
            process = subprocess.Popen(
                sqlmap_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd='/tmp'
            )
            
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    # Show important lines in real-time
                    if any(keyword in line.lower() for keyword in ['testing', 'parameter', 'payload', 'vulnerable', 'injectable', 'found', 'error', 'info']):
                        if 'error' in line.lower():
                            print(f"{Colors.RED}[SQLMAP] {line}{Colors.END}")
                        elif 'vulnerable' in line.lower() or 'injectable' in line.lower():
                            print(f"{Colors.RED}[SQLMAP] {line}{Colors.END}")
                        elif 'testing' in line.lower() or 'parameter' in line.lower():
                            print(f"{Colors.YELLOW}[SQLMAP] {line}{Colors.END}")
                        elif 'found' in line.lower():
                            print(f"{Colors.GREEN}[SQLMAP] {line}{Colors.END}")
                        else:
                            print(f"{Colors.CYAN}[SQLMAP] {line}{Colors.END}")
            
            result_code = process.poll()
            full_output = '\n'.join(output_lines)
            
            if result_code == 0:
                print(f"\n{Colors.BLUE}[INFO] SQLMap scan completed successfully{Colors.END}")
                vulnerable_params = self._parse_sqlmap_output(full_output)
                if vulnerable_params:
                    print(f"{Colors.RED}[VULNERABLE] SQL injection found!{Colors.END}")
                    for param in vulnerable_params:
                        print(f"  {Colors.WHITE}Parameter: {param}{Colors.END}")
                    
                    return {
                        'vulnerable': True,
                        'parameters': vulnerable_params,
                        'tool': 'sqlmap',
                        'output': full_output
                    }
                else:
                    print(f"{Colors.GREEN}[SAFE] No SQL injection vulnerabilities found{Colors.END}")
                    return {
                        'vulnerable': False,
                        'tool': 'sqlmap',
                        'output': full_output
                    }
            else:
                print(f"{Colors.RED}[ERROR] SQLMap failed with exit code {result_code}{Colors.END}")
                if output_lines:
                    print(f"{Colors.YELLOW}[ERROR OUTPUT] Last few lines:{Colors.END}")
                    for line in output_lines[-5:]:
                        print(f"  {Colors.RED}{line}{Colors.END}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[-] SQLMap timeout{Colors.END}")
            return None
        except Exception as e:
            print(f"{Colors.RED}[-] SQLMap error: {e}{Colors.END}")
            return None
    
    def _parse_sqlmap_output(self, output):
        """Parse SQLMap output for vulnerabilities"""
        vulnerable_params = []
        
        lines = output.split('\n')
        for line in lines:
            if 'Parameter:' in line and 'is vulnerable' in line:
                # Extract parameter name
                param_match = re.search(r'Parameter: (\w+)', line)
                if param_match:
                    vulnerable_params.append(param_match.group(1))
            elif 'injectable' in line.lower():
                # Look for injectable parameters
                param_match = re.search(r'(\w+).*injectable', line)
                if param_match:
                    vulnerable_params.append(param_match.group(1))
        
        return vulnerable_params
    
    def manual_sql_injection_test(self, url, parameters):
        """Manual SQL injection testing"""
        print(f"{Colors.YELLOW}[*] Manual SQL injection testing on {url}...{Colors.END}")
        
        results = []
        
        for param_name, param_value in parameters.items():
            print(f"  {Colors.CYAN}[*] Testing parameter: {param_name}{Colors.END}")
            
            for payload_type, payloads in self.payloads.items():
                for payload in payloads[:3]:  # Test first 3 payloads of each type
                    test_params = parameters.copy()
                    test_params[param_name] = param_value + payload
                    
                    try:
                        response = requests.get(
                            url, 
                            params=test_params, 
                            timeout=10, 
                            verify=False
                        )
                        
                        # Check for SQL error indicators
                        if self._detect_sql_errors(response.text):
                            result = {
                                'parameter': param_name,
                                'payload': payload,
                                'payload_type': payload_type,
                                'vulnerable': True,
                                'response_length': len(response.text),
                                'status_code': response.status_code
                            }
                            results.append(result)
                            print(f"    {Colors.RED}[VULNERABLE] {payload_type} SQL injection detected{Colors.END}")
                            break
                        
                    except requests.exceptions.RequestException as e:
                        continue
        
        return results
    
    def _detect_sql_errors(self, response_text):
        """Detect SQL error messages"""
        sql_errors = [
            'sql syntax',
            'mysql_fetch',
            'ORA-01756',
            'Microsoft OLE DB',
            'ODBC SQL Server',
            'SQLServer JDBC',
            'PostgreSQL query failed',
            'unterminated quoted string',
            'quoted string not properly terminated',
            'SQL command not properly ended',
            'Warning: mysql_',
            'MySQLSyntaxErrorException',
            'valid MySQL result',
            'check the manual that corresponds to your MySQL',
            'Unknown column',
            'where clause',
            'MySqlException',
            'SqlException',
            'OracleException',
            'SQLite3::SQLException'
        ]
        
        response_lower = response_text.lower()
        for error in sql_errors:
            if error.lower() in response_lower:
                return True
        
        return False

class XSSTester:
    """Cross-Site Scripting (XSS) vulnerability testing"""
    
    def __init__(self):
        self.payload_manager = PayloadManager()
        self.payloads = self._load_xss_payloads()
        self.results = []
    
    def _load_xss_payloads(self):
        """Load XSS payloads from PayloadManager"""
        print(f"{Colors.CYAN}[INFO] Loading XSS payloads from PayloadManager...{Colors.END}")
        
        payloads = {
            'reflected': self.payload_manager.get_payload_list('xss', 'reflected') or [],
            'stored': self.payload_manager.get_payload_list('xss', 'stored') or [],
            'dom_based': self.payload_manager.get_payload_list('xss', 'dom_based') or [],
            'basic': self.payload_manager.get_payload_list('xss', 'basic') or [],
            'advanced': self.payload_manager.get_payload_list('xss', 'advanced') or [],
            'polyglot': self.payload_manager.get_payload_list('xss', 'polyglot') or []
        }
        
        # Count total payloads loaded
        total_payloads = sum(len(p) for p in payloads.values())
        print(f"{Colors.GREEN}[+] Loaded {total_payloads} XSS payloads from manager{Colors.END}")
        
        # Fallback to built-in if manager fails
        if total_payloads == 0:
            print(f"{Colors.YELLOW}[!] No payloads from manager, using fallback payloads{Colors.END}")
            payloads = self._get_fallback_xss_payloads()
        
        return payloads
    
    def _get_fallback_xss_payloads(self):
        """Fallback XSS payloads if PayloadManager fails"""
        return {
            'reflected': [
                '<script>alert("XSS")</script>',
                '<img src=x onerror=alert("XSS")>',
                '<svg onload=alert("XSS")>',
                '"><script>alert("XSS")</script>',
                "'><script>alert('XSS')</script>",
                '<iframe src="javascript:alert(`XSS`)">',
                '<input onfocus=alert("XSS") autofocus>',
                '<select onfocus=alert("XSS") autofocus>',
                '<textarea onfocus=alert("XSS") autofocus>',
                '<keygen onfocus=alert("XSS") autofocus>',
                '<body onload=alert("XSS")>',
                '<div onmouseover=alert("XSS")>'
            ],
            'stored': [
                '<script>alert("Stored XSS")</script>',
                '<img src=x onerror=alert("Stored")>',
                '<<SCRIPT>alert("Stored")//<</SCRIPT>',
                '<SCRIPT SRC=http://xss.rocks/xss.js></SCRIPT>',
                '<svg/onload=alert("Stored")>',
                '<iframe src=javascript:alert("Stored")>',
                '<object data="javascript:alert(\'Stored\')">'
            ],
            'dom_based': [
                '#<img src=/ onerror=alert("DOM")>',
                '#<svg onload=alert("DOM")>',
                '#<iframe src=javascript:alert("DOM")>',
                'javascript:alert("DOM")',
                'data:text/html,<script>alert("DOM")</script>'
            ]
        }
    
    def test_reflected_xss(self, url, parameters):
        """Test for reflected XSS"""
        print(f"{Colors.YELLOW}[*] Testing for reflected XSS...{Colors.END}")
        
        results = []
        
        for param_name, param_value in parameters.items():
            print(f"  {Colors.CYAN}[*] Testing parameter: {param_name}{Colors.END}")
            
            for payload in self.payloads['reflected']:
                test_params = parameters.copy()
                test_params[param_name] = payload
                
                try:
                    response = requests.get(
                        url, 
                        params=test_params, 
                        timeout=10, 
                        verify=False,
                        allow_redirects=True
                    )
                    
                    # Check if payload is reflected in response
                    if payload in response.text:
                        result = {
                            'type': 'Reflected XSS',
                            'parameter': param_name,
                            'payload': payload,
                            'vulnerable': True,
                            'url': response.url
                        }
                        results.append(result)
                        print(f"    {Colors.RED}[VULNERABLE] Reflected XSS found with payload: {payload[:30]}...{Colors.END}")
                        break
                
                except requests.exceptions.RequestException:
                    continue
        
        return results
    
    def test_stored_xss(self, url, form_data):
        """Test for stored XSS"""
        print(f"{Colors.YELLOW}[*] Testing for stored XSS...{Colors.END}")
        
        results = []
        
        for field_name, field_value in form_data.items():
            print(f"  {Colors.CYAN}[*] Testing form field: {field_name}{Colors.END}")
            
            for payload in self.payloads['stored']:
                test_data = form_data.copy()
                test_data[field_name] = payload
                
                try:
                    # Submit the form
                    response = requests.post(
                        url,
                        data=test_data,
                        timeout=10,
                        verify=False,
                        allow_redirects=True
                    )
                    
                    # Check if payload was stored (simple check)
                    if payload in response.text:
                        result = {
                            'type': 'Stored XSS',
                            'field': field_name,
                            'payload': payload,
                            'vulnerable': True,
                            'url': url
                        }
                        results.append(result)
                        print(f"    {Colors.RED}[VULNERABLE] Stored XSS found with payload: {payload[:30]}...{Colors.END}")
                        break
                
                except requests.exceptions.RequestException:
                    continue
        
        return results
    
    def test_dom_xss(self, url):
        """Test for DOM-based XSS"""
        print(f"{Colors.YELLOW}[*] Testing for DOM-based XSS...{Colors.END}")
        
        results = []
        
        for payload in self.payloads['dom_based']:
            test_url = f"{url}{payload}"
            
            try:
                response = requests.get(
                    test_url,
                    timeout=10,
                    verify=False,
                    allow_redirects=True
                )
                
                # Look for dangerous DOM manipulation patterns
                if self._detect_dom_vulnerabilities(response.text, payload):
                    result = {
                        'type': 'DOM-based XSS',
                        'payload': payload,
                        'vulnerable': True,
                        'url': test_url
                    }
                    results.append(result)
                    print(f"    {Colors.RED}[VULNERABLE] DOM XSS found with payload: {payload}{Colors.END}")
                    break
            
            except requests.exceptions.RequestException:
                continue
        
        return results
    
    def _detect_dom_vulnerabilities(self, response_text, payload):
        """Detect DOM-based XSS vulnerabilities"""
        # Look for JavaScript that processes URL fragments or parameters
        dom_patterns = [
            'location.hash',
            'location.search',
            'document.URL',
            'document.location',
            'window.location',
            'location.href',
            'document.referrer',
            'window.name',
            'history.pushState',
            'history.replaceState'
        ]
        
        response_lower = response_text.lower()
        
        # Check if payload appears in dangerous contexts
        if payload.lower() in response_lower:
            return True
        
        # Check for patterns that suggest DOM manipulation
        for pattern in dom_patterns:
            if pattern in response_lower and 'innerHTML' in response_lower:
                return True
        
        return False

class DirectoryTraversalTester:
    """Directory traversal and Local File Inclusion testing"""
    
    def __init__(self):
        self.payload_manager = PayloadManager()
        self.payloads = self._load_traversal_payloads()
        self.common_files = self._load_common_files()
        self.results = []
    
    def _load_traversal_payloads(self):
        """Load directory traversal payloads from PayloadManager"""
        print(f"{Colors.CYAN}[INFO] Loading directory traversal payloads from PayloadManager...{Colors.END}")
        
        payloads = {
            'lfi': self.payload_manager.get_payload_list('web', 'lfi') or [],
            'path_traversal': self.payload_manager.get_payload_list('web', 'path_traversal') or [],
            'lfi_windows': self.payload_manager.get_payload_list('web', 'lfi_windows') or []
        }
        
        # Count total payloads loaded
        total_payloads = sum(len(p) for p in payloads.values())
        print(f"{Colors.GREEN}[+] Loaded {total_payloads} directory traversal payloads from manager{Colors.END}")
        
        # Fallback to built-in if manager fails
        if total_payloads == 0:
            print(f"{Colors.YELLOW}[!] No payloads from manager, using fallback payloads{Colors.END}")
            payloads = self._get_fallback_traversal_payloads()
        
        return payloads
    
    def _get_fallback_traversal_payloads(self):
        """Fallback directory traversal payloads if PayloadManager fails"""
        return {
            'unix': [
                '../../../etc/passwd',
                '../../../../etc/passwd',
                '../../../../../etc/passwd',
                '../../../../../../etc/passwd',
                '../../../etc/hosts',
                '../../../proc/version',
                '../../../etc/shadow',
                '/etc/passwd',
                '/etc/hosts',
                '/proc/version',
                '....//....//....//etc/passwd',
                '..\\..\\..\\etc\\passwd'
            ],
            'windows': [
                '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
                '..\\..\\..\\windows\\win.ini',
                '..\\..\\..\\windows\\system.ini',
                '..\\..\\..\\boot.ini',
                '..\\..\\..\\windows\\WindowsUpdate.log',
                'C:\\windows\\system32\\drivers\\etc\\hosts',
                'C:\\windows\\win.ini',
                'C:\\boot.ini',
                '....\\\\....\\\\....\\\\windows\\\\win.ini'
            ],
            'encoded': [
                '%2e%2e%2f%2e%2e%2f%2e%2e%2f%65%74%63%2f%70%61%73%73%77%64',
                '%2e%2e%5c%2e%2e%5c%2e%2e%5c%77%69%6e%64%6f%77%73%5c%77%69%6e%2e%69%6e%69',
                '..%252f..%252f..%252fetc%252fpasswd',
                '..%c0%af..%c0%af..%c0%afetc%c0%afpasswd',
                '%252e%252e%252fetc%252fpasswd'
            ]
        }
    
    def _load_common_files(self):
        """Load list of common files to target for traversal attacks"""
        return [
            # Unix/Linux files
            '/etc/passwd',
            '/etc/shadow',
            '/etc/hosts',
            '/etc/resolv.conf',
            '/etc/issue',
            '/proc/version',
            '/proc/cmdline',
            '/proc/self/environ',
            '/var/log/apache2/access.log',
            '/var/log/apache/access_log',
            '/var/log/httpd/access_log',
            # Windows files
            'C:\\windows\\win.ini',
            'C:\\windows\\system.ini',
            'C:\\boot.ini',
            'C:\\windows\\system32\\drivers\\etc\\hosts',
            'C:\\windows\\system32\\config\\sam',
            'C:\\windows\\repair\\sam',
            'C:\\windows\\system32\\config\\system',
            'C:\\windows\\system32\\config\\software',
            # Application files
            '/var/www/html/index.php',
            '/var/www/index.php',
            '/home/www/index.php',
            'web.config',
            'app.config',
            '.env',
            'config.php',
            'database.php'
        ]
    
    def test_directory_traversal(self, url, parameters):
        """Test for directory traversal vulnerabilities"""
        print(f"{Colors.YELLOW}[*] Testing for directory traversal...{Colors.END}")
        
        results = []
        
        for param_name, param_value in parameters.items():
            print(f"  {Colors.CYAN}[*] Testing parameter: {param_name}{Colors.END}")
            
            # Test all payload types
            for payload_type, payloads in self.payloads.items():
                for payload in payloads:
                    test_params = parameters.copy()
                    test_params[param_name] = payload
                    
                    try:
                        response = requests.get(
                            url,
                            params=test_params,
                            timeout=10,
                            verify=False
                        )
                        
                        # Check for successful file inclusion
                        if self._detect_file_inclusion(response.text, payload):
                            result = {
                                'type': 'Directory Traversal',
                                'parameter': param_name,
                                'payload': payload,
                                'payload_type': payload_type,
                                'vulnerable': True,
                                'response_snippet': response.text[:200]
                            }
                            results.append(result)
                            print(f"    {Colors.RED}[VULNERABLE] Directory traversal found: {payload}{Colors.END}")
                            break
                    
                    except requests.exceptions.RequestException:
                        continue
        
        return results
    
    def _detect_file_inclusion(self, response_text, payload):
        """Detect successful file inclusion"""
        # Unix file signatures
        unix_signatures = [
            'root:x:0:0:',  # /etc/passwd
            'daemon:x:1:1:',
            'localhost',  # /etc/hosts
            'kernel version',  # /proc/version
            'Linux version'
        ]
        
        # Windows file signatures
        windows_signatures = [
            '[fonts]',  # win.ini
            '[boot loader]',  # boot.ini
            'default=multi',
            '[Mail]',
            '[MCI Extensions]'
        ]
        
        response_lower = response_text.lower()
        
        # Check for Unix signatures
        for signature in unix_signatures:
            if signature.lower() in response_lower:
                return True
        
        # Check for Windows signatures
        for signature in windows_signatures:
            if signature.lower() in response_lower:
                return True
        
        # Check for generic error patterns that might indicate file access
        error_patterns = [
            'no such file or directory',
            'permission denied',
            'access denied',
            'file not found'
        ]
        
        for pattern in error_patterns:
            if pattern in response_lower and 'etc' in payload.lower():
                return True
        
        return False

class CSRFTester:
    """Cross-Site Request Forgery (CSRF) testing"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.results = []
    
    def test_csrf_protection(self, url, form_data=None):
        """Test for CSRF protection mechanisms"""
        print(f"{Colors.YELLOW}[*] Testing CSRF protection...{Colors.END}")
        
        results = []
        
        try:
            # Get the original form
            response = requests.get(url, verify=False, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all forms
            forms = soup.find_all('form')
            
            for form in forms:
                form_action = form.get('action', url)
                form_method = form.get('method', 'get').lower()
                
                # Extract form fields
                form_fields = {}
                for input_field in form.find_all(['input', 'textarea', 'select']):
                    field_name = input_field.get('name')
                    field_value = input_field.get('value', 'test')
                    field_type = input_field.get('type', 'text')
                    
                    if field_name:
                        form_fields[field_name] = field_value
                
                # Check for CSRF tokens
                csrf_tokens = self._detect_csrf_tokens(form_fields, response.text)
                
                if not csrf_tokens:
                    # Try to submit without CSRF token
                    csrf_result = self._test_csrf_submission(form_action, form_method, form_fields)
                    if csrf_result['vulnerable']:
                        results.append(csrf_result)
                        print(f"  {Colors.RED}[VULNERABLE] No CSRF protection on form: {form_action}{Colors.END}")
                else:
                    print(f"  {Colors.GREEN}[PROTECTED] CSRF tokens found: {csrf_tokens}{Colors.END}")
        
        except Exception as e:
            print(f"{Colors.RED}[-] CSRF testing error: {e}{Colors.END}")
        
        return results
    
    def _detect_csrf_tokens(self, form_fields, response_text):
        """Detect CSRF tokens in form"""
        csrf_indicators = [
            'csrf', 'token', '_token', 'authenticity_token',
            'csrftoken', 'csrf_token', '__token', 'anti_csrf',
            'form_token', 'security_token', 'nonce'
        ]
        
        found_tokens = []
        
        # Check form fields
        for field_name in form_fields.keys():
            for indicator in csrf_indicators:
                if indicator.lower() in field_name.lower():
                    found_tokens.append(field_name)
        
        # Check meta tags in response
        for indicator in csrf_indicators:
            if f'name="{indicator}"' in response_text or f"name='{indicator}'" in response_text:
                found_tokens.append(f"meta_{indicator}")
        
        return found_tokens
    
    def _extract_csrf_tokens(self, html_content):
        """Extract CSRF tokens from HTML content - for test compatibility"""
        return self._detect_csrf_tokens({}, html_content)
    
    def _test_csrf_submission(self, action_url, method, form_data):
        """Test form submission without CSRF token"""
        try:
            if method == 'post':
                response = requests.post(
                    action_url,
                    data=form_data,
                    verify=False,
                    timeout=10,
                    allow_redirects=False
                )
            else:
                response = requests.get(
                    action_url,
                    params=form_data,
                    verify=False,
                    timeout=10,
                    allow_redirects=False
                )
            
            # Check if request was successful (not blocked by CSRF protection)
            if response.status_code in [200, 302, 303]:
                return {
                    'type': 'CSRF',
                    'form_action': action_url,
                    'method': method,
                    'vulnerable': True,
                    'status_code': response.status_code
                }
            else:
                return {'vulnerable': False}
        
        except requests.exceptions.RequestException:
            return {'vulnerable': False}

class DirectoryBruteForcer:
    """Directory and file brute forcing using FFUF"""
    
    def __init__(self):
        self.wordlist_manager = WordlistManager()
        self.ffuf_path = self._find_ffuf()
        self.gobuster_path = self._find_gobuster()
        self.wordlists = self._find_wordlists()
        self.results = []
    
    def _find_ffuf(self):
        """Find FFUF installation"""
        try:
            result = subprocess.run(['which', 'ffuf'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'ffuf'
        except:
            pass
        
        # Check common paths
        possible_paths = ['/usr/bin/ffuf', '/opt/ffuf/ffuf']
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _find_gobuster(self):
        """Find Gobuster installation"""
        try:
            result = subprocess.run(['which', 'gobuster'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'gobuster'
        except:
            pass
        
        return None
    
    def _find_wordlists(self):
        """Find available wordlists"""
        wordlist_paths = [
            '/usr/share/seclists/Discovery/Web-Content/common.txt',
            '/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt',
            '/usr/share/wordlists/dirb/common.txt',
            '/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt',
            '/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt',
            '/usr/share/seclists/Discovery/Web-Content/web-extensions.txt'
        ]
        
        available_wordlists = []
        for wordlist in wordlist_paths:
            if os.path.exists(wordlist):
                available_wordlists.append(wordlist)
        
        return available_wordlists
    
    def _get_wordlist(self):
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
        
        # Fallback to system wordlists
        if self.wordlists:
            print(f"{Colors.YELLOW}[!] Using system wordlist: {self.wordlists[0]}{Colors.END}")
            return self.wordlists[0]
        
        return None
    
    def brute_force_directories(self, url, wordlist=None, threads=50):
        """Brute force directories and files"""
        print(f"{Colors.YELLOW}[*] Starting directory brute force on {url}...{Colors.END}")
        
        if not wordlist and self.wordlists:
            wordlist = self.wordlists[0]  # Use first available wordlist
        
        if not wordlist:
            print(f"{Colors.RED}[-] No wordlist found{Colors.END}")
            return []
        
        # Prefer FFUF over Gobuster
        if self.ffuf_path:
            return self._ffuf_scan(url, wordlist, threads)
        elif self.gobuster_path:
            return self._gobuster_scan(url, wordlist, threads)
        else:
            print(f"{Colors.RED}[-] No directory brute forcing tools found{Colors.END}")
            return []
    
    def _ffuf_scan(self, url, wordlist, threads):
        """Run FFUF directory scan"""
        print(f"  {Colors.CYAN}[*] Using FFUF with wordlist: {os.path.basename(wordlist)}{Colors.END}")
        
        # Prepare FFUF command
        ffuf_cmd = [
            self.ffuf_path,
            '-u', f'{url}/FUZZ',
            '-w', wordlist,
            '-t', str(threads),
            '-timeout', '10',
            '-fc', '404',
            '-o', f'/tmp/ffuf_output_{int(time.time())}.json',
            '-of', 'json',
            '-s'  # Silent mode
        ]
        
        try:
            print(f"{Colors.PURPLE}[CMD] {' '.join(ffuf_cmd[:6])}...{Colors.END}")
            result = subprocess.run(
                ffuf_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return self._parse_ffuf_output(result.stderr)  # FFUF outputs results to stderr
            else:
                print(f"{Colors.RED}[-] FFUF failed: {result.stderr[:200]}{Colors.END}")
                return []
        
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[-] FFUF scan timed out{Colors.END}")
            return []
        except Exception as e:
            print(f"{Colors.RED}[-] FFUF error: {e}{Colors.END}")
            return []
    
    def _parse_ffuf_output(self, output):
        """Parse FFUF output"""
        results = []
        
        # FFUF outputs results line by line
        for line in output.split('\n'):
            if line.strip() and not line.startswith('::'):
                # Parse FFUF output format: URL [Status: XXX, Size: XXX, Words: XXX, Lines: XXX]
                if '[Status:' in line:
                    parts = line.split('[Status:')
                    if len(parts) == 2:
                        path = parts[0].strip()
                        status_info = parts[1]
                        
                        # Extract status code
                        status_match = re.search(r'(\d+)', status_info)
                        status_code = int(status_match.group(1)) if status_match else 0
                        
                        # Extract size
                        size_match = re.search(r'Size: (\d+)', status_info)
                        size = int(size_match.group(1)) if size_match else 0
                        
                        result = {
                            'path': path,
                            'status_code': status_code,
                            'size': size,
                            'tool': 'ffuf'
                        }
                        results.append(result)
                        
                        # Color code based on status
                        if status_code == 200:
                            color = Colors.GREEN
                        elif status_code in [301, 302]:
                            color = Colors.YELLOW
                        elif status_code == 403:
                            color = Colors.RED
                        else:
                            color = Colors.WHITE
                        
                        print(f"  {color}[{status_code}] {path} (Size: {size}){Colors.END}")
        
        return results
    
    def _gobuster_scan(self, url, wordlist, threads):
        """Run Gobuster directory scan"""
        print(f"  {Colors.CYAN}[*] Using Gobuster with wordlist: {os.path.basename(wordlist)}{Colors.END}")
        
        gobuster_cmd = [
            self.gobuster_path, 'dir',
            '-u', url,
            '-w', wordlist,
            '-t', str(threads),
            '--timeout', '10s',
            '-q'  # Quiet mode
        ]
        
        try:
            print(f"{Colors.PURPLE}[CMD] {' '.join(gobuster_cmd[:6])}...{Colors.END}")
            result = subprocess.run(
                gobuster_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return self._parse_gobuster_output(result.stdout, url)
            else:
                print(f"{Colors.RED}[-] Gobuster failed: {result.stderr[:200]}{Colors.END}")
                return []
        
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[-] Gobuster scan timed out{Colors.END}")
            return []
        except Exception as e:
            print(f"{Colors.RED}[-] Gobuster error: {e}{Colors.END}")
            return []
    
    def _parse_gobuster_output(self, output, base_url):
        """Parse Gobuster output"""
        results = []
        
        for line in output.split('\n'):
            if line.strip() and not line.startswith('='):
                # Gobuster format: /path (Status: XXX) [Size: XXX]
                match = re.match(r'(/\S+)\s+\(Status:\s+(\d+)\)\s+\[Size:\s+(\d+)\]', line)
                if match:
                    path = match.group(1)
                    status_code = int(match.group(2))
                    size = int(match.group(3))
                    
                    result = {
                        'path': f"{base_url}{path}",
                        'status_code': status_code,
                        'size': size,
                        'tool': 'gobuster'
                    }
                    results.append(result)
                    
                    # Color code based on status
                    if status_code == 200:
                        color = Colors.GREEN
                    elif status_code in [301, 302]:
                        color = Colors.YELLOW
                    elif status_code == 403:
                        color = Colors.RED
                    else:
                        color = Colors.WHITE
                    
                    print(f"  {color}[{status_code}] {path} (Size: {size}){Colors.END}")
        
        return results

class NucleiScanner:
    """Nuclei vulnerability scanner integration"""
    
    def __init__(self):
        self.nuclei_path = self._find_nuclei()
        self.templates_path = self._find_templates()
        self.results = []
    
    def _find_nuclei(self):
        """Find Nuclei installation"""
        try:
            result = subprocess.run(['which', 'nuclei'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'nuclei'
        except:
            pass
        
        # Check common paths
        possible_paths = ['/usr/bin/nuclei', '/opt/nuclei/nuclei']
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _find_templates(self):
        """Find Nuclei templates"""
        template_paths = [
            '~/nuclei-templates',
            '/usr/share/nuclei-templates',
            '/opt/nuclei-templates'
        ]
        
        for path in template_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path
        
        return None
    
    def scan_with_nuclei(self, url, severity=['critical', 'high', 'medium']):
        """Run Nuclei scan"""
        print(f"{Colors.YELLOW}[*] Running Nuclei scan on {url}...{Colors.END}")
        
        if not self.nuclei_path:
            print(f"{Colors.RED}[-] Nuclei not found. Install with: apt install nuclei{Colors.END}")
            return []
        
        # Build Nuclei command
        nuclei_cmd = [
            self.nuclei_path,
            '-u', url,
            '-severity', ','.join(severity),
            '-o', f'/tmp/nuclei_output_{int(time.time())}.json',
            '-json',
            '-silent'
        ]
        
        # Add templates path if available
        if self.templates_path:
            nuclei_cmd.extend(['-t', self.templates_path])
        
        try:
            print(f"{Colors.PURPLE}[CMD] {' '.join(nuclei_cmd[:6])}...{Colors.END}")
            result = subprocess.run(
                nuclei_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                return self._parse_nuclei_output(result.stdout)
            else:
                print(f"{Colors.RED}[-] Nuclei failed: {result.stderr[:200]}{Colors.END}")
                return []
        
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[-] Nuclei scan timed out{Colors.END}")
            return []
        except Exception as e:
            print(f"{Colors.RED}[-] Nuclei error: {e}{Colors.END}")
            return []
    
    def _parse_nuclei_output(self, output):
        """Parse Nuclei JSON output"""
        results = []
        
        for line in output.split('\n'):
            if line.strip():
                try:
                    vuln = json.loads(line)
                    
                    result = {
                        'template_id': vuln.get('template-id', 'unknown'),
                        'name': vuln.get('info', {}).get('name', 'Unknown'),
                        'severity': vuln.get('info', {}).get('severity', 'unknown'),
                        'description': vuln.get('info', {}).get('description', ''),
                        'url': vuln.get('matched-at', ''),
                        'type': vuln.get('type', 'unknown')
                    }
                    results.append(result)
                    
                    # Color code by severity
                    severity = result['severity'].lower()
                    if severity == 'critical':
                        color = Colors.RED
                    elif severity == 'high':
                        color = Colors.RED
                    elif severity == 'medium':
                        color = Colors.YELLOW
                    elif severity == 'low':
                        color = Colors.BLUE
                    else:
                        color = Colors.WHITE
                    
                    print(f"  {color}[{severity.upper()}] {result['name']} - {result['template_id']}{Colors.END}")
                
                except json.JSONDecodeError:
                    continue
        
        return results

class WebApplicationSecuritySuite:
    """Main web application security testing suite"""
    
    def __init__(self):
        # Component initialization with proper naming for test compatibility
        self.sqli_tester = SQLInjectionTester()
        self.xss_tester = XSSTester() 
        self.directory_tester = DirectoryTraversalTester()
        self.csrf_tester = CSRFTester()
        self.directory_bruteforcer = DirectoryBruteForcer()
        self.nuclei_scanner = NucleiScanner()
        
        # Legacy aliases for backward compatibility
        self.sql_tester = self.sqli_tester
        self.traversal_tester = self.directory_tester
        
        self.results = {}
        self.version = "2.0"
        
        # Create output directory
        self.output_dir = "output/web_security"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def print_banner(self):
        """Display framework banner"""
        banner = pyfiglet.figlet_format("WebAppSec", font="slant")
        print(f"{Colors.BLUE}{banner}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}WebAppSec v1.0 - Advanced Web Application Security Suite{Colors.END}")
        print(f"{Colors.GREEN}by Braintree - Comprehensive Web Vulnerability Testing{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}")
        print(f"{Colors.BLUE}SQL Injection | XSS | Directory Traversal | CSRF | Nuclei Scan{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}\n")
    
    def comprehensive_web_scan(self, url):
        """Run comprehensive web security scan"""
        print(f"{Colors.BOLD}{Colors.BLUE}COMPREHENSIVE WEB SECURITY SCAN{Colors.END}")
        print(f"{Colors.WHITE}Target: {url}{Colors.END}\n")
        
        results = {}
        
        # Phase 1: Information Gathering
        print(f"{Colors.BOLD}Phase 1: Information Gathering{Colors.END}")
        info_results = self._gather_web_info(url)
        results['information_gathering'] = info_results
        
        # Phase 2: Directory Brute Forcing
        print(f"\n{Colors.BOLD}Phase 2: Directory and File Discovery{Colors.END}")
        directory_results = self.directory_bruteforcer.brute_force_directories(url)
        results['directory_bruteforce'] = directory_results
        
        # Phase 3: SQL Injection Testing
        print(f"\n{Colors.BOLD}Phase 3: SQL Injection Testing{Colors.END}")
        
        # Extract parameters from URL for testing
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        test_params = {k: v[0] if v else 'test' for k, v in query_params.items()}
        
        if not test_params:
            test_params = {'id': '1', 'search': 'test'}  # Default test parameters
        
        # Test with SQLMap
        sqlmap_results = self.sql_tester.test_url_with_sqlmap(url)
        if sqlmap_results:
            results['sql_injection_sqlmap'] = sqlmap_results
        
        # Manual SQL injection testing
        manual_sql_results = self.sql_tester.manual_sql_injection_test(url, test_params)
        results['sql_injection_manual'] = manual_sql_results
        
        # Phase 4: XSS Testing
        print(f"\n{Colors.BOLD}Phase 4: Cross-Site Scripting (XSS) Testing{Colors.END}")
        
        # Reflected XSS
        reflected_xss = self.xss_tester.test_reflected_xss(url, test_params)
        results['xss_reflected'] = reflected_xss
        
        # DOM XSS
        dom_xss = self.xss_tester.test_dom_xss(url)
        results['xss_dom'] = dom_xss
        
        # Phase 5: Directory Traversal Testing
        print(f"\n{Colors.BOLD}Phase 5: Directory Traversal Testing{Colors.END}")
        traversal_results = self.traversal_tester.test_directory_traversal(url, test_params)
        results['directory_traversal'] = traversal_results
        
        # Phase 6: CSRF Testing
        print(f"\n{Colors.BOLD}Phase 6: CSRF Protection Testing{Colors.END}")
        csrf_results = self.csrf_tester.test_csrf_protection(url)
        results['csrf'] = csrf_results
        
        # Phase 7: Nuclei Vulnerability Scan
        print(f"\n{Colors.BOLD}Phase 7: Nuclei Vulnerability Scan{Colors.END}")
        nuclei_results = self.nuclei_scanner.scan_with_nuclei(url)
        results['nuclei'] = nuclei_results
        
        # Store results
        self.results = results
        
        # Generate report
        print(f"\n{Colors.BOLD}Phase 8: Generating Report{Colors.END}")
        report_file = self._generate_report(url, results)
        
        # Display summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}WEB SECURITY SCAN COMPLETED{Colors.END}")
        print(f"Target: {url}")
        print(f"Directories Found: {len(directory_results)}")
        print(f"SQL Injection Vulnerabilities: {len(manual_sql_results)}")
        print(f"XSS Vulnerabilities: {len(reflected_xss) + len(dom_xss)}")
        print(f"Directory Traversal: {len(traversal_results)}")
        print(f"CSRF Issues: {len(csrf_results)}")
        print(f"Nuclei Findings: {len(nuclei_results)}")
        print(f"Report: {report_file}")
        
        return results
    
    def _gather_web_info(self, url):
        """Gather basic web application information"""
        print(f"{Colors.CYAN}[*] Gathering web application information...{Colors.END}")
        
        info = {}
        
        try:
            response = requests.get(url, verify=False, timeout=10)
            
            info['status_code'] = response.status_code
            info['headers'] = dict(response.headers)
            info['server'] = response.headers.get('Server', 'Unknown')
            info['powered_by'] = response.headers.get('X-Powered-By', 'Unknown')
            info['content_type'] = response.headers.get('Content-Type', 'Unknown')
            info['content_length'] = len(response.text)
            
            # Extract title
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            info['title'] = title_tag.text.strip() if title_tag else 'No title'
            
            # Find forms
            forms = soup.find_all('form')
            info['forms_count'] = len(forms)
            info['forms'] = []
            
            for form in forms:
                form_info = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': []
                }
                
                for input_field in form.find_all('input'):
                    form_info['inputs'].append({
                        'name': input_field.get('name'),
                        'type': input_field.get('type', 'text')
                    })
                
                info['forms'].append(form_info)
            
            # Find links
            links = soup.find_all('a', href=True)
            info['links_count'] = len(links)
            
            # Find JavaScript files
            scripts = soup.find_all('script', src=True)
            info['scripts'] = [script['src'] for script in scripts]
            
            print(f"  {Colors.GREEN}[INFO] Server: {info['server']}{Colors.END}")
            print(f"  {Colors.GREEN}[INFO] Title: {info['title']}{Colors.END}")
            print(f"  {Colors.GREEN}[INFO] Forms found: {info['forms_count']}{Colors.END}")
            print(f"  {Colors.GREEN}[INFO] Links found: {info['links_count']}{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}[-] Information gathering failed: {e}{Colors.END}")
            info['error'] = str(e)
        
        return info
    
    def _generate_report(self, url, results):
        """Generate HTML security report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"{self.output_dir}/web_security_report_{timestamp}.html"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Security Scan Report</title>
    <style>
        body {{ font-family: 'Arial', sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 30px; margin-bottom: 30px; border-radius: 10px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .section {{ margin-bottom: 30px; padding: 20px; border-left: 5px solid #667eea; background-color: #f8f9fa; }}
        .vulnerability {{ background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin-bottom: 15px; border-radius: 5px; }}
        .critical {{ border-left-color: #dc3545; background-color: #f8d7da; }}
        .high {{ border-left-color: #fd7e14; background-color: #fff3cd; }}
        .medium {{ border-left-color: #ffc107; background-color: #fff3cd; }}
        .low {{ border-left-color: #28a745; background-color: #d1ecf1; }}
        .safe {{ border-left-color: #28a745; background-color: #d4edda; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .path {{ display: inline-block; background-color: #007bff; color: white; padding: 3px 8px; margin: 2px; border-radius: 3px; font-size: 0.8em; }}
        .status-200 {{ background-color: #28a745; }}
        .status-403 {{ background-color: #dc3545; }}
        .status-302 {{ background-color: #ffc107; color: #000; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WEB SECURITY SCAN REPORT</h1>
        <h2>WebAppSec v1.0 by Braintree - Advanced Web Application Security</h2>
        <p>Target: {url}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="container">
        <div class="section">
            <h2>Executive Summary</h2>
            <table>
                <tr><th>Test Category</th><th>Vulnerabilities Found</th><th>Status</th></tr>
                <tr><td>SQL Injection</td><td>{len(results.get('sql_injection_manual', []))}</td><td>{'VULNERABLE' if results.get('sql_injection_manual') else 'SAFE'}</td></tr>
                <tr><td>Cross-Site Scripting (XSS)</td><td>{len(results.get('xss_reflected', [])) + len(results.get('xss_dom', []))}</td><td>{'VULNERABLE' if (results.get('xss_reflected') or results.get('xss_dom')) else 'SAFE'}</td></tr>
                <tr><td>Directory Traversal</td><td>{len(results.get('directory_traversal', []))}</td><td>{'VULNERABLE' if results.get('directory_traversal') else 'SAFE'}</td></tr>
                <tr><td>CSRF Protection</td><td>{len(results.get('csrf', []))}</td><td>{'VULNERABLE' if results.get('csrf') else 'PROTECTED'}</td></tr>
                <tr><td>Nuclei Findings</td><td>{len(results.get('nuclei', []))}</td><td>{'ISSUES FOUND' if results.get('nuclei') else 'CLEAN'}</td></tr>
                <tr><td>Directory Discovery</td><td>{len(results.get('directory_bruteforce', []))}</td><td>{len(results.get('directory_bruteforce', []))} paths found</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Target Information</h2>
            {self._generate_info_section(results.get('information_gathering', {}))}
        </div>
        
        <div class="section">
            <h2>Directory Discovery</h2>
            {self._generate_directory_section(results.get('directory_bruteforce', []))}
        </div>
        
        <div class="section">
            <h2>SQL Injection Testing</h2>
            {self._generate_sql_section(results.get('sql_injection_manual', []))}
        </div>
        
        <div class="section">
            <h2>Cross-Site Scripting (XSS)</h2>
            {self._generate_xss_section(results.get('xss_reflected', []), results.get('xss_dom', []))}
        </div>
        
        <div class="section">
            <h2>Directory Traversal</h2>
            {self._generate_traversal_section(results.get('directory_traversal', []))}
        </div>
        
        <div class="section">
            <h2>CSRF Protection</h2>
            {self._generate_csrf_section(results.get('csrf', []))}
        </div>
        
        <div class="section">
            <h2>Nuclei Vulnerability Scan</h2>
            {self._generate_nuclei_section(results.get('nuclei', []))}
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <ul>
                <li><strong>Input Validation:</strong> Implement proper input validation and sanitization</li>
                <li><strong>Parameterized Queries:</strong> Use prepared statements to prevent SQL injection</li>
                <li><strong>Output Encoding:</strong> Properly encode all user input in output</li>
                <li><strong>CSRF Tokens:</strong> Implement CSRF protection on all state-changing operations</li>
                <li><strong>Security Headers:</strong> Configure appropriate security headers</li>
                <li><strong>File Access Controls:</strong> Restrict file system access and validate file paths</li>
                <li><strong>Regular Updates:</strong> Keep all software components up to date</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"{Colors.GREEN}[+] Report generated: {report_file}{Colors.END}")
            return report_file
        
        except Exception as e:
            print(f"{Colors.RED}[-] Failed to generate report: {e}{Colors.END}")
            return None
    
    def _generate_info_section(self, info):
        """Generate information section HTML"""
        if not info:
            return "<p>No information gathered.</p>"
        
        html = f"""
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Server</td><td>{info.get('server', 'Unknown')}</td></tr>
            <tr><td>Title</td><td>{info.get('title', 'No title')}</td></tr>
            <tr><td>Powered By</td><td>{info.get('powered_by', 'Unknown')}</td></tr>
            <tr><td>Content Type</td><td>{info.get('content_type', 'Unknown')}</td></tr>
            <tr><td>Forms Found</td><td>{info.get('forms_count', 0)}</td></tr>
            <tr><td>Links Found</td><td>{info.get('links_count', 0)}</td></tr>
        </table>
        """
        return html
    
    def _generate_directory_section(self, directories):
        """Generate directory discovery section HTML"""
        if not directories:
            return "<p>No directories discovered.</p>"
        
        html = "<table><tr><th>Path</th><th>Status Code</th><th>Size</th><th>Tool</th></tr>"
        for directory in directories:
            status_class = f"status-{directory.get('status_code', 0)}"
            html += f"""<tr>
                <td><span class="path {status_class}">{directory.get('path', '')}</span></td>
                <td>{directory.get('status_code', 'Unknown')}</td>
                <td>{directory.get('size', 0)} bytes</td>
                <td>{directory.get('tool', 'Unknown')}</td>
            </tr>"""
        html += "</table>"
        return html
    
    def _generate_sql_section(self, sql_results):
        """Generate SQL injection section HTML"""
        if not sql_results:
            return '<div class="safe">No SQL injection vulnerabilities found.</div>'
        
        html = ""
        for result in sql_results:
            html += f"""
            <div class="vulnerability high">
                <h4>SQL Injection - {result.get('payload_type', 'Unknown').title()}</h4>
                <p><strong>Parameter:</strong> {result.get('parameter', 'Unknown')}</p>
                <p><strong>Payload:</strong> <code>{result.get('payload', '')}</code></p>
                <p><strong>Status Code:</strong> {result.get('status_code', 'Unknown')}</p>
            </div>"""
        
        return html
    
    def _generate_xss_section(self, reflected_xss, dom_xss):
        """Generate XSS section HTML"""
        if not reflected_xss and not dom_xss:
            return '<div class="safe">No XSS vulnerabilities found.</div>'
        
        html = ""
        
        # Reflected XSS
        for result in reflected_xss:
            html += f"""
            <div class="vulnerability high">
                <h4>Reflected XSS</h4>
                <p><strong>Parameter:</strong> {result.get('parameter', 'Unknown')}</p>
                <p><strong>Payload:</strong> <code>{result.get('payload', '')}</code></p>
                <p><strong>URL:</strong> {result.get('url', '')}</p>
            </div>"""
        
        # DOM XSS
        for result in dom_xss:
            html += f"""
            <div class="vulnerability high">
                <h4>DOM-based XSS</h4>
                <p><strong>Payload:</strong> <code>{result.get('payload', '')}</code></p>
                <p><strong>URL:</strong> {result.get('url', '')}</p>
            </div>"""
        
        return html
    
    def _generate_traversal_section(self, traversal_results):
        """Generate directory traversal section HTML"""
        if not traversal_results:
            return '<div class="safe">No directory traversal vulnerabilities found.</div>'
        
        html = ""
        for result in traversal_results:
            html += f"""
            <div class="vulnerability high">
                <h4>Directory Traversal</h4>
                <p><strong>Parameter:</strong> {result.get('parameter', 'Unknown')}</p>
                <p><strong>Payload:</strong> <code>{result.get('payload', '')}</code></p>
                <p><strong>Type:</strong> {result.get('payload_type', 'Unknown')}</p>
                <p><strong>Response Snippet:</strong> <code>{result.get('response_snippet', '')[:100]}...</code></p>
            </div>"""
        
        return html
    
    def _generate_csrf_section(self, csrf_results):
        """Generate CSRF section HTML"""
        if not csrf_results:
            return '<div class="safe">CSRF protection appears to be in place.</div>'
        
        html = ""
        for result in csrf_results:
            html += f"""
            <div class="vulnerability medium">
                <h4>CSRF Vulnerability</h4>
                <p><strong>Form Action:</strong> {result.get('form_action', 'Unknown')}</p>
                <p><strong>Method:</strong> {result.get('method', 'Unknown').upper()}</p>
                <p><strong>Status Code:</strong> {result.get('status_code', 'Unknown')}</p>
                <p><strong>Description:</strong> Form submission successful without CSRF token</p>
            </div>"""
        
        return html
    
    def _generate_nuclei_section(self, nuclei_results):
        """Generate Nuclei section HTML"""
        if not nuclei_results:
            return '<div class="safe">No vulnerabilities found by Nuclei scan.</div>'
        
        html = ""
        for result in nuclei_results:
            severity = result.get('severity', 'unknown').lower()
            css_class = severity if severity in ['critical', 'high', 'medium', 'low'] else 'medium'
            
            html += f"""
            <div class="vulnerability {css_class}">
                <h4>{result.get('name', 'Unknown Vulnerability')} ({result.get('severity', 'Unknown').upper()})</h4>
                <p><strong>Template ID:</strong> {result.get('template_id', 'Unknown')}</p>
                <p><strong>Type:</strong> {result.get('type', 'Unknown')}</p>
                <p><strong>URL:</strong> {result.get('url', 'Unknown')}</p>
                <p><strong>Description:</strong> {result.get('description', 'No description available')}</p>
            </div>"""
        
        return html
    
    def safe_input(self, prompt, default=""):
        """Safe input handler with EOF protection"""
        try:
            return input(prompt).strip()
        except EOFError:
            print(f"\n{Colors.YELLOW}[!] End of input detected. Using default: '{default}'{Colors.END}")
            return default
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[!] Interrupted by user{Colors.END}")
            return "0"
    
    def validate_url(self, url):
        """Validate and normalize URL"""
        if not url:
            print(f"{Colors.RED}[-] No URL provided{Colors.END}")
            return None
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            print(f"{Colors.YELLOW}[!] Added http:// protocol: {url}{Colors.END}")
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not parsed.netloc:
                print(f"{Colors.RED}[-] Invalid URL format: {url}{Colors.END}")
                return None
            return url
        except Exception as e:
            print(f"{Colors.RED}[-] URL validation failed: {e}{Colors.END}")
            return None
    
    def get_target_info(self, url):
        """Get detailed information about the target"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}TARGET RECONNAISSANCE{Colors.END}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
        
        try:
            from urllib.parse import urlparse
            import socket
            import requests
            
            parsed = urlparse(url)
            hostname = parsed.netloc
            
            print(f"{Colors.WHITE}Target URL: {url}{Colors.END}")
            print(f"{Colors.WHITE}Hostname: {hostname}{Colors.END}")
            print(f"{Colors.WHITE}Protocol: {parsed.scheme}{Colors.END}")
            print(f"{Colors.WHITE}Path: {parsed.path or '/'}{Colors.END}")
            
            # Resolve IP
            try:
                ip = socket.gethostbyname(hostname)
                print(f"{Colors.GREEN}[+] IP Address: {ip}{Colors.END}")
            except socket.gaierror:
                print(f"{Colors.RED}[-] Could not resolve hostname{Colors.END}")
                return False
            
            # Test connectivity
            try:
                print(f"{Colors.YELLOW}[*] Testing connectivity...{Colors.END}")
                response = requests.get(url, timeout=10, verify=False)
                print(f"{Colors.GREEN}[+] Target is reachable{Colors.END}")
                print(f"{Colors.BLUE}[INFO] Status Code: {response.status_code}{Colors.END}")
                print(f"{Colors.BLUE}[INFO] Server: {response.headers.get('Server', 'Unknown')}{Colors.END}")
                print(f"{Colors.BLUE}[INFO] Content-Type: {response.headers.get('Content-Type', 'Unknown')}{Colors.END}")
                
                # Extract title if HTML
                if 'text/html' in response.headers.get('Content-Type', ''):
                    try:
                        import re
                        title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                        if title_match:
                            title = title_match.group(1).strip()
                            print(f"{Colors.BLUE}[INFO] Page Title: {title}{Colors.END}")
                    except:
                        pass
                        
                return True
            except requests.exceptions.RequestException as e:
                print(f"{Colors.RED}[-] Target not reachable: {e}{Colors.END}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}[-] Error getting target info: {e}{Colors.END}")
            return False
    
    def run(self):
        """Run the web application security suite interactively"""
        while True:
            try:
                print(f"\n{Colors.BOLD}{Colors.BLUE}WEB APPLICATION SECURITY - MAIN MENU{Colors.END}")
                print(f"{Colors.BLUE}{'-' * 70}{Colors.END}")
                print(f"{Colors.WHITE}[1] Comprehensive Web Security Scan{Colors.END}")
                print(f"{Colors.WHITE}[2] SQL Injection Testing Only{Colors.END}")
                print(f"{Colors.WHITE}[3] XSS Testing Only{Colors.END}")
                print(f"{Colors.WHITE}[4] Directory Brute Force Only{Colors.END}")
                print(f"{Colors.WHITE}[5] CSRF Testing Only{Colors.END}")
                print(f"{Colors.WHITE}[6] Directory Traversal Testing Only{Colors.END}")
                print(f"{Colors.WHITE}[7] Nuclei Vulnerability Scan Only{Colors.END}")
                print(f"{Colors.WHITE}[8] Custom Scan Configuration{Colors.END}")
                print(f"{Colors.WHITE}[0] Exit{Colors.END}")
                print(f"{Colors.BLUE}{'-' * 70}{Colors.END}")
                
                choice = self.safe_input(f"\n{Colors.WHITE}[WEBSEC-VULN] Select option: {Colors.END}", "0")
                
                if choice == '1':
                    url = self.safe_input(f"{Colors.WHITE}Enter target URL: {Colors.END}")
                    if url and self.validate_url(url):
                        if self.get_target_info(url):
                            print(f"\n{Colors.BOLD}{Colors.GREEN}Starting Comprehensive Web Security Scan{Colors.END}")
                            self.comprehensive_web_scan(url)
                
                elif choice == '2':
                    url = self.safe_input(f"{Colors.WHITE}Enter target URL for SQL Injection testing: {Colors.END}")
                    if url and self.validate_url(url):
                        if self.get_target_info(url):
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}SQL INJECTION TESTING MODULE{Colors.END}")
                            print(f"{Colors.YELLOW}{'=' * 50}{Colors.END}")
                            
                            # SQLMap test
                            print(f"\n{Colors.BOLD}Phase 1: SQLMap Automated Testing{Colors.END}")
                            sqlmap_result = self.sql_tester.test_url_with_sqlmap(url)
                            
                            # Manual testing
                            print(f"\n{Colors.BOLD}Phase 2: Manual SQL Injection Testing{Colors.END}")
                            test_params = {'id': '1', 'search': 'test', 'q': 'test', 'page': '1', 'cat': 'default'}
                            manual_results = self.sql_tester.manual_sql_injection_test(url, test_params)
                            
                            # Results summary
                            print(f"\n{Colors.BOLD}{Colors.CYAN}SQL INJECTION TESTING RESULTS{Colors.END}")
                            print(f"{Colors.CYAN}{'=' * 40}{Colors.END}")
                            
                            vulnerable = False
                            if sqlmap_result and sqlmap_result.get('vulnerable'):
                                print(f"{Colors.RED}[CRITICAL] SQLMap found vulnerabilities{Colors.END}")
                                vulnerable = True
                                if sqlmap_result.get('databases'):
                                    print(f"{Colors.RED}[+] Databases found: {', '.join(sqlmap_result['databases'])}{Colors.END}")
                                    
                            if manual_results:
                                print(f"{Colors.RED}[VULNERABLE] Manual testing found {len(manual_results)} potential issues{Colors.END}")
                                vulnerable = True
                                for result in manual_results[:3]:  # Show first 3 results
                                    print(f"{Colors.RED}  - {result.get('type', 'SQL Injection')}: {result.get('parameter', 'Unknown param')}{Colors.END}")
                                    
                            if not vulnerable:
                                print(f"{Colors.GREEN}[SAFE] No SQL injection vulnerabilities detected{Colors.END}")
                                print(f"{Colors.BLUE}[INFO] Target appears to be properly protected against SQL injection{Colors.END}")
                
                elif choice == '3':
                    url = self.safe_input(f"{Colors.WHITE}Enter target URL for XSS testing: {Colors.END}")
                    if url and self.validate_url(url):
                        if self.get_target_info(url):
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}XSS VULNERABILITY TESTING MODULE{Colors.END}")
                            print(f"{Colors.YELLOW}{'=' * 45}{Colors.END}")
                            
                            test_params = {'q': 'test', 'search': 'test', 'name': 'user', 'comment': 'hello'}
                            
                            print(f"\n{Colors.BOLD}Phase 1: Reflected XSS Testing{Colors.END}")
                            print(f"{Colors.CYAN}[*] Testing common injection points...{Colors.END}")
                            reflected_results = self.xss_tester.test_reflected_xss(url, test_params)
                            
                            print(f"\n{Colors.BOLD}Phase 2: DOM-based XSS Testing{Colors.END}")
                            print(f"{Colors.CYAN}[*] Analyzing client-side JavaScript...{Colors.END}")
                            dom_results = self.xss_tester.test_dom_xss(url)
                            
                            # Results summary
                            print(f"\n{Colors.BOLD}{Colors.CYAN}XSS TESTING RESULTS{Colors.END}")
                            print(f"{Colors.CYAN}{'=' * 30}{Colors.END}")
                            
                            total_xss = len(reflected_results) + len(dom_results)
                            if total_xss > 0:
                                print(f"{Colors.RED}[VULNERABLE] Found {total_xss} XSS vulnerabilities{Colors.END}")
                                if reflected_results:
                                    print(f"{Colors.RED}[+] Reflected XSS: {len(reflected_results)} issues{Colors.END}")
                                    for result in reflected_results[:2]:  # Show first 2
                                        print(f"{Colors.RED}  - Parameter: {result.get('parameter', 'Unknown')}{Colors.END}")
                                if dom_results:
                                    print(f"{Colors.RED}[+] DOM XSS: {len(dom_results)} issues{Colors.END}")
                            else:
                                print(f"{Colors.GREEN}[SAFE] No XSS vulnerabilities detected{Colors.END}")
                                print(f"{Colors.BLUE}[INFO] Target appears to properly filter user input{Colors.END}")
                
                elif choice == '4':
                    url = self.safe_input(f"{Colors.WHITE}Enter target URL for directory brute force: {Colors.END}")
                    if url and self.validate_url(url):
                        if self.get_target_info(url):
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}DIRECTORY BRUTE FORCE MODULE{Colors.END}")
                            print(f"{Colors.YELLOW}{'=' * 40}{Colors.END}")
                            print(f"{Colors.CYAN}[*] Starting directory enumeration...{Colors.END}")
                            
                            results = self.directory_bruteforcer.brute_force_directories(url)
                            
                            print(f"\n{Colors.BOLD}{Colors.CYAN}DIRECTORY ENUMERATION RESULTS{Colors.END}")
                            print(f"{Colors.CYAN}{'=' * 35}{Colors.END}")
                            
                            if results:
                                print(f"{Colors.GREEN}[+] Directory brute force completed. Found {len(results)} accessible paths{Colors.END}")
                                print(f"{Colors.BLUE}[INFO] Discovered directories and files:{Colors.END}")
                                # Handle both list and dict formats
                                if isinstance(results, list):
                                    for result in results[:10]:  # Show first 10
                                        if isinstance(result, dict):
                                            path = result.get('path', 'Unknown')
                                            status = result.get('status_code', 'Unknown')
                                            print(f"{Colors.GREEN}  - {path} (Status: {status}){Colors.END}")
                                        else:
                                            print(f"{Colors.GREEN}  - {result}{Colors.END}")
                                elif isinstance(results, dict):
                                    for path, status in list(results.items())[:10]:  # Show first 10
                                        print(f"{Colors.GREEN}  - {path} (Status: {status}){Colors.END}")
                                if len(results) > 10:
                                    print(f"{Colors.CYAN}  ... and {len(results) - 10} more{Colors.END}")
                            else:
                                print(f"{Colors.YELLOW}[!] No accessible directories found with common wordlist{Colors.END}")
                                print(f"{Colors.BLUE}[INFO] Target may have restrictive directory permissions{Colors.END}")
                
                elif choice == '5':
                    url = self.safe_input(f"{Colors.WHITE}Enter target URL for CSRF testing: {Colors.END}")
                    if url and self.validate_url(url):
                        if self.get_target_info(url):
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}CSRF PROTECTION TESTING MODULE{Colors.END}")
                            print(f"{Colors.YELLOW}{'=' * 40}{Colors.END}")
                            print(f"{Colors.CYAN}[*] Analyzing CSRF protection mechanisms...{Colors.END}")
                            
                            results = self.csrf_tester.test_csrf_protection(url)
                            
                            print(f"\n{Colors.BOLD}{Colors.CYAN}CSRF TESTING RESULTS{Colors.END}")
                            print(f"{Colors.CYAN}{'=' * 25}{Colors.END}")
                            
                            if results:
                                print(f"{Colors.RED}[VULNERABLE] Found {len(results)} CSRF protection issues{Colors.END}")
                                for result in results[:3]:  # Show first 3 results
                                    form_action = result.get('form_action', 'Unknown')
                                    method = result.get('method', 'Unknown')
                                    print(f"{Colors.RED}  - Form: {form_action} (Method: {method}){Colors.END}")
                            else:
                                print(f"{Colors.GREEN}[PROTECTED] CSRF protection appears adequate{Colors.END}")
                                print(f"{Colors.BLUE}[INFO] Target implements proper CSRF tokens{Colors.END}")
                
                elif choice == '6':
                    url = self.safe_input(f"{Colors.WHITE}Enter target URL for directory traversal testing: {Colors.END}")
                    if url and self.validate_url(url):
                        if self.get_target_info(url):
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}DIRECTORY TRAVERSAL TESTING MODULE{Colors.END}")
                            print(f"{Colors.YELLOW}{'=' * 45}{Colors.END}")
                            print(f"{Colors.CYAN}[*] Testing path traversal vulnerabilities...{Colors.END}")
                            
                            test_params = {'file': 'index.html', 'path': 'home', 'page': 'main', 'doc': 'readme.txt'}
                            results = self.traversal_tester.test_directory_traversal(url, test_params)
                            
                            print(f"\n{Colors.BOLD}{Colors.CYAN}DIRECTORY TRAVERSAL RESULTS{Colors.END}")
                            print(f"{Colors.CYAN}{'=' * 35}{Colors.END}")
                            
                            if results:
                                print(f"{Colors.RED}[VULNERABLE] Found {len(results)} directory traversal issues{Colors.END}")
                                for result in results[:3]:  # Show first 3
                                    param = result.get('parameter', 'Unknown')
                                    payload_type = result.get('payload_type', 'Unknown')
                                    print(f"{Colors.RED}  - Parameter: {param} (Type: {payload_type}){Colors.END}")
                            else:
                                print(f"{Colors.GREEN}[SAFE] No directory traversal vulnerabilities found{Colors.END}")
                                print(f"{Colors.BLUE}[INFO] Target properly validates file paths{Colors.END}")
                
                elif choice == '7':
                    url = self.safe_input(f"{Colors.WHITE}Enter target URL for Nuclei vulnerability scan: {Colors.END}")
                    if url and self.validate_url(url):
                        if self.get_target_info(url):
                            print(f"\n{Colors.BOLD}{Colors.YELLOW}NUCLEI VULNERABILITY SCANNER{Colors.END}")
                            print(f"{Colors.YELLOW}{'=' * 35}{Colors.END}")
                            print(f"{Colors.CYAN}[*] Running comprehensive vulnerability scan...{Colors.END}")
                            print(f"{Colors.CYAN}[*] This may take several minutes depending on target{Colors.END}")
                            
                            results = self.nuclei_scanner.scan_with_nuclei(url)
                            
                            print(f"\n{Colors.BOLD}{Colors.CYAN}NUCLEI SCAN RESULTS{Colors.END}")
                            print(f"{Colors.CYAN}{'=' * 25}{Colors.END}")
                            
                            if results:
                                print(f"{Colors.YELLOW}[FINDINGS] Nuclei found {len(results)} potential issues{Colors.END}")
                                
                                # Categorize by severity
                                critical = [r for r in results if r.get('severity', '').lower() == 'critical']
                                high = [r for r in results if r.get('severity', '').lower() == 'high']
                                medium = [r for r in results if r.get('severity', '').lower() == 'medium']
                                low = [r for r in results if r.get('severity', '').lower() == 'low']
                                
                                if critical:
                                    print(f"{Colors.RED}[CRITICAL] {len(critical)} critical severity issues{Colors.END}")
                                if high:
                                    print(f"{Colors.RED}[HIGH] {len(high)} high severity issues{Colors.END}")
                                if medium:
                                    print(f"{Colors.YELLOW}[MEDIUM] {len(medium)} medium severity issues{Colors.END}")
                                if low:
                                    print(f"{Colors.BLUE}[LOW] {len(low)} low severity issues{Colors.END}")
                                    
                                # Show top findings
                                print(f"\n{Colors.CYAN}[INFO] Top findings:{Colors.END}")
                                for result in results[:5]:  # Show first 5
                                    severity = result.get('severity', 'Unknown').upper()
                                    name = result.get('name', 'Unknown')
                                    template_id = result.get('template_id', 'Unknown')
                                    print(f"{Colors.WHITE}  - [{severity}] {name} ({template_id}){Colors.END}")
                            else:
                                print(f"{Colors.GREEN}[CLEAN] No vulnerabilities found by Nuclei{Colors.END}")
                                print(f"{Colors.BLUE}[INFO] Target appears to be well-secured{Colors.END}")
                
                elif choice == '8':
                    print(f"\n{Colors.BOLD}{Colors.YELLOW}CUSTOM SCAN CONFIGURATION{Colors.END}")
                    print(f"{Colors.YELLOW}{'=' * 35}{Colors.END}")
                    print(f"{Colors.CYAN}[*] Custom scan configuration allows you to:{Colors.END}")
                    print(f"  {Colors.WHITE}- Select specific vulnerability tests{Colors.END}")
                    print(f"  {Colors.WHITE}- Configure scan parameters{Colors.END}")
                    print(f"  {Colors.WHITE}- Set custom payloads{Colors.END}")
                    print(f"  {Colors.WHITE}- Export results in different formats{Colors.END}")
                    print(f"{Colors.BLUE}[INFO] This feature will be available in future updates{Colors.END}")
                
                elif choice == '0' or choice.lower() == 'exit' or choice == "":
                    print(f"\n{Colors.GREEN}[*] Returning to main menu...{Colors.END}")
                    break
                
                else:
                    if choice:
                        print(f"{Colors.RED}[-] Invalid choice '{choice}'. Please try again.{Colors.END}")
                
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    self.safe_input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[*] Returning to main menu...{Colors.END}")
                break
            except EOFError:
                print(f"\n{Colors.YELLOW}[*] EOF detected, returning to main menu...{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.END}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="WebAppSec v1.0 - Advanced Web Application Security Suite by Braintree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 web_application_security.py                           # Interactive mode
  python3 web_application_security.py -u https://example.com   # Full scan
        """
    )
    
    parser.add_argument('-u', '--url', help='Target URL')
    parser.add_argument('--sql-only', action='store_true', help='SQL injection testing only')
    parser.add_argument('--xss-only', action='store_true', help='XSS testing only')
    parser.add_argument('--directory-only', action='store_true', help='Directory brute force only')
    parser.add_argument('--nuclei-only', action='store_true', help='Nuclei scan only')
    
    args = parser.parse_args()
    
    # Create suite instance
    suite = WebApplicationSecuritySuite()
    suite.print_banner()
    
    if args.url:
        url = args.url
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        if args.sql_only:
            print(f"{Colors.BOLD}SQL Injection Testing Only{Colors.END}")
            sqlmap_result = suite.sql_tester.test_url_with_sqlmap(url)
            test_params = {'id': '1', 'search': 'test'}
            manual_results = suite.sql_tester.manual_sql_injection_test(url, test_params)
            
        elif args.xss_only:
            print(f"{Colors.BOLD}XSS Testing Only{Colors.END}")
            test_params = {'q': 'test', 'search': 'test'}
            reflected_results = suite.xss_tester.test_reflected_xss(url, test_params)
            dom_results = suite.xss_tester.test_dom_xss(url)
            
        elif args.directory_only:
            print(f"{Colors.BOLD}Directory Brute Force Only{Colors.END}")
            results = suite.directory_bruteforcer.brute_force_directories(url)
            
        elif args.nuclei_only:
            print(f"{Colors.BOLD}Nuclei Scan Only{Colors.END}")
            results = suite.nuclei_scanner.scan_with_nuclei(url)
            
        else:
            # Full comprehensive scan
            results = suite.comprehensive_web_scan(url)
    else:
        # Interactive mode
        suite.run()

if __name__ == "__main__":
    main()