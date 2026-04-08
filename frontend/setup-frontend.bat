@echo off
echo Setting up AI PriceOptima Frontend...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js found. Installing dependencies...

REM Clear npm cache to avoid issues
npm cache clean --force

REM Install dependencies with legacy peer deps to avoid version conflicts
npm install --legacy-peer-deps

if %errorlevel% neq 0 (
    echo ERROR: npm install failed. Trying alternative approach...
    
    REM Try with different registry
    npm install --registry https://registry.npmjs.org/ --legacy-peer-deps
    
    if %errorlevel% neq 0 (
        echo ERROR: Installation failed. Please try these manual steps:
        echo 1. Delete node_modules folder and package-lock.json
        echo 2. Run: npm install --legacy-peer-deps
        echo 3. If still fails, run: npm install --force
        pause
        exit /b 1
    )
)

echo.
echo Installation completed successfully!
echo.
echo Starting the frontend server...
echo The application will open at: http://localhost:3000
echo.
echo Make sure the backend is running on: http://localhost:8001
echo.

REM Start the development server
npm start

pause
