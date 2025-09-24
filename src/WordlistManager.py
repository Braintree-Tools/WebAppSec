#!/usr/bin/env python3

"""
BRAINTREE WebSec Toolkit - Wordlist Manager
Comprehensive management and access to security wordlists
Handles passwords, usernames, directories, subdomains, and fuzzing payloads
"""

import os
import random
import requests
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
import urllib.parse
import gzip

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

class WordlistManager:
    """Comprehensive wordlist management for security testing"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.wordlists_dir = self.base_dir / "wordlists"
        self.ensure_wordlist_structure()
        
        # Complete wordlist registry with all 147 discovered files
        self.WORDLISTS = {
            "passwords": {
                "xato_net_10_million_passwords_10000": {
                    "path": "passwords/xato-net-10-million-passwords-10000.txt",
                    "description": "Top 10,000 passwords from 10M password dataset"
                },
                "rockyou": {
                    "path": "passwords/rockyou.txt", 
                    "description": "RockYou password database leak"
                },
                "common_passwords": {
                    "path": "passwords/common_passwords.txt",
                    "description": "Common passwords compilation"
                },
                "top_1000_passwords": {
                    "path": "passwords/top_1000_passwords.txt",
                    "description": "Top 1000 most common passwords"
                },
                "numeric_passwords": {
                    "path": "passwords/numeric_passwords.txt",
                    "description": "Numeric password patterns"
                },
                "default_passwords": {
                    "path": "passwords/default-passwords.txt",
                    "description": "Default device and service passwords"
                },
                "oracle_ebs_passwordlist": {
                    "path": "passwords/Oracle EBS passwordlist.txt",
                    "description": "Oracle EBS default passwords"
                },
                "oracle_ebs_userlist": {
                    "path": "passwords/Oracle EBS userlist.txt",
                    "description": "Oracle EBS default usernames"
                },
                "mysql_betterdefaultpasslist": {
                    "path": "passwords/mysql-betterdefaultpasslist.txt",
                    "description": "MySQL default passwords"
                },
                "mssql_betterdefaultpasslist": {
                    "path": "passwords/mssql-betterdefaultpasslist.txt",
                    "description": "MSSQL default passwords"
                },
                "oracle_betterdefaultpasslist": {
                    "path": "passwords/oracle-betterdefaultpasslist.txt",
                    "description": "Oracle default passwords"
                },
                "postgres_betterdefaultpasslist": {
                    "path": "passwords/postgres-betterdefaultpasslist.txt",
                    "description": "PostgreSQL default passwords"
                },
                "db2_betterdefaultpasslist": {
                    "path": "passwords/db2-betterdefaultpasslist.txt",
                    "description": "DB2 default passwords"
                },
                "ssh_betterdefaultpasslist": {
                    "path": "passwords/ssh-betterdefaultpasslist.txt",
                    "description": "SSH default passwords"
                },
                "telnet_betterdefaultpasslist": {
                    "path": "passwords/telnet-betterdefaultpasslist.txt",
                    "description": "Telnet default passwords"
                },
                "windows_betterdefaultpasslist": {
                    "path": "passwords/windows-betterdefaultpasslist.txt",
                    "description": "Windows default passwords"
                },
                "vnc_betterdefaultpasslist": {
                    "path": "passwords/vnc-betterdefaultpasslist.txt",
                    "description": "VNC default passwords"
                },
                "tomcat_betterdefaultpasslist": {
                    "path": "passwords/tomcat-betterdefaultpasslist.txt",
                    "description": "Tomcat default passwords"
                },
                "tomcat_betterdefaultpasslist_base64encoded": {
                    "path": "passwords/tomcat-betterdefaultpasslist_base64encoded.txt",
                    "description": "Tomcat base64 encoded default passwords"
                },
                "avaya_defaultpasslist": {
                    "path": "passwords/avaya_defaultpasslist.txt",
                    "description": "Avaya default passwords"
                },
                "citrix": {
                    "path": "passwords/citrix.txt",
                    "description": "Citrix passwords"
                },
                "cirt_net_collection": {
                    "path": "passwords/cirt-net_collection.txt",
                    "description": "CIRT.net password collection"
                },
                "cryptominers": {
                    "path": "passwords/cryptominers.txt",
                    "description": "Cryptominer related passwords"
                },
                "integration_test": {
                    "path": "passwords/integration_test.txt",
                    "description": "Integration test passwords"
                },
                "telnet_phenoelit": {
                    "path": "passwords/telnet-phenoelit.txt",
                    "description": "Telnet phenoelit password list"
                },
                "perf_test_large": {
                    "path": "passwords/perf_test_large.txt",
                    "description": "Large performance test password list"
                }
            },
            "usernames": {
                "xato_net_10_million_usernames": {
                    "path": "users/xato-net-10-million-usernames.txt",
                    "description": "10 million usernames from data breaches"
                },
                "names": {
                    "path": "users/names.txt",
                    "description": "Common first names"
                },
                "common_usernames": {
                    "path": "usernames/common-usernames.txt",
                    "description": "Common username patterns"
                },
                "forenames_india_top1000": {
                    "path": "usernames/forenames-india-top1000.txt",
                    "description": "Top 1000 Indian forenames"
                }
            },
            "directories": {
                "dirbuster_2007_directory_list_2_3_small": {
                    "path": "directories/DirBuster-2007_directory-list-2.3-small.txt",
                    "description": "DirBuster directory list (small)"
                },
                "dirbuster_2007_directory_list_2_3_medium": {
                    "path": "directories/DirBuster-2007_directory-list-2.3-medium.txt",
                    "description": "DirBuster directory list (medium)"
                },
                "combined_directories": {
                    "path": "directories/combined_directories.txt",
                    "description": "Combined directory wordlist"
                }
            },
            "subdomains": {
                "dns_jhaddix": {
                    "path": "subdomains/dns-Jhaddix.txt",
                    "description": "Jhaddix subdomain wordlist"
                },
                "combined_subdomains": {
                    "path": "subdomains/combined_subdomains.txt",
                    "description": "Combined subdomain wordlist"
                },
                "deepmagic_com_prefixes_top50000": {
                    "path": "subdomains/deepmagic.com-prefixes-top50000.txt",
                    "description": "Top 50,000 subdomain prefixes"
                }
            },
            "fuzzing": {
                "xss_without_parentheses_semi_colons_portswigger": {
                    "path": "fuzzing/XSS/robot-friendly/xss-without-parentheses-semi-colons-portswigger.txt",
                    "description": "XSS payloads without parentheses and semicolons"
                },
                "xss_ende_xssattacks": {
                    "path": "fuzzing/XSS/robot-friendly/XSS-EnDe-xssAttacks.txt",
                    "description": "XSS EnDe attack vectors"
                },
                "xss_ende_h4k": {
                    "path": "fuzzing/XSS/robot-friendly/XSS-EnDe-h4k.txt",
                    "description": "XSS EnDe h4k payloads"
                },
                "xss_jhaddix": {
                    "path": "fuzzing/XSS/human-friendly/XSS-Jhaddix.txt",
                    "description": "Jhaddix XSS payload collection"
                },
                "xss_ofjaaah": {
                    "path": "fuzzing/XSS/human-friendly/XSS-OFJAAAH.txt",
                    "description": "OFJAAAH XSS payloads"
                },
                "xss_rsnake": {
                    "path": "fuzzing/XSS/robot-friendly/XSS-RSNAKE.txt",
                    "description": "RSnake XSS cheat sheet payloads"
                },
                "xss_vectors_mario": {
                    "path": "fuzzing/XSS/human-friendly/XSS-Vectors-Mario.txt",
                    "description": "Mario XSS vector collection"
                },
                "xss_polyglots": {
                    "path": "fuzzing/XSS/Polyglots/XSS-Polyglots.txt",
                    "description": "XSS polyglot payloads"
                },
                "xss_polyglots_dmiessler": {
                    "path": "fuzzing/XSS/Polyglots/XSS-Polyglots-Dmiessler.txt",
                    "description": "Dmiessler XSS polyglots"
                },
                "xss_polyglot_ultimate_0xsobky": {
                    "path": "fuzzing/XSS/Polyglots/XSS-Polyglot-Ultimate-0xsobky.txt",
                    "description": "Ultimate XSS polyglot by 0xsobky"
                },
                "xss_innerht_ml": {
                    "path": "fuzzing/XSS/Polyglots/XSS-innerht-ml.txt",
                    "description": "innerHTML XSS payloads"
                },
                "xss_payloadbox": {
                    "path": "fuzzing/XSS/human-friendly/XSS-payloadbox.txt",
                    "description": "PayloadBox XSS collection"
                },
                "xss_with_context_jhaddix": {
                    "path": "fuzzing/XSS/human-friendly/XSS-With-Context-Jhaddix.txt",
                    "description": "Context-aware XSS payloads"
                },
                "xss_ende_evation": {
                    "path": "fuzzing/XSS/human-friendly/XSS-EnDe-evation.txt",
                    "description": "XSS evasion techniques"
                },
                "xss_fuzzing": {
                    "path": "fuzzing/XSS/robot-friendly/XSS-Fuzzing.txt",
                    "description": "XSS fuzzing payloads"
                },
                "xss_somdev": {
                    "path": "fuzzing/XSS/robot-friendly/XSS-Somdev.txt",
                    "description": "Somdev XSS payloads"
                },
                "xss_ende_mario": {
                    "path": "fuzzing/XSS/robot-friendly/XSS-EnDe-mario.txt",
                    "description": "XSS EnDe Mario collection"
                },
                "sqli_polyglots": {
                    "path": "fuzzing/Databases/SQLi/SQLi-Polyglots.txt",
                    "description": "SQL injection polyglot payloads"
                },
                "nosql": {
                    "path": "fuzzing/Databases/SQLi/NoSQL.txt",
                    "description": "NoSQL injection payloads"
                },
                "mssql_enumeration_extended": {
                    "path": "fuzzing/Databases/SQLi/MSSQL-Enumeration-Extended.txt",
                    "description": "Extended MSSQL enumeration payloads"
                },
                "mysql_read_files": {
                    "path": "fuzzing/Databases/SQLi/MySQL-Read-Files.txt",
                    "description": "MySQL file reading payloads"
                },
                "mysql_sqli_login_bypass": {
                    "path": "fuzzing/Databases/SQLi/MySQL-SQLi-Login-Bypass.txt",
                    "description": "MySQL login bypass payloads"
                },
                "lfi_lfisuite_pathtotest_huge": {
                    "path": "fuzzing/LFI/LFI-LFISuite-pathtotest-huge.txt",
                    "description": "Large LFI path testing wordlist"
                },
                "lfi_gracefulsecurity_linux": {
                    "path": "fuzzing/LFI/LFI-gracefulsecurity-linux.txt",
                    "description": "Linux LFI payloads"
                },
                "lfi_lfisuite_pathtotest": {
                    "path": "fuzzing/LFI/LFI-LFISuite-pathtotest.txt",
                    "description": "LFI path testing wordlist"
                },
                "lfi_etc_files_of_all_linux_packages": {
                    "path": "fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt",
                    "description": "Linux package configuration files"
                },
                "lfi_windows_adeadfed": {
                    "path": "fuzzing/LFI/LFI-Windows-adeadfed.txt",
                    "description": "Windows LFI payloads by adeadfed"
                },
                "lfi_gracefulsecurity_windows": {
                    "path": "fuzzing/LFI/LFI-gracefulsecurity-windows.txt",
                    "description": "Windows LFI payloads"
                },
                "lfi_linux_and_windows_by_1n3_crowdshield": {
                    "path": "fuzzing/LFI/LFI-linux-and-windows_by-1N3@CrowdShield.txt",
                    "description": "Cross-platform LFI payloads"
                },
                "omi_agent_linux": {
                    "path": "fuzzing/LFI/OMI-Agent-Linux.txt",
                    "description": "OMI Agent Linux file paths"
                },
                "objects": {
                    "path": "fuzzing/objects.txt",
                    "description": "Object enumeration wordlist"
                },
                "objects_lowercase": {
                    "path": "fuzzing/objects-lowercase.txt",
                    "description": "Lowercase object names"
                },
                "objects_uppercase": {
                    "path": "fuzzing/objects-uppercase.txt",
                    "description": "Uppercase object names"
                },
                "actions": {
                    "path": "fuzzing/actions.txt",
                    "description": "Action enumeration wordlist"
                },
                "actions_uppercase": {
                    "path": "fuzzing/actions-uppercase.txt",
                    "description": "Uppercase action names"
                },
                "api_endpoints": {
                    "path": "fuzzing/api-endpoints.txt",
                    "description": "API endpoint wordlist"
                },
                "api_endpoints_res": {
                    "path": "fuzzing/api-endpoints-res.txt",
                    "description": "API resource endpoints"
                },
                "api_seen_in_wild": {
                    "path": "fuzzing/api-seen-in-wild.txt",
                    "description": "API endpoints seen in the wild"
                },
                "burp_parameter_names": {
                    "path": "fuzzing/burp-parameter-names.txt",
                    "description": "Burp Suite parameter names"
                },
                "command_injection_commix": {
                    "path": "fuzzing/command-injection-commix.txt",
                    "description": "Command injection payloads for Commix"
                },
                "template_engines_expression": {
                    "path": "fuzzing/template-engines-expression.txt",
                    "description": "Template engine expression payloads"
                },
                "big_list_of_naughty_strings": {
                    "path": "fuzzing/big-list-of-naughty-strings.txt",
                    "description": "Big list of naughty strings for testing"
                },
                "salesforce_aura_objects": {
                    "path": "fuzzing/salesforce-aura-objects.txt",
                    "description": "Salesforce Aura framework objects"
                },
                "windows_attacks_fuzzdb": {
                    "path": "fuzzing/Windows-Attacks.fuzzdb.txt",
                    "description": "Windows attack payloads from FuzzDB"
                },
                "unixattacks_fuzzdb": {
                    "path": "fuzzing/UnixAttacks.fuzzdb.txt",
                    "description": "Unix attack payloads from FuzzDB"
                }
            },
            "payloads": {
                "hello_00world": {
                    "path": "payloads/file-names/null-byte/Hello%00World.txt",
                    "description": "Null byte injection test file"
                },
                "hello_hostname_world": {
                    "path": "payloads/file-names/exec/Hello`hostname`World.txt",
                    "description": "Command injection test file"
                },
                "eicar_com": {
                    "path": "payloads/eicar-com.txt",
                    "description": "EICAR test file for antivirus testing"
                }
            }
        }
        
        # Built-in wordlist generators for missing files
        self.generators = {
            'common_passwords': self._generate_common_passwords,
            'common_usernames': self._generate_common_usernames,
            'directory_names': self._generate_directory_names,
            'subdomain_names': self._generate_subdomain_names,
            'parameter_names': self._generate_parameter_names
        }
    
    def ensure_wordlist_structure(self):
        """Ensure wordlist directory structure exists"""
        categories = ["passwords", "usernames", "directories", "subdomains", "fuzzing", "payloads"]
        
        for category in categories:
            category_dir = self.wordlists_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
    
    def get_wordlist(self, category: str, name: str) -> Optional[Path]:
        """Get path to a specific wordlist"""
        if category not in self.WORDLISTS:
            print(f"{Colors.RED}[-] Unknown category: {category}{Colors.END}")
            return None
            
        if name not in self.WORDLISTS[category]:
            print(f"{Colors.RED}[-] Unknown wordlist: {name} in category {category}{Colors.END}")
            return None
        
        wordlist_info = self.WORDLISTS[category][name]
        wordlist_path = self.wordlists_dir / wordlist_info["path"]
        
        # Create the file if it doesn't exist using generators
        if not wordlist_path.exists():
            if name in self.generators:
                self.generators[name](wordlist_path)
            else:
                # Create a basic file with description
                wordlist_path.parent.mkdir(parents=True, exist_ok=True)
                with open(wordlist_path, 'w') as f:
                    f.write(f"# {wordlist_info['description']}\n")
                    f.write("# This file needs to be populated with actual data\n")
                print(f"{Colors.YELLOW}[!] Created empty wordlist: {wordlist_path}{Colors.END}")
        
        return wordlist_path
    
    def list_available_wordlists(self) -> Dict[str, Dict[str, Dict[str, Union[str, bool, int]]]]:
        """List all available wordlists with their status"""
        available = {}
        
        for category, wordlists in self.WORDLISTS.items():
            available[category] = {}
            for name, info in wordlists.items():
                wordlist_path = self.wordlists_dir / info["path"]
                available[category][name] = {
                    "description": info["description"],
                    "exists": wordlist_path.exists(),
                    "size": wordlist_path.stat().st_size if wordlist_path.exists() else 0
                }
        
        return available
    
    def get_wordlist_stats(self, category: str, name: str) -> Optional[Dict[str, Union[str, int, float]]]:
        """Get statistics for a wordlist"""
        wordlist_path = self.get_wordlist(category, name)
        if not wordlist_path or not wordlist_path.exists():
            return None
        
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Filter out comments and empty lines
        words = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        
        if not words:
            return None
        
        lengths = [len(word) for word in words]
        unique_words = set(words)
        
        return {
            "path": str(wordlist_path),
            "size_bytes": wordlist_path.stat().st_size,
            "line_count": len(lines),
            "word_count": len(words),
            "unique_count": len(unique_words),
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "avg_length": sum(lengths) / len(lengths) if lengths else 0
        }
    
    def filter_wordlist(self, category: str, name: str, **filters) -> Optional[Path]:
        """Filter a wordlist based on criteria"""
        wordlist_path = self.get_wordlist(category, name)
        if not wordlist_path or not wordlist_path.exists():
            return None
        
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        
        # Apply filters
        filtered_words = words
        
        if filters.get('min_length'):
            filtered_words = [w for w in filtered_words if len(w) >= filters['min_length']]
            
        if filters.get('max_length'):
            filtered_words = [w for w in filtered_words if len(w) <= filters['max_length']]
            
        if filters.get('contains'):
            filtered_words = [w for w in filtered_words if filters['contains'].lower() in w.lower()]
            
        if filters.get('starts_with'):
            filtered_words = [w for w in filtered_words if w.lower().startswith(filters['starts_with'].lower())]
            
        if filters.get('ends_with'):
            filtered_words = [w for w in filtered_words if w.lower().endswith(filters['ends_with'].lower())]
        
        # Save filtered wordlist
        output_path = wordlist_path.parent / f"{wordlist_path.stem}_filtered.txt"
        with open(output_path, 'w') as f:
            for word in filtered_words:
                f.write(f"{word}\n")
        
        print(f"{Colors.GREEN}[+] Filtered {len(words)} -> {len(filtered_words)} words{Colors.END}")
        return output_path
    
    def download_popular_wordlists(self):
        """Download popular wordlists from the internet"""
        popular_lists = {
            "rockyou": "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt",
            "common_passwords": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt",
            "common_usernames": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/top-usernames-shortlist.txt"
        }
        
        for name, url in popular_lists.items():
            print(f"{Colors.BLUE}[*] Downloading {name}...{Colors.END}")
            try:
                response = requests.get(url, stream=True, timeout=30)
                if response.status_code == 200:
                    # Find appropriate category and path
                    for category, wordlists in self.WORDLISTS.items():
                        if name in wordlists:
                            output_path = self.wordlists_dir / wordlists[name]["path"]
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(output_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            print(f"{Colors.GREEN}[+] Downloaded {name} to {output_path}{Colors.END}")
                            break
                else:
                    print(f"{Colors.RED}[-] Failed to download {name}: HTTP {response.status_code}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}[-] Error downloading {name}: {e}{Colors.END}")
    
    def _generate_common_passwords(self, output_path: Path):
        """Generate a common password list"""
        passwords = [
            "123456", "password", "123456789", "12345678", "12345", "1234567",
            "qwerty", "abc123", "password1", "1234567890", "123123", "000000",
            "iloveyou", "1234", "1q2w3e4r5t", "qwertyuiop", "123", "monkey",
            "dragon", "654321", "superman", "1qaz2wsx", "123qwe", "zxcvbnm",
            "121212", "asdfgh", "654321", "666666", "987654321", "qazwsx",
            "admin", "password123", "welcome", "login", "master", "hello",
            "guest", "root", "administrator", "user", "test", "demo"
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Common passwords for testing\n")
            for password in passwords:
                f.write(f"{password}\n")
    
    def _generate_common_usernames(self, output_path: Path):
        """Generate a common username list"""
        usernames = [
            "admin", "administrator", "root", "user", "test", "guest", "demo",
            "service", "operator", "manager", "support", "help", "info", "mail",
            "www", "web", "apache", "nginx", "mysql", "postgres", "oracle",
            "mssql", "ftp", "ssh", "telnet", "backup", "monitor", "log"
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Common usernames for testing\n")
            for username in usernames:
                f.write(f"{username}\n")
    
    def _generate_directory_names(self, output_path: Path):
        """Generate common directory names"""
        directories = [
            "admin", "administrator", "login", "test", "demo", "backup", "config",
            "data", "db", "database", "files", "images", "img", "css", "js",
            "scripts", "includes", "lib", "tmp", "temp", "cache", "logs", "log",
            "uploads", "downloads", "docs", "documentation", "help", "support"
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Common directory names for testing\n")
            for directory in directories:
                f.write(f"{directory}\n")
    
    def _generate_subdomain_names(self, output_path: Path):
        """Generate common subdomain names"""
        subdomains = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1",
            "webdisk", "ns2", "cpanel", "whm", "autodiscover", "autoconfig",
            "m", "imap", "test", "ns", "blog", "pop3", "dev", "www2", "admin",
            "forum", "news", "vpn", "ns3", "mail2", "new", "mysql", "old",
            "www1", "beta", "exchange", "owa", "www3", "mssql", "mail1",
            "api", "secure", "staging", "demo", "support", "help", "shop"
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Common subdomain names for testing\n")
            for subdomain in subdomains:
                f.write(f"{subdomain}\n")
    
    def _generate_parameter_names(self, output_path: Path):
        """Generate common parameter names"""
        parameters = [
            "id", "user", "username", "password", "pass", "email", "name",
            "action", "cmd", "command", "file", "path", "dir", "page", "q",
            "query", "search", "term", "keyword", "url", "redirect", "return",
            "callback", "jsonp", "format", "type", "mode", "debug", "test"
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Common parameter names for testing\n")
            for param in parameters:
                f.write(f"{param}\n")

# Convenience functions for quick access
def get_passwords(name: str = "common_passwords") -> Optional[Path]:
    """Get password wordlist"""
    manager = WordlistManager()
    return manager.get_wordlist("passwords", name)

def get_usernames(name: str = "common_usernames") -> Optional[Path]:
    """Get username wordlist"""
    manager = WordlistManager()
    return manager.get_wordlist("usernames", name)

def get_directories(name: str = "dirbuster_2007_directory_list_2_3_medium") -> Optional[Path]:
    """Get directory wordlist"""
    manager = WordlistManager()
    return manager.get_wordlist("directories", name)

def get_subdomains(name: str = "dns_jhaddix") -> Optional[Path]:
    """Get subdomain wordlist"""
    manager = WordlistManager()
    return manager.get_wordlist("subdomains", name)

def get_fuzzing_payloads(name: str = "xss_jhaddix") -> Optional[Path]:
    """Get fuzzing payload wordlist"""
    manager = WordlistManager()
    return manager.get_wordlist("fuzzing", name)

if __name__ == "__main__":
    # CLI interface for wordlist management
    import argparse
    
    parser = argparse.ArgumentParser(description="BRAINTREE Wordlist Manager")
    parser.add_argument('--list', action='store_true', help='List available wordlists')
    parser.add_argument('--download', action='store_true', help='Download popular wordlists')
    parser.add_argument('--stats', help='Get statistics for wordlist (format: category:name)')
    parser.add_argument('--get', help='Get path to wordlist (format: category:name)')
    parser.add_argument('--filter', help='Filter wordlist (format: category:name)')
    parser.add_argument('--min-length', type=int, default=0, help='Minimum word length for filtering')
    parser.add_argument('--max-length', type=int, default=100, help='Maximum word length for filtering')
    parser.add_argument('--contains', help='Words must contain this string')
    parser.add_argument('--starts-with', help='Words must start with this string')
    parser.add_argument('--ends-with', help='Words must end with this string')
    
    args = parser.parse_args()
    
    manager = WordlistManager()
    
    if args.list:
        available = manager.list_available_wordlists()
        print(f"\n{Colors.BOLD}Available Wordlists ({sum(len(wl) for wl in available.values())} total):{Colors.END}")
        for category, wordlists in available.items():
            print(f"\n{Colors.CYAN}{category.upper()} ({len(wordlists)} wordlists):{Colors.END}")
            for name, info in wordlists.items():
                status = f"{Colors.GREEN}[+]{Colors.END}" if info["exists"] else f"{Colors.RED}[-]{Colors.END}"
                size = f"({info['size']} bytes)" if info["exists"] else "(not found)"
                print(f"  {status} {name} {size}")
                print(f"      {Colors.YELLOW}{info['description']}{Colors.END}")
    
    elif args.download:
        manager.download_popular_wordlists()
    
    elif args.stats:
        try:
            category, name = args.stats.split(':')
            stats = manager.get_wordlist_stats(category, name)
            if stats:
                print(f"\n{Colors.BOLD}Wordlist Statistics: {category}:{name}{Colors.END}")
                print(f"Path: {stats['path']}")
                print(f"Size: {stats['size_bytes']} bytes")
                print(f"Lines: {stats['line_count']}")
                print(f"Words: {stats['word_count']}")
                print(f"Unique words: {stats['unique_count']}")
                print(f"Average length: {stats['avg_length']:.1f} characters")
                print(f"Length range: {stats['min_length']}-{stats['max_length']} characters")
        except ValueError:
            print(f"{Colors.RED}[-] Use format: category:name{Colors.END}")
    
    elif args.get:
        try:
            category, name = args.get.split(':')
            path = manager.get_wordlist(category, name)
            if path:
                print(f"{path}")
        except ValueError:
            print(f"{Colors.RED}[-] Use format: category:name{Colors.END}")
    
    elif args.filter:
        try:
            category, name = args.filter.split(':')
            filtered_path = manager.filter_wordlist(
                category, name,
                min_length=args.min_length,
                max_length=args.max_length,
                contains=args.contains,
                starts_with=args.starts_with,
                ends_with=args.ends_with
            )
            if filtered_path:
                print(f"Filtered wordlist saved to: {filtered_path}")
        except ValueError:
            print(f"{Colors.RED}[-] Use format: category:name{Colors.END}")
    
    else:
        print("BRAINTREE Wordlist Manager")
        print("Use --help for available options")