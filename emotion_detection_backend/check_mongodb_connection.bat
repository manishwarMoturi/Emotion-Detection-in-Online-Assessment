@echo off
echo Checking MongoDB connection...

REM Set MongoDB path
set MONGOSH_PATH="C:\Program Files\MongoDB\mongosh-2.3.5-win32-x64\bin\mongosh.exe"

REM Check if mongosh exists
if not exist %MONGOSH_PATH% (
    echo MongoDB Shell not found at: %MONGOSH_PATH%
    echo Please make sure MongoDB Shell is installed correctly
    pause
    exit /b 1
)

echo Attempting to connect to MongoDB...
%MONGOSH_PATH% --eval "db.version()"

if %errorLevel% == 0 (
    echo.
    echo MongoDB is running and accessible!
    echo You can connect to it at: mongodb://localhost:27017
) else (
    echo.
    echo Failed to connect to MongoDB
    echo Error code: %errorLevel%
)

echo.
echo Press any key to exit...
pause >nul 