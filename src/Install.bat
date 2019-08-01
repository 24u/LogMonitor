@echo off

set locpath=%~dp0


set pathToBat="%locpath%LogMonitor\.install_log_monitor.bat"

@echo off
%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\powershell.exe -command "Start-Process '%pathToBat%' -Verb runas"