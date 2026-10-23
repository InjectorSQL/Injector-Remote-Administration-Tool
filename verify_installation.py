#!/usr/bin/env python3
"""
Injector Installation Verification Script
==========================================
Verify that all required files are present and the installation is complete.

Usage:
    python verify_installation.py
"""

import os
import sys

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Required files
REQUIRED_FILES = {
    'Python Server': [
        'injector_server.py',
        'client_manager.py',
        'test_connection.py'
    ],
    'VBScript Client': [
        'remote_admin.vbs'
    ],
    'Windows Utilities': [
        'setup.bat'
    ],
    'Configuration': [
        'requirements.txt'
    ],
    'Documentation': [
        'README.md',
        'SETUP_GUIDE.md',
        'INDEX.md'
    ]
}

# Required directories (will be created by server on first run)
REQUIRED_DIRS = [
    'uploads',
    'downloads',
    'screenshots',
    'webcam'
]

def check_files():
    """Check that all required files exist."""
    print(f"{Colors.OKBLUE}[*] Checking required files...{Colors.ENDC}\n")
    
    all_good = True
    
    for category, files in REQUIRED_FILES.items():
        print(f"{Colors.HEADER}{category}:{Colors.ENDC}")
        for filename in files:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {filename} ({size} bytes)")
            else:
                print(f"  {Colors.FAIL}✗{Colors.ENDC} {filename} {Colors.FAIL}(MISSING){Colors.ENDC}")
                all_good = False
        print()
    
    return all_good

def check_directories():
    """Check that required directories exist or can be created."""
    print(f"{Colors.OKBLUE}[*] Checking required directories...{Colors.ENDC}\n")
    
    all_good = True
    
    for directory in REQUIRED_DIRS:
        if os.path.exists(directory):
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {directory}/ (exists)")
        else:
            print(f"  {Colors.WARNING}⚠{Colors.ENDC} {directory}/ (will be created on first run)")
    
    print()
    return all_good

def check_python():
    """Check Python installation."""
    print(f"{Colors.OKBLUE}[*] Checking Python installation...{Colors.ENDC}\n")
    
    try:
        import sys
        version = sys.version.split()[0]
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Python {version} found")
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Python path: {sys.executable}")
        print()
        return True
    except Exception as e:
        print(f"  {Colors.FAIL}✗{Colors.ENDC} Python not found: {str(e)}")
        print()
        return False

def check_standard_library():
    """Check that required standard library modules are available."""
    print(f"{Colors.OKBLUE}[*] Checking Python standard library modules...{Colors.ENDC}\n")
    
    required_modules = [
        'os',
        'sys',
        'json',
        'base64',
        'socket',
        'threading',
        'time',
        'shutil',
        'datetime',
        'platform',
        'subprocess',
        'hashlib',
        'http.server',
        'socketserver',
        'urllib.parse',
        'cgi'
    ]
    
    all_good = True
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {module}")
        except ImportError:
            print(f"  {Colors.FAIL}✗{Colors.ENDC} {module} {Colors.FAIL}(MISSING){Colors.ENDC}")
            all_good = False
    
    print()
    return all_good

def check_optional_packages():
    """Check for optional packages."""
    print(f"{Colors.OKBLUE}[*] Checking optional packages...{Colors.ENDC}\n")
    
    optional_packages = {
        'requests': 'For connection testing (test_connection.py)',
        'zipfile': 'For creating deployment packages (built-in)',
        'json': 'For configuration management (built-in)'
    }
    
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {package} - {description}")
        except ImportError:
            print(f"  {Colors.WARNING}⚠{Colors.ENDC} {package} - {description} (optional)")
    
    print()

def display_summary():
    """Display verification summary."""
    print(f"{Colors.HEADER}")
    print("=" * 60)
    print("  INSTALLATION VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"{Colors.ENDC}\n")
    
    print(f"{Colors.OKBLUE}Required Files:{Colors.ENDC}")
    files_ok = check_files()
    
    print(f"{Colors.OKBLUE}Required Directories:{Colors.ENDC}")
    dirs_ok = check_directories()
    
    print(f"{Colors.OKBLUE}Python Installation:{Colors.ENDC}")
    python_ok = check_python()
    
    print(f"{Colors.OKBLUE}Standard Library Modules:{Colors.ENDC}")
    stdlib_ok = check_standard_library()
    
    print(f"{Colors.OKBLUE}Optional Packages:{Colors.ENDC}")
    check_optional_packages()
    
    # Final verdict
    print(f"{Colors.HEADER}")
    print("=" * 60)
    print("  FINAL VERDICT")
    print("=" * 60)
    print(f"{Colors.ENDC}\n")
    
    if files_ok and python_ok and stdlib_ok:
        print(f"{Colors.OKGREEN}✓ ALL CHECKS PASSED!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Your Injector installation is ready to use.{Colors.ENDC}\n")
        print(f"{Colors.OKBLUE}Next Steps:{Colors.ENDC}")
        print(f"  1. Start the server: python injector_server.py")
        print(f"  2. Deploy clients: Copy remote_admin.vbs to target machines")
        print(f"  3. Run clients: cscript remote_admin.vbs http://your-server-ip:8080")
        print(f"  4. Test connection: python test_connection.py http://localhost:8080")
    else:
        print(f"{Colors.WARNING}⚠ SOME CHECKS FAILED{Colors.ENDC}")
        print(f"{Colors.WARNING}Please review the output above and fix any issues.{Colors.ENDC}\n")
        if not files_ok:
            print(f"{Colors.FAIL}  - Missing required files{Colors.ENDC}")
        if not python_ok:
            print(f"{Colors.FAIL}  - Python not installed or not in PATH{Colors.ENDC}")
        if not stdlib_ok:
            print(f"{Colors.FAIL}  - Missing required Python modules{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

def main():
    """Main entry point."""
    print(f"{Colors.HEADER}")
    print(r"""
  _____ _ _       _____ _____ ____  _   _ _____ ____
 |_   _| | | ___ |_   _| ____|  _ \| | | |_   _|  _ \
   | | | | |/ _ \  | | |  _| | |_) | | | | | | | |_) |
   | | | |_|  __/  | | | |___|  _ <| |_| | | | |  _ <
   |_|  \___|\___|  |_| |_____|_| \_\\___/  |_| |_| \_\
    """)
    print(f"Injector Installation Verification Tool{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")
    
    display_summary()

if __name__ == '__main__':
    main()