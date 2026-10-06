param(
    [string]$HostAddress = "127.0.0.1",
    [int]$ControlPort = 8081,
    [int]$GuiPort = 8000
)

$pythonExe = "C:\Program Files\Python312\pythonw.exe"
$trayScript = "C:\_Local_DEV\repos\bach\system\hub\_services\chat\chat_tray.py"
Start-Process -FilePath $pythonExe -ArgumentList @($trayScript, "--host", $HostAddress, "--port", "$ControlPort", "--gui-port", "$GuiPort", "--remote", "--brand", "ocean")
