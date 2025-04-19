@echo off
echo Checking MongoDB installation...

REM Check if MongoDB is installed
where mongod >nul 2>&1
if %errorLevel% == 0 (
    echo MongoDB is installed and in PATH
    mongod --version
) else (
    echo MongoDB is not found in PATH
    echo Please install MongoDB from https://www.mongodb.com/try/download/community
    echo Make sure to check "Install MongoDB as a Service" during installation
    pause
    exit /b 1
)

REM Check if MongoDB service exists
sc query MongoDB >nul 2>&1
if %errorLevel% == 0 (
    echo MongoDB service exists
) else (
    echo MongoDB service does not exist
    echo This suggests MongoDB was not installed as a service
    echo Please reinstall MongoDB and check "Install MongoDB as a Service"
    pause
    exit /b 1
)

REM Check if data directory exists
if not exist "C:\data\db" (
    echo Creating MongoDB data directory...
    mkdir "C:\data\db"
    if %errorLevel% == 0 (
        echo Data directory created successfully
    ) else (
        echo Failed to create data directory
        echo Please create it manually: mkdir "C:\data\db"
    )
) else (
    echo MongoDB data directory exists
)

echo.
echo TROUBLESHOOTING STEPS:
echo 1. Make sure MongoDB is installed correctly
echo 2. Try starting MongoDB manually:
echo    "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath="C:\data\db"
echo 3. Check if MongoDB service is running in Services (services.msc)
echo 4. If service won't start, try reinstalling MongoDB
echo.
echo Press any key to exit...
pause >nul 