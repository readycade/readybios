@echo off
setlocal enabledelayedexpansion

:: Author Michael Cabral 2024
:: Title: readybios
:: GPL-3.0 license
:: Description: Extracts/Copies Bios files to Recalbox

::--------------------------------------------------------------------
::VARS::

set "extractPath=\\RECALBOX\share"
set "tempExtractPath=%~dp0Temp"
set "biosExtractPath=%APPDATA%\readycade\bios"
::--------------------------------------------------------------------

REM Check if a file path was passed as an argument
if "%~1"=="" (
    set /p "biosFile=Drag and drop the BIOS file here: "
    if "!biosFile!"=="" (
        echo No file path provided. Exiting script.
        pause
        exit /b
    )
) else (
    set "biosFile=%~1"
)

REM Display the dropped or input file path
echo You selected the file: !biosFile!

::--------------------------------------------------------------------
::CHANGE EZ_Bios.bat to EZ_Bios.exe when making for PRODUCTION!!! ::
REM Pass the selected file path to your main batch script (EZ_Bios.bat)
call EZ_Bios.bat "!biosFile!"
::--------------------------------------------------------------------

rem Author: Michael Cabral

endlocal