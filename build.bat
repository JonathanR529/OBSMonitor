@echo off
set /p AO3_PATH=Enter the full path to the 'accessible_output3' site-packages folder:
if not exist "%AO3_PATH%" (
    echo The path "%AO3_PATH%" does not exist. Exiting.
    pause
    exit /b
)
if exist OBS_Monitor_Win (
    rmdir /s /q OBS_Monitor_Win
)
md OBS_Monitor_Win
echo Building...
python -m nuitka --no-progress --quiet --standalone --windows-console-mode=disable monitor.py
xcopy /E /I /Q monitor.dist OBS_Monitor_Win
md OBS_Monitor_Win\accessible_output3
md OBS_Monitor_Win\accessible_output3\lib
xcopy /E /I /Q "%AO3_PATH%\lib" OBS_Monitor_Win\accessible_output3\lib
if exist monitor.build (
    rmdir /s /q monitor.build
)
if exist monitor.dist (
    rmdir /s /q monitor.dist
)
if exist OBS_Monitor_Win.zip (
    del OBS_Monitor_Win.zip
)
echo Creating ZIP archive...
7z a -tzip OBS_Monitor_Win.zip OBS_Monitor_Win\ >nul
echo Build and packaging complete!
pause