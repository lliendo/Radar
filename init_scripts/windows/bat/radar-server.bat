REM setLOCAL
REM set PATH=%PATH%;ACA PUEDO AGREGAR OTRO path que necesite.

set desc="Radar server"
set name="radar-server"
set service="%name%.py"
set service_args="-c C:\Program Files\Radar\Server\Config\main.yml"
set pidfile="C:\Program Files\Radar\Server\%pidfile%.pid"

set action=%1

if "%action%"=="start" call :start
if "%action%"=="stop" call :stop
if "%action%"=="restart" call :restart
call :help


:start
    if not exist %pidfile% (
        start %service% %service_args%
    ) else (
        echo "%desc% seems to be running. If that's not the case then remove : %pidfile%."
    )
exit /b 0


:stop
    if exist %pidfile% (
        set /p pid=<%pidfile%
        taskkill /pid %pid%
    ) else (
        echo "%desc% seems to be stopped."
    )
exit /b 0

REM Yes, we're duplicating code here... We can't reuse the ':start' and ':stop' calls.
:restart
    if exist %pidfile% (
        set /p pid=<%pidfile%
        taskkill /pid %pid%
    ) else (
        echo "%desc% seems to be stopped."
    )

    if not exist %pidfile% (
        start %service% %service_args%
    ) else (
        echo "%desc% seems to be running. If that's not the case then remove : %pidfile%."
    )
exit /b 0


:help
    echo "Usage : %name%.bat ^(start ^| stop^). Starts or stops the %desc%."
exit /b 0
