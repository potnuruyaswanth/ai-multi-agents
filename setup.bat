@echo off
REM ================================================================
REM AI Productivity Assistant - Local Setup for Windows
REM ================================================================

setlocal enabledelayedexpansion

set "CYAN=[36m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "RED=[31m"
set "RESET=[0m"

echo !CYAN!========================================!RESET!
echo !CYAN!AI Productivity Assistant - Setup!RESET!
echo !CYAN!========================================!RESET!
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if "%errorlevel%"=="0" (
    for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VERSION=%%i"
    echo !GREEN!✓ Python installed: !PYTHON_VERSION!!RESET!
) else (
    echo !RED!✗ Python not installed!RESET!
    echo Please install Python 3.11+ from https://www.python.org/
    exit /b 1
)

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if "%errorlevel%"=="0" (
    for /f "tokens=*" %%i in ('node --version') do set "NODE_VERSION=%%i"
    echo !GREEN!✓ Node.js installed: !NODE_VERSION!!RESET!
) else (
    echo !YELLOW!⚠ Node.js not installed!RESET!
    echo Install from https://nodejs.org/ for frontend development
)

REM Setup backend
echo.
echo Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo !GREEN!✓ Virtual environment created!RESET!
) else (
    echo !YELLOW!⚠ Virtual environment already exists!RESET!
)

call venv\Scripts\activate.bat
echo !GREEN!✓ Virtual environment activated!RESET!

echo Installing dependencies...
pip install -r requirements.txt > nul 2>&1
echo !GREEN!✓ Dependencies installed!RESET!

cd ..

REM Setup frontend
if exist "frontend\package.json" (
    echo.
    echo Setting up frontend...
    cd frontend
    
    if not exist "node_modules" (
        echo Installing npm packages...
        call npm install > nul 2>&1
        echo !GREEN!✓ Frontend dependencies installed!RESET!
    ) else (
        echo !YELLOW!⚠ Node modules already installed!RESET!
    )
    
    cd ..
)

REM Create .env files
echo.
echo Creating environment files...

if not exist "backend\.env" (
    copy backend\.env.example backend\.env
    echo !GREEN!✓ Created backend\.env!RESET!
    echo !YELLOW!⚠ Please edit backend\.env with your configuration!RESET!
) else (
    echo !YELLOW!⚠ backend\.env already exists!RESET!
)

if not exist "frontend\.env" (
    echo VITE_API_BASE=http://localhost:8000 > frontend\.env
    echo !GREEN!✓ Created frontend\.env!RESET!
) else (
    echo !YELLOW!⚠ frontend\.env already exists!RESET!
)

REM Check Docker
echo.
echo !CYAN!========================================!RESET!
echo Checking Docker installation...
docker --version >nul 2>&1
if "%errorlevel%"=="0" (
    echo !GREEN!✓ Docker is installed!RESET!
    
    echo.
    echo How would you like to run the services?
    echo 1) Using Docker Compose (recommended)
    echo 2) Manual setup (requires MongoDB running)
    echo 3) Just setup, don't start services
    set /p choice="Choose an option (1-3): "
    
    if "!choice!"=="1" (
        echo Starting services with Docker Compose...
        docker-compose up -d
        echo !GREEN!✓ Services started!RESET!
        echo.
        echo !CYAN!Services are running:!RESET!
        echo Backend: http://localhost:8000
        echo Frontend: http://localhost:5173
        echo API Docs: http://localhost:8000/docs
    ) else if "!choice!"=="2" (
        echo.
        echo Make sure MongoDB is running on localhost:27017
        echo.
        echo Starting backend...
        cd backend
        call venv\Scripts\activate.bat
        start "AI Assistant Backend" cmd /k "uvicorn api.main:app --reload"
        cd ..
        
        echo Starting frontend...
        cd frontend
        start "AI Assistant Frontend" cmd /k "npm run dev"
        cd ..
        
        echo !GREEN!✓ Services started in separate windows!RESET!
    ) else (
        echo !GREEN!✓ Setup complete!RESET!
        echo Manual start services when ready
    )
) else (
    echo !YELLOW!⚠ Docker not installed!RESET!
    echo Install from https://www.docker.com/products/docker-desktop
    echo.
    echo To start services manually:
    echo 1. Make sure MongoDB is running on localhost:27017
    echo 2. In terminal 1: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn api.main:app --reload
    echo 3. In terminal 2: cd frontend ^&^& npm run dev
)

echo.
echo !GREEN!Setup complete!RESET!
echo Documentation: See README.md for more information
echo.
pause
