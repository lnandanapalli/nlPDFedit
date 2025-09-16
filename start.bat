@echo off
echo 🚀 PDF Chat Assistant Quick Start
echo ===================================

echo.
echo 📋 Checking requirements...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

echo ✅ Python and Node.js found

REM Check if backend virtual environment exists
if not exist "backend\venv" (
    echo 📦 Creating backend virtual environment...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    cd ..
)

REM Setup backend
echo 🔧 Setting up backend...
cd backend
call venv\Scripts\activate.bat
echo 📥 Installing backend dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)

REM Check for OpenAI API key
if not exist ".env" (
    echo.
    echo ⚠️  Warning: No .env file found!
    echo Please create backend\.env with your OpenAI API key:
    echo OPENAI_API_KEY=your_key_here
    echo.
    echo You can continue without it but AI features won't work.
    pause
)

echo 🚀 Starting backend server...
start /B python main.py
cd ..

REM Setup frontend
echo 🔧 Setting up frontend...
cd frontend
if not exist "node_modules" (
    echo 📥 Installing frontend dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

echo 🚀 Starting frontend server...
start /B npm start

echo.
echo ✅ PDF Chat Assistant is starting!
echo.
echo 🌐 URLs:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo 💡 The frontend will open automatically in your browser
echo 🛑 Press any key to stop both servers

pause

echo 🛑 Stopping servers...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo ✅ Servers stopped
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️ Creating .env file...
    copy .env.example .env >nul 2>&1
    echo ⚠️  Please edit .env file and add your OpenAI API key
    echo.
    pause
)

REM Start the application
echo 🚀 Starting PDF Assistant...
echo 💡 The application will open in your default web browser
echo 🌐 URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py

pause