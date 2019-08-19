@echo off

if not exist "%appdata%\24u" mkdir "%appdata%\24u"


@echo off

if not exist "%appdata%\24u\LogMonitor" mkdir "%appdata%\24u\LogMonitor"



@echo off
set locpath=%~dp0
@set path=%locpath:~0,-1%



@echo off

%systemroot%\System32\xcopy /y/s "%path%" "%appdata%\24u\LogMonitor"



@echo off

set "path=%appdata%\24u\LogMonitor\"

echo ***********************************************************************************************
echo To install the script LogMonitor needs Your username, password and path to python3 executable:
@echo off

set /p username="Enter Username: "



@echo off
set "psCommand=%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\powershell.exe -Command "$pword = read-host 'Enter Password: ' -AsSecureString ; ^
    $BSTR=[System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pword); ^
        [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)""
for /f "usebackq delims=" %%p in (`%psCommand%`) do set password=%%p



@echo off 

setlocal enableextensions disabledelayedexpansion



set "search=^<Command^>^</Command^>"

set "replace=^<Command^>%path%LogMonitorStart.bat^</Command^>"



set "textFile=%path%task.xml"



for /f "delims=" %%i in ('type "%textFile%" ^& break ^> "%textFile%" ') do (
    set "line=%%i"
    setlocal enabledelayedexpansion
    >>"%textFile%" echo(!line:%search%=%replace%!
    endlocal
)



set "search=^<WorkingDirectory^>^</WorkingDirectory^>"

set "replace=^<WorkingDirectory^>%path%^</WorkingDirectory^>"

for /f "delims=" %%i in ('type "%textFile%" ^& break ^> "%textFile%" ') do (
    set "line=%%i"
    setlocal enabledelayedexpansion
    >>"%textFile%" echo(!line:%search%=%replace%!
    endlocal
)




set /p pythonPath="Enter executable python3 path: "

@echo @echo off>%path%LogMonitorStart.bat
@echo cd %path%>>%path%LogMonitorStart.bat
@echo %pythonPath% LogMonitor.py>>%path%LogMonitorStart.bat


%SystemRoot%\explorer.exe "%appdata%\24u\LogMonitor"
start notepad "%appdata%\24u\LogMonitor\LogMonitorConfig.txt"


@echo - ! -

@echo For Log Monitor to work properly it is necessary to update the LogMonitorConfig.txt configuration file.
@echo Please confirm when done.

@echo - ! -

@PAUSE

@echo off
%systemroot%\System32\schtasks.exe /Create /XML %textFile% /tn LogMonitor /RU %username% /RP %password%
