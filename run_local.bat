@echo off
:: ============================================================
:: run_local.bat  —  starts backend + frontend
:: Double-click this file OR run it in Command Prompt
:: ============================================================

title RAG Chatbot — Local Dev

echo.
echo  ==========================================
echo   RAG Chatbot — Windows Local Dev Startup
echo  ==========================================
echo.

:: ── Check Python ────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Please install Python 3.11 from https://python.org
    echo Make sure to tick "Add Python to PATH" during install
    pause
    exit /b 1
)

:: ── Check Node ──────────────────────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found.
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

:: ── Backend setup ───────────────────────────────────────────
echo [1/4] Setting up Python backend...
cd backend

if not exist ".env" (
    copy .env.example .env >nul
    echo.
    echo  [!] Created backend\.env from template.
    echo      You MUST fill in your API keys before continuing.
    echo      Open backend\.env in Notepad and add:
    echo        SUPABASE_URL
    echo        SUPABASE_SERVICE_KEY
    echo        GROQ_API_KEY
    echo        GEMINI_API_KEY
    echo.
    echo  Opening backend\.env in Notepad now...
    start notepad .env
    echo.
    pause
)

if not exist "venv\" (
    echo [2/4] Creating Python virtual environment ^(first time only^)...
    python -m venv venv
)

echo [3/4] Installing Python packages...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo  Starting FastAPI backend on http://localhost:8000 ...
start "RAG Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

cd ..

:: ── Frontend setup ──────────────────────────────────────────
echo [4/4] Setting up Next.js frontend...
cd frontend

if not exist ".env.local" (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
    echo  Created frontend\.env.local
)

if not exist "node_modules\" (
    echo  Installing Node packages ^(first time only, ~1 min^)...
    call npm install
)

echo.
echo  Starting Next.js frontend on http://localhost:3000 ...
start "RAG Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

cd ..

:: ── Done ────────────────────────────────────────────────────
echo.
echo  ==========================================
echo   Both servers are starting up!
echo.
echo   Frontend  ^>  http://localhost:3000
echo   Backend   ^>  http://localhost:8000
echo   API Docs  ^>  http://localhost:8000/docs
echo   Ping      ^>  http://localhost:8000/ping
echo.
echo   Two new terminal windows have opened —
echo   one for backend, one for frontend.
echo   Close them to stop the servers.
echo  ==========================================
echo.
pause
