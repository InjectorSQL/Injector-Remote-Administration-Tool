# Injector Remote Administration Tool

## 🚨 IMPORTANT LEGAL NOTICE

**This tool is for AUTHORIZED USE ONLY on systems you own or have explicit permission to manage.**

Unauthorized use of this tool to access, monitor, or control systems without proper authorization may violate:
- Computer Fraud and Abuse Act (CFAA) in the United States
- Computer Misuse Act in the United Kingdom
- Similar cybercrime laws in other jurisdictions
- Ethical guidelines and professional codes of conduct

**Use this tool responsibly and legally. The developers are not responsible for any misuse.**

---

## 📋 Overview

Injector is a Python-based remote administration tool with a client-server architecture designed for managing multiple Windows machines. It provides comprehensive remote management capabilities including file transfer, system monitoring, and visual capture.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Injector Server (Python)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ HTTP Server  │  │ Command      │  │ File Management      │  │
│  │ (Threaded)   │  │ Queue        │  │ (Upload/Download)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                 Interactive Menu System                   ││
│  │  - Color-coded ASCII interface                           ││
│  │  - Multi-client management                               ││
│  │  - Real-time command execution                           ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Remote Admin Client (VBScript)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Auto-       │  │ Command      │  │ File Transfer       │  │
│  │ Registration│  │ Execution    │  │ (Upload/Download)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  - Screenshot Capture (nircmd/PowerShell)                ││
│  │  - Webcam Capture (DirectShow/FFmpeg/fswebcam)            ││
│  │  - System Information Gathering                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Features

#### Core Functionality
- ✅ Multi-PC management capability
- ✅ Client-server architecture
- ✅ HTTP-based communication
- ✅ Multi-threading for concurrent connections
- ✅ Command queuing system
- ✅ Real-time result reporting

#### System Management
- ✅ System information gathering
- ✅ Running processes listing
- ✅ Drive information
- ✅ Directory listing
- ✅ Remote command execution
- ✅ Administrative command execution
- ✅ User messaging
- ✅ Remote reboot/shutdown/logoff

#### File Transfer
- ✅ Upload files to clients
- ✅ Download files from clients
- ✅ Base64 encoding for safe transfer
- ✅ Progress reporting
- ✅ Error handling

#### Visual Monitoring
- ✅ Screenshot capture (nircmd.exe preferred, PowerShell fallback)
- ✅ Webcam capture (DirectShow, FFmpeg, fswebcam fallbacks)
- ✅ Automatic timestamping
- ✅ Image viewing capability

---

## 🛠️ Installation & Setup

### Prerequisites

#### Server Requirements
- Python 3.6 or higher
- Windows, Linux, or macOS
- Network connectivity between server and clients

#### Client Requirements (Windows)
- Windows 7 or higher (Windows 10 recommended)
- PowerShell (for fallback methods)
- Optional: nircmd.exe for screenshot capture
- Optional: FFmpeg for webcam capture

---

### Server Setup

#### 1. Install Python Dependencies

```bash
# Clone or download the repository
cd injector-remote-admin

# No additional Python packages required!
# The server uses only standard library modules
```

#### 2. Create Directory Structure

The server will automatically create the following directories on first run:
```
./
├── uploads/          # Files to be sent to clients
├── downloads/        # Files received from clients
├── screenshots/      # Screenshot captures from clients
└── webcam/           # Webcam images from clients
```

#### 3. Start the Server

```bash
# Default port (8080)
python injector_server.py

# Custom port
python injector_server.py 8081

# With specific host (for remote access)
python injector_server.py 8080
```

#### 4. Server Options

| Argument | Description | Default |
|----------|-------------|---------|
| `[port]` | Server port number | 8080 |

---

### Client Setup

#### 1. Deploy the VBScript Client

Copy `remote_admin.vbs` to the target Windows machine(s).

#### 2. Run the Client

**Method 1: Double-click**
- Simply double-click the `remote_admin.vbs` file
- Uses default server URL: `http://localhost:8080`

**Method 2: Command Line**
```cmd
# Connect to local server
cscript remote_admin.vbs

# Connect to remote server
cscript remote_admin.vbs http://your-server-ip:8080

# Run minimized (no console window)
wscript remote_admin.vbs http://your-server-ip:8080
```

#### 3. Client Registration

- The client automatically registers with the server on first run
- A unique client ID is generated and saved to `injector_client_id.txt`
- The client maintains a persistent connection, polling for commands

---

## 🎯 Usage Guide

### Server Interface

The server provides an interactive color-coded menu system:

```
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

================================================================================
Injector Remote Administration Tool
Server running on port 8080
================================================================================

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

### Menu Options

#### 1. Send Command to Specific PC
- Select a specific client from the list
- Choose a command to execute
- Provide any required arguments
- Command is queued and sent to the selected client

#### 2. Send Command to All PCs
- Send the same command to all connected clients
- Useful for broadcast messages or system-wide operations

#### 3. View Command Results
- View results from executed commands
- Results are displayed with timestamps
- Automatically cleared after viewing

#### 4. View Screenshots
- Browse captured screenshots from clients
- Open screenshot files directly
- View file sizes and timestamps

#### 5. View Webcam Images
- Browse captured webcam images from clients
- Open image files directly
- View file sizes and timestamps

#### 6. Upload File to PC
- Select a file from the `uploads/` directory
- Send it to a specific client
- Client saves the file to its temporary directory

#### 7. Download File from PC
- Request a file from a client
- Specify the file path on the client
- File is saved to the `downloads/` directory on the server

#### 8. Exit
- Shutdown the server
- Exit the application

---

### Available Commands

| Command | Description | Arguments | Example |
|---------|-------------|----------|---------|
| `sysinfo` | Get system information | None | `sysinfo` |
| `processes` | List running processes | None | `processes` |
| `drives` | List available drives | None | `drives` |
| `dir` | List directory contents | `path` | `dir C:\` |
| `exec` | Execute command | `command` | `exec ipconfig /all` |
| `runas` | Run as administrator | `command` | `runas net user` |
| `msg` | Send message to user | `message` | `msg Hello from server` |
| `screenshot` | Capture screenshot | None | `screenshot` |
| `webcam` | Capture webcam image | None | `webcam` |
| `reboot` | Reboot system | None | `reboot` |
| `shutdown` | Shutdown system | None | `shutdown` |
| `logoff` | Log off user | None | `logoff` |
| `upload_file` | Upload file to client | `filename`, `data` | (Internal) |
| `download_file` | Download file from client | `path` | (Internal) |

---

### Command Examples

#### System Information
```
Command: sysinfo
Result:
System Information:
==================
Hostname: CLIENT-PC
Username: JohnDoe
OS: Windows 10
OS Version: 10.0.19045
OS Architecture: AMD64
Processor: Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz
Total Memory: 16384 MB
System Uptime: 2 days, 3 hours, 15 minutes, 30 seconds
Current Time: 12/15/2024 2:30:45 PM
```

#### Directory Listing
```
Command: dir C:\Users
Result:
Directory Listing: C:\Users
=================

Files:
------

Subdirectories:
---------------
  JohnDoe
  Public
  Default
  Default User
```

#### Execute Command
```
Command: exec ipconfig /all
Result:
Command Output:

Windows IP Configuration

   Host Name . . . . . . . . . . . . : CLIENT-PC
   Primary Dns Suffix  . . . . . . . : example.com
   Node Type . . . . . . . . . . . . : Hybrid
   IP Routing Enabled. . . . . . . . : No
   WINS Proxy Enabled. . . . . . . . : No
   DNS Suffix Search List. . . . . . : example.com

Ethernet adapter Ethernet:

   Connection-specific DNS Suffix  . : example.com
   Link-local IPv6 Address . . . . . : fe80::1234:5678:90ab:cdef%19
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1
```

---

## 📁 File Management

### Directory Structure

```
injector-remote-admin/
├── injector_server.py      # Main server script
├── remote_admin.vbs       # Client VBScript
├── README.md              # This documentation
├── uploads/               # Files to send to clients
│   └── example.txt        # Example upload file
├── downloads/             # Files received from clients
│   └── 20241215_143022_client123_file.txt
├── screenshots/           # Screenshot captures
│   └── screenshot_20241215_143022_client123.png
└── webcam/                # Webcam images
    └── webcam_20241215_143022_client123.jpg
```

### File Transfer Workflow

#### Upload to Client
1. Place file in `uploads/` directory on server
2. Select "Upload file to PC" from menu
3. Choose the file and target client
4. Client receives and saves the file

#### Download from Client
1. Select "Download file from PC" from menu
2. Specify file path on client
3. Client reads and sends the file
4. Server saves to `downloads/` directory

---

## 🎨 Visual Monitoring

### Screenshot Capture

The client captures screenshots using the following priority:

1. **nircmd.exe** (Preferred)
   - Fast and reliable
   - Download from: https://www.nirsoft.net/utils/nircmd.html
   - Place in `C:\Windows\` or `C:\Windows\System32\`

2. **PowerShell** (Fallback)
   - Uses .NET System.Drawing
   - Works on most Windows systems
   - No additional dependencies

### Webcam Capture

The client captures webcam images using the following priority:

1. **DirectShow (PowerShell)**
   - Native Windows media capture
   - Requires Windows 10+ for full functionality

2. **FFmpeg**
   - Cross-platform
   - Download from: https://ffmpeg.org/
   - Add to system PATH

3. **fswebcam**
   - Linux/WSL compatible
   - Install via package manager

### Viewing Captures

1. Select "View screenshots" or "View webcam images" from menu
2. Browse available images with timestamps
3. Select an image to open with default viewer
4. Or choose "open" to open the directory in file explorer

---

## 🔧 Configuration

### Server Configuration

Edit `injector_server.py` to customize:

```python
# Change default port
DEFAULT_PORT = 8080

# Change directory names
UPLOADS_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SCREENSHOTS_DIR = "screenshots"
WEBCAM_DIR = "webcam"

# Change color scheme
class Colors:
    HEADER = '\033[95m'    # Purple
    OKBLUE = '\033[94m'    # Blue
    OKGREEN = '\033[92m'   # Green
    WARNING = '\033[93m'   # Yellow
    FAIL = '\033[91m'      # Red
```

### Client Configuration

Edit `remote_admin.vbs` to customize:

```vbs
' Change default server URL
Const SERVER_URL = "http://localhost:8080"

' Change temporary directory
Const TEMP_DIR = "injector_temp"

' Change file names
Const SCREENSHOT_FILE = "injector_screenshot.png"
Const WEBCAM_FILE = "injector_webcam.jpg"
```

---

## 🛡️ Security Considerations

### ⚠️ WARNING: Security Limitations

This tool is designed for **authorized use only** in controlled environments. It has the following security considerations:

1. **No Authentication**: The server does not implement client authentication by default
2. **No Encryption**: Communication is not encrypted (HTTP, not HTTPS)
3. **No Authorization**: Any client can connect to the server
4. **Clear Text**: All commands and data are transmitted in clear text

### Security Recommendations

For production use, implement the following security measures:

#### 1. Network Security
- Run server on internal network only
- Use firewall rules to restrict access
- Consider using VPN for remote connections

#### 2. Authentication
- Add HTTP Basic Authentication
- Implement client certificates
- Use API keys for client registration

#### 3. Encryption
- Use HTTPS instead of HTTP
- Implement TLS/SSL certificates
- Encrypt sensitive data before transmission

#### 4. Authorization
- Implement client whitelisting
- Add IP-based access control
- Use role-based permissions

#### 5. Logging and Monitoring
- Enable detailed logging
- Monitor client connections
- Set up alerts for suspicious activity

---

## 🐛 Troubleshooting

### Common Issues

#### Server Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Change port or stop conflicting service |
| Permission denied | Run with administrator privileges |
| Module not found | Install required Python modules |
| Connection refused | Check firewall settings |

#### Client Issues

| Issue | Solution |
|-------|----------|
| Cannot connect to server | Verify server URL and network connectivity |
| Screenshot capture fails | Install nircmd.exe or enable PowerShell |
| Webcam capture fails | Install FFmpeg or check camera permissions |
| Command execution fails | Check user permissions on client |

### Debug Mode

Enable debug output in the server:

```python
# In injector_server.py, add debug logging
def log_debug(message):
    print(f"{Colors.OKBLUE}[DEBUG] {message}{Colors.ENDC}")
```

### Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check request parameters |
| 404 | Not Found | Verify endpoint URL |
| 500 | Server Error | Check server logs |
| 503 | Service Unavailable | Server is busy or down |

---

## 📊 Performance Optimization

### Server Performance

- **Thread Pool**: The server uses threading for concurrent connections
- **Command Queue**: Commands are queued and processed sequentially per client
- **Memory Usage**: Results are stored in memory and cleared after viewing

### Client Performance

- **Polling Interval**: Client polls for commands every 2 seconds
- **Heartbeat**: Client sends ping every 5 seconds
- **Cleanup**: Temporary files are cleaned up automatically

### Scalability

- **Maximum Clients**: Limited by system resources and thread pool
- **Command Throughput**: Depends on network latency and client processing speed
- **File Transfer**: Base64 encoding adds ~33% overhead to file size

---

## 🔄 Update History

### Version 1.0.0
- Initial release
- Basic client-server architecture
- Core command execution
- File transfer capabilities
- Screenshot and webcam capture
- Interactive menu system

---

## 📜 License

This project is provided as-is for educational and authorized use purposes only. No warranty is expressed or implied.

**Important**: Before using this tool, ensure you have proper authorization for all systems you intend to manage. Unauthorized use may result in legal consequences.

---

## 🙏 Acknowledgments

- Inspired by legitimate remote administration tools
- Built with Python's standard library
- VBScript client for maximum Windows compatibility
- Color-coded interface for better user experience

---

## 📞 Support

For issues, questions, or suggestions:

1. **Check this documentation** for setup and usage instructions
2. **Review the code** for implementation details
3. **Test in a controlled environment** before production use
4. **Ensure proper authorization** for all target systems

---

## ⚠️ FINAL WARNING

**THIS TOOL IS FOR AUTHORIZED USE ONLY.**

By using this software, you agree to:
1. Only use it on systems you own or have explicit permission to manage
2. Comply with all applicable laws and regulations
3. Respect privacy and ethical guidelines
4. Accept full responsibility for your actions

**The developers are not responsible for any misuse of this tool.**

---

*Last updated: December 2024*