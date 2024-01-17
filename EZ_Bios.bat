@echo off
setlocal enabledelayedexpansion

::--------------------------------------------------------------------
::VARS::
set "extractPath=\\RECALBOX\share"
set "tempExtractPath=%~dp0Temp"
set "biosExtractPath=%APPDATA%\readycade\"
set "authURL=https://forum.readycade.com/auth.php"
::--------------------------------------------------------------------


::--------------------------------------------------------------------
::CHECK NETWORK SHARE::

echo Checking if the network share is available...
ping -n 1 RECALBOX >nul
if %errorlevel% neq 0 (
    echo Error: Could not connect to the network share \\RECALBOX.
    echo Please make sure you are connected to the network and try again.
    pause
    exit /b
)
echo.
::--------------------------------------------------------------------

::--------------------------------------------------------------------
::PROMPT FOR USERNAME AND PASSWORD (no echo for password)::

set /p "dbUsername=Enter your username: "
set "dbPassword="
powershell -Command "$dbPassword = Read-Host 'Enter your password' -AsSecureString; [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)) | Out-File -FilePath credentials.txt -Encoding ASCII"
set /p dbPassword=<credentials.txt
del credentials.txt

::--------------------------------------------------------------------

::DELETE THIS BEFORE PRODUCTION!!!!!!!!!::
::--------------------------------------------------------------------
:: To Debug username/password
::echo dbUsername=!dbUsername!
::echo dbPassword=!dbPassword!
::--------------------------------------------------------------------

::--------------------------------------------------------------------
::AUTHENTICATION::

rem Perform authentication by sending a POST request to auth.php using the captured credentials
curl -X POST -d "dbUsername=!dbUsername!&dbPassword=!dbPassword!" -H "Content-Type: application/x-www-form-urlencoded" "!authURL!" > auth_result.txt


rem Check the authentication result
set /p authResult=<auth_result.txt

if "!authResult!" neq "Authenticated" (
    echo Authentication failed. Exiting script...
    del auth_result.txt
    pause
    exit /b
) else (
    echo Authentication successful. Proceeding with installation...
    del auth_result.txt
)

echo.
echo.

::--------------------------------------------------------------------


::--------------------------------------------------------------------
::10 SECOND COUNTDOWN MESSAGE::

REM Wait for 10 seconds and display a countdown message
for /l %%A in (10,-1,1) do (
    cls
    REM Display important notice and warning
    echo "IMPORTANT NOTICE: You are about to extract BIOS files for Recalbox. These files may be protected by copyright laws and their usage might have legal implications. Make sure you have the legal rights to extract and use these files. By proceeding with this extraction, you acknowledge that you are solely responsible for any legal consequences that may arise from your actions."
    echo.
    echo "Readycade Inc and its affiliates are not responsible for any legal issues that may arise from the use of these files. Use at your own risk. We do not condone piracy or any unauthorized use of copyrighted material."
    echo.
    echo.
    echo "Thank you for choosing Readycade!"
    echo.
    echo Starting installation automatically in %%A seconds...
    timeout /t 1 >nul
)

::--------------------------------------------------------------------


::--------------------------------------------------------------------
::INSTALL 7-ZIP::

:: Define the installation directory for 7-Zip
set "installDir=C:\Program Files\7-Zip"

:: Define the 7-Zip version you want to download
set "version=2301"

:: Define the download URL for the specified version
set "downloadURL=https://www.7-zip.org/a/7z%version%-x64.exe"

:: Check if 7-Zip is already installed by looking for 7z.exe in the installation directory
if exist "!installDir!\7z.exe" (
    echo 7-Zip is already installed.
) else (
    :: Echo a message to inform the user about the script's purpose
    echo Downloading and installing 7-Zip...

    :: Define the local directory to save the downloaded installer
    set "localTempDir=%TEMP%"

    :: Download the 7-Zip installer using curl and retain the original name
    cd /d "%localTempDir%"
    curl -L --insecure -o "7z_installer.exe" "!downloadURL!"

    :: Check if the download was successful
    if %errorlevel% neq 0 (
        echo Download failed.
        exit /b %errorlevel%
    )

    :: Run the 7-Zip installer and wait for it to complete
    start /wait "" "7z_installer.exe"

    :: Check if the installation was successful (You may want to customize this part)
    if %errorlevel% neq 0 (
        echo Installation failed.
        exit /b %errorlevel%
    )

    :: Add your additional code here to run after the installation is complete
    echo 7-Zip is now installed.
)

::--------------------------------------------------------------------

::--------------------------------------------------------------------
::PASS FILE PATH WHEN DRAGGED ONTOP OF DRAG-AND-DROP.EXE::

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

REM Create a directory to extract the BIOS files
if not exist "%biosExtractPath%" (
    mkdir "%biosExtractPath%"
)
::--------------------------------------------------------------------

::--------------------------------------------------------------------
::EXTRACTION AND XCOPY TO NETWORK SHARE::

REM Extract the BIOS files using 7-Zip to the biosExtractPath
"C:\Program Files\7-Zip\7z.exe" x "!biosFile!" -o"%biosExtractPath%" -y

REM Add an echo message
echo Copying files to \\RECALBOX\share\bios...

REM Copy the extracted files to the network share
xcopy /Y /I /H /Q /E "%biosExtractPath%\*" "%extractPath%\"
::--------------------------------------------------------------------

::--------------------------------------------------------------------
:: CLEAN UP TEMP FILES::

REM Clean up the temporary extracted folder
rmdir /s /q "%biosExtractPath%"
::--------------------------------------------------------------------

::--------------------------------------------------------------------
::END MESSAGE WITH COUNTDOWN::

:: Wait for 10 seconds and display a countdown message
for /l %%A in (10,-1,1) do (
    cls
    echo Thank you for choosing Readycade!
    echo.
    echo Files copied to \\RECALBOX\bios successful!
    echo Please reboot your device now!
    echo.
    echo Exiting script automatically in %%A seconds...
    timeout /t 1 >nul
)

exit /b

rem Author: Michael Cabral

endlocal