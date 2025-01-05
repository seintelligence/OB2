@echo off
setlocal enabledelayedexpansion

:: Create/clean the destination directory
set "destdir=for Claude"
if exist "%destdir%" (
    echo Cleaning existing directory...
    del /Q "%destdir%\*.*" 2>nul
) else (
    mkdir "%destdir%"
)

:: Counter for copied files
set /a count=0

:: Store the full path of the destination directory to exclude it
for %%I in ("%destdir%") do set "fullpath=%%~fI"

echo Copying Python files...

:: Loop through all .py files in current directory and subdirectories
for /r %%F in (*.py) do (
    :: Check if the file is not in the destination directory
    set "filepath=%%~dpF"
    if /I not "!filepath:%fullpath%=!"=="!filepath!" (
        rem Skip files in destination directory
    ) else (
        set /a count+=1
        :: Get the filename only
        set "filename=%%~nxF"
        :: Copy file to destination
        copy "%%F" "%destdir%\!filename!" >nul
        echo Copied: !filename!
    )
)

:: Display summary
echo.
echo Finished copying !count! Python files to '%destdir%' folder.
echo.

pause