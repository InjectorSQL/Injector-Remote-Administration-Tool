#!/usr/bin/env python3
"""
Injector Connection Test Script
===============================
Test script to verify server-client connectivity.

Usage:
    python test_connection.py [server_url]
    
Example:
    python test_connection.py http://localhost:8080
"""

import sys
import json
import requests
from urllib.parse import urljoin

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def test_server_connection(server_url):
    """Test connection to the Injector server."""
    print(f"{Colors.OKBLUE}[*] Testing connection to: {server_url}{Colors.ENDC}")
    
    try:
        # Test basic connectivity
        response = requests.get(server_url, timeout=5)
        print(f"{Colors.OKGREEN}[+] Server is reachable{Colors.ENDC}")
        print(f"    Status: {response.status_code}")
        print(f"    Headers: {dict(response.headers)}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}[-] Connection failed: Server not reachable{Colors.ENDC}")
        return False
    except requests.exceptions.Timeout:
        print(f"{Colors.FAIL}[-] Connection timeout{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"{Colors.FAIL}[-] Connection error: {str(e)}{Colors.ENDC}")
        return False

def test_register_endpoint(server_url):
    """Test the client registration endpoint."""
    url = urljoin(server_url, "/register?id=test_client")
    print(f"{Colors.OKBLUE}[*] Testing registration endpoint: {url}{Colors.ENDC}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.OKGREEN}[+] Registration endpoint working{Colors.ENDC}")
            print(f"    Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"{Colors.FAIL}[-] Registration failed: {response.status_code}{Colors.ENDC}")
            return False
    except Exception as e:
        print(f"{Colors.FAIL}[-] Registration error: {str(e)}{Colors.ENDC}")
        return False

def test_command_endpoint(server_url, client_id="test_client"):
    """Test the command endpoint."""
    url = urljoin(server_url, f"/command?id={client_id}")
    print(f"{Colors.OKBLUE}[*] Testing command endpoint: {url}{Colors.ENDC}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.OKGREEN}[+] Command endpoint working{Colors.ENDC}")
            print(f"    Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"{Colors.FAIL}[-] Command endpoint failed: {response.status_code}{Colors.ENDC}")
            return False
    except Exception as e:
        print(f"{Colors.FAIL}[-] Command endpoint error: {str(e)}{Colors.ENDC}")
        return False

def test_ping_endpoint(server_url, client_id="test_client"):
    """Test the ping endpoint."""
    url = urljoin(server_url, f"/ping?id={client_id}")
    print(f"{Colors.OKBLUE}[*] Testing ping endpoint: {url}{Colors.ENDC}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.OKGREEN}[+] Ping endpoint working{Colors.ENDC}")
            print(f"    Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"{Colors.FAIL}[-] Ping failed: {response.status_code}{Colors.ENDC}")
            return False
    except Exception as e:
        print(f"{Colors.FAIL}[-] Ping error: {str(e)}{Colors.ENDC}")
        return False

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
    print(f"Injector Connection Test Tool{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    # Parse command line arguments
    server_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    print(f"{Colors.OKBLUE}[*] Server URL: {server_url}{Colors.ENDC}\n")
    
    # Run tests
    results = []
    
    # Test 1: Basic connectivity
    results.append(("Server Connection", test_server_connection(server_url)))
    
    # Test 2: Registration endpoint
    results.append(("Registration Endpoint", test_register_endpoint(server_url)))
    
    # Test 3: Command endpoint
    results.append(("Command Endpoint", test_command_endpoint(server_url)))
    
    # Test 4: Ping endpoint
    results.append(("Ping Endpoint", test_ping_endpoint(server_url)))
    
    # Summary
    print(f"\n{Colors.HEADER}Test Summary:{Colors.ENDC}")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.OKGREEN}[PASS]{Colors.ENDC}" if result else f"{Colors.FAIL}[FAIL]{Colors.ENDC}"
        print(f"  {status} {test_name}")
    
    print(f"\n{Colors.OKBLUE}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}[+] All tests passed! Server is ready.{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}[!] Some tests failed. Check server status.{Colors.ENDC}")

if __name__ == '__main__':
    try:
        import requests
    except ImportError:
        print(f"{Colors.FAIL}[-] requests module not found{Colors.ENDC}")
        print(f"{Colors.OKBLUE}[*] Install with: pip install requests{Colors.ENDC}")
        sys.exit(1)
    
    main()