$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\InterviewAssistant.lnk")
$Shortcut.TargetPath = "C:\Users\Fernando\OneDrive\Desktop\Proyectos\interview_assistant\dist\InterviewAssistant.exe"
$Shortcut.WorkingDirectory = "C:\Users\Fernando\OneDrive\Desktop\Proyectos\interview_assistant\dist"
$Shortcut.Save()
Write-Host "Shortcut created at $DesktopPath\InterviewAssistant.lnk"
